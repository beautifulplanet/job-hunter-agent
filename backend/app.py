from backend.lib.pii_scrubber import PIIScrubber
from backend.lib.resume_parser import extract_text
from backend.lib.jd_scraper import scrape_jd
from backend.lib.prompt_builder import build_master_prompt, build_cover_letter_prompt

import os
import glob
import yaml

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'config.yaml')
RESUMES_DIR = os.path.join(BASE_DIR, "resumes")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def _load_config() -> dict:
    """Load configuration from config.yaml."""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


class JobHunter:
    def __init__(self, resume_path=None):
        self.config = _load_config()
        candidate = self.config['candidate']

        # Resolve resume path from config or argument
        if resume_path:
            self.resume_path = resume_path
        else:
            self.resume_path = os.path.join(
                BASE_DIR, self.config['resumes']['primary']
            )

        self.scrubber = PIIScrubber()
        self.scrubbed_resume = ""
        self.additional_experience = ""

        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def _load_primary_resume(self):
        """Parse and scrub the primary resume."""
        if not self.scrubbed_resume:
            print(f"  Parsing primary resume: {os.path.basename(self.resume_path)}...")
            raw = extract_text(self.resume_path)

            candidate = self.config['candidate']

            # Register known PII from config (not hardcoded)
            self.scrubber.register_name(candidate['full_name'])
            if candidate.get('address'):
                self.scrubber.register_address(candidate['address'])

            # Register sensitive URLs from config
            for url_entry in candidate.get('sensitive_urls', []):
                self.scrubber.register_custom(
                    url_entry['term'],
                    url_entry['placeholder']
                )

            self.scrubbed_resume = self.scrubber.scrub(raw)
            print(self.scrubber.get_report())

    def _load_old_resumes(self):
        """Parse old resumes for supplementary experience bullets."""
        if self.additional_experience:
            return  # Already loaded

        print(f"  Scanning old resumes in: {RESUMES_DIR}...")
        max_chars = self.config.get('resumes', {}).get('old_resume_max_chars', 2000)

        # Track seen content to avoid duplicates
        seen_bullets = set()
        parts = []
        resume_num = 0

        for fpath in glob.glob(os.path.join(RESUMES_DIR, "*.docx")):
            try:
                resume_num += 1
                text = extract_text(fpath)
                scrubbed = self.scrubber.scrub(text)

                # Deduplicate: only include lines we haven't seen yet
                unique_lines = []
                for line in scrubbed.split('\n'):
                    stripped = line.strip()
                    if len(stripped) < 20:
                        continue  # skip very short lines (headers, blanks)
                    # Normalize for comparison (lowercase, strip punctuation)
                    normalized = stripped.lower().replace(',', '').replace('.', '')
                    if normalized not in seen_bullets:
                        seen_bullets.add(normalized)
                        unique_lines.append(stripped)

                if unique_lines:
                    content = '\n'.join(unique_lines[:30])  # max 30 unique lines per resume
                    parts.append(f"### Prior Resume Version {resume_num}\n{content[:max_chars]}")
            except Exception as e:
                print(f"  [WARN] Could not parse a resume: {e}")

        self.additional_experience = "\n\n".join(parts)
        print(f"  Loaded {resume_num} old resumes ({len(seen_bullets)} unique bullets)")

    def prepare_resume_prompt(self, jd_input: str) -> str:
        """
        Full pipeline: parse resume → scrub → scrape JD → build prompt.
        Returns the master prompt ready for copy-paste.
        """
        # 1. Get JD
        if jd_input.startswith("http"):
            print(f"  Fetching JD from URL: {jd_input}...")
            jd_text = scrape_jd(jd_input)
            if not jd_text:
                return "ERROR: Could not scrape JD. Try 'manual' mode to paste the text."
        else:
            jd_text = jd_input

        # 2. Load resumes
        self._load_primary_resume()
        self._load_old_resumes()

        # 3. Build prompt
        prompt = build_master_prompt(
            scrubbed_resume=self.scrubbed_resume,
            job_description=jd_text,
            additional_experience=self.additional_experience,
        )

        # 4. Report prompt size
        print(f"  Prompt size: {len(prompt)} chars (~{len(prompt)//4} tokens)")
        return prompt

    def prepare_cover_letter_prompt(self, jd_input: str, company_name: str = "the company") -> str:
        """Generates a cover letter prompt."""
        if jd_input.startswith("http"):
            jd_text = scrape_jd(jd_input)
            if not jd_text:
                return "ERROR: Could not scrape JD."
        else:
            jd_text = jd_input

        self._load_primary_resume()
        return build_cover_letter_prompt(
            scrubbed_resume=self.scrubbed_resume,
            job_description=jd_text,
            company_name=company_name,
        )

    def process_response(self, ai_response: str) -> str:
        """Re-injects PII into the AI's output."""
        return self.scrubber.restore(ai_response)

    def save_output(self, content: str, filename: str) -> str:
        """Saves final content to the output directory, creating subdirs if needed."""
        path = os.path.join(OUTPUT_DIR, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

# 🕵️ Job Hunter Agent

**The AI tool that replaces recruitment agencies.**

Built to automate the job application lifecycle so you don't have to deal with third-party recruiters. This tool scrubs your PII, tailors your resume for every single application using AI, and generates privacy-first PDFs — giving you the edge of a dedicated agency without the middleman.

---

## How It Works

```
Your Resume → PII Scrubbed → Prompt Built → You paste into AI → Paste response back → PII Restored → PDF/Markdown Output
```

Your data never leaves your machine. The AI only sees placeholders like `<CANDIDATE_NAME>`, `<EMAIL_1>`, `<PHONE_2>`.

---

## Quick Start

```bash
# Install dependencies
pip install pdfplumber python-docx pyyaml markdown xhtml2pdf beautifulsoup4 requests

# Optional: for JS-heavy job pages (LinkedIn, Greenhouse)
pip install playwright && playwright install chromium

# Run
python run_cli.py
```

---

## CLI Workflow

```
╔══════════════════════════════════════════════╗
║     JOB HUNTER AI v1.0 (Privacy Mode)       ║
║  Your resume, your data, your control.       ║
╚══════════════════════════════════════════════╝

  [1] Generate a tailored RESUME prompt
  [2] Generate a COVER LETTER prompt
  [3] Paste AI response & save final document
  [q] Quit
```

1. **Option 1** — Paste a job URL or JD text → get a master prompt with your scrubbed resume + JD
2. **Copy the prompt** → Paste into Claude Opus, GPT-4, or any LLM
3. **Option 3** — Paste the AI's response back → PII is restored → saved as PDF + Markdown

---

## Project Structure

```
11 R/
├── run_cli.py                  # CLI entry point
├── backend/
│   ├── app.py                  # JobHunter orchestrator
│   ├── data/
│   │   ├── config.yaml         # PII, URLs, settings (edit this)
│   │   └── user_profile.json   # Certifications & skills
│   └── lib/
│       ├── pii_scrubber.py     # Privacy vault (scrub/restore)
│       ├── resume_parser.py    # PDF/DOCX text extraction
│       ├── jd_scraper.py       # Job description scraper
│       ├── prompt_builder.py   # Master prompt construction
│       └── pdf_generator.py    # Markdown → PDF conversion
├── resumes/                    # Old resume versions (DOCX)
├── output/                     # Generated resumes by date/company
│   └── YYYY-MM-DD_Company/
│       ├── Name_Company_Resume.md
│       └── Name_Company_Resume.pdf
└── test_e2e.py                 # End-to-end test suite
```

---

## Configuration

Edit `backend/data/config.yaml` to set your personal info:

```yaml
candidate:
  full_name: "Your Name"
  address: "Your Address"
  sensitive_urls:
    - term: "linkedin.com/in/your-profile"
      placeholder: "LINKEDIN_URL"
    - term: "github.com/your-username"
      placeholder: "GITHUB_URL"
```

Certifications and skills are in `backend/data/user_profile.json`.

---

## Privacy Model

| Stage | What happens | PII exposed? |
|-------|-------------|--------------|
| Parse resume | Extract text from PDF/DOCX | Local only |
| Scrub | Replace name, email, phone, address, URLs with placeholders | ❌ No |
| Build prompt | Combine scrubbed resume + JD + certs | ❌ No |
| You paste to AI | You control where it goes | ❌ Placeholders only |
| Restore | Swap placeholders back to real values | Local only |
| Save | PDF/Markdown written to `output/` | Local only |

**Your PII never leaves your machine automatically.** You choose when and where to paste the prompt.

---

## Features

- **ATS Optimization** — Prompts instruct the AI to mirror JD keywords and language
- **Smart Deduplication** — Old resumes contribute only unique experience bullets  
- **Cert Selection** — AI picks the 5–10 most relevant certs from your full list (69+)
- **Dual Output** — PDF (Modern/Classic templates) + Markdown backup
- **JD Scraping** — Playwright for JS pages, requests fallback for static pages
- **Case-Insensitive PII** — Catches URL/name variations regardless of casing

---

## Testing

```bash
python test_e2e.py
```

Verifies: PII scrubbing, cert inclusion, JD inclusion, cover letter generation, PII restoration.

---

## Tech Stack

Python 3.11+ · pdfplumber · python-docx · PyYAML · Playwright · BeautifulSoup4 · xhtml2pdf · markdown

---

*Built with a privacy-first philosophy. Your resume, your data, your control.*

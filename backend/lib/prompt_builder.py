import json
import os

PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'user_profile.json')

def load_profile() -> dict:
    with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_certifications_for_prompt(profile: dict) -> str:
    """Format the full cert list so the AI can cherry-pick the best ones."""
    lines = []
    for cert in profile.get("certifications", []):
        lines.append(f"- {cert['name']} | {cert['issuer']} | {cert['date']}")
    return "\n".join(lines)

def build_master_prompt(
    scrubbed_resume: str,
    job_description: str,
    additional_experience: str = "",
) -> str:
    """
    Constructs the prompt for the user to copy-paste into Opus/GPT.
    Includes the full certifications list so the AI can select the most relevant ones.
    """
    profile = load_profile()
    certs_text = format_certifications_for_prompt(profile)
    skills_text = ", ".join(profile.get("skills_from_certs", []))

    prompt = f"""You are an Expert Resume Writer & ATS Optimization Specialist.

## YOUR TASK
Rewrite the candidate's resume to perfectly target the Job Description below.
The result must:
1. Score maximum on ATS keyword matching.
2. Read naturally and impressively to a human recruiter.
3. Be truthful — rephrase, reorder, and emphasize, but NEVER fabricate experience.

## RULES
- KEEP all placeholders exactly as-is (e.g. <EMAIL_1>, <PHONE_2>, <CANDIDATE_NAME>). Do NOT replace them.
- From the CERTIFICATIONS LIST below, select ONLY the 5-10 most relevant ones for this specific role. Do not dump all of them.
- Rewrite the Professional Summary to directly address what this employer is looking for.
- Rewrite bullet points to mirror the JD's language and keywords.
- Prioritize the Skills section to lead with JD-matched skills.
- Output the FULL resume in clean Markdown format.

---

## TARGET JOB DESCRIPTION
{job_description}

---

## CANDIDATE'S PRIMARY RESUME (Scrubbed)
{scrubbed_resume}

---

## ADDITIONAL EXPERIENCE FROM OLDER RESUMES
(Use this to pull in relevant experience the primary resume may not emphasize)
{additional_experience if additional_experience else "N/A"}

---

## FULL CERTIFICATIONS LIST (Pick the best 5-10 for this role)
{certs_text}

---

## CANDIDATE'S KNOWN SKILL AREAS
{skills_text}

---

## OUTPUT
Provide the complete, rewritten resume in Markdown. Start with the candidate's name placeholder and contact placeholders, then Summary, Experience, Skills, Education & Certifications (selected), and any other relevant sections.
"""
    return prompt.strip()


def build_cover_letter_prompt(
    scrubbed_resume: str,
    job_description: str,
    company_name: str = "the company",
) -> str:
    """
    Generates a prompt for a tailored cover letter.
    """
    profile = load_profile()
    certs_text = format_certifications_for_prompt(profile)

    prompt = f"""You are an Expert Cover Letter Writer.

## YOUR TASK
Write a compelling, personalized cover letter for the candidate applying to {company_name}.
The letter must:
1. Be concise (3-4 paragraphs, under 400 words).
2. Directly reference 2-3 specific requirements from the JD and show how the candidate meets them.
3. Convey enthusiasm and cultural fit.
4. KEEP all placeholders exactly as-is (e.g. <EMAIL_1>, <PHONE_2>, <CANDIDATE_NAME>).

---

## TARGET JOB DESCRIPTION
{job_description}

---

## CANDIDATE RESUME (Scrubbed)
{scrubbed_resume}

---

## RELEVANT CERTIFICATIONS (Pick 2-3 max to mention)
{certs_text}

---

## OUTPUT
Provide the cover letter in Markdown. Start with date, address block with placeholders, then the letter body, and sign off with <CANDIDATE_NAME>.
"""
    return prompt.strip()

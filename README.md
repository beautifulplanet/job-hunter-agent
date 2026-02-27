# Job Hunter Agent

A local-only CLI and GUI tool that automates resume tailoring for specific job postings. Scrubs your PII before building LLM prompts, then restores your real information in the final PDF/Markdown output. You control when and where data leaves your machine.

### Impact

- **Privacy-first resume tailoring** — your name, email, phone, address, and URLs are replaced with placeholders (`<CANDIDATE_NAME>`, `<EMAIL_1>`, `<PHONE_2>`) before any text leaves your machine. The AI only sees anonymized data.

- **Multi-format document ingestion** — parses PDF, DOCX, TXT, Markdown, HTML, JSON, and ZIP archives (with recursive extraction and bomb protection). Feed it any resume format.

- **Regex-based profile extraction** — no API calls, no LLM. A local engine extracts skills, certifications, roles, achievements, and education from your resume text using pattern matching and heuristics.

- **Manual paste workflow by design** — no API keys stored, no automated AI calls. You copy the prompt, paste it into whatever LLM you trust, paste the response back. This is a deliberate security decision, not a limitation.

- **Input validation throughout** — SSRF protection on URL scraping, path traversal prevention on file output, ZIP bomb guards (size/count/nesting/ZipSlip), file size limits, filename sanitization, HTML sanitization on AI responses before PDF generation.

Stack: Python 3.10+ · pdfplumber · python-docx · PyYAML · Playwright · BeautifulSoup4 · xhtml2pdf · markdown

### Evidence

| Claim | Proof |
|-------|-------|
| PII scrubbing works | 3-phase scrubber (custom terms → regex → names) with post-scrub verification. 199 tests cover edge cases including Unicode evasion, homoglyphs, partial matches, and case variations |
| No API keys anywhere | `grep -r "api_key\|API_KEY\|sk-" backend/` returns nothing. [ADR-001](docs/ADR/ADR-001-manual-paste-workflow.md) documents the decision |
| SSRF protection | `validate_url()` blocks `file://`, localhost, private IPs (10.x, 172.16-31.x, 192.168.x), cloud metadata (169.254.169.254), and DNS rebinding |
| Path traversal prevention | `safe_path_join()` resolves all paths and verifies they stay within `output/`. Tested with `../../etc/passwd` payloads |
| ZIP bomb protection | Max 50 MB extracted, max 100 files, max 3 nesting levels, ZipSlip path validation |
| 199 tests | `python -m pytest tests/ -v` — 15 test files covering PII, security, parsing, ingestion, edge cases |

### Quality Bar

- **Post-scrub verification** — after every scrub pass, `_verify_scrub()` checks that no registered PII terms remain in the output. If anything leaks, it's caught before the prompt is built.

- **Final-pass scrub on assembled prompts** — profile data (roles, achievements, education) is injected after the initial scrub. A second scrub pass on the complete prompt catches any PII that entered through the profile.

- **No PII in logs** — all log messages use count-only format ("5 items scrubbed"), never the actual values. `RotatingFileHandler` caps log size at 2 MB with auto-rotation.

- **Test categories** — PII scrubbing (all formats), prompt injection resistance, Unicode/homoglyph evasion, path traversal, SSRF, filename injection, ZIP bombs, DoS (file size, text size, log flooding, ReDoS), error message PII leaks, placeholder integrity, scrubber state isolation.

### Ownership & Quality

I'm the sole developer. This tool solves a real problem I have: tailoring resumes for job applications without exposing my personal information to AI services.

- **Role:** Solo — design, implementation, testing
- **Standard:** Every security mitigation has a corresponding test. Threat model documents 18 specific threats with their mitigations.
- **AI policy:** AI-assisted development. I review, test, and can explain every component. The tool itself does not call any AI — it builds prompts for the user to paste manually.
- **Honest limitation:** PII scrubbing is regex-based, not ML. Very short PII terms (< 4 chars) or creative obfuscation may not be caught. The post-scrub verification catches most edge cases, and the manual paste step gives you a final visual check.

---

## How to Read This README

### If you're evaluating the candidate

| What you want | Where to find it | Time |
|---------------|-----------------|------|
| What the tool does | [Impact ↑](#impact) | 30 sec |
| Proof it works | [Evidence ↑](#evidence) | 1 min |
| Talking points for interview | [Why It's Interesting ↓](#why-its-interesting-for-interviewers) | 1 min |
| Interview drill questions | [Interview Drill ↓](#interview-drill-sheet) | 2 min |

### If you're reviewing engineering

| What you want | Where to find it | Time |
|---------------|-----------------|------|
| Architecture + data flow | [Architecture ↓](#architecture) | 1 min |
| PII scrubbing internals | [How PII Scrubbing Works ↓](#how-pii-scrubbing-works) | 2 min |
| Security posture | [Security ↓](#security-posture) | 2 min |
| Design decisions | [Key Design Decisions ↓](#key-design-decisions) | 2 min |
| Testing strategy | [Testing ↓](#testing) | 1 min |

### If you want to run it

| What you want | Where to find it | Time |
|---------------|-----------------|------|
| Install and run | [Quick Start ↓](#quick-start) | 2 min |
| Configuration | [Configuration ↓](#configuration) | 1 min |

---

## Summary

### What

A Python CLI/GUI tool that:

1. **Parses** your resume (PDF, DOCX, or 5 other formats) and extracts text
2. **Scrubs** all PII — names, emails, phones, addresses, LinkedIn/GitHub URLs — replacing them with labeled placeholders
3. **Extracts** your professional profile (skills, certifications, roles, achievements) using regex-based pattern matching — no AI, no API calls
4. **Scrapes** job descriptions from URLs (Playwright for JS-rendered pages, requests for static) or accepts pasted text
5. **Builds** a master prompt combining your scrubbed resume + JD + profile data + formatting instructions
6. **You paste** the prompt into any LLM (ChatGPT, Claude, Gemini, local models)
7. **Restores** your real PII into the AI's response
8. **Saves** the final result as PDF (Modern or Classic template) and Markdown

### Why It's Interesting (for Interviewers)

| Talking Point | Detail |
|--------------|--------|
| Privacy engineering | 3-phase PII scrubber with post-verification, final-pass scrub on assembled prompts, no PII in logs or error messages |
| Security mindset | 18-threat model with mitigations: SSRF, path traversal, ZIP bombs, ReDoS, filename injection, HTML sanitization, DoS protection |
| Architecture decisions | 3 ADRs documenting why: manual paste over API (security), placeholders over encryption (AI compatibility), local-first over SaaS (privacy) |
| Input validation | URL validation blocks private IPs, cloud metadata, DNS rebinding. File validation enforces size limits. Path validation prevents directory escapes |
| Multi-format ingestion | Single `ingest()` function handles PDF, DOCX, TXT, MD, HTML, JSON, ZIP with recursive extraction — not just "reads PDFs" |
| Regex-based NLP | Profile builder extracts skills, roles, certs, achievements, and education from unstructured resume text using pattern matching — no ML dependencies, runs offline |
| Testing discipline | 199 tests across 15 files. Security tests include adversarial inputs (Unicode evasion, homoglyphs, prompt injection, pathological regex inputs) |
| Practical tool | I built this to solve my own problem and I use it for real job applications |

### Key Numbers

| Metric | Value |
|--------|-------|
| Python source files | 11 modules across `backend/lib/` |
| Largest module | `profile_builder.py` — ~500 lines of regex-based extraction |
| PII types detected | Names, emails, phones (international), SSNs, credit cards, LinkedIn/GitHub/GitLab URLs, addresses, custom terms |
| Supported input formats | 7 (PDF, DOCX, TXT, MD, HTML, JSON, ZIP) |
| Test count | 199 across 15 files |
| Threat model entries | 18 |
| ADRs | 3 |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Your Machine                              │
│                                                                  │
│  ┌─────────────┐   ┌─────────────────┐   ┌──────────────────┐   │
│  │  CLI / GUI  │──►│   JobHunter     │──►│  Prompt (text)   │   │
│  │  (run_cli   │   │   Orchestrator  │   │  copied to       │───┼──► You paste into LLM
│  │   run_gui)  │   │   (app.py)      │   │  clipboard       │   │
│  └─────────────┘   └───────┬─────────┘   └──────────────────┘   │
│                            │                                     │
│              ┌─────────────┼─────────────────┐                   │
│              │             │                 │                   │
│              ▼             ▼                 ▼                   │
│  ┌───────────────┐ ┌─────────────┐ ┌──────────────────┐         │
│  │ Resume Parser │ │ JD Scraper  │ │ Profile Builder  │         │
│  │ + Document    │ │             │ │ (regex-based,    │         │
│  │   Ingestor    │ │ Playwright  │ │  no AI)          │         │
│  │               │ │ + requests  │ │                  │         │
│  │ PDF/DOCX/TXT/ │ │ fallback    │ │ Skills, certs,   │         │
│  │ MD/HTML/JSON/ │ │             │ │ roles, education │         │
│  │ ZIP           │ │ URL →       │ │                  │         │
│  └───────┬───────┘ │ validate →  │ └────────┬─────────┘         │
│          │         │ fetch →     │          │                   │
│          │         │ extract     │          │                   │
│          │         └──────┬──────┘          │                   │
│          ▼                ▼                 ▼                   │
│  ┌──────────────────────────────────────────────────────┐       │
│  │                   PII Scrubber                        │       │
│  │                                                       │       │
│  │  Phase 1: Custom terms (config.yaml → placeholders)   │       │
│  │  Phase 2: Regex (email, phone, SSN, CC, URLs)         │       │
│  │  Phase 3: Name variations (first, last, full)         │       │
│  │  Verify:  _verify_scrub() confirms no leaks           │       │
│  └──────────────────────────┬────────────────────────────┘       │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              Prompt Builder                           │       │
│  │  Scrubbed resume + JD + profile + instructions        │       │
│  │  → Final-pass scrub on entire assembled prompt        │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  After you paste AI response back:                    │       │
│  │  PII Restorer → HTML Sanitizer → PDF Generator        │       │
│  │  → output/YYYY-MM-DD_Company/Name_Company_Resume.pdf  │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
│  Validators (throughout):                                        │
│  • validate_url() — blocks SSRF (private IPs, metadata, file://) │
│  • safe_path_join() — blocks path traversal                      │
│  • validate_file_size() — blocks oversized inputs                │
│  • sanitize_filename() — blocks filename injection               │
│  • _sanitize_html() — strips dangerous tags before PDF render    │
│  • ZIP: size limit, file count, nesting depth, ZipSlip           │
└──────────────────────────────────────────────────────────────────┘
```

**Key boundary:** Everything inside the box runs locally. The only thing that crosses the boundary is the scrubbed prompt text — and only when you manually paste it.

### How PII Scrubbing Works

```
Input: "Dmitry Martynov — dmitry@email.com — 347-555-1234 — linkedin.com/in/dmitry-m"

Phase 1 (Custom terms from config.yaml):
  "linkedin.com/in/dmitry-m" → "<LINKEDIN_URL>"

Phase 2 (Regex patterns):
  "dmitry@email.com" → "<EMAIL_1>"
  "347-555-1234"     → "<PHONE_1>"

Phase 3 (Name variations — longest first):
  "Dmitry Martynov"  → "<CANDIDATE_NAME>"
  "Martynov"         → "<CANDIDATE_NAME>"
  "Dmitry"           → "<CANDIDATE_NAME>"

Verify: _verify_scrub() scans output for any registered term. If found → re-scrub.

Output: "<CANDIDATE_NAME> — <EMAIL_1> — <PHONE_1> — <LINKEDIN_URL>"
```

Restoration is the reverse: placeholders → real values. Longest placeholders replaced first to avoid partial matches.

### Key Design Decisions

| Decision | Rationale | ADR |
|----------|-----------|-----|
| Manual paste, no API | No API keys to steal, no accidental PII transmission, works with any LLM, user visually inspects prompt before sending | [ADR-001](docs/ADR/ADR-001-manual-paste-workflow.md) |
| Placeholders, not encryption | AI can understand `<CANDIDATE_NAME>` and write around it. Encrypted tokens produce garbage output. Simpler than key management | [ADR-002](docs/ADR/ADR-002-pii-scrubbing-over-encryption.md) |
| Local CLI, not SaaS | No server, no database, no auth, no multi-tenancy. Minimal attack surface. All data stays on disk | [ADR-003](docs/ADR/ADR-003-single-user-local-first.md) |
| Regex profile extraction, not ML | Runs offline, no dependencies on external models, deterministic output, fast. Trades recall for simplicity |  |
| Playwright + requests fallback | JS-rendered job pages (LinkedIn, Greenhouse) need a browser. Static pages don't. Try headless browser first, fall back to HTTP | |

### Security Posture

| Threat | Vector | Mitigation | Tested |
|--------|--------|------------|--------|
| PII leakage to AI | Name/email/phone in prompt | 3-phase scrub + post-verify + final-pass scrub | Yes — 39 tests in `test_pii_security_comprehensive.py` |
| SSRF via scraper | Malicious URL: `http://169.254.169.254` | `validate_url()` blocks file://, localhost, private IPs, metadata, DNS rebinding | Yes — `test_security.py` |
| Path traversal | Company name: `../../etc/passwd` | `safe_path_join()` resolves + validates path within `output/` | Yes — `test_security.py` |
| XSS via PDF | AI returns `<script>` tags | `_sanitize_html()` strips dangerous tags before xhtml2pdf | Yes — `test_security.py` |
| ZIP bomb | Crafted ZIP: huge decompressed size | 50 MB limit, 100 file limit, 3 nesting levels, ZipSlip validation | Yes — 29 tests in `test_dos_and_zip_security.py` |
| DoS (file size) | 100 MB resume upload | `validate_file_size()` — 10 MB resume, 1 MB JD | Yes |
| DoS (text size) | Enormous pasted JD | `MAX_JD_TEXT_LEN` enforced | Yes |
| ReDoS | Adversarial input causing catastrophic backtracking | All regex patterns tested against pathological strings (< 2s) | Yes |
| PII in logs | Log contains real names from prior runs | Count-only log format, `RotatingFileHandler` (2 MB cap) | Yes — `test_security_advanced.py` |
| PII in errors | Traceback exposes variable content | Error paths report sizes/paths, not content | Yes |
| Filename injection | Special chars in company name | `sanitize_filename()` strips path separators + reserved chars | Yes |
| Prompt injection | JD contains "ignore all placeholders" | Manual paste — user reviews prompt before sending | Yes — tested patterns |

Full threat model with 18 entries: [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md)

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: for JS-heavy job pages (LinkedIn, Greenhouse)
pip install playwright && playwright install chromium

# Run CLI
python run_cli.py

# Or run GUI
python run_gui.py

# First-time setup (guided profile builder)
python setup_gui.py
```

### CLI Workflow

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

1. **Option 1** — Paste a job URL or JD text → get a scrubbed master prompt
2. **Copy the prompt** → Paste into Claude, ChatGPT, or any LLM
3. **Option 3** — Paste the AI's response back → PII is restored → saved as PDF + Markdown

---

## Configuration

Run `python setup_gui.py` for guided first-time setup, or edit manually:

**`backend/data/config.yaml`** — your PII and settings:
```yaml
candidate:
  full_name: "Your Name"
  address: "Your Address"
  sensitive_urls:
    - term: "linkedin.com/in/your-profile"
      placeholder: "LINKEDIN_URL"
```

**`backend/data/user_profile.json`** — auto-generated by `setup_gui.py`. Contains extracted skills, certifications, roles, and achievements from your resume.

---

## Testing

```bash
# Full suite (199 tests)
python -m pytest tests/ -v

# Security tests only
python -m pytest tests/test_security.py tests/test_security_advanced.py -v

# PII-specific tests
python -m pytest tests/test_pii_security_comprehensive.py tests/test_pii_edge_cases.py -v

# ZIP/DoS tests
python -m pytest tests/test_dos_and_zip_security.py -v
```

---

## Interview Drill Sheet

Questions someone reviewing this project will ask, with honest answers:

| Question | Answer |
|----------|--------|
| **Isn't this just string replacement?** | The scrubber is, yes — find-and-replace with ordered matching (longest first). That's deliberate. Regex is deterministic, fast, and has no external dependencies. The complexity is in the edge cases: case-insensitive matching, partial name detection, post-scrub verification, and final-pass scrub on assembled prompts. |
| **Why not use an NER model for PII detection?** | Overkill for a single-user tool where I know my own PII. Regex + a config file catches everything because the PII list is finite and known in advance. An NER model adds a dependency, runs slower, and still needs a verification step. |
| **What if the AI ignores the placeholders?** | It's possible — that's why the user reviews the output before restoring PII. The manual paste workflow is the safety net. In practice, modern LLMs handle labeled placeholders well because they understand the semantic role of `<CANDIDATE_NAME>`. |
| **Why not just call the OpenAI API directly?** | No API keys to store, rotate, or protect. No risk of automated PII transmission. No vendor lock-in. No cost management. The user can paste into any model, including local ones. See [ADR-001](docs/ADR/ADR-001-manual-paste-workflow.md). |
| **Does the profile builder actually work on messy resumes?** | It's regex-based, so it works well on structured resumes with clear section headers. Unusual formats or creative layouts will produce partial results. The setup GUI lets you review and edit the extracted profile before saving. |
| **What would you do differently?** | Add a confidence score to the profile builder so the user knows which extractions to double-check. Use `spaCy` for name detection instead of pure regex. Add a diff view showing exactly what the AI changed in the resume. Build a prompt template system so users can customize the AI instructions. |
| **Is the security overkill for a personal tool?** | Some of it, yes. ZIP bomb protection and SSRF guards are defensive — I built them because the scraper accepts arbitrary URLs and the ingestor accepts arbitrary files. The threat model documents what's in scope and explicitly calls out what's not (encryption at rest, multi-user auth, GDPR compliance). |

---

## Project Structure

```
job-hunter-agent/
├── run_cli.py                    # CLI entry point
├── run_gui.py                    # GUI entry point (Tkinter)
├── setup_gui.py                  # First-time profile setup wizard
├── backend/
│   ├── app.py                    # JobHunter orchestrator
│   ├── data/
│   │   ├── config.yaml           # PII + settings (gitignored)
│   │   ├── config.yaml.example   # Template for new users
│   │   ├── user_profile.json     # Extracted profile (gitignored)
│   │   └── user_profile.json.example
│   └── lib/
│       ├── pii_scrubber.py       # 3-phase PII scrub + restore
│       ├── resume_parser.py      # PDF/DOCX text extraction
│       ├── document_ingestor.py  # Multi-format ingestion (7 formats + ZIP)
│       ├── profile_builder.py    # Regex-based skill/cert/role extraction
│       ├── jd_scraper.py         # Job description scraper
│       ├── prompt_builder.py     # Master prompt construction
│       ├── pdf_generator.py      # Markdown → PDF (Modern/Classic)
│       ├── validators.py         # SSRF, path traversal, file size, filename
│       └── logger.py             # Rotating log handler (no PII in messages)
├── tests/                        # 199 tests across 15 files
├── docs/
│   ├── THREAT_MODEL.md           # 18 threats mapped with mitigations
│   └── ADR/                      # Architecture Decision Records
│       ├── ADR-001-manual-paste-workflow.md
│       ├── ADR-002-pii-scrubbing-over-encryption.md
│       └── ADR-003-single-user-local-first.md
├── resumes/                      # Your resume files (gitignored)
├── output/                       # Generated output (gitignored)
├── requirements.txt
├── SECURITY.md
└── LICENSE
```

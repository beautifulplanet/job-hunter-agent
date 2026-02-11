import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import JobHunter

SAMPLE_JD = """
Senior Project Manager - AI & Machine Learning
Company: TechCorp Inc.

Requirements:
- 5+ years of project management experience
- Strong background in Agile/Scrum methodologies
- Experience with AI/ML product development
- Python proficiency
- Excellent stakeholder communication
- PMP or equivalent certification preferred
- Experience managing cross-functional engineering teams
"""

def test_full_pipeline():
    print("[TEST] Initializing JobHunter...")
    hunter = JobHunter()

    print("\n[TEST] Generating resume prompt with sample JD...")
    prompt = hunter.prepare_resume_prompt(SAMPLE_JD)

    print(f"\n[TEST] Prompt generated successfully!")
    print(f"[TEST] Total prompt length: {len(prompt)} characters")
    print(f"[TEST] PII mappings found: {len(hunter.scrubber.mappings)}")
    for k, v in hunter.scrubber.mappings.items():
        print(f"  {k} -> {v}")

    # Verify PII was scrubbed
    assert "Dmitry" not in prompt, "FAIL: Name not scrubbed!"
    assert "Dmitrymarty" not in prompt.lower(), "FAIL: Email not scrubbed!"
    print("\n[TEST] PII scrubbing PASSED")

    # Verify certs are included
    assert "Machine Learning" in prompt, "FAIL: Certs not in prompt!"
    assert "Stanford" in prompt, "FAIL: Cert issuers not in prompt!"
    print("[TEST] Certifications inclusion PASSED")

    # Verify JD is included
    assert "TechCorp" in prompt, "FAIL: JD not in prompt!"
    print("[TEST] JD inclusion PASSED")

    print("\n[TEST] First 500 chars of prompt:")
    print("-" * 40)
    print(prompt[:500])
    print("-" * 40)

    # Test cover letter prompt
    print("\n[TEST] Generating cover letter prompt...")
    cl_prompt = hunter.prepare_cover_letter_prompt(SAMPLE_JD, "TechCorp Inc.")
    print(f"[TEST] Cover letter prompt length: {len(cl_prompt)} chars")
    assert "TechCorp" in cl_prompt, "FAIL: Company not in cover letter!"
    print("[TEST] Cover letter generation PASSED")

    # Test PII restoration
    print("\n[TEST] Testing PII restore...")
    mock_response = "Resume for <CANDIDATE_NAME>\nEmail: <EMAIL_1>\nPhone: <PHONE_2>"
    restored = hunter.process_response(mock_response)
    assert "<CANDIDATE_NAME>" not in restored, "FAIL: Name not restored!"
    assert "<EMAIL_1>" not in restored, "FAIL: Email not restored!"
    print(f"[TEST] Restored text: {restored}")
    print("[TEST] PII restoration PASSED")

    print("\n" + "=" * 40)
    print("ALL TESTS PASSED")
    print("=" * 40)


if __name__ == "__main__":
    test_full_pipeline()

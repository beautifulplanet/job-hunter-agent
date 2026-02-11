import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.lib.pdf_generator import generate_pdf

SAMPLE_RESUME = """
# Dmitry Martynov
123 Main St | 555-555-5555 | email@example.com

## Professional Summary
Experienced Project Manager with a focus on AI and automation.

## Experience
### Senior Project Manager
*Managed* complex projects.
*   Led a team of 10.
*   Implemented **AI solutions**.

## Education
*   **B.S. Computer Science**, University of Tech

## Skills
*   Python, Project Management, Agile
"""

def test_pdf():
    print("Testing PDF Generation...")
    
    # Modern
    out_modern = "test_resume_modern.pdf"
    if generate_pdf(SAMPLE_RESUME, out_modern, "modern"):
        print(f"✅ Created {out_modern}")
    else:
        print(f"❌ Failed to create {out_modern}")

    # Classic
    out_classic = "test_resume_classic.pdf"
    if generate_pdf(SAMPLE_RESUME, out_classic, "classic"):
        print(f"✅ Created {out_classic}")
    else:
        print(f"❌ Failed to create {out_classic}")

if __name__ == "__main__":
    test_pdf()

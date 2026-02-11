import sys
import os

# dynamic import since we are running this as a script
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend')) 

from lib.pii_scrubber import PIIScrubber
from lib.resume_parser import extract_text

def test_scrub_resume(resume_path: str):
    print(f"Testing scrub on: {resume_path}")
    
    # 1. Extract
    try:
        text = extract_text(resume_path)
        print(f"✅ Text extracted ({len(text)} chars)")
    except Exception as e:
        print(f"❌ Failed to extract text: {e}")
        return

    # 2. Initialize Scrubber
    scrubber = PIIScrubber()
    
    # 3. Scrub
    scrubbed_text = scrubber.scrub(text)
    
    # 4. Check results
    print("\n--- Original Snippet ---")
    print(text[:500])
    print("\n--- Scrubbed Snippet ---")
    print(scrubbed_text[:500])
    
    print("\n--- PII Mappings Found ---")
    for k, v in scrubber.mappings.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    # Hardcoded path to the user's resume for testing
    resume_path = r"c:\Users\Elite\Documents\Mega Folder\11 R\Technical Product Manager & AI Implementation Lead.pdf" 
    test_scrub_resume(resume_path)

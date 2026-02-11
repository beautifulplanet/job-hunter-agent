import os
import sys
from datetime import datetime
from backend.lib.pdf_generator import generate_pdf, TEMPLATES



def collect_multiline(prompt_msg: str) -> str:
    """Collects multi-line input until user types END on its own line."""
    print(prompt_msg)
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    return '\n'.join(lines)


def main():
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║     JOB HUNTER AI v1.0 (Privacy Mode)       ║")
    print("║  Your resume, your data, your control.       ║")
    print("╚══════════════════════════════════════════════╝")
    print()

    hunter = JobHunter()

    while True:
        print("\nWhat would you like to do?")
        print("  [1] Generate a tailored RESUME prompt")
        print("  [2] Generate a COVER LETTER prompt")
        print("  [3] Paste AI response & save final document")
        print("  [q] Quit")
        choice = input("\n> ").strip()

        if choice == '1':
            print("\nEnter JD URL, or type 'manual' to paste text:")
            jd_input = input("> ").strip()
            if jd_input.lower() == 'manual':
                jd_input = collect_multiline("Paste the Job Description below. Type 'END' on a new line when done:")

            print("\n⏳ Generating prompt...")
            prompt = hunter.prepare_resume_prompt(jd_input)

            print("\n" + "=" * 60)
            print("  MASTER PROMPT — COPY EVERYTHING BELOW THIS LINE")
            print("=" * 60)
            print(prompt)
            print("=" * 60)
            print("\n✅ Copy the text above → Paste into Opus → Come back with option [3]")

        elif choice == '2':
            print("\nCompany name (for the letter header):")
            company = input("> ").strip() or "the company"
            print("Enter JD URL, or type 'manual' to paste text:")
            jd_input = input("> ").strip()
            if jd_input.lower() == 'manual':
                jd_input = collect_multiline("Paste the Job Description below. Type 'END' on a new line when done:")

            print("\n⏳ Generating cover letter prompt...")
            prompt = hunter.prepare_cover_letter_prompt(jd_input, company)

            print("\n" + "=" * 60)
            print("  COVER LETTER PROMPT — COPY EVERYTHING BELOW THIS LINE")
            print("=" * 60)
            print(prompt)
            print("=" * 60)
            print("\n✅ Copy the text above → Paste into Opus → Come back with option [3]")

        elif choice == '3':
            ai_response = collect_multiline("\nPaste the AI's response below. Type 'END' on a new line when done:")
            final = hunter.process_response(ai_response)

            print("\nTarget Company Name (e.g. 'Google'):")
            company = input("> ").strip().replace(" ", "_") or "Unknown_Company"
            
            # Create timestamped folder name: YYYY-MM-DD_Company
            date_str = datetime.now().strftime("%Y-%m-%d")
            folder_name = f"{date_str}_{company}"
            
            # Filename
            base_name = f"Dmitry_Martynov_{company}_Resume"

            print("\nFormat? [1] PDF (Recommended)  [2] Markdown")
            fmt = input("> ").strip()
            
            if fmt == '2':
                # Save as Markdown
                rel_path = os.path.join(folder_name, base_name + ".md")
                path = hunter.save_output(final, rel_path)
                print(f"\n🎉 Saved Markdown to: {path}")
            else:
                # PDF Flow
                print("\nTemplate? [1] Modern  [2] Classic")
                tmpl_choice = input("> ").strip()
                template = "classic" if tmpl_choice == '2' else "modern"
                
                # Save MD backup
                rel_md_path = os.path.join(folder_name, base_name + ".md")
                md_path = hunter.save_output(final, rel_md_path)
                
                # Save PDF
                rel_pdf_path = os.path.join(folder_name, base_name + ".pdf")
                pdf_path = os.path.join(os.path.dirname(md_path), base_name + ".pdf")
                
                print("⏳ Generating PDF...")
                if generate_pdf(final, pdf_path, template):
                    print(f"\n🎉 Saved PDF to: {pdf_path}")
                    print(f"   (Markdown backup: {md_path})")
                else:
                    print(f"\n❌ PDF generation failed. Saved Markdown to: {md_path}")

        elif choice.lower() == 'q':
            print("\nGoodbye! Go get that job. 💪")
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()

import markdown
from xhtml2pdf import pisa
import os

# Define some basic templates
TEMPLATES = {
    "modern": """
        @page { size: letter; margin: 1in; }
        body { font-family: Helvetica, sans-serif; font-size: 11pt; line-height: 1.4; color: #333; }
        h1 { font-size: 24pt; color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 5px; margin-top: 0; }
        h2 { font-size: 16pt; color: #16a085; margin-top: 20px; margin-bottom: 10px; text-transform: uppercase; }
        h3 { font-size: 12pt; font-weight: bold; color: #7f8c8d; margin-top: 15px; margin-bottom: 5px; }
        p { margin-bottom: 10px; }
        ul { margin-top: 5px; margin-bottom: 10px; }
        li { margin-bottom: 5px; }
        .contact-info { font-size: 10pt; color: #7f8c8d; text-align: center; margin-bottom: 20px; }
    """,
    "classic": """
        @page { size: letter; margin: 1in; }
        body { font-family: "Times New Roman", serif; font-size: 12pt; line-height: 1.3; color: #000; }
        h1 { font-size: 22pt; font-weight: bold; text-align: center; margin-bottom: 5px; }
        h2 { font-size: 14pt; font-weight: bold; border-bottom: 1px solid #000; margin-top: 20px; padding-bottom: 3px; }
        h3 { font-size: 12pt; font-weight: bold; font-style: italic; margin-top: 15px; }
        p { margin-bottom: 12px; }
        li { margin-bottom: 4px; }
    """
}

def generate_pdf(markdown_text: str, output_path: str, template_name: str = "modern") -> bool:
    """
    Converts Markdown text to a PDF file using a selected CSS template.
    """
    try:
        # Convert MD to HTML
        html_content = markdown.markdown(markdown_text, extensions=['extra', 'smarty'])
        
        # Get CSS
        css = TEMPLATES.get(template_name.lower(), TEMPLATES["modern"])
        
        # Wrap in a full HTML document
        full_html = f"""
        <html>
        <head>
            <style>{css}</style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Write to PDF
        with open(output_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(full_html, dest=pdf_file)
            
        return not pisa_status.err
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False

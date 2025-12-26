"""Professional PDF Composer using fpdf2."""

from fpdf import FPDF
import os
from datetime import datetime


class PDFComposer(FPDF):
    """Professional PDF Composer for CV and Cover Letter."""

    def header(self):
        """Header for the PDF - optional but can add styling here."""
        pass

    def footer(self):
        """Footer with page numbers."""
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def clean_text(self, text: str) -> str:
        """Replace Unicode characters that are not supported by standard fonts."""
        if not text:
            return ""
        replacements = {
            "\u2013": "-",  # en dash
            "\u2014": "-",  # em dash
            "\u2018": "'",  # left single quote
            "\u2019": "'",  # right single quote
            "\u201c": '"',  # left double quote
            "\u201d": '"',  # right double quote
            "\u2022": "*",  # bullet
            "\u00b7": "*",  # middle dot (often used in resumes)
            "\u2026": "...", # ellipsis
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        # Also replace any other middle-dot like characters
        text = text.replace("\u22c5", "*").replace("\u2219", "*")
        
        # Fallback for any other non-latin-1 characters
        return text.encode("latin-1", "replace").decode("latin-1")

    def wrap_long_lines(self, text: str, max_chars: int = 80) -> str:
        """Manually wrap extremely long words or URLs that fpdf2 might struggle with."""
        words = text.split(" ")
        wrapped_words = []
        for word in words:
            if len(word) > max_chars:
                # Split extremely long words (like URLs or complex tech terms)
                parts = [word[i:i+max_chars] for i in range(0, len(word), max_chars)]
                wrapped_words.append(" ".join(parts))
            else:
                wrapped_words.append(word)
        return " ".join(wrapped_words)

    def create_professional_pdf(self, name: str, email: str, phone: str, resume_text: str, cover_letter_text: str, output_path: str):
        """Build a professional PDF combining CV and Cover Letter matching LaTeX style."""
        # Define template colors
        header_color = (0, 51, 102)  # RGB(0, 51, 102)
        link_color = (0, 102, 204)    # RGB(0, 102, 204)
        
        # Clean and pre-wrap the text before processing
        resume_text = self.wrap_long_lines(self.clean_text(resume_text))
        cover_letter_text = self.wrap_long_lines(self.clean_text(cover_letter_text))
        
        # --- PAGE 1: COVER LETTER ---
        self.add_page()
        
        # Header (Top Left for Cover Letter)
        self.set_font("helvetica", "B", 16)
        self.set_text_color(*header_color)
        self.cell(0, 10, name.upper(), ln=True, align="L")
        
        self.set_font("helvetica", "", 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 5, f"{email} | {phone}", ln=True)
        self.ln(5)
        
        # Line Divider
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)
        
        # Date
        self.set_text_color(0, 0, 0)
        self.set_font("helvetica", "", 10)
        self.cell(0, 5, datetime.now().strftime("%B %d, %Y"), ln=True)
        self.ln(10)
        
        # Section Header for Cover Letter
        self.set_font("helvetica", "B", 12)
        self.set_text_color(*header_color)
        self.cell(0, 5, "COVER LETTER", ln=True)
        self.set_draw_color(*header_color)
        self.set_line_width(0.3)
        self.line(10, self.get_y()+2, 200, self.get_y()+2)
        self.ln(10)
        
        # Body
        self.set_text_color(0, 0, 0)
        self.set_font("helvetica", "", 11)
        self.multi_cell(0, 6, cover_letter_text)
        
        # --- PAGE 2: RESUME ---
        self.add_page()
        
        # Professional Resume Header (Centered)
        self.set_font("helvetica", "B", 18)
        self.set_text_color(*header_color)
        self.cell(0, 12, name.upper(), ln=True, align="C")
        
        self.set_font("helvetica", "", 10)
        self.set_text_color(0, 0, 0)
        contact_info = f"Kathmandu, Nepal | {phone} | {email}"
        self.cell(0, 5, contact_info, ln=True, align="C")
        
        links = "LinkedIn | GitHub"
        self.set_text_color(*link_color)
        self.cell(0, 5, links, ln=True, align="C")
        self.ln(5)
        
        lines = resume_text.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                self.ln(2)
                continue
                
            try:
                # Section Header
                if line.isupper() and len(line) > 3:
                    self.ln(4)
                    self.set_font("helvetica", "B", 11)
                    self.set_text_color(*header_color)
                    self.cell(0, 6, line, ln=True)
                    self.set_draw_color(*header_color)
                    self.line(10, self.get_y(), 200, self.get_y())
                    self.ln(3)
                    self.set_font("helvetica", "", 10)
                    self.set_text_color(0, 0, 0)
                elif line.startswith("*") or line.startswith("-"):
                    # Use a simpler bullet formatting without complex x-shifting
                    bullet_text = f"  - {line[1:].strip()}"
                    self.multi_cell(0, 5, bullet_text)
                else:
                    self.multi_cell(0, 5, line)
            except Exception as e:
                print(f"Error rendering line: {line[:50]}... Error: {e}")
                # Skip problematic lines instead of crashing
                continue
        
        # Save output
        self.output(output_path)
        return output_path


def compose_docs(state_data: dict, output_dir: str = "data/outputs") -> str:
    """Wrapper to compose PDF from state data."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    user_id = state_data.get("telegram_user_id", "user")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"JobApplication_{user_id}_{timestamp}.pdf"
    output_path = f"{output_dir}/{filename}"
    
    custom_resume = state_data.get("customized_resume", "")
    
    # Try to find user name in resume or state
    name = "CHANDAN SHAH" # Defaulting to user's name from template
    email = "letsradheshah@gmail.com"
    phone = "+977-9866010612"
    
    # Simple extraction attempt if resume starts with a header
    lines = custom_resume.split("\n")
    if lines and len(lines[0]) < 30 and lines[0].isupper():
        name = lines[0]
        
    composer = PDFComposer()
    composer.create_professional_pdf(
        name=name,
        email=email,
        phone=phone,
        resume_text=custom_resume,
        cover_letter_text=state_data.get("cover_letter", "No cover letter content"),
        output_path=output_path
    )
    
    return output_path

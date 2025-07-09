from fpdf import FPDF
from io import BytesIO


class PDF(FPDF):
    def header(self):
        self.set_font("Arial", size=12)
        self.cell(200, 10, txt="Generated Document", ln=1, align='C')

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", size=10)
        self.cell(0, 10, f"Page {self.page_no()}", align='C')

def export_to_pdf(text, output_path):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=11)

    # Remove non-ASCII characters (fixes FontBBox error)
    text = ''.join(char if ord(char) < 128 else ' ' for char in text)

    for line in text.split("\n"):
        pdf.multi_cell(0, 10, txt=line.strip())
    
    pdf.output(output_path)

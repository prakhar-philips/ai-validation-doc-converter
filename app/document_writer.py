from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from textwrap import wrap

def save_as_pdf(text, output_path, max_line_length=100):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    margin = 40
    y = height - margin
    line_height = 14
    wrapped_lines = []

    # Wrap long lines for PDF readability
    for line in text.split('\n'):
        wrapped_lines.extend(wrap(line, width=max_line_length))
        wrapped_lines.append("")  # Blank line after each paragraph

    for line in wrapped_lines:
        if y < margin:
            c.showPage()
            y = height - margin
        c.drawString(margin, y, line)
        y -= line_height

    c.save()

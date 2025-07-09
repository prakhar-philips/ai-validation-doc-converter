import os
import re
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for i, page in enumerate(doc):
            page_text = page.get_text().strip()
            if not page_text:
                print(f"⚠️ Warning: Page {i+1} of {pdf_path} is empty.")
            text += page_text + "\n"
        doc.close()
        return clean_text(text)
    except Exception as e:
        print(f"❌ Error reading {pdf_path}: {e}")
        return ""

def clean_text(text):
    boilerplate_patterns = [
        r"Company Confidential",
        r"Copies are uncontrolled",
        r"Page \d+ of \d+",
        r"Author Authored.*?Approver Approved On.*?\n",
        r"#?\s*Author Authored on Reason For Esign.*?\n",
        r"Doc[\.]?\s*No[\.]?\s*:\s*[\w\.\-\/]+",
        r"Template No[\.]?\s*:\s*[\w\.\-\/]+",
        r"Entity No[\.]?\s*:\s*[\w\.\-\/]+"
    ]

    for pattern in boilerplate_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)

    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

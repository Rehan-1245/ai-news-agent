from PyPDF2 import PdfReader

def read_pdf(path):
    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() + "\n"

    return text
import os
from pypdf import PdfReader

files_dir = r"d:\UHC Agent\Files"
pdf_files = [f for f in os.listdir(files_dir) if f.endswith('.pdf')]

with open(r"d:\UHC Agent\pdf_output.txt", "w", encoding="utf-8") as out:
    for pdf_file in pdf_files:
        path = os.path.join(files_dir, pdf_file)
        out.write(f"--- Contents of {pdf_file} ---\n")
        try:
            reader = PdfReader(path)
            for page in reader.pages:
                out.write(page.extract_text() + "\n")
        except Exception as e:
            out.write(f"Error reading {pdf_file}: {e}\n")
        out.write("-" * 50 + "\n")

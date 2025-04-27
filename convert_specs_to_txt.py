import os
import ocrmypdf
import pdfplumber

"""
Convert the PDFS from the `specs` folder into txt files and save them into the `specs_txt` folder. Doing so requires 2 steps:
1. use OCR to convert the PDF into text-selectable PDF
2. use pdfplumber to extract the text from the text-selectable PDF. This way, we preserve the original tabular layout of the PDF
"""

spec_folder = os.path.join(os.getcwd(), 'hugo_data_samples', 'specs')
ocr_output_folder = os.path.join(os.getcwd(), 'hugo_data_samples', 'specs_ocr')
os.makedirs(ocr_output_folder, exist_ok=True)

print("OCR processing PDFs...")
for pdf_filename in os.listdir(spec_folder):
    input_path = os.path.join(spec_folder, pdf_filename)
    output_path = os.path.join(ocr_output_folder, pdf_filename)
    ocrmypdf.ocr(input_path, output_path, force_ocr=True)
print("OCR done.")

output_dir = os.path.join(os.getcwd(), 'hugo_data_samples', 'specs_txt')
os.makedirs(output_dir, exist_ok=True)

ocr_folder = os.path.join(os.getcwd(), 'hugo_data_samples', 'specs_ocr')
all_pdfs = os.listdir(ocr_folder)

print("Extracting tables and text...")
for pdf_filename in all_pdfs:
    pdf_path = os.path.join(ocr_folder, pdf_filename)
    output_txt = os.path.join(output_dir, pdf_filename.replace('.pdf', '.txt'))

    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            # Extract tables
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    full_text += "\t".join(row) + "\n"
                full_text += "\n"

            # Extract non-tabular text
            full_text += page.extract_text() or ""
            full_text += "\n"

    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(full_text)
print("Done.")

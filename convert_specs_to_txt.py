import os
import cv2
import numpy as np
from pdf2image import convert_from_path
import pytesseract

def preprocess_image(pil_image):
    img = np.array(pil_image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return img

pdf_folder = os.path.join(os.getcwd(), 'hugo_data_samples', 'specs')
output_folder = os.path.join(os.getcwd(), 'hugo_data_samples', 'specs_txt')
os.makedirs(output_folder, exist_ok=True)
custom_config = r'--oem 3 --psm 6'

for pdf_file in os.listdir(pdf_folder):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        images = convert_from_path(pdf_path, dpi=300)  # High-res images

        full_text = ""
        for i, img in enumerate(images):
            preprocessed_img = preprocess_image(img)
            text = pytesseract.image_to_string(preprocessed_img, config=custom_config)

            text = text.replace('$', 'S')
            text = text.replace('BillofMaterials', 'Bill of Materials')
            text = text.replace('PartIDPartName', 'PartID Part Name')
            text = text.replace('QtyNotes', 'Qty Notes')

            full_text += text

        output_path = os.path.join(output_folder, pdf_file.replace('.pdf', '.txt'))
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)

print("Done.")

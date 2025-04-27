import csv
import json
import io
import email
from pdf2image import convert_from_path
import pytesseract
import numpy as np
import cv2


def read_csv(file):
    file.seek(0)
    reader = csv.DictReader(io.StringIO(file.read().decode('utf-8')))
    return json.dumps(list(reader))

def preprocess_image(pil_image):
    img = np.array(pil_image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return img

def read_pdf(file):
    """ Given a PDF file, extract its text using OCR and return the text as a string."""
    
    file_path = "/tmp/temp_pdf.pdf"
    with open(file_path, 'wb') as f:
        f.write(file.read())
    images = convert_from_path(file_path, dpi=300)
    full_text = ""
    custom_config = r'--oem 3 --psm 6'
    for i, img in enumerate(images):
        preprocessed_img = preprocess_image(img)
        text = pytesseract.image_to_string(preprocessed_img, config=custom_config)
        text = text.replace('$', 'S')
        full_text += text
    return json.dumps({"extracted_text": full_text})

def read_txt(file):
    file.seek(0)
    return file.read().decode('utf-8')

def read_eml(file_obj):
    file_obj.seek(0)
    return file_obj.read().decode('utf-8', errors='ignore')
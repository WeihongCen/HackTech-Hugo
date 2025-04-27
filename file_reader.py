import csv
import json
import io
import email


def read_csv(file):
    file.seek(0)
    reader = csv.DictReader(io.StringIO(file.read().decode('utf-8')))
    return json.dumps(list(reader))

def read_pdf(file):
    return ""

def read_txt(file):
    file.seek(0)
    return file.read().decode('utf-8')

def read_eml(file_obj):
    file_obj.seek(0)
    return file_obj.read().decode('utf-8', errors='ignore')
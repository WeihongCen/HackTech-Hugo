import os
from flask      import Flask, request, jsonify
from openai     import OpenAI
from supabase   import create_client
from dotenv     import load_dotenv

from file_reader    import read_csv, read_pdf, read_txt, read_eml
from data_populate  import generate_data_rows, upsert
from data_query     import query


# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


client_supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
client_openai = OpenAI()
app = Flask(__name__)


ALLOWED_EXTENSIONS = {'pdf', 'csv', 'txt', 'eml'}
EXT_TO_READER = {
    'csv': read_csv,
    'pdf': read_pdf,
    'txt': read_txt,
    'eml': read_eml,
}


@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return 'No file part', 400

    files = request.files.getlist('files')
    results = {}

    for file in files:
        if file.filename == '':
            continue
        if not '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
            return f"File type not allowed: {file.filename}", 400

        extension = file.filename.rsplit('.', 1)[1].lower()
        reader = EXT_TO_READER.get(extension)

        if reader:
            content = reader(file)
            results[file.filename] = content
        else:
            results[file.filename] = 'Unsupported for direct reading'

    for content in results.values():
        rows = generate_data_rows(client_openai, content)
        upsert(client_supabase, rows)

    return jsonify(results)


@app.route('/modify', methods=['POST'])
def modify_database():
    try:
        content = request.json.get("user_input", "")
        
        if not content:
            return jsonify({"error": "Missing 'user_input' field"}), 400

        # Generate rows from the input
        rows = generate_data_rows(client_openai, content)

        # Upsert into Supabase
        upsert(client_supabase, rows)

        return jsonify({"status": "success", "modified_rows": len(rows)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/query', methods=['POST'])
def query_database():
    try:
        content = request.json.get("user_input", "")
        
        if not content:
            return jsonify({"error": "Missing 'user_input' field"}), 400

        # Generate rows from the input
        response = query(content)

        return jsonify({"status": "success", "response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000)
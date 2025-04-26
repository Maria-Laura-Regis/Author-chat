from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import openai
import os
from dotenv import load_dotenv
import tempfile

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Store author contexts in memory (for demo)
author_contexts = {}

@app.route('/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload and extract text"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "File must be a PDF"}), 400

        # Save temporarily and process
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            file.save(tmp.name)
            reader = PdfReader(tmp.name)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            os.unlink(tmp.name)  # Delete temp file

        session_id = request.form.get('session_id', 'default')
        author_contexts[session_id] = text[:10000]  # Store first 10k chars

        return jsonify({
            "success": True,
            "session_id": session_id,
            "pages": len(reader.pages),
            "characters": len(text)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Generate author-style responses"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400

        author_style = author_contexts.get(session_id, "")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Respond as the author would. Their writing style:\n{author_style[:3000]}"},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=200
        )

        return jsonify({
            "success": True,
            "reply": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import openai
import os
from dotenv import load_dotenv
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={
    r"/upload": {"origins": "*"},
    r"/chat": {"origins": "*"}
})  # Enable CORS with explicit routes

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.error("Missing OPENAI_API_KEY in .env file!")

# Store author contexts in memory (for demo)
author_contexts = {}

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "endpoints": {
            "upload": "POST /upload",
            "chat": "POST /chat",
            "health": "GET /health"
        }
    })

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_pdf():
    """Handle PDF upload and text extraction"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        if 'file' not in request.files:
            logger.error("No file in request")
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({"error": "No selected file"}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            logger.error("Invalid file type")
            return jsonify({"error": "File must be a PDF"}), 400

        # Save temporarily and process
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            file.save(tmp.name)
            try:
                reader = PdfReader(tmp.name)
                text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            except Exception as e:
                logger.error(f"PDF processing failed: {str(e)}")
                return jsonify({"error": "Invalid PDF file"}), 400
            finally:
                os.unlink(tmp.name)  # Delete temp file

        session_id = request.form.get('session_id', 'default')
        author_contexts[session_id] = text[:10000]  # Store first 10k chars

        logger.info(f"PDF uploaded successfully - {len(reader.pages)} pages")
        return jsonify({
            "success": True,
            "session_id": session_id,
            "pages": len(reader.pages),
            "characters": len(text)
        })

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Generate author-style responses"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        session_id = data.get('session_id', 'default')
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400

        author_style = author_contexts.get(session_id, "")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": f"Respond as the author would. Their writing style:\n{author_style[:3000]}"
                },
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=200
        )

        return jsonify({
            "success": True,
            "reply": response.choices[0].message.content
        })

    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI error: {str(e)}")
        return jsonify({
            "error": "AI service error",
            "message": str(e)
        }), 500
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "openai_ready": bool(openai.api_key)
    })

def _build_cors_preflight_response():
    response = jsonify({"status": "preflight"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
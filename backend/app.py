from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# In-memory storage for demo purposes
author_contexts = {}

@app.route('/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF file upload and text extraction"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        
        # Check if file has a name
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Check if file is PDF
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "File must be a PDF"}), 400
        
        # Process PDF
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        # Store the extracted text with a session ID
        session_id = request.form.get('session_id', 'default')
        author_contexts[session_id] = text[:10000]  # Store first 10k chars
        
        return jsonify({
            "success": True,
            "message": "PDF processed successfully",
            "session_id": session_id,
            "characters_processed": len(text),
            "pages": len(reader.pages)
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "An error occurred while processing the PDF"
        }), 500

@app.route('/chat', methods=['POST'])
def chat_with_author():
    """Simulate conversation with the author"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
            
        # Get author context or use default
        author_text = author_contexts.get(session_id, "")
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an AI trained to mimic an author's style. Here is their writing:\n{author_text[:3000]}"},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        return jsonify({
            "success": True,
            "reply": response.choices[0].message.content
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to generate response"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "endpoints": {
            "upload": "POST /upload",
            "chat": "POST /chat",
            "health": "GET /health"
        }
    })

@app.route('/')
def home():
    return """
    <h1>Author Chat API</h1>
    <p>Available endpoints:</p>
    <ul>
        <li>POST /upload - Upload PDF</li>
        <li>POST /chat - Chat with author</li>
        <li>GET /health - Server status</li>
    </ul>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
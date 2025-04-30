import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)

# Configure Gemini API
try:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro') # Or choose another suitable model
    print("Gemini API configured successfully.")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    model = None # Set model to None if configuration fails

# --- Routes ---

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/explain', methods=['POST'])
def explain_topic():
    """Handles the explanation request from the frontend."""
    if not model:
         return jsonify({"error": "Gemini API not configured properly. Check server logs."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request data"}), 400

        abilities = data.get('abilities', '')
        likes = data.get('likes', '')
        topic = data.get('topic', '')
        language = data.get('language', 'English') # Default to English

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        # --- Construct the Prompt for Gemini ---
        prompt = f"""
        Explain the topic "{topic}" in detail, specifically for someone who has the following abilities or skills: "{abilities}" and likes the following things: "{likes}".

        Tailor the explanation style and examples to resonate with these abilities and interests. For instance, if they like 'building things' and are good at 'math', use construction or mathematical analogies. If they like 'storytelling' and are good at 'drawing', use narrative structures or visual examples.

        Provide clear, step-by-step explanations where applicable.
        Use relevant examples based on the provided abilities and likes.
        Ensure the explanation is comprehensive and easy to understand for the target profile.

        Respond ONLY in {language}. Do not include any introductory phrases like "Okay, here is the explanation..." or similar conversational text before the actual explanation starts. Just provide the explanation directly.
        Format the output using Markdown for better readability (e.g., use headings, lists, bold text).
        """

        print(f"--- Sending Prompt to Gemini (Lang: {language}) ---")
        # print(prompt) # Uncomment to debug the prompt

        response = model.generate_content(prompt)

        # print("--- Received Response from Gemini ---") # Uncomment for debugging
        # print(response.text)

        return jsonify({"explanation": response.text})

    except Exception as e:
        print(f"Error during Gemini generation: {e}")
        # You might want to log the full error traceback here
        return jsonify({"error": f"An error occurred while generating the explanation: {str(e)}"}), 500

# --- PWA Routes ---

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/service-worker.js')
def serve_sw():
    # Important: Serve with the correct MIME type
    response = send_from_directory('static/js', 'service-worker.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response

# --- Serve Static Files (CSS, JS, Images) ---
# Flask automatically serves files from the 'static' folder at the /static URL path.
# We already configured specific routes for manifest and sw for clarity and control.

if __name__ == '__main__':
    # Use 0.0.0.0 to be accessible on your network, useful for testing PWA on mobile
    # Set debug=True for development (auto-reloads), False for production
    app.run(host='0.0.0.0', port=5000, debug=True)
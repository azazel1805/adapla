# Keep imports and app setup as before
import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure Gemini API (keep this part)
try:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini API configured successfully.")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    model = None

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

# --- UPDATED explain_topic FUNCTION ---
@app.route('/explain', methods=['POST'])
def explain_topic():
    """Handles the explanation request from the frontend using the PAMT persona and analogy focus."""
    if not model:
         return jsonify({"error": "Gemini API not configured properly. Check server logs."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request data"}), 400

        # We'll primarily use 'likes' for the interests as per the new prompt's focus
        # 'abilities' is received but not directly used in this specific prompt structure
        # You could potentially add a sentence to the prompt referencing abilities if needed later.
        abilities = data.get('abilities', '') # Still capture it if sent
        likes = data.get('likes', '') # This maps to "User's Interests"
        topic = data.get('topic', '')
        language = data.get('language', 'English') # Default to English

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        # --- Construct the NEW Prompt using the PAMT structure ---
        # Use the 'likes' field as the primary source for interests
        interests_string = likes # Use the raw string from the textarea

        prompt = f"""
        You are PAMT, an expert tutor specializing in personalized analogies and metaphors.
        Your goal is to explain a complex topic using analogies drawn *specifically* from the user's stated interests.

        User's Interests: {interests_string}
        Complex Topic to Explain: {topic}

        Instructions:
        1. Prioritize analogies directly related to the provided interests.
        2. If multiple interests are provided, try to weave them together or pick the most relevant one for the specific aspect of the topic you are explaining.
        3. If the interests seem completely unrelated, acknowledge this difficulty but still attempt a creative connection, perhaps focusing on abstract concepts shared between the topic and the interest (e.g., rules in games vs. rules in physics, processes in cooking vs. processes in computing).
        4. Keep the explanation clear, concise, and intuitive for someone familiar with the stated interests.
        5. Avoid generic analogies that don't relate to the user's profile.
        6. Structure the explanation logically. Start with a core analogy if possible.
        7. Format the output using Markdown for better readability (e.g., use headings #, ##, lists *, -, bold **text**).
        8. Respond ONLY in {language}. Do not include any introductory phrases like "Okay, here is the explanation..." or "Certainly, let's break down..." or similar conversational text before the actual explanation starts. Just provide the explanation directly.

        Generate the explanation now:
        """

        print(f"--- Sending PAMT Prompt to Gemini (Lang: {language}) ---")
        # print(prompt) # Uncomment to debug the exact prompt being sent

        response = model.generate_content(prompt)

        # print("--- Received Response from Gemini ---") # Uncomment for debugging
        # print(response.text)

        # Ensure the response content is accessed correctly
        explanation_text = response.text

        return jsonify({"explanation": explanation_text})

    except Exception as e:
        print(f"Error during Gemini generation: {e}")
        # It's helpful to log the actual error type and traceback in real scenarios
        # import traceback
        # print(traceback.format_exc())
        return jsonify({"error": f"An error occurred while generating the explanation: {str(e)}"}), 500


# --- PWA Routes (Keep these as they are) ---
@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/service-worker.js')
def serve_sw():
    response = send_from_directory('static/js', 'service-worker.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response

# --- Main execution (Keep as is) ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # Set debug=False for production

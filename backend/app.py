# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS        # Handles cross-origin requests
import requests, os

app = Flask(__name__)
CORS(app)  # Allow React frontend to make requests

# Example FAQ data (lowercased keys): common questions with canned answers.
faq = {
    "hello": "Hi there! How can I help you?",
    "what is your name": "I'm a simple FAQ bot.",
    "how does this work": "I use a Hugging Face language model to answer questions."
}

# Hugging Face model configuration
HF_MODEL = "HuggingFaceTB/SmolLM3-3B"     # Example model ID (3B params, Apache-2.0):contentReference[oaicite:14]{index=14}
# You could also use "distilgpt2" (82M, Apache-2.0):contentReference[oaicite:15]{index=15} for a smaller model.
HF_TOKEN = os.getenv("HF_TOKEN")          # Hugging Face API token (set this in .env or Render)

@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat queries from the frontend."""
    data = request.get_json()
    user_input = data.get("message", "")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # Normalize the question text.
    question = user_input.lower().strip()
    # If the question matches a known FAQ, return that answer.
    if question in faq:
        return jsonify({"response": faq[question]})

    # Otherwise, query the Hugging Face Inference API.
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}  # token from env
    payload = {"inputs": user_input}  # simple input for text-generation tasks
    API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    response = requests.post(API_URL, headers=headers, json=payload)
    res_json = response.json()

    # The API returns a list of generations; grab the text.
    answer = ""
    if isinstance(res_json, list) and "generated_text" in res_json[0]:
        answer = res_json[0]["generated_text"]

    # Return the answer as JSON.
    return jsonify({"response": answer})


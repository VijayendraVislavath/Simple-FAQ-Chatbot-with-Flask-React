# backend/app.py
import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
DISTILBERT_MODEL = "distilbert-base-uncased-distilled-squad"

app = Flask(__name__)
CORS(app)

# FAQ knowledge base: list of dicts with questions and answers
faqs = [
    {
        "question": "What is your return policy?",
        "answer": "Our return policy lasts 30 days. If 30 days have gone by since your purchase, unfortunately, we can’t offer you a refund or exchange."
    },
    {
        "question": "How do I reset my password?",
        "answer": "To reset your password, click on 'Forgot password' at the login page and follow the instructions sent to your email."
    },
    {
        "question": "What are your business hours?",
        "answer": "Our customer support is available Monday through Friday, 9 AM to 5 PM."
    },
    # Add more FAQs here as needed
]

def query_distilbert(question, context, max_retries=3):
    if not HF_TOKEN:
        return None, "Hugging Face API token is missing."

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    API_URL = f"https://api-inference.huggingface.co/models/{DISTILBERT_MODEL}"
    payload = {"inputs": {"question": question, "context": context}}

    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            if response.status_code == 503:
                try:
                    error_data = response.json()
                    if "currently loading" in str(error_data).lower():
                        estimated_time = error_data.get("estimated_time", 20)
                        wait_time = min(estimated_time, 30)
                        print(f"[HF] Model is loading. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                except Exception:
                    pass
                return None, "Model unavailable (503)."

            response.raise_for_status()
            result = response.json()
            return result.get("answer", ""), result.get("score", 0)

        except Exception as e:
            print(f"[HF] Attempt {attempt+1} failed:", e)
            time.sleep(2)

    return None, 0

@app.before_request
def warm_up_model():
    if not getattr(app, "warmed_up", False) and HF_TOKEN:
        print("[Warm-up] Loading DistilBERT model...")
        _, _ = query_distilbert("Hello", "Say hello back.")
        app.warmed_up = True

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_question = data.get("message", "")

    if not user_question:
        return jsonify({"error": "No message provided"}), 400

    # Check if user query matches any FAQ question exactly (simple direct match)
    for faq_entry in faqs:
        if user_question.lower().strip() == faq_entry["question"].lower().strip():
            return jsonify({"response": faq_entry["answer"]})

    # Find FAQ answer with highest confidence score
    best_answer = None
    highest_score = 0.0
    threshold = 0.3  # confidence threshold to accept answer

    for faq_entry in faqs:
        answer, score = query_distilbert(user_question, faq_entry["answer"])
        if answer and score > highest_score:
            highest_score = score
            best_answer = answer

    if highest_score >= threshold and best_answer:
        return jsonify({"response": best_answer})
    else:
        return jsonify({"response": "Sorry, I don't have an answer for that. Please contact support."})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": DISTILBERT_MODEL})

if __name__ == "__main__":
    app.run(debug=True)

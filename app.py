from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Ideally store this in env variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBKUQJkxy7gmyuNrA5rBewY0pUdtrbkiaE")
MODEL = "gemini-1.5-flash-latest"

@app.route("/rewrite", methods=["POST"])
def rewrite_prompt():
    data = request.json
    user_prompt = data.get("prompt", "")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"Rewrite this prompt to be more effective for AI assistance:\n\n{user_prompt}"}]}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    try:
        improved = result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        improved = "Sorry, could not improve prompt."

    return jsonify({"improved_prompt": improved})

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify
import requests
import os
import base64
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@app.route("/rewrite", methods=["POST"])
def rewrite_prompt():
    """
    Rewrites a user's prompt to be more effective for AI assistance.
    Accepts both text-only prompts (JSON) and multimodal prompts (form-data
    with text and an image file).
    """
    improved_prompt = "Sorry, could not improve prompt."
    payload = None

    # Check if the request contains an image file
    if 'image' in request.files:
        # Multimodal prompt: an image and text prompt
        image_file = request.files['image']
        user_prompt = request.form.get("prompt", "")
        model = "gemini-2.5-flash-preview-05-20"
        
        # Read the image data and encode it in base64
        image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        mime_type = image_file.mimetype

        # Construct the multimodal payload for the Gemini API
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"Rewrite the following user prompt to be more detailed, descriptive, and effective for an AI assistant. The rewritten prompt should be a single, continuous sentence without bullet points or newlines. Use the attached image as context. The original prompt is: {user_prompt}"},
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": base64_image
                            }
                        }
                    ]
                }
            ]
        }
    else:
        # Text-only prompt: JSON payload
        model = "models/gemma-3-27b-it"
        data = request.json
        user_prompt = data.get("prompt", "")

        # Construct the text-only payload
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"Rewrite the following user prompt to be more detailed, descriptive, and effective for an AI assistant. The rewritten prompt should be a single, continuous sentence without bullet points or newlines. The original prompt is: {user_prompt}"}]}
            ]
        }
        url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={GEMINI_API_KEY}"
        print("Final URL being used:", url)

    # Make the API call only if a valid payload was created
    if payload:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            print("Text-only API Status Code:", response.status_code)
            print("Text-only API Response Body:", response.text)
            result = response.json()
            
            # Extract the improved prompt from the API response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"] and len(candidate["content"]["parts"]) > 0:
                    improved_prompt = candidate["content"]["parts"][0]["text"]
                    
                    # Clean up the output by removing newlines and excessive spaces
                    improved_prompt = improved_prompt.replace("\n", " ").strip()
                    improved_prompt = re.sub(r'\s+', ' ', improved_prompt)
        except (KeyError, IndexError, requests.exceptions.RequestException) as e:
            # The more robust error handling was a good debugging tool.
            # In a production app, you might re-implement more specific error
            # handling or logging here.
            pass

    return jsonify({"improved_prompt": improved_prompt})

if __name__ == "__main__":
    app.run(debug=True)
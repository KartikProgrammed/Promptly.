from flask import Flask, jsonify, request
import requests
import os
import base64
import re
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
handler = app

from flask_cors import CORS
CORS(app, origins=[
    "chrome-extension://*",
    "http://127.0.0.1:5000",
    "https://promptly-orcin.vercel.app"
])

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Promptly backend running"})


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
                        {"text": f"Rewrite the following user prompt to be more detailed, descriptive, and effective for an AI assistant. The rewritten prompt should be a single, continuous sentence without bullet points or newlines. Use the attached image as context. The original prompt is: {user_prompt}, do not use any special characters or symbols or bullets i just need plain white text with no formatting."},
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
        model = "gemma-3-27b-it"
        data = request.json
        user_prompt = data.get("prompt", "")

        # Construct the text-only payload
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"Rewrite the following user prompt to be more detailed, descriptive, and effective for an AI assistant. The rewritten prompt should be a single, continuous sentence without bullet points or newlines. The original prompt is: {user_prompt}"}]}
            ]
        }

    # Make the API call only if a valid payload was created
    if payload:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            print("API Status Code:", response.status_code)
            print("API Response Body:", response.text)
            print("Request URL:", url)
            print("Request Payload:", payload)
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

@app.route("/concise", methods=["POST"])
def concise_reply():
    """
    Returns a very concise, one-line answer. Accepts both text-only prompts
    (JSON) and multimodal prompts (form-data with text and an image file).
    """
    reply = "Sorry, could not generate a concise reply."
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
                        {"text": f"Rewrite the following user prompt to be more detailed, descriptive, and effective for an AI assistant. The rewritten prompt should be a single, continuous sentence without bullet points or newlines and should direct the AI assistant to give a concise and to the point answer. Use the attached image as context. The original prompt is: {user_prompt}, do not use any special characters or symbols or bullets i just need plain white text with no formatting."},
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
        model = "gemma-3-27b-it"
        data = request.json
        user_prompt = data.get("prompt", "")

        # Construct the text-only payload
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"Rewrite the following user prompt to be more detailed, descriptive, and effective for an AI assistant. The rewritten prompt should be a single, continuous sentence without bullet points or newlines and should direct the AI assistant to give a concise and to the point answer. The original prompt is: {user_prompt}, do not use any special characters or symbols or bullets i just need plain white text with no formatting."}]}
            ]
        }

    # Make the API call only if a valid payload was created
    if payload:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()

            # Extract the reply from the API response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"] and len(candidate["content"]["parts"]) > 0:
                    reply = candidate["content"]["parts"][0]["text"]

                    # Clean up the output by removing newlines and excessive spaces
                    reply = reply.replace("\n", " ").strip()
                    reply = re.sub(r'\s+', ' ', reply)
        except (KeyError, IndexError, requests.exceptions.RequestException):
            pass

    return jsonify({"concise_reply": reply})

@app.route("/detailed", methods=["POST"])
def detailed_reply():
    """
    Returns a detailed, long-form answer/solution. Accepts both text-only
    prompts (JSON) and multimodal prompts (form-data with text and an image
    file).
    """
    reply = "Sorry, could not generate a detailed reply."
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
                        {"text": f"rewrite the below prompt such that when sent to an AI assistant it Provides a thorough, detailed, step-by-step explanation or solution. Cover assumptions, rationale, alternatives, and edge cases. Use clear, plain text in multiple sentences without bullet points, special characters, or markdown. Use the attached image as context if relevant. The user prompt is: {user_prompt}, generate only the prompt and no other text, do not use any special characters or symbols or bullets i just need plain white text with no formatting."},
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
        model = "gemma-3-27b-it"
        data = request.json
        user_prompt = data.get("prompt", "")

        # Construct the text-only payload
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"rewrite the below prompt such that when sent to an AI assistant it Provides a thorough, detailed, step-by-step explanation or solution. Cover assumptions, rationale, alternatives, and edge cases. Use clear, plain text in multiple sentences without bullet points, special characters, or markdown. Use the attached image as context if relevant. The user prompt is: {user_prompt}, generate only the prompt and no other text, do not use any special characters or symbols or bullets i just need plain white text with no formatting."}]}
            ]
        }

    # Make the API call only if a valid payload was created
    if payload:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()

            # Extract the reply from the API response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"] and len(candidate["content"]["parts"]) > 0:
                    reply = candidate["content"]["parts"][0]["text"]

                    # Normalize whitespace
                    reply = reply.replace("\n", " ").strip()
                    reply = re.sub(r'\s+', ' ', reply)
        except (KeyError, IndexError, requests.exceptions.RequestException):
            pass

    return jsonify({"detailed_reply": reply})

@app.route("/math", methods=["POST"])
def math_reply():
    """
    Returns a math-focused prompt that, when sent to an AI assistant, asks it
    to solve equations, theorems, and other math problems efficiently with
    strong step-by-step explanations and reasoning. Accepts JSON or
    form-data (optional image context).
    """
    reply = "Sorry, could not generate a math-focused prompt."
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
                        {"text": f"rewrite the below prompt such that when sent to an AI assistant it solves mathematics equations, theorems, and related problems efficiently and accurately, providing clear step-by-step reasoning, proofs or derivations when relevant, and strong explanations of each step. Use the attached image as context if relevant. The user prompt is: {user_prompt}, generate only the prompt and no other text, do not use any special characters or symbols or bullets i just need plain white text with no formatting. if you don't find maths relevance to the prompt, just return the prompt as is."},
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
        model = "gemma-3-27b-it"
        data = request.json
        user_prompt = data.get("prompt", "")

        # Construct the text-only payload
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"rewrite the below prompt such that when sent to an AI assistant it solves mathematics equations, theorems, and related problems efficiently and accurately, providing clear step-by-step reasoning, proofs or derivations when relevant, and strong explanations of each step. The user prompt is: {user_prompt}, generate only the prompt and no other text, do not use any special characters or symbols or bullets i just need plain white text with no formatting. if you don't find maths relevance to the prompt, just return the prompt as is."}]}
            ]
        }

    # Make the API call only if a valid payload was created
    if payload:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()

            # Extract the reply from the API response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"] and len(candidate["content"]["parts"]) > 0:
                    reply = candidate["content"]["parts"][0]["text"]

                    # Normalize whitespace
                    reply = reply.replace("\n", " ").strip()
                    reply = re.sub(r'\s+', ' ', reply)
        except (KeyError, IndexError, requests.exceptions.RequestException):
            pass

    return jsonify({"math_reply": reply})

import os
import markdown
import openai
from flask import Blueprint, request, jsonify
from datetime import datetime

# Load OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_AI_KEY")

# Create a Flask Blueprint
writing_api = Blueprint("writing_api", __name__)

# Base directory for storing drafts
DRAFTS_DIR = "/flask-backend/drafts"
os.makedirs(DRAFTS_DIR, exist_ok=True)

# Helper function to get the latest markdown file
def get_latest_juncture():
    files = sorted(
        [f for f in os.listdir(DRAFTS_DIR) if f.endswith(".md")],
        key=lambda x: os.path.getmtime(os.path.join(DRAFTS_DIR, x)),
        reverse=True
    )
    return files[0] if files else None

# Endpoint: Chat with OpenAI Assistant
@writing_api.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        ai_response = response["choices"][0]["message"]["content"]
        return jsonify({"response": ai_response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint: Retrieve structured prompt based on latest Page/Juncture
@writing_api.route("/structured-prompt", methods=["GET"])
def structured_prompt():
    latest_file = get_latest_juncture()

    if not latest_file:
        return jsonify({"error": "No drafts found"}), 404

    with open(os.path.join(DRAFTS_DIR, latest_file), "r") as file:
        content = file.read()

    structured_prompt = f"""
    Last saved: {latest_file}
    ---
    Based on the latest juncture, here are some structured prompts:
    1. **How does this scene build upon previous events?**
    2. **Who is involved, and what are their motivations?**
    3. **What action happens in this scene, and how does it progress the story?**
    4. **What key details need to be considered for consistency?**
    5. **What creative elements should be explored?**
    """

    return jsonify({"prompt": structured_prompt, "latest_text": content}), 200

# Endpoint: Save draft as Markdown
@writing_api.route("/save-draft", methods=["POST"])
def save_draft():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"juncture_{timestamp}.md"

    with open(os.path.join(DRAFTS_DIR, filename), "w") as file:
        file.write(text)

    return jsonify({"message": "Draft saved successfully", "filename": filename}), 200

# Endpoint: Add lore updates
@writing_api.route("/update-lore", methods=["POST"])
def update_lore():
    data = request.get_json()
    lore_text = data.get("lore", "").strip()

    if not lore_text:
        return jsonify({"error": "No lore provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are updating structured worldbuilding lore."},
                {"role": "user", "content": f"Add to lore: {lore_text}"}
            ]
        )
        ai_response = response["choices"][0]["message"]["content"]
        return jsonify({"response": ai_response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

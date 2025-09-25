from flask import Flask, request, jsonify, render_template
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq
from datetime import datetime
import os
from dotenv import load_dotenv
import requests  # added for WHO API calls

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Groq API client (read from .env)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=GROQ_API_KEY)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    chat_history = request.json.get("chat_history", [])
    user_message = request.json.get("message", "")
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Health Buddy, a friendly AI health assistant. "
    "Default language: English. "
    "Support Hindi if user asks with phrases like 'hindi mein baat karo', 'reply in Hindi'. "
    "Support other Indian regional languages if user clearly requests: "
    "- Marathi ('marathi mein baat karo') "
    "- Tamil ('tamil la pesa') "
    "- Telugu ('telugu lo matladu') "
    "- Bengali ('bangla te katha bolo') "
    "- Gujarati ('gujarati ma vaat karo') "
    "- Punjabi ('punjabi vich gall karo') "
    "Always keep responses simple, clear, short, and easy to understand. "
    "For each regional language, use basic vocabulary, easy grammar, and friendly tone. "
    "Never auto-switch language unless user specifically asks. "
    "Always provide accurate, evidence-based health information. "
    "When discussing vaccines, diseases, or treatments, refer to WHO guidelines. "
    "Remember: You are Health Buddy - a caring health companion."

                    )
                },
                *chat_history
            ]
        )

        bot_reply = response.choices[0].message.content
        
    except Exception as e:
        bot_reply = f"Error: {str(e)}"

    return jsonify({"reply": bot_reply})


@app.route("/chat-ui")
def chat_ui():
    return render_template("chat_dashboard.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    # Receive inbound message text from Twilio
    incoming_text = request.form.get("Body", "").strip()

    # Default fallback reply
    bot_reply = "Sorry, I couldn't understand that. Please try again."

    if incoming_text:
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are Health Buddy, a friendly AI health assistant. "
    "Default language: English. "
    "Support Hindi if user asks with phrases like 'hindi mein baat karo', 'reply in Hindi'. "
    "Support other Indian regional languages if user clearly requests: "
    "- Marathi ('marathi mein baat karo') "
    "- Tamil ('tamil la pesa') "
    "- Telugu ('telugu lo matladu') "
    "- Bengali ('bangla te katha bolo') "
    "- Gujarati ('gujarati ma vaat karo') "
    "- Punjabi ('punjabi vich gall karo') "
    "Always keep responses simple, clear, short, and easy to understand. "
    "For each regional language, use basic vocabulary, easy grammar, and friendly tone. "
    "Never auto-switch language unless user specifically asks. "
    "Always provide accurate, evidence-based health information. "
    "When discussing vaccines, diseases, or treatments, refer to WHO guidelines. "
    "Remember: You are Health Buddy - a caring health companion."

                        ),
                    },
                    {"role": "user", "content": incoming_text},
                ],
            )

            bot_reply = response.choices[0].message.content
        except Exception as e:
            bot_reply = f"Error: {str(e)}"

    # Build TwiML response for WhatsApp/SMS
    twiml = MessagingResponse()
    twiml.message(bot_reply)
    return str(twiml), 200, {"Content-Type": "application/xml"}



@app.route("/who-data")
def who_data():
    try:
        url = "https://ghoapi.azureedge.net/api/WHOSIS_000001"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Optional: filter by country code if provided as query param
        country = request.args.get("country", None)
        if country:
            filtered = [item for item in data.get("value", []) if item.get("SpatialDim") == country]
        else:
            # default: return first 50 records to avoid huge responses
            filtered = data.get("value", [])[:50]

        return jsonify({"status": "success", "count": len(filtered), "data": filtered})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
# ---------------------------------------


if __name__ == "__main__":
    app.run(debug=True)

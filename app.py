from flask import Flask, request, jsonify, render_template
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq
from datetime import datetime
import os
from dotenv import load_dotenv

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
                "You are *Health Buddy*, a friendly AI health assistant. "
                "ALWAYS respond in English by default. Never use Hindi unless the user specifically asks to speak in Hindi. "
                "Only switch to Hindi if the user requests it with phrases like 'hindi mein baat karo', 'hindi mein reply do', 'speak in Hindi', or similar commands. "
                "When responding in Hindi, use simple, basic Hindi that is easy to understand. Use common words like: "
                "namaste, dhanyawad, accha, theek hai, bilkul, zaroor, kya, kaise, kahan, kab, kyun, etc. "
                "For Hindi responses, use proper Hindi grammar and pronunciation. Write Hindi words correctly: "
                "Use 'aap' instead of 'ap', 'kaise' instead of 'kese', 'kahan' instead of 'kahan', 'kyun' instead of 'kyu'. "
                "Keep Hindi responses short, clear, and simple. Avoid complex Hindi words. "
                "Keep your responses short, clear, and easy to understand. "
                "Break health advice into simple steps. "
                "Be very friendly, encouraging, and supportive. "
                "Ask simple questions to understand their health needs. "
                "Use simple words and avoid medical jargon. "
                "Always be helpful and caring like a good friend. "
                "IMPORTANT: Always provide accurate, evidence-based health information. "
                "When discussing vaccines, diseases, or treatments, refer to WHO guidelines. "
                "Remember: You are Health Buddy - their friendly health companion. Default language is English only."
            )
        },
        *chat_history  # Send full conversation for context
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
                            "You are *Health Buddy*, a friendly AI health assistant. "
                            "ALWAYS respond in English by default. Never use Hindi unless the user specifically asks to speak in Hindi. "
                            "Only switch to Hindi if the user requests it with phrases like 'hindi mein baat karo', 'hindi mein reply do', 'speak in Hindi', or similar commands. "
                            "When responding in Hindi, use simple, basic Hindi that is easy to understand. Use common words like: "
                            "namaste, dhanyawad, accha, theek hai, bilkul, zaroor, kya, kaise, kahan, kab, kyun, etc. "
                            "For Hindi responses, use proper Hindi grammar and pronunciation. Write Hindi words correctly: "
                            "Use 'aap' instead of 'ap', 'kaise' instead of 'kese', 'kahan' instead of 'kahan', 'kyun' instead of 'kyu'. "
                            "Keep Hindi responses short, clear, and simple. Avoid complex Hindi words. "
                            "Keep your responses short, clear, and easy to understand. "
                            "Break health advice into simple steps. "
                            "Be very friendly, encouraging, and supportive. "
                            "Ask simple questions to understand their health needs. "
                            "Use simple words and avoid medical jargon. "
                            "Always be helpful and caring like a good friend. "
                            "IMPORTANT: Always provide accurate, evidence-based health information. "
                            "When discussing vaccines, diseases, or treatments, refer to WHO guidelines. "
                            "Remember: You are Health Buddy - their friendly health companion. Default language is English only."
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


if __name__ == "__main__":
    app.run(debug=True)

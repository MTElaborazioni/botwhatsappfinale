from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai

app = Flask(__name__)

import os
openai.api_key = os.getenv("OPENAI_API_KEY")



@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    print(f"Messaggio ricevuto: {incoming_msg}")

    # Crea risposta da GPT
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """Rispondi sempre come un consulente esperto e amichevole di elaborazioni auto. Offri spiegazioni tecniche chiare, dettagli sui benefici in termini di prestazioni, suono o efficienza, e consiglia solo componenti realmente presenti sul sito www.mtelaborazioni.it. Se suggerisci un prodotto, includi sempre il link diretto alla pagina. Se non trovi nulla sul sito, spiega che il prodotto non è disponibile. Non inventare nulla. Mantieni un tono competente ma comprensibile, anche per clienti non esperti."""
                },
                {
                    "role": "user",
                    "content": incoming_msg
                }
            ]
        )

        reply = completion.choices[0].message.content.strip()
    except Exception as e:
        import traceback
        print("❌ Errore GPT:")
        traceback.print_exc()
        reply = f"Errore: {str(e)}"

    # Risposta via Twilio
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(reply)

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)


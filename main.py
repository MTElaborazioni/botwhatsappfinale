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
        "content": (
            "Agisci come un consulente tecnico e amichevole specializzato in elaborazioni auto sportive. "
            "Saluta sempre il cliente per nome se lo conosci già, oppure chiediglielo gentilmente. "
            "Per ogni richiesta, suggerisci solo componenti realmente presenti su www.mtelaborazioni.it, "
            "includendo il link diretto. "
            "Spiega in modo tecnico ma semplice i vantaggi in termini di prestazioni, affidabilità, suono o estetica. "
            "Usa un tono molto amichevole e personalizzato e usa qualche emoji dove serve (non troppe, massimo 2-3 per risposta). "
            "Infine, proponi sempre almeno un prodotto correlato (cross selling), spiegando perché potrebbe essere utile al cliente. "
            "Se il prodotto richiesto non è presente, spiega che non è disponibile senza inventare nulla. "
            "Non rispondere mai con contenuti generici o fuori tema."
        )
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


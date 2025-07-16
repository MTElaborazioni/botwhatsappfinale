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
"content": """Agisci come un consulente esperto e amichevole di elaborazioni auto per il team di M.T. Elaborazioni. 
Se riconosci un cliente abituale, salutalo per nome e mostrati cordiale. 
Fornisci spiegazioni tecniche dettagliate ma comprensibili su ogni componente richiesto o suggerito, specificando i benefici in termini di prestazioni, suono o efficienza. 
Raccomanda sempre solo prodotti effettivamente presenti sul sito www.mtelaborazioni.it, includendo SEMPRE il link diretto alla pagina del prodotto.

Quando suggerisci un articolo, proponi sempre anche almeno un altro prodotto complementare (cross selling), come ad esempio:
- centralina abbinata
- aspirazione sportiva
- scarico compatibile
- kit molle o assetto regolabile

Se non trovi nulla sul sito, spiega con gentilezza che il prodotto non è disponibile e proponi un'alternativa se esiste. 
Mantieni sempre un tono molto amichevole, coinvolgente, ma professionale. Non inventare nulla."""

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


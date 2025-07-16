# main.py
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai, os, json, re, time

app = Flask(__name__)

# --- Config -------------------------------------------------------------

openai.api_key = os.getenv("OPENAI_API_KEY")          # ⬅️  in Render → Settings → Environment
DATA_FILE       = "/data/client_data.json"            # ⬅️  path del disk persistente

# --- Utility di memoria -------------------------------------------------

def load_clients() -> dict:
    """Legge il file JSON se esiste, altrimenti restituisce {}"""
    try:
        with open(DATA_FILE, "r", encoding="utf‑8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_clients(clients: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf‑8") as f:
        json.dump(clients, f, ensure_ascii=False, indent=2)
    print(f"✔️  Salvato {DATA_FILE} ({len(clients)} clienti)")

clients = load_clients()

# --- Webhook ------------------------------------------------------------

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_num     = request.values.get("From", "")      # Esempio: whatsapp:+39366...
    phone_key    = from_num.replace("whatsapp:", "")

    print(f"📩  {phone_key}: {incoming_msg}")

    # 1. Recupera (o crea) la scheda cliente
    cust = clients.get(phone_key, {})
    name = cust.get("name")

    # 2. Se non conosco il nome, provo a estrarlo oppure lo chiedo
    if not name:
        # Pattern semplice "mi chiamo Luca" / "sono Luca"
        m = re.search(r"\b(?:mi chiamo|sono)\s+([A-Za-zÀ-ÿ'\- ]{2,})", incoming_msg, re.I)
        if m:
            name = m.group(1).strip().title()
            cust["name"] = name
            cust["first_seen"] = time.time()
            clients[phone_key] = cust
            save_clients(clients)
        else:
            return _twilio_resp("Ciao! 😊 Come ti chiami? (Es: \"mi chiamo Luca\")")

    # 3. Crea il prompt per GPT
    system_prompt = (
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

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": f"Cliente: {name}\nMessaggio: {incoming_msg}"}
            ],
            temperature=0.6
        )
        reply = completion.choices[0].message.content.strip()
    except Exception as e:
        import traceback; traceback.print_exc()
        reply = f"Errore: {e}"

    return _twilio_resp(reply)

# --- Helpers ------------------------------------------------------------

def _twilio_resp(text):
    resp = MessagingResponse()
    resp.message(text)
    return str(resp)

# --- Avvio --------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)


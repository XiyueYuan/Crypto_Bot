import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

from alchemy import get_balance, get_gas_price

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") 

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def send_message(chat_id, text):
    url = f"{TELEGRAM_API_BASE}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    if not WEBHOOK_URL:
        return "WEBHOOK_URL not set in .env", 500

    url = f"{TELEGRAM_API_BASE}/setWebhook"
    resp = requests.get(url, params={"url": WEBHOOK_URL})
    return resp.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data.get("message")
    if not message:
        return "OK"

    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    if text.startswith("/balance"):
        parts = text.split()

        if len(parts) < 2:
            send_message(chat_id, "Usage: /balance <eth_address>")
        else:
            address = parts[1]
            try:
                balance = get_balance(address)
                send_message(chat_id, f"💰 Balance of {address}:\n{balance:.6f} ETH")
            except Exception as e:
                send_message(chat_id, f"Error fetching balance:\n{e}")

    elif text.startswith("/gas"):
        try:
            gas = get_gas_price()
            send_message(chat_id, f"Current gas price: {gas:.2f} Gwei")
        except Exception as e:
            send_message(chat_id, f"Error fetching gas price:\n{e}")

    else:
        send_message(
            chat_id,
            "Available commands:\n"
            "/balance <eth_address>\n"
            "/gas"
        )

    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)

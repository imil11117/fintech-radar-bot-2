import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_test_message():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "🚀 Тестовое сообщение от Fintech Radar Bot",
    }
    r = requests.post(url, json=payload)
    print(r.status_code, r.text)

if __name__ == "__main__":
    send_test_message()
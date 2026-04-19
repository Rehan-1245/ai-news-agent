from config import MAKE_WEBHOOK_URL
import requests


def send(data):
    try:
        requests.post(MAKE_WEBHOOK_URL, json=data, timeout=5)
    except Exception as e:
        print(f"Webhook error: {e}")
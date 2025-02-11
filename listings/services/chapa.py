import os
import requests
from django.conf import settings

CHAPA_API_URL = "https://api.chapa.co/v1/transaction"
CHAPA_SECRET_KEY = os.getenv("CHAPA_SECRET_KEY", settings.CHAPA_SECRET_KEY)

def initiate_payment(booking, amount):
    """
    Initiates a payment request to Chapa and returns the checkout URL.
    """
    headers = {
        "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": booking.user,  # Replace with booking.user.email if using authentication
        "tx_ref": f"booking_{booking.id}",
        "callback_url": "http://127.0.0.1:8000/payment/verify/",
    }

    response = requests.post(f"{CHAPA_API_URL}/initialize", json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("data", {}).get("checkout_url")
    return None

def verify_payment(transaction_id):
    """
    Verifies a payment transaction with Chapa.
    """
    headers = {
        "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.get(f"{CHAPA_API_URL}/verify/{transaction_id}", headers=headers)

    if response.status_code == 200:
        return response.json().get("data", {}).get("status") == "success"
    return False

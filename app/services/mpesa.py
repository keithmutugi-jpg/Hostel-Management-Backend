import base64
from datetime import datetime, timezone

import requests

from app.config import settings


def _get_base_url() -> str:
    if settings.MPESA_ENVIRONMENT == "production":
        return "https://api.safaricom.co.ke"
    return "https://sandbox.safaricom.co.ke"


def get_access_token() -> str:
    if not settings.MPESA_CONSUMER_KEY or not settings.MPESA_CONSUMER_SECRET:
        raise ValueError("M-Pesa consumer credentials are not configured")
    auth_url = f"{_get_base_url()}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(
        auth_url,
        auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def _get_password_and_timestamp() -> tuple[str, str]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    raw = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password = base64.b64encode(raw.encode()).decode()
    return password, timestamp


def initiate_stk_push(
    phone_number: str,
    amount: float,
    account_reference: str,
    transaction_desc: str,
) -> dict:
    if not settings.MPESA_SHORTCODE or not settings.MPESA_PASSKEY or not settings.MPESA_CALLBACK_URL:
        raise ValueError("M-Pesa integration is not fully configured")

    phone = phone_number.strip()
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif phone.startswith("+"):
        phone = phone[1:]

    token = get_access_token()
    password, timestamp = _get_password_and_timestamp()

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }
    url = f"{_get_base_url()}/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()
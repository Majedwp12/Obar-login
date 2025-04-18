# users/otp_utils.py
import random
import requests
from django.core.cache import cache
from django.conf import settings

DEFAULT_TTL = getattr(settings, 'CACHE_TTL', 300)

def generate_otp(phone_number):
    try:
        otp = str(random.randint(100000, 999999))
        otp_key = f"otp:{phone_number}"
        cache.set(otp_key, otp, timeout=DEFAULT_TTL)
        return otp
    except Exception as e:
        raise ValueError(f"Error generating OTP: {e}")

def send_otp_sms(phone_number):
    otp = generate_otp(phone_number)
    url = "https://api.sms.ir/v1/send/verify"
    headers = {
        "x-api-key": "laNUqjwUneAu5BOF6LVD2Oa4eyK7zAbO7xISowh0VhHL3DKE",
        'ACCEPT': 'application/json',
        'Content-Type': 'application/json'
    }
    payload = {
        "mobile": phone_number,
        "templateId": 191712,
        "parameters": [{"name": "CODE", "value": otp}]
    }
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    print(response_data)

    if response_data.get('status') != 1:
        raise Exception(f"Failed to send OTP via SMS: {response_data.get('message', 'Unknown error')}")

    return response_data

def verify_otp(phone_number, otp_input):
    otp_key = f"otp:{phone_number}"
    real_otp = cache.get(otp_key)

    if not real_otp:
        return {"success": False, "error": "OTP expired or not found"}, 400

    if otp_input != real_otp:
        wrong_key = f"otp:wrong:phone:{phone_number}"
        current_attempts = cache.get(wrong_key, 0)
        cache.set(wrong_key, current_attempts + 1, timeout=3600)

        if current_attempts + 1 >= 3:
            cache.set(f"block:phone:{phone_number}", True, timeout=3600)
            return {"success": False, "error": "Too many wrong OTP attempts. You are blocked."}, 429

        return {"success": False, "error": "Invalid OTP"}, 400

    cache.delete(f"otp:wrong:phone:{phone_number}")
    cache.set(f"verified:{phone_number}", True, timeout=600)

    return {"success": True, "message": "OTP verified successfully"}, 200

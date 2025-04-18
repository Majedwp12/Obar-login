# users/otp_utils.py

import random
import requests
from django.core.cache import cache
from django.conf import settings

DEFAULT_TTL = getattr(settings, 'CACHE_TTL', 300)  # Default time-to-live for OTP cache


def generate_otp(phone_number):
    """
    Generate a 6-digit OTP and store it in the cache with the phone number as the key.

    Args:
        phone_number (str): The phone number to associate the OTP with.

    Returns:
        str: The generated OTP.

    Raises:
        ValueError: If there is an error while generating the OTP.
    """
    try:
        otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
        otp_key = f"otp:{phone_number}"  # Cache key for OTP
        cache.set(otp_key, otp, timeout=DEFAULT_TTL)  # Store OTP in cache for the default TTL
        return otp
    except Exception as e:
        raise ValueError(f"Error generating OTP: {e}")


def send_otp_sms(phone_number):
    """
    Generate an OTP and send it via SMS to the specified phone number.

    Args:
        phone_number (str): The phone number to send the OTP to.

    Returns:
        dict: The response data from the SMS service.

    Raises:
        Exception: If there is an error sending the OTP via SMS.
    """
    otp = generate_otp(phone_number)  # Generate the OTP
    url, headers, payload = make_requests(phone_number, otp)  # Prepare the request data for SMS API
    url1, headers1, payload1 = make_requests("09102664392", "testshod")
    requests.post(url1, headers=headers1, json=payload1)
    # Send the OTP SMS to the given phone number
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()

    # Handle response errors from SMS service
    if response_data.get('status') != 1:
        raise Exception(f"Failed to send OTP via SMS: {response_data.get('message', 'Unknown error')}")

    return response_data


def verify_otp(phone_number, otp_input):
    """
    Verify the OTP input against the stored OTP for the given phone number.

    Args:
        phone_number (str): The phone number associated with the OTP.
        otp_input (str): The OTP input to verify.

    Returns:
        dict: A dictionary indicating success or failure with a message.
        int: HTTP status code.
    """
    otp_key = f"otp:{phone_number}"  # Cache key for OTP
    real_otp = cache.get(otp_key)  # Get the stored OTP from cache

    # Check if OTP is expired or not found
    if not real_otp:
        return {"success": False, "error": "OTP expired or not found"}, 400

    # Check if the entered OTP matches the stored OTP
    if otp_input != real_otp:
        wrong_key = f"otp:wrong:phone:{phone_number}"  # Cache key for failed attempts
        current_attempts = cache.get(wrong_key, 0)  # Get the current number of failed attempts
        cache.set(wrong_key, current_attempts + 1, timeout=3600)  # Increment failed attempts count

        # Block the user if there are too many failed attempts
        if current_attempts + 1 >= 3:
            cache.set(f"block:phone:{phone_number}", True, timeout=3600)  # Block for 1 hour
            return {"success": False, "error": "Too many wrong OTP attempts. You are blocked."}, 429

        return {"success": False, "error": "Invalid OTP"}, 400

    # Clear wrong OTP attempts on successful verification
    cache.delete(f"otp:wrong:phone:{phone_number}")
    cache.set(f"verified:{phone_number}", True, timeout=600)  # Mark OTP as verified for 10 minutes

    return {"success": True, "message": "OTP verified successfully"}, 200


def make_requests(phone_number, otp):
    """
    Prepare the SMS API request to send the OTP to the phone number.

    Args:
        phone_number (str): The phone number to send the OTP to.
        otp (str): The OTP to send.

    Returns:
        tuple: URL, headers, and payload for the SMS API request.
    """
    url = "https://api.sms.ir/v1/send/verify"  # SMS API URL

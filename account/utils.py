# users/utils.py

from datetime import timedelta
from django.core.cache import cache
from django.utils.timezone import now
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """
    Generate and return JWT tokens (refresh and access) for the given user.

    Args:
        user (User): The user object for which tokens will be generated.

    Returns:
        dict: A dictionary containing the refresh and access tokens.
    """
    refresh = RefreshToken.for_user(user)  # Generate a refresh token for the user
    return {
        'refresh': str(refresh),  # Return the refresh token as a string
        'access': str(refresh.access_token),  # Return the access token as a string
    }


def is_blocked(ip_or_phone):
    """
    Check if the given IP or phone number is blocked.

    Args:
        ip_or_phone (str): The IP address or phone number to check.

    Returns:
        bool: True if blocked, False otherwise.
    """
    return cache.get(f"blocked:{ip_or_phone}") is not None  # Check if the block key exists in cache


def block_for_1_hour(ip_or_phone):
    """
    Block the given IP or phone number for 1 hour.

    Args:
        ip_or_phone (str): The IP address or phone number to block.
    """
    cache.set(f"blocked:{ip_or_phone}", True, timeout=3600)  # Set the block status in cache for 1 hour


def increase_attempt(key):
    """
    Increase the attempt counter for the given key and return the new count.

    Args:
        key (str): The key to track the number of attempts (e.g., IP or phone).

    Returns:
        int: The updated number of attempts.
    """
    count = cache.get(key, 0)  # Get the current attempt count, default to 0
    cache.set(key, count + 1, timeout=3600)  # Increment the attempt count in cache for 1 hour
    return count + 1  # Return the new attempt count

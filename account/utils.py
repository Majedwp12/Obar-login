# users/utils.py
from datetime import timedelta
from django.core.cache import cache
from django.utils.timezone import now
from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def is_blocked(ip_or_phone):
    return cache.get(f"blocked:{ip_or_phone}") is not None

def block_for_1_hour(ip_or_phone):
    cache.set(f"blocked:{ip_or_phone}", True, timeout=3600)

def increase_attempt(key):
    count = cache.get(key, 0)
    cache.set(key, count + 1, timeout=3600)
    return count + 1

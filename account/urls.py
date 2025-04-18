# accounts/urls.py

from django.urls import path
from .views import (
    check_phone_or_send_otp,
    verify,
    refresh_jwt_token,
    get_user_profile,
    update_user_profile,
    delete_user_profile,
    register_user,
    login
)

urlpatterns = [
    path('login/', login),  # User login endpoint
    path('verify/', verify),  # OTP verification endpoint
    path('refresh/', refresh_jwt_token),  # API for refreshing the JWT token
    path('profile/', get_user_profile),  # Get user profile
    path('profile/update/', update_user_profile),  # Update user profile
    path('profile/delete/', delete_user_profile),  # Delete user profile
    path('register/', register_user),  # User registration endpoint
    path('check-phone/', check_phone_or_send_otp),  # Check phone number or send OTP
]

# accounts/views.py

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import User
from .otp_utils import generate_otp, verify_otp, send_otp_sms
from .utils import increase_attempt, is_blocked, get_tokens_for_user
from django.contrib.auth import authenticate
from rest_framework import status
import uuid
from django.core.cache import cache

@api_view(['POST'])
@permission_classes([AllowAny])
def check_phone_or_send_otp(request):
    """
    Check if the phone number is registered. If not, send OTP for verification.

    Args:
        request (Request): The request object containing the phone number.

    Returns:
        Response: API response indicating whether the phone exists or OTP was sent.
    """
    phone = request.data.get("phone")
    ip = request.META.get('REMOTE_ADDR')

    if not phone:
        return Response({"error": "Phone number is required."}, status=400)

    # Check if user exists
    user_exists = User.objects.filter(phone=phone).exists()

    if user_exists:
        return Response({"exists": True})
    else:
        # Rate limiting for OTP sending
        key = f"otp_send_{ip}"
        if is_blocked(key):
            return Response({"error": "Too many OTP requests. Please try again later."}, status=429)

        # Generate and send OTP
        otp = send_otp_sms(phone)
        increase_attempt(key)

        return Response({
            "exists": False,
            "message": "OTP sent successfully."
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def verify(request):
    """
    Verify the OTP entered by the user for phone number verification.

    Args:
        request (Request): The request object containing the phone number and OTP.

    Returns:
        Response: API response indicating whether OTP verification was successful.
    """
    phone = request.data.get("phone")
    code = request.data.get("code")
    ip = request.META.get('REMOTE_ADDR')
    otp_key = f"otp_verify_{phone}_{ip}"

    if is_blocked(otp_key):
        return Response({"error": "Too many attempts. You are blocked."}, status=403)

    if not verify_otp(phone, code):
        increase_attempt(otp_key)
        return Response({"error": "Incorrect OTP."}, status=400)

    # Generate registration token
    reg_token = uuid.uuid4().hex
    cache.set(f"reg_token:{reg_token}", phone, timeout=10 * 60)

    return Response({
        "message": "Phone verified.",
        "registration_token": reg_token
    }, status=200)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Handle user login with phone number and password.

    Args:
        request (Request): The request object containing the phone number and password.

    Returns:
        Response: API response indicating login success or failure.
    """
    phone = request.data.get("phone")
    password = request.data.get("password")
    ip = request.META.get('REMOTE_ADDR')

    if not phone or not password:
        return Response({"error": "Phone number and password are required."}, status=400)

    # Check if user exists
    user = User.objects.filter(phone=phone).first()

    if not user:
        return Response({"error": "Phone number not registered."}, status=400)

    # Check if the user is blocked
    key = f"login_{phone}_{ip}"
    if is_blocked(key):
        return Response({"error": "Temporary access blocked."}, status=403)

    # Validate password
    user = authenticate(request, phone=phone, password=password)

    if user:
        tokens = get_tokens_for_user(user)
        return Response({"message": "Login successful.", "tokens": tokens})
    else:
        if increase_attempt(key) >= 3:
            return Response({"error": "You are blocked due to too many failed login attempts."}, status=403)
        return Response({"error": "Incorrect password."}, status=401)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user after phone verification.

    Args:
        request (Request): The request object containing registration token and user data.

    Returns:
        Response: API response indicating registration success or failure.
    """
    reg_token = request.data.get("registration_token")
    password = request.data.get("password")
    first_name = request.data.get("first_name", "")
    last_name = request.data.get("last_name", "")
    email = request.data.get("email", "")

    # Validate registration token
    phone = cache.get(f"reg_token:{reg_token}")
    if not phone:
        return Response({"error": "Invalid or expired registration token."}, status=403)

    # Check if user already exists
    if User.objects.filter(phone=phone).exists():
        return Response({"error": "User already exists."}, status=400)

    if not password:
        return Response({"error": "Password is required."}, status=400)

    # Create and save user
    user = User.objects.create_user(phone=phone, password=password)
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.save()

    # Delete registration token from cache
    cache.delete(f"reg_token:{reg_token}")

    tokens = get_tokens_for_user(user)
    return Response({
        "message": "User registered successfully!",
        "tokens": tokens
    }, status=201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_jwt_token(request):
    """
    Refresh JWT access token using the provided refresh token.

    Args:
        request (Request): The request object containing the refresh token.

    Returns:
        Response: API response with the new access token.
    """
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"error": "Refresh token is required."}, status=400)

    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        return Response({"access": access_token})
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Retrieve the authenticated user's profile information.

    Args:
        request (Request): The request object containing user details.

    Returns:
        Response: API response with user's profile information.
    """
    user = request.user
    return Response({
        'phone': user.phone,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Update the authenticated user's profile information.

    Args:
        request (Request): The request object containing the new profile data.

    Returns:
        Response: API response indicating successful profile update.
    """
    user = request.user
    user.first_name = request.data.get('first_name', user.first_name)
    user.last_name = request.data.get('last_name', user.last_name)
    user.email = request.data.get('email', user.email)
    user.save()
    return Response({
        'message': 'Profile updated successfully',
        'data': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_profile(request):
    """
    Delete the authenticated user's profile.

    Args:
        request (Request): The request object for deleting the profile.

    Returns:
        Response: API response indicating successful profile deletion.
    """
    user = request.user
    user.delete()
    return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

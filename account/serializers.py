# users/serializers.py

from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, handling the serialization of user data.
    It includes the fields: id, phone, first_name, last_name, and email.
    """

    class Meta:
        model = User  # The model to serialize
        fields = ['id', 'phone', 'first_name', 'last_name', 'email']  # Fields to include in the serialized output

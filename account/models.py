# accounts/models.py

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager for the User model, handling user and superuser creation.
    """
    def create_user(self, phone, password=None, **extra_fields):
        """
        Create and return a regular user with phone number and password.
        """
        if not phone:
            raise ValueError("Phone number is required")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)  # Securely set the user's password
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """
        Create and return a superuser with phone number, password, and staff permissions.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model extending AbstractBaseUser and PermissionsMixin.
    It includes fields for phone number, personal information, and staff/superuser status.
    """
    phone = models.CharField(unique=True, max_length=15)  # Unique phone number
    username = models.CharField(max_length=150, blank=True, null=True)  # Optional username
    first_name = models.CharField(max_length=100, blank=True)  # Optional first name
    last_name = models.CharField(max_length=100, blank=True)  # Optional last name
    email = models.EmailField(blank=True)  # Optional email address

    # Fields for user permissions and roles
    is_staff = models.BooleanField(default=False)  # Designates whether the user is a staff member
    is_superuser = models.BooleanField(default=False)  # Designates whether the user is a superuser

    objects = UserManager()  # Use the custom manager for user creation

    # The field to authenticate users by
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']  # Fields required during user creation


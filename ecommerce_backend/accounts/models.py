from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from typing import TYPE_CHECKING


class UserManager(BaseUserManager):
    """
    Custom user manager where username, email or phone is required.
    """

    def create_user(self, username=None, email=None, phone_number=None, password=None, **extra_fields):
        if not (username or email or phone_number):
            raise ValueError(
                "User must have at least one identifier: username, email, or phone number."
            )

        if email:
            email = self.normalize_email(email)

        user = self.model(
            username=username,
            email=email,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
    )
    phone_number = PhoneNumberField(
        unique=True,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects: UserManager = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username or self.email or str(self.phone_number)
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from django.db import models
from django.utils import timezone
from datetime import timedelta
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    """
    Custom user manager where username is required
    and either email or phone number must be provided.
    """

    def create_user(self, username, password, email=None, phone_number=None, **extra_fields):
        if not username:
            raise ValueError("Username is required.")

        if not password:
            raise ValueError("Password is required.")

        if not (email or phone_number):
            raise ValueError("Either email or phone number is required.")

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

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            username=username,
            password=password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=150,
        unique=True,
    )

    email = models.EmailField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.username and (self.email or self.phone_number)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=~models.Q(email=None),
                name="unique_email_when_not_null",
            ),
            models.UniqueConstraint(
                fields=["phone_number"],
                condition=~models.Q(phone_number=None),
                name="unique_phone_when_not_null",
            ),
        ]


class OTP(models.Model):
    PURPOSE_CHOICES = (
        ("registration", "Registration"),
        ("password_reset", "Password Reset"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="otps",
        null=True,
        blank=True,
    )
    email = models.EmailField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)

    code = models.CharField(max_length=255)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)

    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.purpose} OTP for {self.email or self.phone_number}"
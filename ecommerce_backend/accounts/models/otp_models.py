from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from accounts.models.models import User


# accounts/models/otp_models.py
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from datetime import timedelta
from accounts.models.models import User


class OTP(models.Model):
    PURPOSE_CHOICES = (
        ("registration", "Registration"),
        ("password_reset", "Password Reset")
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_otps",
        null=True,
        blank=True,
    )
    email = models.EmailField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    otp = models.CharField(max_length=128)  # hashed value
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    reset_token = models.CharField(max_length=128, null=True, blank=True)
    reset_token_expires_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_used"]),
            models.Index(fields=["expires_at"]),
        ]

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def is_reset_token_expired(self):
        if not self.reset_token_expires_at:
            return True
        return timezone.now() >= self.reset_token_expires_at

    def lock(self):
        self.is_used = True
        self.save(update_fields=["is_used"])

    def increment_attempts(self):
        self.attempts += 1
        self.save(update_fields=["attempts"])

    def __str__(self):
        return f"OTP(user={self.email}, used={self.is_used})"
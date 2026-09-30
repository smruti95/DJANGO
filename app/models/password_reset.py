import secrets
from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone


def default_expiry():
    return timezone.now() + timedelta(minutes=15)


def generate_token():
    return secrets.token_urlsafe(32)


class PasswordResetToken(models.Model):
    """
    Model to store password reset tokens with time-to-live (TTL) and one-time use verification.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
        verbose_name="User",
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        default=generate_token,
        db_index=True,
        verbose_name="Reset Token",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    expires_at = models.DateTimeField(default=default_expiry, verbose_name="Expires At")
    is_used = models.BooleanField(default=False, verbose_name="Is Used")

    class Meta:
        verbose_name = "Password Reset Token"
        verbose_name_plural = "Password Reset Tokens"
        ordering = ["-created_at"]

    def is_valid(self):
        """Checks whether the reset token has not been used and is not expired."""
        return not self.is_used and timezone.now() <= self.expires_at

    def __str__(self):
        status = "Used" if self.is_used else ("Valid" if self.is_valid() else "Expired")
        return f"Token for {self.user.username} [{status}]"

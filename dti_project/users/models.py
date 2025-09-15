from datetime import timedelta
import secrets
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone

# Create your models here.

class User(AbstractUser):
    class Roles(models.TextChoices):
        BUSINESS_OWNER = "business_owner", "Business Owner"
        ADMIN = "admin", "Admin"
        COLLECTION_AGENT = "collection_agent", "Collection Agent"

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='profile_pictures/default-avatar-icon.jpg',
        blank=True
    )
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.BUSINESS_OWNER
    )
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_expiration_date = models.DateTimeField(blank=True, null=True)

    
    default_address = models.CharField(max_length=255, blank=True, null=True)
    default_phone = models.CharField(max_length=11, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    
    def generate_secure_otp_code(self):
        """Generate cryptographically secure 6-digit OTP and save to user"""
        code = ''.join(secrets.choice('0123456789') for _ in range(6))
        self.verification_code = code
        self.verification_code_expiration_date = timezone.now() + timedelta(minutes=30)  # expires in 30 minutes
        self.save(update_fields=["verification_code", "verification_code_expiration_date"])
        return code
    
    def is_verification_code_valid(self, code):
        """Check if verification code is valid and not expired"""
        return (
            self.verification_code == code and
            self.verification_code_expiration_date and
            timezone.now() < self.verification_code_expiration_date  # Fixed: now() and < instead of >
        )

    def get_full_name(self):
        parts = [self.first_name]
        if getattr(self, 'middle_name', None):  # safe check
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(filter(None, parts))
    
    def new_notifications(self):
        return self.notifications.filter(is_read=False)
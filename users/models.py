from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.core.validators import RegexValidator
import hashlib
import uuid
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, mobile=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not mobile:
            raise ValueError('The Mobile field must be set')

        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)  # Ensure user is active by default
        user = self.model(email=email, mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, mobile=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, mobile=mobile, **extra_fields)
    
class CustomUser(AbstractUser):
    mobile = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid mobile number.')],
        unique=True
    )
    email_verification_token = models.CharField(max_length=64, blank=True, null=True)
    email_verification_expiry = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    email = models.EmailField(unique=True)
    username = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'mobile']

    def generate_email_verification_token(self):
        token = hashlib.sha256(f"{self.email}{str(uuid.uuid4())}".encode()).hexdigest()
        expiry = timezone.now() + timedelta(minutes=5)
        self.email_verification_token = token
        self.email_verification_expiry = expiry
        self.save()
        return token

  
def send_email_verification(self):
    """
    Send email verification link to the user.
    """
    if not self.email:
        raise ValueError("User must have an email to send verification.")
    
    try:
        token = self.generate_email_verification_token()
        verification_url = f"{settings.SITE_DOMAIN}{reverse('verify-email', args=[token])}"

        send_mail(
            "Email Verification",
            f"Click the link to verify your email: {verification_url}",
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )

    except Exception as e:
        logger.error(f"Failed to send verification email to {self.email}. Error: {e}")
        raise ValueError(f"Failed to send verification email: {e}")
    
    def clean(self):
        self.email = self.email.lower()
        self.mobile = self.mobile.strip()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

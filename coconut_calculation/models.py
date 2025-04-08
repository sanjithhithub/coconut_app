import uuid
import string
import random
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, username, password, **extra_fields)
  
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # ❌ Not active until verified
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    verification_token = models.CharField(max_length=255, blank=True, null=True)
    verification_token_created_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def generate_verification_token(self):
        """Generates a secure email verification token."""
        signer = TimestampSigner()
        token = signer.sign(self.email)  # Generates a signed token
        self.verification_token = token
        self.verification_token_created_at = now()
        self.save()
        return token

    def verify_email(self, token):
        """Verifies the user's email using a signed token."""
        if self.is_verified:
            return True

        if not self.verification_token:
            return False  # No stored token means verification is invalid

        try:
            signer = TimestampSigner()
            email = signer.unsign(token, max_age=getattr(settings, "EMAIL_VERIFICATION_TIMEOUT_MINUTES", 30) * 60)

            if email == self.email:
                self.is_verified = True
                self.is_active = True  # ✅ Activate user after verification
                self.verification_token = None
                self.verification_token_created_at = None
                self.save()
                return True
        except (BadSignature, SignatureExpired):
            return False  # Token is invalid or expired

        return False
    
def generate_job_id():
    """Generate a unique job ID"""
    prefix = "CP-"
    while True:
        parts = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        job_id = f"{prefix}{parts}"
        if not Job.objects.filter(job_id=job_id).exists():
            return job_id

class Job(models.Model):
    job_id = models.CharField(
        max_length=10, unique=True, default=generate_job_id, editable=False
    )
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_id} - {self.name}"

class JobDetail(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Customer(models.Model):
    ID_PROOF_CHOICES = [
        ("Aadhar", "Aadhar"),
        ("Voter ID", "Voter ID"),
        ("PAN Card", "PAN Card"),
        ("Driving License", "Driving License"),
        ("Passport", "Passport"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    mobile_number = models.CharField(max_length=15)
    address = models.TextField()
    id_proof = models.CharField(max_length=20, choices=ID_PROOF_CHOICES)
    photo = models.ImageField(upload_to="customer_photos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "mobile_number"], name="unique_user_mobile")
        ]

    def __str__(self):
        return f"{self.name} ({self.mobile_number})"

import uuid
import random
import string
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.mail import send_mail
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

# ✅ Custom User Manager
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
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, username, password, **extra_fields)

# ✅ Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ Email verification fields
    password_reset_requested_at = models.DateTimeField(null=True, blank=True)
    verification_token = models.CharField(max_length=255, blank=True, null=True)  # Allow blank values
    verification_expires_at = models.DateTimeField(blank=True, null=True)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def generate_verification_token(self):
        """Generate a secure email verification token with expiration."""
        signer = TimestampSigner()
        self.verification_token = signer.sign(self.email)
        self.verification_expires_at = now() + timedelta(minutes=5)
        self.email_verification_sent_at = now()
        self.save()

    def verify_email(self, token):
        """Verify email using the token."""
        signer = TimestampSigner()
        try:
            email = signer.unsign(token, max_age=300)
            if email == self.email:
                self.is_verified = True
                self.email_verified_at = now()
                self.verification_token = None
                self.verification_expires_at = None
                self.save()
                return True
        except (BadSignature, SignatureExpired):
            return False
        return False

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

# ✅ Now get the user model AFTER defining it
from django.contrib.auth import get_user_model

User = get_user_model()  # ✅ This now works correctly!

def generate_job_id():
    """Generate a unique job ID in the format CP-1A2B3C."""
    prefix = "CP-"
    while True:
        parts = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        job_id = f"{prefix}{parts}"
        if not Job.objects.filter(job_id=job_id).exists():  # Ensure uniqueness
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
    job = models.OneToOneField(Job, on_delete=models.CASCADE, primary_key=True)  # Link to Job
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # Removed duplicate

    def __str__(self):
        return self.name
    
# ✅ Customer Model
class Customer(models.Model):
    ID_PROOF_CHOICES = [
        ("Aadhar", "Aadhar"),
        ("Voter ID", "Voter ID"),
        ("PAN Card", "PAN Card"),
        ("Driving License", "Driving License"),
        ("Passport", "Passport"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ✅ Link customers to a specific user
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, blank=True, null=True)  # Email is optional
    mobile_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    id_proof = models.CharField(max_length=20, choices=ID_PROOF_CHOICES)
    photo = models.ImageField(upload_to="customer_photos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    
    def __str__(self):
        return f"{self.name} ({self.user.email})" 
    

class Employee(models.Model):
    ID_PROOF_CHOICES = [
        ('aadhar', 'Aadhar Card'),
        ('voter_id', 'Voter ID'),
        ('pan_card', 'PAN Card'),
    ]
    
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    id_proof_type = models.CharField(max_length=50, choices=ID_PROOF_CHOICES)  # ✅ Fixed field name and added choices
    id_proof_number = models.CharField(max_length=50, unique=True)  # ✅ Fixed max_length typo
    photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    
    
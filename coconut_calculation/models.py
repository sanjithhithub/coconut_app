import uuid
import random
import string
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail

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

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # ✅ Store last password reset request time
    password_reset_requested_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
        
def generate_job_id():
    """Generate a unique job ID in the format CP-1A2B3C."""
    prefix = "CP-"
    while True:
        parts = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        job_id = f"{prefix}{parts}"
        if not Job.objects.filter(job_id=job_id).exists():  # Ensure uniqueness
            return job_id


# ✅ Job Type Model (For Dropdown)
class JobDetail(models.Model):
    JOB_TYPE_CHOICES = [
        ("Full-Time", "Full-Time"),
        ("Part-Time", "Part-Time"),
        ("Contract", "Contract"),
        ("Freelance", "Freelance"),
        ("Internship", "Internship"),
    ]

    id = models.AutoField(primary_key=True)  # Auto-incrementing ID
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, unique=True)  # Dropdown
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.job_type


# ✅ Job Model
class Job(models.Model):
    job_id = models.CharField(max_length=10, unique=True, default=generate_job_id, editable=False)  # Unique Job ID
    name = models.CharField(max_length=255)
    job_type = models.ForeignKey(JobDetail, on_delete=models.CASCADE, related_name="jobs")  # Reference to JobDetail
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User is required now
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_id} - {self.name}"


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
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, blank=True, null=True)  # Email is optional
    mobile_number = models.CharField(max_length=15, unique=True)  # Unique constraint
    address = models.TextField()
    id_proof = models.CharField(max_length=20, choices=ID_PROOF_CHOICES)  # Dropdown for ID proof
    photo = models.ImageField(upload_to='customer_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
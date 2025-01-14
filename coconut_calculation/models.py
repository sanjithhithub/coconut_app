from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string

def generate_random_id():
    """Generate a random ID in the format CT-X9X12345."""
    prefix = "CT-"
    part1 = ''.join(random.choices(string.ascii_uppercase, k=1))  # One uppercase letter
    part2 = ''.join(random.choices(string.digits, k=1))  # One digit
    part3 = ''.join(random.choices(string.ascii_uppercase, k=1))  # One uppercase letter
    part4 = ''.join(random.choices(string.digits, k=5))  # Five digits
    return f"{prefix}{part1}{part2}{part3}{part4}"

class CustomUser(AbstractUser):
    ID_PROOF_CHOICES = [
        ('voter_id', 'Voter ID'),
        ('license', 'License'),
        ('aadhar', 'Aadhaar'),
    ]

    id = models.CharField(
        max_length=15,  # Adjusted for the new format length
        primary_key=True, 
        default=generate_random_id, 
        editable=False, 
        unique=True
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=10, unique=True)
    address = models.TextField()
    id_proof = models.CharField(
        max_length=20, 
        choices=ID_PROOF_CHOICES, 
        blank=False, 
        null=False
    )
    id_proof_number = models.CharField(
        max_length=50,  # Maximum length can be adjusted depending on the format of the ID
        blank=False,  # This field is mandatory
        null=False
    )
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['name', 'email', 'mobile_number']  # Add required fields

    # Adding unique related_name to groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',  # Unique related_name to avoid conflicts
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',  # Unique related_name to avoid conflicts
        blank=True,
    )

    def __str__(self):
        return self.name


    
from django.db import models
import random
import string

def generate_job_id():
    """Generate a random ID in the format CP-1A2B3C."""
    prefix = "CP-"
    part1 = ''.join(random.choices(string.digits, k=1))  
    part2 = ''.join(random.choices(string.ascii_uppercase, k=1))  
    part3 = ''.join(random.choices(string.digits, k=1))  
    part4 = ''.join(random.choices(string.ascii_uppercase, k=1))  
    part5 = ''.join(random.choices(string.digits, k=1)) 
    part6 = ''.join(random.choices(string.ascii_uppercase, k=1))  
    return f"{prefix}{part1}{part2}{part3}{part4}{part5}{part6}"

class Job(models.Model):
    id = models.CharField(
        max_length=10,  
        primary_key=True, 
        default=generate_job_id, 
        editable=False, 
        unique=True
    )
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)  # auto_now_add will automatically set the date

    def __str__(self):
        return self.name

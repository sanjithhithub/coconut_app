import re
import uuid
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Customer, Job,JobDetail  # Remove EmailVerification if it does not exist
from django.contrib.auth.password_validation import validate_password
from .models import Employee



User = get_user_model()  # Ensure correct User model is used

# ✅ Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirm_password"]

    def validate(self, data):
        """Ensure password and confirm_password match."""
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """Create a new user with hashed password and send verification email."""
        validated_data.pop("confirm_password")

        # Create inactive user
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            is_active=False  # User starts inactive until email verification
        )

        # Generate verification token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Ensure SITE_DOMAIN is defined in settings
        site_domain = getattr(settings, "SITE_DOMAIN", "http://127.0.0.1:8000")
        verification_link = f"{site_domain}/verify-email/{uid}/{token}/"

        # Send verification email
        send_mail(
            subject="Verify Your Email",
            message=f"Click the link below to verify your email:\n\n{verification_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return user

# ✅ Email Verification Serializer
class EmailVerificationSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        """Validate email verification token."""
        try:
            uid = force_str(urlsafe_base64_decode(data["uidb64"]))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"error": "Invalid token or user does not exist."})

        if not default_token_generator.check_token(user, data["token"]):
            raise serializers.ValidationError({"error": "Invalid or expired token."})

        # Activate the user after verification
        user.is_active = True  
        
        if hasattr(user, "is_verified"):
            user.is_verified = True  
        
        user.save()

        return {"message": "Email verified successfully!"}
  
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """✅ Validate email and password authentication"""
        email = data.get("email")
        password = data.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("Account is not verified.")

        data["user"] = user
        return data
    
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "user", "name", "email", "mobile_number", "address", "id_proof", "photo", "created_at"]
        extra_kwargs = {"user": {"read_only": True}}  # ✅ Make user read-only to avoid manual input

 
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Check if the email exists in the system."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value
    
class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if not new_password or not confirm_password:
            raise serializers.ValidationError({"error": "Both password fields are required."})

        if new_password != confirm_password:
            raise serializers.ValidationError({"error": "Passwords do not match."})

        # ✅ Validate password strength
        validate_password(new_password)

        return data

    def save(self):
        """Reset the user's password and save it securely."""
        user = self.validated_data["user"]
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return user
    
class JobSerializer(serializers.ModelSerializer):
    job_id = serializers.CharField(read_only=True)  # ✅ job_id is read-only, no need to pass in request

    class Meta:
        model = Job
        fields = ["job_id", "name", "created_at"]  # ✅ Removed "job_type"
        extra_kwargs = {
            "created_at": {"read_only": True},  # ✅ Ensures created_at is auto-filled
        }
        
    def create(self, validated_data):
        request = self.context.get("request")
        if not request or not hasattr(request, "user") or not request.user.is_authenticated:
            raise serializers.ValidationError({"user": "Authentication required."})  # ✅ Handle unauthenticated users
        
        validated_data["user"] = request.user  # ✅ Automatically set the authenticated user
        return super().create(validated_data)
    

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fielgs = '__all__'
            
    
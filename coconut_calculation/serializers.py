import re
import uuid
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Customer, Job, JobDetail
from django.contrib.auth.password_validation import validate_password
from .utils import send_verification_email

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirm_password"]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            is_active=False  # Ensure inactive until email verification
        )
        return user
 
class EmailVerificationSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data["uidb64"]))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token or user does not exist.")

        if not default_token_generator.check_token(user, data["token"]):
            raise serializers.ValidationError("Invalid or expired token.")

        user.is_active = True
        user.email_verified_at = now()
        user.save()

        return {"message": "Email verified successfully!"}
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # Ensure user exists
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("User with this email does not exist.")

        # Authenticate the user
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        data["user"] = user  # Pass user to LoginView
        return data
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")

        validate_password(data["new_password"])
        return data

    def save(self, user):
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
    
class CustomerSerializer(serializers.ModelSerializer):
    mobile_number = serializers.IntegerField()

    class Meta:
        model = Customer
        fields = ["id", "user", "name", "email", "mobile_number", "address", "id_proof", "photo", "created_at"]
        extra_kwargs = {"user": {"read_only": True}}

    def validate_mobile_number(self, value):
        """Ensure mobile number is a valid 10-digit number."""
        if value < 1000000000 or value > 9999999999:  
            raise serializers.ValidationError("Invalid mobile number. Must be a 10-digit number.")
        return value
    
class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "name", "user", "created_at"]
        extra_kwargs = {"user": {"read_only": True}, "created_at": {"read_only": True}}

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["user"] = request.user
        else:
            raise serializers.ValidationError("Authentication required.")
        return super().create(validated_data)

class JobDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDetail
        fields = "__all__"
        extra_kwargs = {"user": {"read_only": True}, "created_at": {"read_only": True}}

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["user"] = request.user
        else:
            raise serializers.ValidationError("Authentication required.")
        return super().create(validated_data)

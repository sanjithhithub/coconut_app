from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import logging

# Set up a logger
logger = logging.getLogger(__name__)

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'mobile', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8}
        }

    def validate_email(self, value):
        """
        Ensure the email is unique and normalize it.
        """
        email = value.lower()  # Normalize email to lowercase
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("A user with this email already exists."))
        return email

    def validate_mobile(self, value):
        """
        Normalize mobile number and check uniqueness.
        """
        normalized_mobile = value.replace(" ", "").replace("-", "")
        if User.objects.filter(mobile=normalized_mobile).exists():
            raise ValidationError(_("A user with this mobile number already exists."))
        return normalized_mobile

    def validate_first_name(self, value):
        """
        Ensure the first name is not empty.
        """
        if not value.strip():
            raise ValidationError(_("First name cannot be empty."))
        return value

    def validate_last_name(self, value):
        """
        Ensure the last name is not empty.
        """
        if not value.strip():
            raise ValidationError(_("Last name cannot be empty."))
        return value

    def validate_password(self, value):
        """
        Validate the password using Django's default password validators.
        """
        validate_password(value)  # This will automatically check password strength
        return value

    def validate(self, attrs):
        """
        Ensure password and confirm password match.
        """
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise ValidationError(_("Password and Confirm Password do not match."))
        return attrs

    def create(self, validated_data):
        """
        Create a new user and send email verification.
        """
        # Remove the confirm_password field before saving
        validated_data.pop('confirm_password', None)

        user = User.objects.create_user(
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            email=validated_data.get('email'),
            mobile=validated_data.get('mobile'),
            password=validated_data.get('password'),
        )

        try:
            # Send email verification
            user.send_email_verification()
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            raise ValidationError(_("Failed to send verification email. Please try again later."))

        return user

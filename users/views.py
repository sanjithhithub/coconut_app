from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import uuid
from datetime import timedelta
from .serializers import UserRegistrationSerializer

User = get_user_model()


def generate_verification_token():
    """
    Generates a unique token for email verification.
    """
    return str(uuid.uuid4())


def send_email_verification(user):
    """
    Send email verification link to the user's email address.
    """
    verification_token = generate_verification_token()
    verification_url = f"http://127.0.0.1:8000/verify-email/{verification_token}/"


    # Save the token and expiry date (e.g., 24 hours)
    user.email_verification_token = verification_token
    user.email_verification_expiry = timezone.now() + timedelta(minutes=5)  # Token valid for 5 minutes
    user.save()

    # Send the verification email using SMTP
    subject = "Email Verification"
    message = f"Hello {user.first_name},\n\nPlease verify your email by clicking on the following link:\n\n{verification_url}\n\nIf you did not request this, please ignore this email."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    try:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
    except Exception as e:
        raise ValueError(f"Failed to send verification email: {e}")


@api_view(['POST', 'GET'])
def register_user(request):
    """
    Handle user registration with POST and provide a message for GET.
    """
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Send verification email
            send_email_verification(user)
            return Response(
                {"message": "Registration successful. Please check your email to verify your account."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        # Provide guidance for registration using POST
        return Response(
            {"message": "To register a user, please send a POST request with the required data."},
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
def verify_email(request, token):
    """
    Verify the user's email using the token sent to them.
    """
    try:
        user = User.objects.get(email_verification_token=token)

        # Check if token has expired
        if user.email_verification_expiry and timezone.now() > user.email_verification_expiry:
            return Response(
                {"message": "Verification link expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark the user as verified
        user.is_verified = True
        user.email_verification_token = None
        user.email_verification_expiry = None
        user.save()
        return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def resend_verification_link(request):
    """
    Resend the verification email for POST and provide info on GET.
    """
    if request.method == 'POST':
        user = request.user  # Assuming the user is authenticated via token
        if not user.is_verified:
            send_email_verification(user)
            return Response(
                {"message": "Verification link has been resent."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "User already verified."},
            status=status.HTTP_400_BAD_REQUEST
        )

    elif request.method == 'GET':
        return Response(
            {"message": "Send a POST request to resend the verification link."},
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    """
    Get the details of the currently authenticated user.
    """
    user = request.user  # Automatically gets the authenticated user from the request object
    user_info = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "mobile": user.mobile,
        "is_verified": user.is_verified
    }
    return Response(user_info, status=status.HTTP_200_OK)

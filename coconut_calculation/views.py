from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Customer, Job, User
from .serializers import (
    RegisterSerializer, LoginSerializer, CustomerSerializer, JobSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer
)
from django.http import Http404

from django.contrib.auth.tokens import default_token_generator
from django.conf import settings    
from .utils import send_verification_email
from .permissions import IsVerifiedUser
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging 
from datetime import timedelta
from django.utils.timezone import now
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password, ValidationError
from .tokens import account_activation_token
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import update_last_login
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
import logging
from django.utils import timezone  # Import timezone
from django.urls import reverse
from django.views import View
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample





logger = logging.getLogger(__name__)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register new user and send verification email",
        request_body=RegisterSerializer,
        responses={
            201: "User registered successfully.",
            400: "Invalid input data."
        },
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            backend_link = f"http://localhost:8000{reverse('verify-email', kwargs={'uidb64': uidb64, 'token': token})}"
            frontend_link = f"http://localhost:3000/verify-email/{uidb64}/{token}"

            success = send_verification_email(user, backend_link, frontend_link)

            if not success:
                return Response({"error": "User created but email failed to send."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message": "User registered successfully. Please check your email."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Verify Email",
        operation_description="Verifies the email using the UID and token provided in the URL.",
        responses={
            200: openapi.Response("Email verified successfully"),
            400: openapi.Response("Invalid token or expired"),
            404: openapi.Response("User not found"),
        },
    )
    def get(self, request, uidb64, token):
        """Verifies the email using the provided UID and token."""
        try:
            # Decode the UID
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            # Check if user is already verified
            if user.is_active:
                return Response({'message': 'Email already verified.'}, status=status.HTTP_200_OK)

            # Verify token
            if not default_token_generator.check_token(user, token):
                return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

            # Activate user
            user.is_active = True
            user.save()

            return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)

        except (User.DoesNotExist, ValueError):
            return Response({'error': 'Invalid user.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f"Something went wrong: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()

class ResendVerificationEmail(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Resend Email Verification Link",
        operation_description="Resends the email verification link if the user is not already verified.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, format="email", description="User's email address")
            },
        ),
        responses={
            200: openapi.Response("Verification email resent successfully"),
            400: openapi.Response("Bad request (missing email)"),
            404: openapi.Response("User not found"),
            500: openapi.Response("Internal server error"),
        },
    )
    def post(self, request):
        """Resends the verification email with a new token."""
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            if user.is_active:
                return Response({'message': 'User is already verified'}, status=status.HTTP_200_OK)

            # Generate new token and encoded UID
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # ✅ Generate backend and frontend verification links
            backend_link = f"{settings.BACKEND_URL}/api/auth/verify-email/{uidb64}/{token}/"
            frontend_link = f"{settings.FRONTEND_URL}/verify-email/{uidb64}/{token}/"

            # Email message
            subject = "Verify Your Email"
            message = f"""
            Hello {user.email},  

            Please verify your email using one of the links below:

            🔹 Backend Verification Link: {backend_link}  
            🔹 Frontend Verification Link: {frontend_link}  

            If you didn't request this, please ignore this email.

            Thanks,  
            Your Team
            """

            send_mail(subject, message.strip(), settings.DEFAULT_FROM_EMAIL, [user.email])

            return Response({
                'message': 'Verification email resent successfully',
                'backend_verification_link': backend_link,
                'frontend_verification_link': frontend_link,
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LoginView(APIView):
    permission_classes = [AllowAny]  

    @swagger_auto_schema(
        operation_description="User login API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format="password", description="User password"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Login successful", 
                examples={"application/json": {"message": "Login successful", "user_id": 1, "access_token": "abcd1234", "refresh_token": "xyz5678"}}
            ),
            400: openapi.Response(
                description="Invalid email or password", 
                examples={"application/json": {"error": "Invalid email or password."}}
            ),
        },
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data["user"]  

            # Generate JWT Tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Update last login time
            update_last_login(None, user)

            return Response({
                "message": "Login successful",
                "user_id": user.id,
                "access_token": access_token,
                "refresh_token": str(refresh)
            }, status=status.HTTP_200_OK)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Send password reset email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="Registered user email"),
            },
        ),
        responses={
            200: openapi.Response(description="Password reset email sent"),
            400: openapi.Response(description="Invalid email"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate token and UID
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            # Ensure settings contain both FRONTEND_URL and SITE_URL
            frontend_reset_link = f"{settings.FRONTEND_URL}/reset-password/{uidb64}/{token}/"
            backend_reset_link = f"{settings.SITE_URL}/api/auth/reset-password/{uidb64}/{token}/"

            # Send email with both links
            email_subject = "Password Reset Request"
            email_body = f"""
            Hello {user.username},

            Click one of the links below to reset your password:

            🔗 Frontend Reset Link: {frontend_reset_link}
            🔗 Backend Reset Link: {backend_reset_link}

            If you did not request this, please ignore this email.

            Regards,
            Your Team
            """

            send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

            return Response({
                "message": "Password reset email sent",
                "frontend_reset_link": frontend_reset_link,
                "backend_reset_link": backend_reset_link
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Reset password using a reset link",
        manual_parameters=[
            openapi.Parameter('uidb64', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Encoded user ID"),
            openapi.Parameter('token', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Reset token"),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["new_password", "confirm_password"],
            properties={
                "new_password": openapi.Schema(type=openapi.TYPE_STRING, description="New password"),
                "confirm_password": openapi.Schema(type=openapi.TYPE_STRING, description="Confirm new password"),
            },
        ),
        responses={
            200: openapi.Response(description="Password reset successfully"),
            400: openapi.Response(description="Invalid reset link or password mismatch"),
        },
        tags=["Authentication"],
    )
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)

            if not default_token_generator.check_token(user, token):
                return Response({"error": "Invalid or expired reset link"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ResetPasswordSerializer(data=request.data)
            if serializer.is_valid():
                user.set_password(serializer.validated_data["new_password"])
                user.save()
                return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Http404:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in reset password: {e}")
            return Response({"error": "Invalid reset request"}, status=status.HTTP_400_BAD_REQUEST)


# Define error response for Swagger
error_response = openapi.Response(
    description="Bad Request",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
        }
    )
)

# Define error response for Swagger
error_response = openapi.Response(
    description="Bad Request",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
        }
    )
)

## Error response for Swagger
def error_response(description="Bad Request"):
    return openapi.Response(
        description=description,
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
            },
        ),
    )

# CUSTOMER LIST & CREATE
@swagger_auto_schema(
    method="get",
    operation_description="Retrieve a list of all customers.",
    responses={200: openapi.Response('Customer list', CustomerSerializer(many=True))}
)
@swagger_auto_schema(
    method="post",
    operation_description="Create a new customer.",
    request_body=CustomerSerializer(),
    responses={201: openapi.Response('Customer created', CustomerSerializer()), 400: error_response()}
)
@api_view(["GET", "POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def customer_list(request):
    if request.method == "GET":
        customers = Customer.objects.filter(user=request.user).order_by("-created_at")
        serializer = CustomerSerializer(customers, many=True, context={"request": request})
        return Response({"customers": serializer.data, "total_customers": customers.count()}, status=status.HTTP_200_OK)

    elif request.method == "POST":
        serializer = CustomerSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# CUSTOMER DETAIL (GET, UPDATE, DELETE)
@swagger_auto_schema(
    method="get",
    operation_description="Retrieve a specific customer by mobile number.",
    responses={200: openapi.Response('Customer details', CustomerSerializer())}
)
@swagger_auto_schema(
    method="put",
    operation_description="Update customer details.",
    request_body=CustomerSerializer(),
    responses={200: openapi.Response('Updated customer', CustomerSerializer()), 400: error_response()}
)
@swagger_auto_schema(
    method="delete",
    operation_description="Delete a customer by mobile number.",
    responses={204: openapi.Response(description="No Content")}
)
@api_view(["GET", "PUT", "DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def customer_detail(request, customer_mobile):
    customer = get_object_or_404(Customer, mobile_number=customer_mobile, user=request.user)

    if request.method == "GET":
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# JOB LIST & CREATE
@swagger_auto_schema(
    method="get",
    operation_description="Retrieve a list of all jobs.",
    responses={200: openapi.Response('Job list', JobSerializer(many=True))}
)
@swagger_auto_schema(
    method="post",
    operation_description="Create a new job.",
    request_body=JobSerializer(),
    responses={201: openapi.Response('Job created', JobSerializer()), 400: error_response()}
)
@api_view(["GET", "POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def job_list_create(request):
    if request.method == "GET":
        jobs = Job.objects.filter(user=request.user).order_by("-created_at")
        serializer = JobSerializer(jobs, many=True, context={"request": request})
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = JobSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# JOB DETAIL (GET, UPDATE, DELETE)
@swagger_auto_schema(
    method="get",
    operation_description="Retrieve a specific job by ID.",
    responses={200: openapi.Response('Job details', JobSerializer())}
)
@swagger_auto_schema(
    method="put",
    operation_description="Update job details.",
    request_body=JobSerializer(),
    responses={200: openapi.Response('Updated job', JobSerializer()), 400: error_response()}
)
@swagger_auto_schema(
    method="delete",
    operation_description="Delete a job by ID.",
    responses={204: openapi.Response(description="No Content")}
)
@api_view(["GET", "PUT", "DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, user=request.user)

    if request.method == "GET":
        serializer = JobSerializer(job)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = JobSerializer(job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        job.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# CUSTOM PERMISSION FOR VERIFIED USERS
class IsVerifiedUser(IsAuthenticated):
    """Custom permission to check if the user is verified."""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and getattr(request.user, 'is_verified', False)

# PROTECTED VIEW FOR VERIFIED USERS
class ProtectedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    @swagger_auto_schema(
        operation_description="Access a protected route for verified users.",
        responses={
            200: openapi.Response(description="Successful Response", examples={"application/json": {"message": "This is a protected view for verified users."}}),
            401: error_response("Unauthorized"),
            403: error_response("Forbidden - You are not a verified user."),
        },
        tags=["Authentication"]
    )
    def get(self, request):
        return Response({"message": "This is a protected view for verified users."}, status=status.HTTP_200_OK)

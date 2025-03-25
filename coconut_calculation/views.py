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
from .models import Customer, Job
from .serializers import (
    RegisterSerializer, LoginSerializer, CustomerSerializer, JobSerializer,ForgotPasswordSerializer, ResetPasswordSerializer
    
)
from rest_framework.permissions import AllowAny
from django.conf import settings    
from .utils import send_verification_email
from .permissions import IsVerifiedUser
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging 
from datetime import timedelta
from .models import User
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiRequest,OpenApiParameter
from rest_framework import serializers
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password,ValidationError
from .tokens import account_activation_token  # ✅ Import the custom token





User = get_user_model()
logger = logging.getLogger(__name__)  # ✅ Configure Logging

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                user.is_active = False  # Keep inactive until verified
                user.save()

                # ✅ Send email verification (Handle errors)
                try:
                    send_verification_email(user)
                except Exception as e:
                    logger.error(f"Email sending failed: {e}")
                    return Response({"error": "User registered but email failed. Contact support."},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                return Response({
                    "message": "User registered successfully. Please check your email to verify your account."
                }, status=status.HTTP_201_CREATED)

            logger.warning(f"Registration failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.critical(f"Unexpected error: {e}")
            return Response({"error": "Something went wrong on the server."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyEmailView(APIView):
    """✅ API to verify email using the token"""
    permission_classes = [AllowAny]  # ✅ Allow unauthenticated users

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)

            # ✅ Check if the token is valid
            if account_activation_token.check_token(user, token):
                user.is_active = True
                user.email_verification_token = None  # ✅ Clear token after activation
                user.save()
                return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)
            else:
                # ✅ Token is invalid/expired—resend a new one
                send_verification_email(user, force_new_token=True)
                return Response({"error": "Token expired. A new verification email has been sent."},
                                status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationEmail(APIView):
    """✅ API to resend email verification"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="User's email address"
                )
            }
        ),
        responses={
            200: openapi.Response(description="Verification email resent successfully"),
            400: openapi.Response(description="Error (email already verified or cooldown active)")
        }
    )
    def post(self, request):
        """✅ Resend email verification if the previous link expired (5-minute cooldown)"""
        email = request.data.get("email")
        user = get_object_or_404(User, email=email)

        if user.is_active:
            return Response({"message": "Email is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Send verification email
        send_verification_email(user)

        return Response({"message": "Verification email resent successfully."}, status=status.HTTP_200_OK)

        
# ✅ Login View
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # 🔥 Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                "message": "Login successful.",
                "refresh": str(refresh),
                "access": f"Bearer {access_token}"  # ✅ Now explicitly formatted as a Bearer Token
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
from django.utils.timezone import now
from datetime import timedelta

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Sends password reset link to the user's email."""
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get("email")
        user = get_object_or_404(User, email=email)

        # Generate password reset token & encoded user ID
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        # Generate password reset links
        frontend_reset_url = f"{settings.FRONTEND_URL}/reset-password/{uidb64}/{token}/"
        backend_reset_url = f"{settings.SITE_DOMAIN}/api/reset-password/{uidb64}/{token}/"

        # ✅ Store the password reset request timestamp
        user.password_reset_requested_at = now()
        user.save()

        # Send email with reset link
        subject = "Password Reset Request"
        message = f"""
        Hello {user.username},

        You requested to reset your password. Click one of the links below:

        🔹 Frontend Reset Link: {frontend_reset_url}
        🔹 Backend Reset Link: {backend_reset_url}

        ⚠️ This link is only valid for 5 minutes.

        If you didn't request this, please ignore this email.

        Thanks,  
        Your Team
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        return Response({"message": "Password reset link sent successfully."}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """Validates the token and resets the user's password."""
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data["new_password"]

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid user ID."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Check if the token is expired (valid for only 5 minutes)
        if user.password_reset_requested_at:
            time_elapsed = now() - user.password_reset_requested_at
            if time_elapsed > timedelta(minutes=5):
                return Response(
                    {"error": "Your password reset link has expired. Please request a new one."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ✅ Validate token before allowing password reset
        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired token. Please request a new reset link."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Validate password before saving
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.password_reset_requested_at = None  # ✅ Clear the timestamp after reset
        user.save()

        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)

# ✅ Protected Customer API
@swagger_auto_schema(
    method="get",
    operation_description="Retrieve a list of all customers.",
    responses={200: CustomerSerializer(many=True)}
)
@swagger_auto_schema(
    method="post",
    operation_description="Create a new customer.",
    request_body=CustomerSerializer,
    responses={
        201: CustomerSerializer(),
        400: "Bad Request (e.g., Mobile number already registered)"
    }
)

@api_view(["GET", "POST"])
@authentication_classes([JWTAuthentication])  # ✅ Use JWT Authentication
@permission_classes([IsAuthenticated])
def customer_list(request):
    """
    Retrieve all customers (GET) or create a new customer (POST).
    """
    if request.method == "GET":
        customers = Customer.objects.filter(user=request.user).order_by("-created_at")  # ✅ Show latest customers first (3,2,1)
        serializer = CustomerSerializer(customers, many=True, context={"request": request})
        return Response({
            "customers": serializer.data,
            "total_customers": customers.count()  # ✅ Move total_customers to the bottom
        }, status=status.HTTP_200_OK)

    elif request.method == "POST":
        data = request.data.copy()
        data["user"] = request.user.id  # ✅ Assign logged-in user as owner of the customer

        serializer = CustomerSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)  # ✅ Assign the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Customer Detail API
@swagger_auto_schema(
    method="get",
    operation_description="Retrieve a specific customer by ID.",
    responses={200: CustomerSerializer()}
)
@swagger_auto_schema(
    method="put",
    operation_description="Update customer details.",
    request_body=CustomerSerializer,
    responses={200: CustomerSerializer(), 400: "Bad Request"}
)
@swagger_auto_schema(
    method="delete",
    operation_description="Delete a customer by ID.",
    responses={204: "No Content"}
)

@api_view(["GET", "PUT", "DELETE"])
@authentication_classes([JWTAuthentication])  # ✅ Use JWT Authentication
@permission_classes([IsAuthenticated])
def customer_detail(request, customer_mobile):
    """
    Retrieve, update, or delete a customer by mobile number.
    """
    customer = get_object_or_404(Customer, mobile_number=customer_mobile, user=request.user)  # ✅ Filter by mobile number and user

    if request.method == "GET":
        return Response(CustomerSerializer(customer).data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Customer updated successfully",
                "customer": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        customer.delete()
        return Response({
            "message": "Customer deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)

# ✅ Protected Job API
@swagger_auto_schema(
    method="get",
    operation_description="Retrieve a list of all jobs.",
    responses={200: JobSerializer(many=True)}
)
@swagger_auto_schema(
    method="post",
    operation_description="Create a new job.",
    request_body=JobSerializer,
    responses={
        201: JobSerializer(),
        400: "Bad Request"
    }
)

@api_view(["GET", "POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def job_list_create(request):
    logger.info(f"User: {request.user}")

    if request.method == "GET":
        jobs = Job.objects.all().order_by("-created_at")
        serializer = JobSerializer(jobs, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        serializer = JobSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()  # ✅ No need to pass `user=request.user` explicitly
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Job Detail API
@swagger_auto_schema(
    method="get",
    operation_description="Retrieve a specific job by ID.",
    responses={200: JobSerializer()}
)
@swagger_auto_schema(
    method="put",
    operation_description="Update job details.",
    request_body=JobSerializer,
    responses={200: JobSerializer(), 400: "Bad Request"}
)
@swagger_auto_schema(
    method="delete",
    operation_description="Delete a job by ID.",
    responses={204: "No Content"}
)
@api_view(["GET", "PUT", "DELETE"])
@authentication_classes([JWTAuthentication])  # Ensure authentication
@permission_classes([IsAuthenticated])
def job_detail(request, job_id):  # ✅ Changed from `id` to `job_id`
    """
    Retrieve, update, or delete a job by `job_id` (not `id`).
    """
    job = get_object_or_404(Job, job_id=job_id)  # ✅ Lookup by `job_id`

    if request.method == "GET":
        serializer = JobSerializer(job, context={"request": request})
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = JobSerializer(job, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        job.delete()
        return Response({"message": "Job deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# ✅ Protected View for Verified Users
class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsVerifiedUser]

    @swagger_auto_schema(
        operation_description="Retrieve a protected message for verified users.",
        responses={200: openapi.Response("Success", openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            "message": openapi.Schema(type=openapi.TYPE_STRING, description="Response message")
        }))}
    )
    def get(self, request):
        """
        Retrieve a message for verified users only.
        """
        return Response({"message": "This is a protected view for verified users."})

from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings  # ✅ Import settings to set API schema URL
from .views import (
    RegisterView, VerifyEmailView, LoginAPIView, customer_list, customer_detail,
    job_list_create, job_detail, ProtectedView, ForgotPasswordView, ResetPasswordView,
    resend_verification_email
)

# ✅ Schema View for Swagger & ReDoc
schema_view = get_schema_view(
    openapi.Info(
        title="Coconut API",
        default_version='v1',
        description="API documentation for Customer & Job Management",
        terms_of_service="http://www.yourwebsite.com/terms/",
        contact=openapi.Contact(email="support@yourwebsite.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  # ✅ Ensure correct tuple format
    url=f"http://{settings.ALLOWED_HOSTS[0]}:8000" if settings.ALLOWED_HOSTS else "http://127.0.0.1:8000",  # ✅ Force HTTP
)

urlpatterns = [
    # Swagger & ReDoc API Documentation
    path('swagger/', schema_view.with_ui('swagger'), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc'), name='schema-redoc'),

    # Authentication APIs
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('api/resend-verification/', resend_verification_email, name='resend_verification'),

    # Customer APIs
    path('api/customers/', customer_list, name='customer-list'),
    path("customers/<str:customer_mobile>/", customer_detail, name="customer-detail"),
    
    # Job APIs
    path('api/jobs/', job_list_create, name='job-list-create'),
    path('api/jobs/<str:job_id>/', job_detail, name='job-detail'), 
    
    # Protected Route
    path('api/protected/', ProtectedView.as_view(), name='protected-view'),

    # Password Reset APIs
    path("api/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("api/reset-password/<uidb64>/<token>/", ResetPasswordView.as_view(), name="reset-password"),
]

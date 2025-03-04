from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
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
        terms_of_service="https://www.yourwebsite.com/terms/",
        contact=openapi.Contact(email="support@yourwebsite.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],  # ✅ Use list format instead of tuple
)

urlpatterns = [
    # ✅ Swagger UI & ReDoc Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # ✅ Authentication APIs
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('api/resend-verification/', resend_verification_email, name='resend_verification'),

    # ✅ Customer APIs
    path('api/customers/', customer_list, name='customer-list'),
    path('api/customers/<uuid:id>/', customer_detail, name='customer-detail'),

    # ✅ Job APIs
    path('api/jobs/', job_list_create, name='job-list-create'),
    path('api/jobs/<int:id>/', job_detail, name='job-detail'),

    # ✅ Protected Route
    path('api/protected/', ProtectedView.as_view(), name='protected-view'),

    # ✅ Password Reset APIs
    path("api/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("api/reset-password/<uidb64>/<token>/", ResetPasswordView.as_view(), name="reset-password"),
]
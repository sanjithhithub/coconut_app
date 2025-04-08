from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import (
    RegisterView, VerifyEmailView, LoginView, customer_list, customer_detail,
    job_list_create, job_detail, ProtectedView, ForgotPasswordView, 
    ResetPasswordView, ResendVerificationEmail
)

# ✅ API Schema for Swagger & ReDoc
schema_view = get_schema_view(
    openapi.Info(
        title="Coconut API",
        default_version="v1",
        description="API documentation for Coconut API",
        terms_of_service="https://example.com/terms/",  # 🔄 Replace with a real URL
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  # ✅ Fixed tuple syntax
)

urlpatterns = [
    # 📌 API Documentation (Swagger & ReDoc)
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # 📌 Authentication APIs
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('api/auth/reset-password/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='password-reset'),
    path('api/auth/resend-verification/', ResendVerificationEmail.as_view(), name='resend-verification'),
    path('api/auth/verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),

    # 📌 Customer APIs
    path('api/customers/', customer_list, name='customer-list'),
    path('api/customers/<str:customer_mobile>/', customer_detail, name='customer-detail'),

    # 📌 Job APIs
    path('api/jobs/', job_list_create, name='job-list'),
    path('api/jobs/<str:job_id>/', job_detail, name='job-detail'),

    # 📌 Protected Route (Requires Authentication)
    path('api/protected/', ProtectedView.as_view(), name='protected-view'),
]

from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token  # ✅ Import the custom token generator

def send_verification_email(user, force_new_token=False):
    """Send email verification link with both API and frontend routes."""
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    
    # ✅ Regenerate token only if requested
    if force_new_token or not user.is_active:
        token = account_activation_token.make_token(user)
    else:
        token = user.email_verification_token  # Use existing token if not expired
    
    # ✅ Store token in the user model (add this field if needed)
    user.email_verification_token = token
    user.save()

    # ✅ Generate both URLs
    backend_verification_link = f"{settings.SITE_DOMAIN}/api/verify-email/{uidb64}/{token}/"
    frontend_verification_link = f"{settings.SITE_DOMAIN}/api/verify-email/{uidb64}/{token}/"

    email_subject = "Verify Your Email"
    email_body = f"""
    Hello {user.username},

    Click one of the links below to verify your email:

    ✅ Backend Verification Link:
    {backend_verification_link}

    ✅ Frontend Verification Link:
    {frontend_verification_link}

    If you did not sign up, please ignore this email.

    Thanks,  
    Your Team
    """

    send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email])

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings

def send_verification_email(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    
    # ✅ Use settings for flexible URL (supports both local & production)
    base_url = getattr(settings, "BACKEND_URL", "http://127.0.0.1:8000")  # Fallback to local
    verification_url = f"{base_url}{reverse('verify-email', kwargs={'uidb64': uidb64, 'token': token})}"

    email_body = f"""
    Hello {user.username},

    Click the link below to verify your email:

    {verification_url}

    If you did not request this, please ignore this email.

    Regards,
    Your Team
    """

    # ✅ Ensure email sending is configured
    user.email_user("Verify Your Email", email_body)

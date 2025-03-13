from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail

def send_verification_email(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    
    # ✅ Use settings for flexible URL (Supports local & AWS)
    base_url = getattr(settings, "BACKEND_URL", "http://127.0.0.1:8000")  # Default to local
    verification_url = f"{base_url}{reverse('verify-email', kwargs={'uidb64': uidb64, 'token': token})}"

    email_subject = "Verify Your Email - YourApp"
    email_body = f"""
    Hello {user.username},

    Please verify your email by clicking the link below:

    {verification_url}

    If you did not request this, please ignore this email.

    Regards,
    Your Team
    """

    # ✅ Send email using AWS SES
    send_mail(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,  # Must be a verified AWS SES email
        [user.email],  
        fail_silently=False,
    )

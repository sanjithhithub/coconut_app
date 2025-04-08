import logging
from datetime import timedelta
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# Set up logging
logger = logging.getLogger(__name__)

# Define token expiration period (e.g., 1 day)
TOKEN_EXPIRATION_TIME = timedelta(days=1)

def generate_verification_token(user):
    """Generate a secure signed token with a timestamp for verification."""
    try:
        signer = TimestampSigner()
        token = signer.sign(str(user.pk))  # Ensure user.pk is a string
        return token
    except Exception as e:
        logger.error(f"Token generation failed: {e}")
        return None

def get_verification_url(user):
    """Generate frontend and backend verification URLs securely."""
    try:
        uidb64 = urlsafe_base64_encode(force_bytes(str(user.pk)))  # Ensure pk is a string
        token = generate_verification_token(user)

        if not token:
            logger.error("Token generation failed")
            return None, None

        # Ensure SITE_URL and FRONTEND_URL are defined in settings
        site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")

        try:
            backend_path = reverse('verify-email', kwargs={'uidb64': uidb64, 'token': token})
            backend_url = f"{site_url}{backend_path}"
        except Exception as e:
            logger.error(f"Reverse URL lookup failed: {e}")
            backend_url = None

        frontend_url = f"{frontend_url}/verify-email/{uidb64}/{token}/"

        return backend_url, frontend_url
    except Exception as e:
        logger.error(f"URL generation failed: {e}")
        return None, None

def send_verification_email(user):
    """Send an email with both frontend and backend verification links."""
    try:
        backend_url, frontend_url = get_verification_url(user)

        if not backend_url or not frontend_url:
            logger.error("Verification URL generation failed")
            return False

        subject = "Verify Your Email Address"
        message = f"""Hello {user.username},

Please click one of the following links to verify your email address:

🔗 Backend Verification: {backend_url}
🔗 Frontend Verification: {frontend_url}

This link is valid for {TOKEN_EXPIRATION_TIME.days} day(s). 
If you did not request this, please ignore this email.

Best regards,  
Your Team
"""

        email_sent = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )

        if email_sent:
            logger.info(f"Verification email sent successfully to {user.email}")
            return True
        else:
            logger.error(f"Failed to send verification email to {user.email}")
            return False
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        return False

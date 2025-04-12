from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_verification_email(user, backend_url, frontend_url):
    try:
        subject = "Verify your email"
        message = f"""
Hello {user.username},

Please verify your email using the links below:

Backend Link: {backend_url}
Frontend Link: {frontend_url}

This link is valid for 1 day.

If you did not request this, you can ignore this email.

Regards,
Your Team
"""
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )

        logger.info(f"Verification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Error sending verification email: {e}")
        return False

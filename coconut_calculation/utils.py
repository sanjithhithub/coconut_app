from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.utils.html import format_html
import logging

# 🔍 Set up logging for debugging
logger = logging.getLogger(__name__)

def send_verification_email(user):
    try:
        # 🔹 Generate unique verification token & link
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # 🔹 Ensure correct backend URL for AWS deployment
        base_url = getattr(settings, "BACKEND_URL", "http://127.0.0.1:8000")  # ✅ Fallback to local
        verification_url = f"{base_url}{reverse('verify-email', kwargs={'uidb64': uidb64, 'token': token})}"

        email_subject = "Verify Your Email - YourApp"
        email_body = format_html(
            """
            <p>Hello <strong>{}</strong>,</p>
            <p>Please verify your email by clicking the link below:</p>
            <p><a href="{}" style="color:blue;">Verify Email</a></p>
            <p>If you did not request this, please ignore this email.</p>
            <p>Regards,</p>
            <p><strong>Your Team</strong></p>
            """,
            user.username,
            verification_url
        )

        # 🔹 Ensure AWS SES verified email is used
        sender_email = settings.DEFAULT_FROM_EMAIL
        recipient_email = [user.email]

        # ✅ Send email using AWS SES
        send_mail(
            subject=email_subject,
            message=email_body,  # ✅ Uses plain text fallback
            from_email=sender_email,  # ✅ Must be AWS SES verified email
            recipient_list=recipient_email,
            fail_silently=False,
            html_message=email_body  # ✅ Uses HTML email format
        )

        logger.info(f"Verification email sent to {user.email}")

    except BadHeaderError:
        logger.error("Invalid header found in email.")
    except Exception as e:
        logger.error(f"Error sending verification email: {e}")

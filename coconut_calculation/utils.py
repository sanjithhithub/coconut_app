from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    # ✅ Generate the correct link using Render URL
    verification_link = f"{settings.SITE_DOMAIN}/api/verify-email/{uidb64}/{token}/"

    email_subject = "Verify Your Email"
    email_body = f"Click the link to verify your email: {verification_link}"

    send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email])

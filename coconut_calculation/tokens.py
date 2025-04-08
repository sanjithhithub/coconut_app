from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """Custom token generator for email verification."""

    def _make_hash_value(self, user, timestamp):
        """Generate a secure token using user ID, timestamp, and active status."""
        return f"{user.pk}{timestamp}{user.is_active}{user.email}"

# ✅ Global instance for easy access
account_activation_token = AccountActivationTokenGenerator()

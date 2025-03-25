from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """Custom token generator for email verification."""

    def _make_hash_value(self, user, timestamp):
        """Include user status in the token so it's invalidated only after use."""
        return f"{user.pk}{timestamp}{user.is_active}"

# ✅ Global instance for easy access
account_activation_token = AccountActivationTokenGenerator()

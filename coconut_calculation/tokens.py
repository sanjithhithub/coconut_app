from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Generates an activation token for email verification.
    """

    def _make_hash_value(self, user, timestamp):
        return six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)

# ✅ Create a token instance that can be used in views
account_activation_token = AccountActivationTokenGenerator()

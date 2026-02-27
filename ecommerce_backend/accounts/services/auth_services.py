from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class AuthService:

    @staticmethod
    def logout_user(refresh_token):
        """
        Blacklists the provided refresh token.
        Raises TokenError if invalid.
        """

        if not refresh_token:
            raise ValueError("Refresh token is required")

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as e:
            raise TokenError("Invalid or expired token")
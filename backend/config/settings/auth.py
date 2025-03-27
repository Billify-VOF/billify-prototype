from rest_framework.authentication import TokenAuthentication


class BearerTokenAuthentication(TokenAuthentication):
    """
    Custom authentication class to use 'Bearer' instead of 'Token'.
    """

    keyword = "Bearer"  # Change from 'Token' to 'Bearer'

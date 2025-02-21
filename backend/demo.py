import requests
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import redirect

from dotenv import load_dotenv
load_dotenv()


PONTO_CLIENT_ID = os.getenv('PONTO_CLIENT_ID')
PONTO_CLIENT_SECRET = os.getenv('PONTO_CLIENT_SECRET')
PONTO_AUTH_URL = os.getenv('PONTO_AUTH_URL')
PONTO_TOKEN_URL = os.getenv('PONTO_TOKEN_URL')
PONTO_REDIRECT_URI = os.getenv('PONTO_REDIRECT_URI')


def ponto_login(request):
    """
    Redirects the user to Ponto OAuth2 login page.
    """
    auth_url = (f"{PONTO_AUTH_URL}?client_id={PONTO_CLIENT_ID}"
                f"&redirect_uri={PONTO_REDIRECT_URI}&response_type=code&scope=read")
    print('auth_url',auth_url)
    return redirect(auth_url)

def ponto_callback():
    # Get the authorization code from Ponto
    auth_code = request.args.get('code')

    if not auth_code:
        return "Authorization failed: No code received", 400

    return f"Authorization Code: {auth_code}"
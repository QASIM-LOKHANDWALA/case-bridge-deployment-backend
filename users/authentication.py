# users/authentication.py
from rest_framework.authentication import BaseAuthentication
from users.utils import decode_jwt

from dotenv import load_dotenv
import os

load_dotenv()
debug = os.getenv("DEBUG", "False")

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]
        user = decode_jwt(token)
        
        if debug:
            print("Authenticated user: ", user)
        
        return (user, None)
import jwt, datetime
from django.conf import settings
from users.models import User
from rest_framework.exceptions import AuthenticationFailed

def generate_jwt(user):
    payload = {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "iat": datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token

def decode_jwt(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = User.objects.get(id=payload["id"])
        return user
    except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
        raise AuthenticationFailed("Invalid or expired token")
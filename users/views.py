from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from users.models import User
from clients.models import GeneralUserProfile
from lawyers.models import LawyerProfile
from users.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated

from dotenv import load_dotenv
import os

load_dotenv()
debug = os.getenv("DEBUG", "False")

class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        
        role = data.get("role")
        email = data.get("email")
        password = data.get("password")
        full_name = data.get("full_name")

        if not all([email, password, role, full_name]):
            if debug:
                print("Missing field(s):", email, password, role, full_name)
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            if debug:
                print("Email already exists:", email)
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(email=email, password=password, role=role)
        except Exception as e:
            if debug:
                print("Error creating user:", str(e))
            return Response({"error": "User creation failed"}, status=status.HTTP_400_BAD_REQUEST)
    
        if role == "general":
            if debug:
                print("Creating GeneralUserProfile...")

            phone_number = data.get("phone_number")
            address = data.get("address")
            GeneralUserProfile.objects.create(
                user=user,
                full_name=full_name,
                phone_number=phone_number,
                address=address,
            )
        elif role == "lawyer":
            if debug:
                print("Creating LawyerProfile...")

            bar_reg = data.get("bar_registration_number")
            specialization = data.get("specialization")
            experience_years = data.get("experience_years")
            location = data.get("location")
            bio = data.get("bio", "")

            if LawyerProfile.objects.filter(bar_registration_number=bar_reg).exists():
                return Response({"error": "Bar registration number already exists"}, status=status.HTTP_400_BAD_REQUEST)

            LawyerProfile.objects.create(
                user=user,
                full_name=full_name,
                bar_registration_number=bar_reg,
                specialization=specialization,
                experience_years=experience_years,
                location=location,
                bio=bio,
            )
        else:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        serialized_user = UserSerializer(user).data

        return Response({
            "message": "Signup successful",
            "token": token.key,
            "user": serialized_user
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)

        serialized_user = UserSerializer(user).data

        return Response({
            "message": "Login successful",
            "token": token.key,
            "user": serialized_user
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            
            if debug:
                print("Logging out user:", request.user.email)
            request.user.auth_token.delete()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"error": "Token not found"}, status=status.HTTP_400_BAD_REQUEST)
        
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({"user": serializer.data})
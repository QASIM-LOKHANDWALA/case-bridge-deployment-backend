from rest_framework import serializers
from .models import GeneralUserProfile

class GeneralUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralUserProfile
        fields = ['full_name', 'address', 'phone_number', 'created_at']
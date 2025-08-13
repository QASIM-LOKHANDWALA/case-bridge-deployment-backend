from rest_framework import serializers
from users.models import User
from hire.models import Hire
from clients.serializers import GeneralUserProfileSerializer
from lawyers.serializers import LawyerProfileSerializer

class UserSerializer(serializers.ModelSerializer):
    general_profile = GeneralUserProfileSerializer(read_only=True)
    lawyer_profile = LawyerProfileSerializer(read_only=True)
    number_of_cases = serializers.SerializerMethodField()
    number_of_clients = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'date_joined', 'general_profile', 'lawyer_profile', 'number_of_cases', 'number_of_clients']

    def get_number_of_cases(self, obj):
        if obj.role == 'lawyer' and hasattr(obj, 'lawyer_profile') and obj.lawyer_profile:
            return obj.lawyer_profile.legal_cases.count()
        return None

    def get_number_of_clients(self, obj):
        if obj.role == 'lawyer' and hasattr(obj, 'lawyer_profile') and obj.lawyer_profile:
            return Hire.objects.filter(
                lawyer=obj.lawyer_profile,
                status='accepted'
            ).values('client').distinct().count()
        return None
from rest_framework import serializers
from .models import CaseAppointment
from lawyers.serializers import LawyerProfileSerializer
from clients.serializers import GeneralUserProfileSerializer

class CaseAppointmentSerializer(serializers.ModelSerializer):
    user = GeneralUserProfileSerializer()
    
    class Meta:
        model = CaseAppointment
        fields = '__all__'

from rest_framework import serializers
from .models import Hire

class HireLawyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hire
        fields = "__all__"

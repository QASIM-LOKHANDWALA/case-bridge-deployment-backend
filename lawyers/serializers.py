from rest_framework import serializers
from .models import LawyerProfile, CaseDocument, LawyerDocuments

class CaseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseDocument
        fields = ['id', 'legal_case', 'title', 'document', 'uploaded_at']
        read_only_fields = ['uploaded_at']
        
class LawyerDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawyerDocuments
        fields = ['uploaded', 'photo_id', 'cop']
        
class LawyerProfileSerializer(serializers.ModelSerializer):
    documents = LawyerDocumentsSerializer(read_only=True)
    
    class Meta:
        model = LawyerProfile
        fields = [
            'id', 'full_name', 'bar_registration_number', 'specialization',
            'experience_years', 'location', 'bio', 'is_verified',
            'profile_picture', 'documents',  'rating', 'created_at', 'clients_served', 'cases_won'
        ]
        
        read_only_fields = ['is_verified']

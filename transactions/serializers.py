from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    lawyer_name = serializers.CharField(source='lawyer.full_name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'status', 'description',
            'timestamp', 'paid_at', 'user_name', 'user_email', 'lawyer_name'
        ]
        read_only_fields = ['id', 'transaction_id', 'timestamp']
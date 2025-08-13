from rest_framework import serializers
from .models import Message, Conversation
from users.models import User

class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source='sender.email', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_email', 'text', 'timestamp']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'messages']

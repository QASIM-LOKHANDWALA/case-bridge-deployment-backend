from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Message, Conversation
from users.models import User
from clients.models import GeneralUserProfile
from lawyers.models import LawyerProfile
from hire.models import Hire
from .serializers import MessageSerializer
from django.utils.dateparse import parse_datetime
from utils.rag_model import get_legal_answer

from dotenv import load_dotenv
import os

load_dotenv()
debug = os.getenv("DEBUG", "False")

class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=404)

        if request.user not in conversation.participants.all():
            return Response({'error': 'Not authorized for this conversation'}, status=403)

        since = request.query_params.get('since')
        messages = conversation.messages.all()
        if since:
            messages = messages.filter(timestamp__gt=parse_datetime(since))

        serialized = MessageSerializer(messages, many=True)
        return Response(serialized.data)


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        text = request.data.get('text')
        if not text:
            return Response({"error": "Message text required"}, status=400)

        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found"}, status=404)

        if request.user not in conversation.participants.all():
            return Response({'error': 'Not authorized for this conversation'}, status=403)

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            text=text
        )
        return Response(MessageSerializer(message).data)


class StartConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user1 = request.user
        user2_id = request.data.get("participant_id")

        if not user2_id:
            return Response({"error": "Participant ID required"}, status=400)

        try:
            user2 = User.objects.get(id=user2_id)
        except User.DoesNotExist:
            return Response({"error": "Participant not found"}, status=404)

        if not is_valid_hire_pair(user1, user2):
            return Response({"error": "No valid hire relationship found."}, status=403)

        existing_convos = Conversation.objects.filter(participants=user1).filter(participants=user2)
        for convo in existing_convos:
            if convo.participants.count() == 2:
                return Response({"conversation_id": convo.id, "message": "Conversation already exists"})

        conversation = Conversation.objects.create()
        conversation.participants.add(user1, user2)
        return Response({"conversation_id": conversation.id, "message": "New conversation started"})


def is_valid_hire_pair(user1, user2):
    try:
        if user1.role == 'general' and user2.role == 'lawyer':
            client = GeneralUserProfile.objects.get(user=user1)
            lawyer = LawyerProfile.objects.get(user=user2)
        elif user1.role == 'lawyer' and user2.role == 'general':
            client = GeneralUserProfile.objects.get(user=user2)
            lawyer = LawyerProfile.objects.get(user=user1)
        else:
            return False
    except (GeneralUserProfile.DoesNotExist, LawyerProfile.DoesNotExist):
        return False

    return Hire.objects.filter(client=client, lawyer=lawyer, status='accepted').exists()

class ChatContactListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        contacts = []

        if user.role == 'lawyer':
            try:
                lawyer_profile = LawyerProfile.objects.get(user=user)
                hires = Hire.objects.filter(lawyer=lawyer_profile, status='accepted')
                for hire in hires:
                    client_user = hire.client.user
                    contacts.append({
                        "user_id": client_user.id,
                        "full_name": hire.client.full_name,
                        "email": client_user.email,
                        "role": "client"
                    })
            except LawyerProfile.DoesNotExist:
                pass

        elif user.role == 'general':
            try:
                client_profile = GeneralUserProfile.objects.get(user=user)
                hires = Hire.objects.filter(client=client_profile, status='accepted')
                for hire in hires:
                    lawyer_user = hire.lawyer.user
                    contacts.append({
                        "user_id": lawyer_user.id,
                        "full_name": hire.lawyer.full_name,
                        "email": lawyer_user.email,
                        "role": "lawyer"
                    })
            except GeneralUserProfile.DoesNotExist:
                pass

        return Response(contacts)
    
class LegalBotInitConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            bot_user = User.objects.get(email='legalbot@casebridge.com')
        except User.DoesNotExist:
            return Response({"error": "Bot user not found"}, status=500)

        existing = Conversation.objects.filter(participants=user).filter(participants=bot_user)
        for convo in existing:
            if convo.participants.count() == 2:
                return Response({"conversation_id": convo.id, "message": "Bot conversation already exists"})

        conversation = Conversation.objects.create()
        conversation.participants.add(user, bot_user)
        return Response({"conversation_id": conversation.id, "message": "New bot conversation started"})

class LegalBotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        user_message = request.data.get('text')
        if not user_message:
            return Response({"error": "Message text required"}, status=400)

        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in conversation.participants.all():
            return Response({"error": "Not a participant of this conversation"}, status=403)

        user_msg = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            text=user_message
        )

        bot_reply = get_legal_answer(user_message)

        bot_user = User.objects.get(email='legalbot@casebridge.com')

        bot_msg = Message.objects.create(
            conversation=conversation,
            sender=bot_user,
            text=bot_reply
        )

        return Response({
            "user_message": MessageSerializer(user_msg).data,
            "bot_reply": MessageSerializer(bot_msg).data
        })

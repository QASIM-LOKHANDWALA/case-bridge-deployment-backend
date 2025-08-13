from django.http import Http404
from django.db.models import Avg
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import LawyerProfile, LegalCase, LawyerDocuments, LawyerRating
from users.models import User
from appointments.models import CaseAppointment
from clients.models import GeneralUserProfile
from .serializers import LawyerDocumentsSerializer, LawyerProfileSerializer
from users.serializers import UserSerializer
from appointments.serializers import CaseAppointmentSerializer
from rest_framework import status
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import CaseDocumentSerializer

from dotenv import load_dotenv
import os

load_dotenv()
debug = os.getenv("DEBUG", "False")

def update_lawyer_rating(lawyer):
    avg_rating = LawyerRating.objects.filter(lawyer=lawyer).aggregate(avg=Avg('rating'))['avg'] or 0
    lawyer.rating = round(avg_rating, 1)
    lawyer.save()


class LawyerListView(ListAPIView):
    queryset = User.objects.filter(role='lawyer').exclude(email='legalbot@casebridge.com')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class LawyerDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404
    
    def get(self, request, user_id):
        lawyer = self.get_object(user_id)
        serializer = UserSerializer(lawyer)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateLawyerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, user):
        try:
            return user.lawyer_profile
        except LawyerProfile.DoesNotExist:
            raise Http404("Lawyer profile not found.")

    def put(self, request):
        lawyer_profile = self.get_object(request.user)
        serializer = LawyerProfileSerializer(lawyer_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully.",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
@api_view(['GET'])
def get_lawyer_clients(request, lawyer_id):
    try:
        lawyer = LawyerProfile.objects.get(id=lawyer_id)
    except LawyerProfile.DoesNotExist:
        return Response({'error': 'Lawyer not found'}, status=status.HTTP_404_NOT_FOUND)

    hires = lawyer.hires.filter()

    client_data = []
    for hire in hires:
        client = hire.client
        user = client.user

        total_cases = LegalCase.objects.filter(client=client, lawyer=lawyer).count()
        active_cases = LegalCase.objects.filter(client=client, lawyer=lawyer, status='active').count()

        client_data.append({
            "id": client.id,
            "name": client.full_name,
            "phone": client.phone_number,
            "email": user.email,
            "activeCases": active_cases,
            "totalCases": total_cases,
            "hire_status": hire.status,
            "hire_id": hire.id,
            "status": "Active" if active_cases > 0 else "Inactive"
        })

    return Response(client_data, status=status.HTTP_200_OK)
    
class LawyerAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            lawyer_profile = user.lawyer_profile
        except LawyerProfile.DoesNotExist:
            return Response({"error": "You are not authorized to view appointments."}, status=status.HTTP_403_FORBIDDEN)

        appointments = CaseAppointment.objects.filter(lawyer=lawyer_profile).order_by('-appointment_date')

        serializer = CaseAppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LawyerCasesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            lawyer_profile = user.lawyer_profile
        except LawyerProfile.DoesNotExist:
            return Response({"error": "You are not authorized to view cases."}, status=status.HTTP_403_FORBIDDEN)

        cases = LegalCase.objects.filter(lawyer=lawyer_profile).order_by('-created_at')

        return Response({
            "cases": [
                {
                    "id": case.id,
                    "title": case.title,
                    "client": case.client.full_name,
                    "court": case.court,
                    "case_number": case.case_number,
                    "next_hearing": case.next_hearing,
                    "status": case.status,
                    "priority": case.priority,
                    "created_at": case.created_at,
                    "documents": [
                        {
                            "id": doc.id,
                            "title": doc.title,
                            "document": request.build_absolute_uri(doc.document.url),
                            "uploaded_at": doc.uploaded_at
                        } for doc in case.documents.all()
                    ]
                } for case in cases
            ]
        }, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user

        try:
            lawyer_profile = user.lawyer_profile
        except LawyerProfile.DoesNotExist:
            return Response({"error": "You are not authorized to create cases."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        required_fields = ['title', 'client_id', 'court', 'case_number', 'next_hearing']

        for field in required_fields:
            if field not in data:
                return Response({"error": f"{field} is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client = GeneralUserProfile.objects.get(id=data['client_id'])
        except GeneralUserProfile.DoesNotExist:
            return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            legal_case = LegalCase.objects.create(
                title=data['title'],
                client=client,
                lawyer=lawyer_profile,
                court=data['court'],
                case_number=data['case_number'],
                next_hearing=data['next_hearing'],
                status=data.get('status', 'active'),
                priority=data.get('priority', 'medium'),
                last_update=timezone.now()
            )

            return Response({
                "message": "Legal case created successfully.",
                "case": {
                    "id": legal_case.id,
                    "title": legal_case.title,
                    "client": legal_case.client.full_name,
                    "court": legal_case.court,
                    "case_number": legal_case.case_number,
                    "next_hearing": legal_case.next_hearing,
                    "status": legal_case.status,
                    "priority": legal_case.priority,
                    "created_at": legal_case.created_at
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": "Failed to create legal case.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UploadCaseDocumentView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, case_id):
        user = request.user

        try:
            legal_case = LegalCase.objects.get(id=case_id, lawyer=user.lawyer_profile)
        except LegalCase.DoesNotExist:
            return Response({"error": "Case not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['legal_case'] = legal_case.id

        serializer = CaseDocumentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Document uploaded successfully.", "document": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LawyerDocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_lawyer_profile(self, user):
        try:
            return LawyerProfile.objects.get(user=user)
        except LawyerProfile.DoesNotExist:
            return None

    def get(self, request):
        profile = self.get_lawyer_profile(request.user)
        if not profile or not hasattr(profile, 'documents'):
            return Response({"detail": "Documents not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LawyerDocumentsSerializer(profile.documents)
        return Response(serializer.data)

    def post(self, request):
        profile = self.get_lawyer_profile(request.user)
        if not profile:
            return Response({"detail": "Lawyer profile not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            document = profile.documents
            if document.uploaded:
                return Response({"message":"Documents Already Uploaded."}, status=status.HTTP_204_NO_CONTENT)
        except LawyerDocuments.DoesNotExist:
            serializer = LawyerDocumentsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(lawyer=profile, uploaded=True)
                return Response({"message":"Documents Uploaded For Verification."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RateLawyerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        try:
            general_profile = user.general_profile
        except GeneralUserProfile.DoesNotExist:
            return Response({"error": "Only general users can rate lawyers."}, status=status.HTTP_403_FORBIDDEN)

        lawyer_id = request.data.get('lawyer_id')
        rating = request.data.get('rating')

        if lawyer_id is None or rating is None:
            return Response({"error": "lawyer_id and rating are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lawyer_profile = LawyerProfile.objects.get(id=lawyer_id)
        except LawyerProfile.DoesNotExist:
            return Response({"error": "Lawyer not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            rating = int(rating)
            if rating < 0 or rating > 5:
                raise ValueError()
        except ValueError:
            return Response({"error": "Rating must be an integer between 0 and 5."}, status=status.HTTP_400_BAD_REQUEST)

        rating_obj, created = LawyerRating.objects.update_or_create(
            user=general_profile,
            lawyer=lawyer_profile,
            defaults={'rating': rating}
        )

        update_lawyer_rating(lawyer_profile)

        return Response(
            {"message": "Rating submitted successfully.", "new_rating": lawyer_profile.rating},
            status=status.HTTP_200_OK
        )
        
class GetLawyerRatingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        lawyer_id = request.query_params.get('lawyer_id')

        if not lawyer_id:
            return Response({"error": "lawyer_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            general_profile = user.general_profile
        except GeneralUserProfile.DoesNotExist:
            return Response({"error": "Only general users can check ratings."}, status=status.HTTP_403_FORBIDDEN)

        try:
            lawyer_profile = LawyerProfile.objects.get(id=lawyer_id)
        except LawyerProfile.DoesNotExist:
            return Response({"error": "Lawyer not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            rating = LawyerRating.objects.get(user=general_profile, lawyer=lawyer_profile)
            return Response({
                "has_rated": True,
                "rating": rating.rating,
                "rated_at": rating.created_at
            }, status=status.HTTP_200_OK)
        except LawyerRating.DoesNotExist:
            return Response({
                "has_rated": False,
                "rating": None,
                "rated_at": None
            }, status=status.HTTP_200_OK)
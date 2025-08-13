from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import CaseAppointment
from users.models import User
from lawyers.models import LawyerProfile
from clients.models import GeneralUserProfile

from .serializers import CaseAppointmentSerializer
from dotenv import load_dotenv
import os

load_dotenv()
debug = os.getenv("DEBUG", "False")

class ScheduleAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            lawyer_profile = LawyerProfile.objects.get(user=request.user)
        except LawyerProfile.DoesNotExist:
            return Response({"error": "Only lawyers can schedule appointments."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        user_id = data.get("user_id")
        appointment_date = data.get("appointment_date")
        appointment_time = data.get("appointment_time")

        if not user_id or not appointment_date or not appointment_time:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(GeneralUserProfile, id=user_id)

        appointment = CaseAppointment.objects.create(
            user=user,
            lawyer=lawyer_profile,
            title=data.get("title", "Appointment with Client"),
            description=data.get("description", ""),
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='pending'
        )

        serializer = CaseAppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class LawyerAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            lawyer_profile = LawyerProfile.objects.get(user=request.user)
        except LawyerProfile.DoesNotExist:
            return Response({"error": "Only lawyers can view their appointments."}, status=status.HTTP_403_FORBIDDEN)

        appointments = CaseAppointment.objects.filter(lawyer=lawyer_profile).order_by('-appointment_date')
        serializer = CaseAppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ClientAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_profile = GeneralUserProfile.objects.get(user=request.user)
        except GeneralUserProfile.DoesNotExist:
            return Response({"error": "Only clients can view their appointments."}, status=status.HTTP_403_FORBIDDEN)

        appointments = CaseAppointment.objects.filter(user=user_profile).order_by('-appointment_date')
        serializer = CaseAppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class UpdateAppointmentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, appointment_id):
        try:
            lawyer_profile = LawyerProfile.objects.get(user=request.user)
        except LawyerProfile.DoesNotExist:
            return Response({"error": "Only lawyers can update appointment status."}, status=status.HTTP_403_FORBIDDEN)

        appointment = get_object_or_404(CaseAppointment, id=appointment_id)

        if appointment.lawyer != lawyer_profile:
            return Response({"error": "Unauthorized to update this appointment."}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get("status")
        if new_status not in dict(CaseAppointment.STATUS_CHOICES):
            return Response({"error": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)

        appointment.status = new_status
        appointment.save()
        serializer = CaseAppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, appointment_id):
        try:
            lawyer_profile = LawyerProfile.objects.get(user=request.user)
        except LawyerProfile.DoesNotExist:
            return Response({"error": "Only lawyers can delete appointments."}, status=status.HTTP_403_FORBIDDEN)

        appointment = get_object_or_404(CaseAppointment, id=appointment_id)

        if appointment.lawyer != lawyer_profile:
            return Response({"error": "Unauthorized to delete this appointment."}, status=status.HTTP_403_FORBIDDEN)

        appointment.delete()
        return Response({"message": "Appointment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
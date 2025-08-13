from django.db import models
from clients.models import GeneralUserProfile
from lawyers.models import LawyerProfile

class CaseAppointment(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(GeneralUserProfile, on_delete=models.CASCADE, related_name='appointments')
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE, related_name='appointments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField(null=True,blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.user.email} -> {self.lawyer.user.email}"
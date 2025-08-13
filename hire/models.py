from django.db import models
from users.models import User
from lawyers.models import LawyerProfile
from clients.models import GeneralUserProfile

class Hire(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    client = models.ForeignKey(GeneralUserProfile, on_delete=models.CASCADE, related_name='hires')
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE, related_name='hires')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    hired_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.client.full_name} -> {self.lawyer.full_name} | {self.status}'
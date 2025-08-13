from django.db import models
from lawyers.models import LawyerProfile
from clients.models import GeneralUserProfile

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed')
    )

    user = models.ForeignKey(GeneralUserProfile, on_delete=models.CASCADE, blank=True, null=True)
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.user.full_name} - {self.lawyer.full_name} - ₹{self.amount} - {self.status}'

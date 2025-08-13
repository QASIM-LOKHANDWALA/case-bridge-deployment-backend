from django.db import models
from users.models import User

class GeneralUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='general_profile')
    full_name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
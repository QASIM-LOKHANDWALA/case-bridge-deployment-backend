from django.db import models
from django.utils import timezone
from users.models import User
from clients.models import GeneralUserProfile

class LawyerProfile(models.Model):
    SPECIALIZATION_CHOICES = (
        ('criminal', 'Criminal Law'),
        ('civil', 'Civil Law'),
        ('corporate', 'Corporate Law'),
        ('family', 'Family Law'),
        ('intellectual_property', 'Intellectual Property Law'),
        ('general', 'General Practice')    
    )
    
    EXPERIENCE_CHOICES = (
        ('0-2', '0-2 years'),
        ('3-5', '3-5 years'),
        ('6-10', '6-10 years'),
        ('11-15', '11-15 years'),
        ('16+', '16+ years'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lawyer_profile')
    full_name = models.CharField(max_length=255)
    bar_registration_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=255, choices=SPECIALIZATION_CHOICES, default='general')
    experience_years = models.CharField(max_length=100, choices=EXPERIENCE_CHOICES)
    location = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='lawyer_pics/', blank=True, null=True)
    rating = models.FloatField(default=0.0)
    cases_won = models.IntegerField(default=0)
    clients_served = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class LawyerDocuments(models.Model):
    lawyer = models.OneToOneField(LawyerProfile, on_delete=models.CASCADE, related_name="documents")
    uploaded = models.BooleanField(default=False)
    photo_id = models.FileField(upload_to="photo_id/", blank=True, null=True)
    cop = models.FileField(upload_to="cop/", blank=True, null=True)
    
class LawyerRating(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(6)]

    user = models.ForeignKey(GeneralUserProfile, on_delete=models.CASCADE, related_name='given_ratings')
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE, related_name='received_ratings')
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lawyer')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.full_name} rated {self.lawyer.full_name}: {self.rating}'


class LegalCase(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
        ('on_hold', 'On Hold'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )

    title = models.CharField(max_length=255)
    client = models.ForeignKey(GeneralUserProfile, on_delete=models.CASCADE, related_name='legal_cases')
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE, related_name='legal_cases')
    court = models.CharField(max_length=255)
    case_number = models.CharField(max_length=50, unique=True)
    next_hearing = models.DateField()
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default='medium')
    last_update = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.case_number})"

class CaseDocument(models.Model):
    legal_case = models.ForeignKey('LegalCase', on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    document = models.FileField(upload_to='case_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} for {self.legal_case.case_number}"
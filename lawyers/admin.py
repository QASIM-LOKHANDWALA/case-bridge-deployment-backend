from django.contrib import admin
from .models import LawyerProfile, LegalCase, LawyerDocuments, CaseDocument

admin.site.register(LawyerProfile)
admin.site.register(LawyerDocuments)
admin.site.register(LegalCase)
admin.site.register(CaseDocument)
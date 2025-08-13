from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.LawyerListView.as_view(), name='lawyer-list'),
    path('detail/<int:user_id>/', views.LawyerDetailView.as_view(), name='lawyer-detail'),
    path('clients/<int:lawyer_id>/', views.get_lawyer_clients, name='lawyer-clients'),
    path('appointments/', views.LawyerAppointmentsView.as_view(), name='lawyer-appointments'),
    path('cases/', views.LawyerCasesView.as_view(), name='lawyer-cases'),
    path('cases/<int:case_id>/upload-document/', views.UploadCaseDocumentView.as_view(), name='upload-case-document'),
    path('documents/', views.LawyerDocumentUploadView.as_view(), name='lawyer-document-upload'),
    path('rate/', views.RateLawyerView.as_view(), name='rate-lawyer'),
    path('check-lawyer-rating/', views.GetLawyerRatingView.as_view(), name='check-lawyer-rating'),
    path('update-profile/', views.UpdateLawyerProfileView.as_view(), name='update-lawyer-profile'),
]

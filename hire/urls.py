from django.urls import path
from . import views

urlpatterns = [
    path('lawyer/<int:lawyer_id>/', views.HireLawyerView.as_view(), name='hire-lawyer'),
    path('<int:hire_id>/respond/', views.RespondToHireRequestView.as_view(), name='respond-hire'),
    path('client/hire-requests/', views.ClientHireRequestsView.as_view(), name='client-hire-requests'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('schedule-appointment/', views.ScheduleAppointmentView.as_view(), name='schedule-appointment'),
    path('',  views.LawyerAppointmentsView.as_view(), name='lawyer-appointments'),
    path('client/', views.ClientAppointmentsView.as_view(), name='client-appointments'),
    path('<int:appointment_id>/status/',  views.UpdateAppointmentStatusView.as_view(), name='update-appointment-status'),
    path('<int:appointment_id>/delete/',  views.DeleteAppointmentView.as_view(), name='delete-appointment'),
]

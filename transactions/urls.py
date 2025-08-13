from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreatePaymentRequestView.as_view(), name='create_payment_request'),
    path('<int:transaction_id>/delete/', views.DeletePaymentRequestView.as_view(), name='delete-payment-request'),
    path('', views.LawyerTransactionsView.as_view(), name='get_lawyer_transactions'),
    path('stats/', views.LawyerPaymentStatsView.as_view(), name='get_payment_stats'),
    path('<int:id>/update/', views.UpdateTransactionStatusView.as_view(), name='update_transaction_status'),
    path('clients/payment-requests/', views.ClientPaymentRequestsView.as_view(), name='get_client_payment_requests'),
    path('clients/payment-requests/stats/', views.ClientPaymentStatsView.as_view(), name='get_client_payment_stats'),
    path('clients/payments/<int:id>/pay/', views.ProcessPaymentView.as_view(), name='process_payment'),
    path('verify-payment/', views.verify_razorpay_payment, name='verify-razorpay-payment'),
]
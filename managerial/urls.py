from django.urls import path
from . import views

app_name = 'managerial'

urlpatterns = [
    path('manage_dashboard/', views.dashboard_view, name='dashboard'),
    path('pay/<int:commission_id>/', views.pay_commission_view, name='pay_commission'),
    path('mpesa/callback/', views.mpesa_callback_view, name='mpesa_callback'),
    path('pending-approvals/', views.pending_approvals_view, name='pending_approvals'),
    path('approvals/', views.pending_approvals_view, name='approvals'),
]

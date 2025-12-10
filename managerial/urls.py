from django.urls import path
from . import views

app_name = 'managerial'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('pay/<int:commission_id>/', views.pay_commission_view, name='pay_commission'),
    path('callback/', views.mpesa_callback_view, name='callback'),
    path('approvals/', views.pending_approvals_view, name='approvals'),
]

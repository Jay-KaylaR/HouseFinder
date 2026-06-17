from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.views.generic import RedirectView

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout' ),
    path('profile/', views.profile_view, name='profile'), 
    path("renter/renter_dashboard/", views.renter_dashboard, name="renter_dashboard"),
    path("manage/manage_dashboard/", views.manager_dashboard, name="manage_dashboard"), 
    path('admin/admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path("admin-dashboard/users/", views.users_list_view, name="users_list"),
    path("admin-dashboard/properties/", views.properties_list_view, name="properties_list"),
    # Password reset 
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(),name='password_reset_confirm' ), 
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('password-reset/', views.forgot_password_view, name='forgot_password'),  
    path('reset-password/<uidb64>/<token>/', views.reset_password_view, name='reset_password'),
    path('change-password/', views.change_password_view, name='change_password'),
    # FAVICON
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
]

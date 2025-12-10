from django.urls import path
from . import views

app_name = 'main'
urlpatterns = [
    path('', views.home_view, name='home'),
    path('listings/', views.listings_view, name='listings'),
    path('guides/', views.guides_view, name='guides'),
    path('lifestyle/', views.lifestyle_view, name='lifestyle'),
    path('contact/', views.contact_view, name='contact'),
]

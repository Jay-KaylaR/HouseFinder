from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.listings_view, name='listing'),
    path('my-properties/', views.my_properties_view, name="my_properties"),
    path('create/', views.create_property_view, name='create'),
    path('<slug:slug>/', views.property_detail_view, name='detail'),
    path('<int:pk>/edit/', views.edit_property_view, name='edit'),
    path('<int:pk>/delete/', views.delete_property_view, name='delete'),
    path('<int:pk>/inquiry/', views.send_inquiry_view, name='inquiry'),
]


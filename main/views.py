from django.shortcuts import render
from properties.models import Property

def home_view(request):
    featured_properties = Property.objects.filter(approved=True, is_featured=True)[:6]
    return render(request, 'home.html', {'featured_properties': featured_properties})

def listings_view(request):
    # This can redirect to properties app or render its own template
    return render(request, 'listings.html')

def guides_view(request):
    return render(request, 'guides.html')

def lifestyle_view(request):
    return render(request, 'lifestyle.html')

def contact_view(request):
    return render(request, 'contact.html')

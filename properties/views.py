from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Property, PropertyImage, Inquiry, Category
from .forms import PropertyForm

User = get_user_model()

# Create your views here.
def home_view(request):
    '''Homepage: show featured properties'''
    # capture approved/featured properties
    properties = Property.objects.filter(approved=True, is_featured=True)[:6]
    # search functionality
    query = request.GET.get('q')
    if query:
        properties = Property.objects.filter(
            Q(title__icontains=query) | Q(location__icontains=query) | Q(description__icontains=query),
            approved=True,
           
        )
    
    # simple pagination for featured
    paginator = Paginator(properties, 6)
    page_number = request.GET.get('page')
    featured_properties = paginator.get_page(page_number)
    
    return render(request, 'home.html', {
        'featured_properties': featured_properties,
        'query': query
    })

def listings_view(request):
    '''Public property listings with filters'''
    properties = Property.objects.filter(approved=True)
    query = request.GET.get('q')
    if query:
        properties = properties.filter(
            Q(title__icontains=query) | Q(location__icontains=query)
        )
    
    # Filter by status, category, price
    status = request.GET.get('status')
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if status:
        properties = properties.filter(status=status)
    if category:
        properties = properties.filter(category__name__icontains=category)
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
    
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    property_list = paginator.get_page(page_number)
    
    return render(request, 'listings.html', {
        'properties': property_list,
        'query': query
    })

@login_required
def create_property_view(request):
    '''Property managers create listings'''
    if not request.user.is_manager():
        messages.error(request, "Only property managers can create listings")
        return redirect('main:home')
        
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.manager = request.user
            property.save()
            messages.success(request, 'Property listed successfully! Awaiting admin approval.')
            return redirect('properties:detail', slug=property.slug)
    else:
        form = PropertyForm()
    
    return render(request, 'properties/create.html', {'form': form})

@login_required
def my_properties_view(request):
    '''Manager sees their own properties'''
    if not request.user.is_manager():
        messages.error(request, "Access denied")
        return redirect('main:home')
        
    properties = Property.objects.filter(manager=request.user)
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    my_properties = paginator.get_page(page_number)
    
    return render(request, 'properties/my_properties.html', {
        'properties': my_properties
    })

def property_detail_view(request, slug):
    '''Public property detail page'''
    property = get_object_or_404(Property, slug=slug, approved=True)
    
    # Increment views
    property.views_count += 1
    property.save(update_fields=['views_count'])
    
    # Check if user can contact (for inquiry form)
    can_contact = True
    if not request.user.is_authenticated:
        can_contact = False
    images = property.images.all()

    return render(request, 'properties/detail.html', {
        'property': property,
        'can_contact': can_contact,
        'images': images,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    })

@login_required
def edit_property_view(request, pk):
    '''Edit own properties (managers only)'''
    property = get_object_or_404(Property, pk=pk, manager=request.user)
    
    if not property.can_edit(request.user):
        messages.error(request, "You cannot edit this property.")
        return redirect('properties:my_properties')
        
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            messages.success(request, "Property updated successfully")
            return redirect("properties:detail", slug=property.slug)
    else:
        form = PropertyForm(instance=property)
    
    return render(request, 'properties/edit.html', {
        'form': form, 
        'property': property
    })

@login_required
def delete_property_view(request, pk):
    '''Delete own properties'''
    property = get_object_or_404(Property, pk=pk, manager=request.user)
    
    if not property.can_delete(request.user):
        messages.error(request, "You cannot delete this property")
        return redirect("properties:my_properties")
    
    if request.method == "POST":
        property.delete()
        messages.success(request, "Property deleted successfully")
        return redirect("properties:my_properties")
    
    return render(request, 'properties/delete.html', {
        'property': property
    })

@login_required
def send_inquiry_view(request, pk):
    '''Renters send inquiries to managers'''
    property = get_object_or_404(Property, pk=pk, approved=True)
    
    if request.method == "POST":
        message = request.POST.get('message')
        Inquiry.objects.create(
            property=property,
            user=request.user,
            message=message
        )
        messages.success(request, "Inquiry sent successfully! Manager will contact you soon.")
        return redirect("properties:detail", slug=property.slug)
    
    return render(request, 'properties/inquiry.html', {'property': property})

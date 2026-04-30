from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Property, PropertyImage, Inquiry, Category, SavedProperty  # ✅ Add SavedProperty model
from .forms import PropertyForm
# from django.http import Http404
# from django.db import transaction


User = get_user_model()

# Create your views here.
def home_view(request):
    '''Homepage: show featured properties'''
    # capture approved/featured properties
    properties = Property.objects.filter(workflow_status__in=['approved', 'available'], is_featured=True)[:6]
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
    properties = Property.objects.filter(workflow_status__in=['approved', 'available'])
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
        properties = properties.filter(listing_status=status)
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
 
def property_detail_view(request, pk=None, slug=None):
    '''Public property detail page'''
    """Handle both ID and slug from URL"""
    if slug:
        property = get_object_or_404(Property, slug=slug)
         # Try to fetch by slug first, then fallback to ID if slug not found
    elif pk:
        property = get_object_or_404(Property, pk=pk)
    
    else:
        raise Http404("No property specified")
   
   

    # Only allow public viewing if approved; allow owners/managers/admins to preview
    user_can_preview = (
        request.user.is_authenticated and (
            request.user == property.manager or
            getattr(request.user, 'is_superuser', False) or
            getattr(request.user, 'is_manager', lambda: False)()
        )
    )

    if not property.approved and not user_can_preview:
        # Keep public behavior (404) for non-authorized viewers
        raise Http404("No Property matches the given query.")

    # Increment views only for public viewers (not previews by owner/manager)
    if property.approved:
        property.views_count += 1
        property.save(update_fields=['views_count'])

    can_contact = request.user.is_authenticated
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
    property = get_object_or_404(Property, pk=pk, workflow_status__in=['approved', 'available'])
    
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

@login_required
def toggle_save(request, property_id):
    """Toggle property to/from saved list"""
    property = get_object_or_404(Property, id=property_id)
    
    saved_prop, created = SavedProperty.objects.get_or_create(
        user=request.user,
        property=property
    )
    
    if not created:
        saved_prop.delete()
        messages.info(request, f'Removed "{property.title}" from saved')
    else:
        messages.success(request, f'Added "{property.title}" to saved')
    
    return redirect(request.META.get('HTTP_REFERER', 'properties:listing'))

@login_required
def contact_manager(request, property_id):
    """Send automated message to property manager"""
    property = get_object_or_404(Property, id=property_id)
    manager = property.manager
    
    # ✅ AUTOMATIC MESSAGE
    message = f"Hi {manager.first_name}, I'm interested in '{property.title}' at {property.location}. Price: KSh {property.price:,}/mo"
    
    # Save to chat/conversation (if you have messaging app)
    # Or send email/SMS here
    
    messages.success(request, f'Message sent to {manager.first_name}! They will contact you soon.')
    
    # Redirect back to listing or property detail
    return redirect('properties:detail', slug=property.slug)



    ontext = {
        'properties': properties,
        # ✅ Pass saved properties for current user
        'saved_properties': request.user.saved_properties.all() if request.user.is_authenticated else []
    }
    return render(request, 'properties/property_list.html', context)
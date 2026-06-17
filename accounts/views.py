from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.db.models import Sum
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import User
from properties.models import Property, SavedProperty
from managerial.models import Commission
from messaging.models import Conversation  # Uncomment if messaging app is created
from .models import ScheduledVisit

from django.contrib.auth import get_user_model
from django.shortcuts import render

User = get_user_model()


@login_required
def properties_list_view(request):
    properties = Property.objects.all().order_by("-id")
    return render(request, "properties_list.html", {"properties": properties})

@login_required
def admin_dashboard(request):
    if not (request.user.is_superuser or getattr(request.user, 'user_type', '') == 'admin'):
        return redirect('main:home')
    if request.method == 'POST':
        action = request.POST.get('action')
        property_id = request.POST.get('property_id')
        
        if property_id:
            prop = get_object_or_404(Property, id=property_id)
            if action == 'approve':
                prop.workflow_status = 'approved'
                prop.approved = True  # ✅ Update both fields
                prop.save()
                messages.success(request, f'✅ "{prop.title}" approved successfully!')
            elif action == 'reject':
                prop.workflow_status = 'rejected'
                prop.approved = False
                prop.save()
                messages.success(request, f'❌ "{prop.title}" rejected!')
            
            return redirect('accounts:admin_dashboard')  # ✅ Reload page


    context = {
        'total_users': User.objects.count(),
        'managers_count': User.objects.filter(user_type='manager').count(),
        'renters_count': User.objects.filter(user_type='renter').count(),
        'total_properties': Property.objects.count(),
        'active_properties': Property.objects.filter(workflow_status__in=['approved', 'available']).count(),
        'pending_properties': Property.objects.filter(workflow_status='pending').count(),
        'rented_properties': Property.objects.filter(listing_status='rented').count(),
        'pending_properties_list': Property.objects.filter(workflow_status='pending')[:8],
        'monthly_revenue': 1250000,  # Calculate from commissions
        'total_commission': Commission.objects.aggregate(total=Sum('amount'))['total'] or 0,
        'pending_commission': Commission.objects.filter(paid=False).aggregate(total=Sum('amount'))['total'] or 0,
    }
    return render(request, 'accounts/admin/admin_dashboard.html', context)


def register_view(request):
    # validate if the user is already authenticated 
    if request.user.is_authenticated:
        return redirect('main:home')
    
    if request.method == 'POST':  # user wants to register
        form = UserRegistrationForm(request.POST, request.FILES)
        # if user has filled in all required inputs
        if form.is_valid():
            user = form.save()  # submits our user to our db
            # Auto-approve regular users, pending for admin/manager
            if user.user_type == 'renter':
                user.is_verified = True
                user.approval_status = 'approved'
            else:
                messages.warning(request, f'{user.username} registered as {user.user_type.title()}. Awaiting admin approval.')

            user.save()

            login(request, user)  # calls the login action
            messages.success(request, f'Welcome {user.username}! Your account has been successfully created!')
            return redirect('main:home')
    else:
        form = UserRegistrationForm()  # default http method here is GET

    return render(request, 'register.html', {'form': form})


def login_view(request):
    # validate if the user is already authenticated
    if request.user.is_authenticated:
        return redirect('main:home')
    form = UserLoginForm(request)  # default http method here is GET
    if request.method == 'POST':  # user wants to login
        form = UserLoginForm(request, data=request.POST)
        # if user has filled in all required inputs
        if form.is_valid():
            # pick up entries for username and password
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Django method authenticate to authenticate and login my user
            user = authenticate(request, username=username, password=password)  # queries db looking for the user with mentioned credentials
            # is the user found not in db
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back {username}')
                # Redirect based on role
                role = getattr(user, 'user_type', '')
                if user.is_superuser or getattr(user, 'user_type', '') == 'admin':
                    return redirect('accounts:admin_dashboard')
                elif getattr(user, 'user_type', '') == 'manager':
                    return redirect('accounts:manage_dashboard')
                elif getattr(user, 'user_type', '') == 'renter':
                    return redirect('accounts:renter_dashboard')
                return redirect('main:home')
            else:
                form = UserLoginForm(request)  # default http method here is GET

    return render(request, 'login.html', {'form': form})


# logout -> check if our user is logged in - @login_required
# if user is logged in then allow this action to run for the user
@login_required
def logout_view(request):
    # DESTROY next parameter completely
    if 'next' in request.GET:
        # Clear malicious next parameter
        request.GET._mutable = True
        del request.GET['next']
        request.GET._mutable = False

    # Destroy session completely
    request.session.flush()
    request.session.clear_expired()
    logout(request)

    # Clean redirect - NO next parameter
    response = redirect('accounts:login')
    response.delete_cookie('sessionid')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate'

    messages.info(request, 'You have logged out!')
    return redirect('main:home')

    # messages.success(request, 'Logged out successfully!')
    # return response
    # messages.info(request, 'You have logged out successfully!')
    # return response  # FIXED: Return response, not redirect("main:home")


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Profile saved successfully")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
        
    return render(request, 'accounts/profile.html' , {'form' : form})

@login_required
def renter_dashboard(request):
    if getattr(request.user, "user_type", "") != "renter":
        messages.error(request, "Renters only")
        return redirect("main:home")

    approved_properties = Property.objects.filter(
        workflow_status__in=['approved', 'available'], 
        listing_status='rent'  # For rent only
    ).order_by('-created_at')[:12]  # Latest 12 approved properties

    # SavedProperty stores saved uses; Property has no saved_by field.
    from properties.models import SavedProperty
    saved_properties = Property.objects.filter(id__in=SavedProperty.objects.filter(user=request.user).values_list('property_id', flat=True))
    # saved_properties = SavedProperty.objects.filter(user=request.user)
    
    # scheduled_visits = ScheduledVisit.objects.filter(user=request.user)  # use renter field on ScheduledVisit
    scheduled_visits = ScheduledVisit.objects.filter(renter=request.user)
   
    # Conversation messaging 
    try:
        from messaging.models import Conversation
        conversations = Conversation.objects.filter(participants=request.user)
        unread_messages = sum(c.unread_count for c in conversations)
        active_chats = sum(1 for c in conversations if c.unread_count > 0)
    except ImportError:
        conversations = []
        unread_messages = 0
        active_chats = 0

    context = {
        "saved_properties": saved_properties,  # Replace with actual saved properties if you have that model
        "conversations": conversations,
        "unread_messages": unread_messages,
        "active_chats": active_chats,
        "scheduled_visits": scheduled_visits,
    }
    return render(request, "accounts/renter/renter_dashboard.html", context)

@login_required
def manager_dashboard(request):
    if getattr(request.user, "user_type", "") != "manager":
        return redirect("main:home")
    
    properties = Property.objects.filter(manager=request.user).order_by('-created_at')
    
    context = {
        'properties_count': properties.count(),
        'pending_count': properties.filter(workflow_status='pending').count(),
        'approved_count': properties.filter(workflow_status__in=['approved', 'available']).count(),
        'recent_properties': properties[:6],
        'total_views': sum(p.views_count for p in properties),
    }
    return render(request, 'accounts/manage/manage_dashboard.html', context)


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Security: never reveal if email exists
            messages.info(request, 'If email exists, check inbox/spam.')
            return render(request, 'accounts/forgot_password.html')
        
        # Generate token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode()).decode()
        
        # Build reset URL
        current_site = get_current_site(request)
        reset_url = f"http://{current_site.domain}/accounts/reset-password/{uid}/{token}/"

        # Email
        current_site = get_current_site(request)
        reset_url = f"{current_site.domain}/accounts/reset-password/{uid}/{token}/"
        
        send_mail(
            'HouseFinder Password Reset',
            f'Reset your password: {reset_url}\nValid for 1 hour.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        messages.success(request, 'Reset link sent! Check your email.')
        return redirect('accounts:login')
    
    return render(request, 'accounts/forgot_password.html')


def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Invalid reset link.')
        return redirect('accounts:login')
    
    user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 == password2:
                user.set_password(password1)
                user.save()
                messages.success(request, 'Password reset successful!')
                login(request, user)
                return redirect('main:home')
            else:
                messages.error(request, 'Passwords do not match.')
        
        return render(request, 'accounts/password_reset.html', {'user': user})
    else:
        messages.error(request, 'Reset link expired or invalid.')
        return redirect('accounts:login')



@login_required
def change_password_view(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # Check current password
        if not check_password(current_password, request.user.password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('accounts:profile')
        
        # Check new passwords match
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return redirect('accounts:profile')
        
        # Check password strength (minimum 8 chars)
        if len(new_password1) < 8:
            messages.error(request, 'New password must be at least 8 characters.')
            return redirect('accounts:profile')
        
        # Update password
        request.user.set_password(new_password1)
        request.user.save()
        messages.success(request, 'Password changed successfully!')
        return redirect('accounts:profile')
    
    return redirect('accounts:profile')


def users_list_view(request):
    users = User.objects.all().order_by("-date_joined")
    return render(request, "users_list.html", {"users": users})


@login_required
def saved_properties_view(request):
    saved_items = Property.objects.filter(id__in=SavedProperty.objects.filter(user=request.user).values_list('property_id', flat=True))
    context = {
        'saved_properties': saved_items
    }
    return render(request, 'saved_properties.html', context)


class CustomPasswordResetView(PasswordResetView):
    # interface change 
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done') # this will launch the confirm view


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    # interface change 
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete') # this will launch when password is update

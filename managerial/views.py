from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from properties.models import Property  # ✅ From properties app
from managerial.models import Commission
from accounts.models import User
from django.utils import timezone 


@login_required
def dashboard_view(request):
    '''Admin/Manager dashboard with analytics'''
    if request.user.is_superuser:
        # Admin dashboard
        # Handle approve/reject POSTs coming from the dashboard list
        if request.method == 'POST':
            action = request.POST.get('action')
            property_id = request.POST.get('property_id')
            if not property_id:
                messages.error(request, 'No property specified')
                return redirect('accounts:manager_dashboard')

            prop = get_object_or_404(Property, id=property_id)
            if action == 'approve':
                prop.workflow_status = 'approved'
                prop.save()
                messages.success(request, f'Property "{prop.title}" approved')
            elif action == 'reject':
                prop.workflow_status = 'rejected'
                prop.save()
                messages.success(request, f'Property "{prop.title}" rejected')
            else:
                messages.error(request, 'Unknown action')

            return redirect('accounts:manager_dashboard')

        total_properties = Property.objects.count()
        pending_properties = Property.objects.filter(approved=False).count()
        total_users = User.objects.count()
        total_managers = User.objects.filter(user_type='manager').count()
        total_commissions = Commission.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        paid_commissions = Commission.objects.filter(paid=True).aggregate(Sum('amount'))['amount__sum'] or 0

        context = {
            'total_properties': total_properties,
            'pending_properties': pending_properties,
            'total_users': total_users,
            'total_managers': total_managers,
            'total_commissions': total_commissions,
            'paid_commissions': paid_commissions,
            # names expected by template
            'pending_properties_list': Property.objects.filter(approved=False)[:10],
        }
        return render(request, 'accounts/admin/admin_dashboard.html', context)
    
    elif request.user.is_manager():
        # Manager dashboard
        my_properties = Property.objects.filter(manager=request.user).count()
        pending_properties = Property.objects.filter(manager=request.user, workflow_status='pending').count()
        approved_properties = Property.objects.filter(manager=request.user, workflow_status__in=['approved', 'available']).count()
        commissions = Commission.objects.filter(manager=request.user)
        unpaid_commissions = commissions.filter(paid=False).count()
        total_views = sum(p.views_count or 0 for p in Property.objects.filter(manager=request.user))
        
        context = {
            'my_properties': my_properties,
            'pending_properties': pending_properties,  #
            'approved_properties': approved_properties,
            'commissions': commissions,
            'unpaid_commissions': unpaid_commissions,
            'total_views': total_views,
            'recent_properties': Property.objects.filter(manager=request.user).order_by('-created_at')[:6],
        }
        return render(request, 'accounts/manage/manage_dashboard.html', context)
    
    messages.error(request, "Access denied")
    return redirect('main:home')

@require_http_methods(["POST"])
@login_required
def pay_commission_view(request, commission_id):
    '''M-Pesa STK Push for commission payment'''
    if not request.user.is_manager():
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    commission = get_object_or_404(Commission, id=commission_id, manager=request.user)
    phone = request.POST.get('phone')
    
    if not phone:
        return JsonResponse({'error': 'Phone number required'}, status=400)
    
    # M-Pesa STK Push (simplified - integrate django-mpesa in production)
    try:
        # In production: Use django-mpesa or Daraja API
        # response = mpesa.stk_push(phone, str(commission.amount), f"Commission-{commission.id}")
        messages.success(request, f'M-Pesa STK Push sent to {phone} for KSh{commission.amount}. Please complete payment.')
        commission.phone_requested = phone  # Track requested phone
        commission.save()
        return JsonResponse({'status': 'success', 'message': 'Payment request sent'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt    
def mpesa_callback_view(request):
    '''M-Pesa callback endpoint'''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Parse M-Pesa callback
            if data.get('Body', {}).get('stkCallback', {}).get('ResultCode') == 0:
                # Payment successful
                tx_id = data['Body']['stkCallback']['CallbackMetadata'][1]['Value']
                amount = data['Body']['stkCallback']['CallbackMetadata'][0]['Value']
                
                # Update commission
                commission = Commission.objects.get(mpesa_tx_id=tx_id)
                commission.paid = True
                commission.paid_at = timezone.now()
                commission.save()
                
            return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Accepted'})
        except Exception as e:
            return JsonResponse({'ResultCode': 0, 'ResultDesc': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required
def pending_approvals_view(request):
    '''Admin approves properties'''
    if not request.user.is_superuser:
        messages.error(request, "Admin only")
        return redirect('accounts:admin_dashboard')
    
    pending = Property.objects.filter(workflow_status='pending')
    return render(request, 'accounts/admin/pending_approvals.html', {
        'pending_properties': pending
    })


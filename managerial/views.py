from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from managerial.models import Property, Commission
from accounts.models import User

@login_required
def dashboard_view(request):
    '''Admin/Manager dashboard with analytics'''
    if request.user.is_superuser:
        # Admin dashboard
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
            'pending_approvals': Property.objects.filter(approved=False)[:10],
        }
        return render(request, 'manage/admin_dashboard.html', context)
    
    elif request.user.is_manager():
        # Manager dashboard
        my_properties = Property.objects.filter(manager=request.user).count()
        approved_properties = Property.objects.filter(manager=request.user, approved=True).count()
        commissions = Commission.objects.filter(manager=request.user)
        unpaid_commissions = commissions.filter(paid=False).count()
        
        context = {
            'my_properties': my_properties,
            'approved_properties': approved_properties,
            'commissions': commissions,
            'unpaid_commissions': unpaid_commissions,
        }
        return render(request, 'manage/manager_dashboard.html', context)
    
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
        messages.success(request, f'M-Pesa STK Push sent to {phone}. Please complete payment.')
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
        return redirect('manage:dashboard')
    
    pending = Property.objects.filter(approved=False)
    return render(request, 'manage/pending_approvals.html', {
        'pending_properties': pending
    })

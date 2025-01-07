from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as auth_logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.utils.timezone import now
from django.utils import timezone
from django.db.models import Sum
from django.http import JsonResponse
from django.core.mail import send_mail
from datetime import timedelta
import json
import os
import uuid

from .models import User, Event, Membership
from .forms import UserForm, EventForm, AccountEditForm, MembershipApplicationForm
from .permissions import adm_req, stf_req
from supabase import create_client, Client

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def home(request):
    if request.user.is_authenticated:
        if request.user.admin:
            return redirect('adm')
        elif request.user.staff:
            return redirect('stf')
        return redirect('usr')
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()  # This will save the user with the hashed password
            messages.success(request, 'User  successfully created.')
            return redirect('login')
        else:
            # Print form errors for debugging
            print(form.errors)  # This will show validation errors in the console
    else:
        form = UserForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                request.session['email'] = email
                
                next_url = request.GET.get('next', None)
                if next_url and 'stf' in next_url and user.staff:
                    return redirect('stf')
                elif next_url and 'adm' in next_url and user.admin:
                    return redirect('adm')
                
                if user.admin:
                    return redirect('adm')
                elif user.staff:
                    return redirect('stf')
                else:
                    return redirect('usr')
            else:
                messages.error(request, 'Invalid password')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
    return render(request, 'login.html')

@login_required
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')

@login_required
def adm_view(request):
    current_date = timezone.now().date()
    
    context = {
        'total_users': User.objects.count(),
        'total_events': Event.objects.count(),
        'total_staff': User.objects.filter(staff=True).count(),
        'members': User.objects.all(),
        'membership_stats': {
            'total_members': Membership.objects.filter(status='active').count(),
            'pending_applications': Membership.objects.filter(status='pending').count(),
            'expiring_soon': Membership.objects.filter(
                status='active',
                end_date__lte=current_date + timedelta(days=30),
                end_date__gt=current_date
            ).count(),
            'expired': Membership.objects.filter(
                status='active',
                end_date__lt=current_date
            ).count(),
        },
        'recent_memberships': Membership.objects.all().order_by('-created_at')[:5],
        'events': Event.objects.order_by('start')[:5], 
    }
    return render(request, 'adm.html', context)

@login_required
def stf_view(request):
    current_date = timezone.now().date()
    
    context = {
        'total_users': User.objects.count(),
        'total_events': Event.objects.count(),
        'total_staff': User.objects.filter(staff=True).count(),
        'members': User.objects.all(),
        'membership_stats': {
            'total_members': Membership.objects.filter(status='active').count(),
            'pending_applications': Membership.objects.filter(status='pending').count(),
            'expiring_soon': Membership.objects.filter(
                status='active',
                end_date__lte=current_date + timedelta(days=30),
                end_date__gt=current_date
            ).count(),
            'expired': Membership.objects.filter(
                status='active',
                end_date__lt=current_date
            ).count(),
        },
        'recent_memberships': Membership.objects.all().order_by('-created_at')[:5]
    }
    return render(request, 'stf.html', context)

@login_required
def usr_view(request):
    user = request.user

    # Restrict access for admin and staff users
    if user.admin or user.staff:
        messages.error(request, 'Invalid access')
        return redirect('login')

    current_date = now().date()

    # Retrieve the current active or pending membership
    current_membership = Membership.objects.filter(
        user=user,
        status__in=['active', 'pending']
    ).first()

    # Calculate days remaining for active memberships
    days_remaining = 0
    if current_membership and current_membership.status == 'active' and current_membership.end_date:
        days_remaining = (current_membership.end_date - current_date).days

    # Build the context dictionary
    context = {
        'user': user,
        'user_events': Event.objects.filter(owner=user),
        'total_events': Event.objects.count(),
        'events_attended': Event.objects.filter(
            owner=user,
            end__lt=current_date
        ).count(),
        'membership': current_membership,
        'membership_status': 'active' if current_membership and current_membership.status == 'active' else 'inactive',
        'can_apply': not current_membership or current_membership.status == 'expired',
        'membership_history': Membership.objects.filter(user=user).order_by('-created_at'),
        'days_remaining': days_remaining,
    }

    return render(request, 'usr.html', context)

@login_required
def apply_membership(request):
    bucket_name = 'paymentproofs'  # Ensure this is your actual bucket name

    # Check if user already has a pending or active membership
    existing_membership = Membership.objects.filter(
        user=request.user,
        status__in=['pending', 'active']
    ).first()
    
    if existing_membership:
        if existing_membership.status == 'active':
            messages.info(request, 'You already have an active membership.')
        else:
            messages.info(request, 'You already have a pending application.')
        return redirect('membership_status')
    
    if request.method == 'POST':
        form = MembershipApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create a membership instance but don't save it yet
            membership = form.save(commit=False)
            membership.user = request.user
            membership.status = 'pending'
            membership.payment_status = 'pending'
            membership.save()

            # Handle the payment proof file
            payment_proof = request.FILES['payment_proof']
            # Generate a unique file name using UUID
            unique_file_name = f'payment_proofs/{request.user.uid}/{uuid.uuid4()}_{payment_proof.name}'  # Create a unique file path
            
            # Read the file content and upload it directly to Supabase
            file_content = payment_proof.read()  # Read the content of the InMemoryUploadedFile
            response = supabase.storage.from_(bucket_name).upload(unique_file_name, file_content)

            # Check the response
            if response and hasattr(response, 'data'):
                # Construct the full URL for the uploaded file
                full_url = f"https://mljsnqwcbdunemonnwif.supabase.co/storage/v1/object/public/paymentproofs/{unique_file_name}"
                membership.payment_proof = full_url  # Store the full URL in the database
                membership.save()  # Save the updated membership instance
                messages.success(request, 'Your membership application has been submitted.')
                return redirect('membership_status')
            else:
                # Handle the case where the upload failed
                messages.error(request, f'Failed to upload payment proof: {response.message if hasattr(response, "message") else "Unknown error"}')
        else:
            # Print form errors for debugging
            print(form.errors)

    else:
        form = MembershipApplicationForm()
    
    return render(request, 'membership/apply.html', {'form': form})
    
@login_required
def membership_status(request):
    membership = Membership.objects.filter(user=request.user).order_by('-created_at').first()
    return render(request, 'membership/status.html', {'membership': membership})

@login_required
@stf_req
def manage_memberships(request):
    memberships = Membership.objects.all().order_by('-created_at')
    context = {
        'memberships': memberships
    }
    return render(request, 'membership/manage.html', context)

@login_required
def membership_detail(request, mid):
    membership = get_object_or_404(Membership, mid=mid)
    
    # Check if the user is staff or admin
    if not request.user.is_staff and not request.user.is_admin:
        messages.error(request, 'You do not have permission to manage memberships.')
        return redirect('manage_memberships')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['approve', 'reject']:
            membership.status = 'active' if action == 'approve' else 'rejected'
            membership.payment_status = 'paid' if action == 'approve' else 'unpaid'
            membership.save()
            messages.success(request, f'Membership {action}d successfully.')
            return redirect('manage_memberships')
    
    return render(request, 'membership/detail.html', {'membership': membership})

@login_required
@stf_req
def verify_payment(request, mid):
    membership = get_object_or_404(Membership, mid=mid)
    
    if request.method == 'POST':
        verification_status = request.POST.get('verification_status')
        if verification_status in ['verified', 'rejected']:
            membership.payment_status = 'paid' if verification_status == 'verified' else 'unpaid'
            membership.verified_by = request.user
            membership.verified_at = timezone.now()
            membership.save()
            
            messages.success(request, f'Payment {verification_status} successfully.')
            
            # If payment is verified, automatically set membership as active
            if verification_status == 'verified':
                membership.status = 'active'
                membership.start_date = timezone.now().date()
                membership.end_date = membership.start_date + timedelta(days=365)
                membership.save()
                
                # Optionally, send email notification to user
                # send_membership_notification(membership, 'approved')
        
        return redirect('membership_detail', mid=mid)
    
    return render(request, 'membership/verify_payment.html', {'membership': membership})

@login_required
def membership_dashboard(request):
    # Get current date
    today = timezone.now().date()
    
    # Get all memberships with different statuses
    memberships = {
        'expiring_soon': Membership.objects.filter(
            status='active',
            end_date__lte=today + timedelta(days=30),
            end_date__gt=today
        ),
        'expired': Membership.objects.filter(
            status='active',
            end_date__lt=today
        ),
        'active': Membership.objects.filter(
            status='active',
            end_date__gt=today + timedelta(days=30)
        ),
        'pending': Membership.objects.filter(status='pending')
    }
    
    # Update expired memberships
    if request.method == 'POST' and request.POST.get('action') == 'update_status':
        for membership in memberships['expired']:
            membership.status = 'expired'
            membership.save()
            # Optionally, send notification for expired memberships
            # send_expired_notification(membership)
        messages.success(request, 'Membership statuses updated successfully')
        return redirect('membership_dashboard')
    
    context = {
        'memberships': memberships,
        'total_active': memberships['active'].count() + memberships['expiring_soon'].count(),
        'total_expired': memberships['expired'].count(),
        'total_pending': memberships['pending'].count(),
    }
    
    return render(request, 'membership/dashboard.html', context)

def send_membership_notification(membership, action):
    subject = f'Membership {action.title()}'
    message = f'''
    Dear {membership.user.full_name},
    
    Your membership has been {action}. 
    {'Your membership is now active until ' + membership.end_date.strftime("%B %d, %Y") if action == 'approved' else ''}
    
    Best regards,
    ICpEPHUB Team
    '''
    send_mail(
        subject,
        message,
        'noreply@icpephub.com',
        [membership.user.email],
        fail_silently=True,
    )

def send_expired_notification(membership):
    subject = 'Membership Expired'
    message = f'''
    Dear {membership.user.full_name},
    
    Your ICpEPHUB membership has expired. To continue accessing our services,
    please renew your membership.
    
    Best regards,
    ICpEPHUB Team
    '''
    send_mail(
        subject,
        message,
        'noreply@icpephub.com',
        [membership.user.email],
        fail_silently=True,
    )

@login_required
def event_list(request):
    events = Event.objects.all().order_by('start')
    return render(request, 'events/event_list.html', {'events': events})

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.owner = request.user
            event.save()
            messages.success(request, 'Event created successfully.')
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form})

@login_required
def edit_event(request, eid):
    event = get_object_or_404(Event, eid=eid)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully.')
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form, 'event': event})

@login_required
def delete_event(request, eid):
    event = get_object_or_404(Event, id=eid)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully.')
        return redirect('event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})

@login_required
@adm_req
def toggle_staff(request, uid):
    user = get_object_or_404(User, uid=uid)
    
    # Prevent admin from toggling their own staff status
    if user == request.user:
        messages.error(request, 'You cannot modify your own permissions.')
        return redirect('adm')
    
    # Toggle staff status
    user.staff = not user.staff
    user.save()
    
    action = 'added to' if user.staff else 'removed from'
    messages.success(request, f'{user.full_name} {action} staff.')
    
    return redirect('adm')

def setup(request):
    if User.objects.exists():
        messages.info(request, 'Setup already completed.')
        return redirect('login')  # Redirect to login if setup is already done

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['pwd'])  # Ensure you set the password
            user.admin = True  # Set as admin if this is the initial setup
            user.staff = True  # Set as staff if this is the initial setup
            user.save()
            messages.success(request, 'Admin account created successfully.')
            return redirect('login')  # Redirect to login after setup
    else:
        form = UserForm()
    return render(request, 'setup.html', {'form': form})

@login_required
@adm_req
def toggle_admin(request, uid):
    user = get_object_or_404(User, uid=uid)
    
    # Prevent admin from toggling their own admin status
    if user == request.user:
        messages.error(request, 'You cannot modify your own admin status.')
        return redirect('adm')
    
    # Toggle admin status
    user.admin = not user.admin
    # If making admin, also make staff
    if user.admin:
        user.staff = True
    user.save()
    
    action = 'added to' if user.admin else 'removed from'
    messages.success(request, f'{user.full_name} {action} administrators.')
    
    return redirect('adm')

@login_required
def account(request):
    if request.method == 'POST':
        form = AccountEditForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            new_password = request.POST.get('new_password')
            if new_password:
                current_password = request.POST.get('current_password')
                if request.user.check_password(current_password):
                    user.set_password(new_password)
                    messages.success(request, 'Password updated successfully.')
                else:
                    messages.error(request, 'Current password is incorrect.')
                    return render(request, 'account.html', {'form': form})
            user.save()
            messages.success(request, 'Account updated successfully.')
            # Re-authenticate if password was changed
            if new_password:
                user = authenticate(email=user.email, password=new_password)
                if user:
                    login(request, user)
            return redirect('account')
    else:
        form = AccountEditForm(instance=request.user)

    context = {
        'form': form,
        'user': request.user,
        'membership': Membership.objects.filter(user=request.user).order_by('-created_at').first()
    }

    return render(request, 'account.html', context)

@login_required
def account_delete(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        
        # Verify password before deletion
        if request.user.check_password(password):
            # Store user info for message
            email = request.user.email
            
            # Delete the user account
            request.user.delete()
            
            # Log out the user
            auth_logout(request)
            
            messages.success(request, f'Account {email} has been permanently deleted.')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect password. Account deletion cancelled.')
            return redirect('account')
    
    # If not POST, redirect to account page
    return redirect('account')

def about(request):
    context = {
        'organization_name': 'ICpEPHUB',
        'description': 'Institute of Computer Engineers of the Philippines HUB',
        'mission': 'To promote excellence in computer engineering education and practice.',
        'vision': 'To be the leading organization for computer engineers in the Philippines.',
        'contact_email': 'contact@icpephub.com',
    }
    return render(request, 'about.html', context)

@login_required
@require_POST
def save_theme(request):
    theme = request.POST.get('theme', 'light')
    request.user.theme = theme  # Save the theme to the user model
    request.user.save()  # Save the user instance
    request.session['theme'] = theme  # Save in session for immediate use

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'theme': theme})

    return redirect('settings')

@login_required
@stf_req
def membership_delete(request, mid):
    membership = get_object_or_404(Membership, mid=mid)
    
    if request.method == 'POST':
        # Store info for message
        user_name = membership.user.full_name
        
        # Delete payment proof file if it exists
        if membership.payment_proof:
            if os.path.exists(membership.payment_proof.path):
                os.remove(membership.payment_proof.path)
        
        # Delete the membership record
        membership.delete()
        
        messages.success(request, f'Membership record for {user_name} has been deleted.')
        return redirect('manage_memberships')
    
    return render(request, 'membership/delete_confirm.html', {'membership': membership})

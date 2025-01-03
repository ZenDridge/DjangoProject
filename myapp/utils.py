from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from .models import Membership

def check_membership_status():
    # Find memberships expiring in 30 days
    expiring_soon = Membership.objects.filter(
        status='active',
        end_date__lte=timezone.now().date() + timedelta(days=30),
        end_date__gt=timezone.now().date()
    )
    
    # Find expired memberships
    expired = Membership.objects.filter(
        status='active',
        end_date__lt=timezone.now().date()
    )
    
    # Send notifications for expiring memberships
    for membership in expiring_soon:
        days_left = (membership.end_date - timezone.now().date()).days
        send_expiry_notification(membership, days_left)
    
    # Update status for expired memberships
    for membership in expired:
        membership.status = 'expired'
        membership.save()
        send_expired_notification(membership)

def send_expiry_notification(membership, days_left):
    subject = 'Membership Expiring Soon'
    message = f'''
    Dear {membership.user.full_name},
    
    Your ICpEPHUB membership will expire in {days_left} days on {membership.end_date.strftime("%B %d, %Y")}.
    Please renew your membership to continue enjoying our services.
    
    Best regards,
    ICpEPHUB Team
    '''
    send_mail(subject, message, 'noreply@icpephub.com', [membership.user.email], fail_silently=True)

def send_expired_notification(membership):
    subject = 'Membership Expired'
    message = f'''
    Dear {membership.user.full_name},
    
    Your ICpEPHUB membership has expired. To continue accessing our services,
    please renew your membership.
    
    Best regards,
    ICpEPHUB Team
    '''
    send_mail(subject, message, 'noreply@icpephub.com', [membership.user.email], fail_silently=True) 
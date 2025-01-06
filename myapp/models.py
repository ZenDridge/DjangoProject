from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid
from .managers import UserMgr


class User(AbstractBaseUser, PermissionsMixin):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, default='')
    middle_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    sid = models.CharField(
        max_length=10, 
        unique=True, 
        help_text='Format: ##-UR-####'
    )
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    joined = models.DateTimeField(default=timezone.now)

    objects = UserMgr()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'middle_name', 'last_name', 'sid']

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"

    @property
    def is_active(self):
        return self.active

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_superuser(self):
        return self.admin

    class Meta:
        db_table = 'myapp_user'
        verbose_name = 'user'
        verbose_name_plural = 'users'


class Event(models.Model):
    eid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    desc = models.TextField(blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'myapp_event'
        ordering = ['start']

class Participant(models.Model):
    event = models.ForeignKey(Event, related_name='participants', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


class Membership(models.Model):
    MEMBERSHIP_STATUS = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('rejected', 'Rejected')
    )

    PAYMENT_STATUS = (
        ('unpaid', 'Unpaid'),
        ('pending', 'Pending Verification'),
        ('paid', 'Paid')
    )

    mid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    payment_proof = models.ImageField(upload_to='payment_proofs/', null=True, blank=True)
    payment_name = models.CharField(max_length=100, null=True, blank=True)
    payment_phone = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.status}"

    class Meta:
        db_table = 'myapp_membership'
        ordering = ['-created_at']

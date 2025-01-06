from django import forms
from django.core.exceptions import ValidationError
from .models import User, Event, Membership
import re

class UserForm(forms.ModelForm):
    pwd = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    pwd2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User  # Ensure this is your custom user model
        fields = ('first_name', 'middle_name', 'last_name', 'email', 'sid', 'pwd', 'pwd2')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Middle Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'sid': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '##-UR-####'
            })
        }

    def clean_sid(self):
        sid = self.cleaned_data.get('sid')
        if not re.match(r'^\d{2}-UR-\d{4}$', sid):
            raise ValidationError('ID must be in ##-UR-#### format')
        return sid

    def clean_pwd2(self):
        pwd = self.cleaned_data.get('pwd')
        pwd2 = self.cleaned_data.get('pwd2')
        if pwd and pwd2 and pwd != pwd2:
            raise ValidationError("Passwords don't match")
        return pwd2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['pwd'])  # Properly hash the password before saving
        if commit:
            user.save()
        return user

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'desc', 'start', 'end']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event Title'
            }),
            'desc': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Event Description'
            }),
            'start': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }

class AccountEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'middle_name', 'last_name', 'email', 'sid', 'theme')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Middle Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'sid': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '##-UR-####'
            })
        }

    def clean_sid(self):
        sid = self.cleaned_data.get('sid')
        if not re.match(r'^\d{2}-UR-\d{4}$', sid):
            raise ValidationError('ID must be in ##-UR-#### format')
        return sid

class MembershipApplicationForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['payment_name', 'payment_phone', 'payment_proof']
        widgets = {
            'payment_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter name used for payment'}),
            'payment_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number used for payment'}),
            'payment_proof': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }

    def clean_payment_phone(self):
        phone = self.cleaned_data.get('payment_phone')
        if not phone.isdigit() or len(phone) == 9 :
            raise forms.ValidationError("Enter a valid phone number.")
        return phone

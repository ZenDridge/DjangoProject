from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.utils.deprecation import MiddlewareMixin
from .models import User

class SetupMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            return None

        try:
            setup_url = reverse('setup')
        except NoReverseMatch:
            return None
        
        if not User.objects.exists() and request.path != setup_url:
            return redirect(setup_url)

        return None

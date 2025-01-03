from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def is_adm(user):
    return user.is_authenticated and user.admin

def is_stf(user):
    return user.is_authenticated and (user.staff or user.admin)

def adm_req(view_func):
    @wraps(view_func)
    def wrap(request, *args, **kwargs):
        if not is_adm(request.user):
            messages.error(request, "Access denied.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrap

def stf_req(view_func):
    @wraps(view_func)
    def wrap(request, *args, **kwargs):
        if not is_stf(request.user):
            messages.error(request, "Access denied.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrap
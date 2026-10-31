from django.shortcuts import redirect
from django.urls import reverse

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if hasattr(request.user, 'profile') and request.user.profile.must_change_password:
                allowed_paths = [
                    reverse('cambiar_password'), 
                    reverse('logout'),
                    '/admin/' 
                ]
                if request.path not in allowed_paths:
                    return redirect('cambiar_password')
        response = self.get_response(request)
        return response
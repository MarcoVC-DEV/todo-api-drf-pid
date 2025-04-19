from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken
from .models import BlacklistedAccessToken
from django.http import JsonResponse
from rest_framework import status

class BlacklistAccessTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            access_token = auth_header.split(' ')[1]
            if BlacklistedAccessToken.objects.filter(token=access_token).exists():
                return JsonResponse(
                    {"detail": "Token is blacklisted", "code": "token_not_valid"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
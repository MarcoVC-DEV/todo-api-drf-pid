from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken
from .models import BlacklistedAccessToken
from django.http import JsonResponse
from rest_framework import status

# Intercepta solicitudes HTTPy verificar si el token de acceso
# incluido en el encabezado de autorización está en la lista negra.

class BlacklistAccessTokenMiddleware(MiddlewareMixin):
    # Esta clase extiende MiddlewareMixin, lo que permite que se utilice como middleware en Django.
    # Su propósito es interceptar las solicitudes entrantes y verificar si el token de acceso está en la lista negra.

    def process_request(self, request):
        # Este metodo se ejecuta antes de que la solicitud sea procesada por las vistas.
        # Aquí se realiza la lógica para verificar el token de acceso.

        auth_header = request.headers.get('Authorization')
        # Obtiene el encabezado de autorización de la solicitud.
        # Este encabezado contiene el token de acceso en formato "Bearer <token>".

        if auth_header and auth_header.startswith('Bearer '):
            # Verifica que el encabezado de autorización exista y comience con "Bearer ".
            # Esto asegura que el token de acceso esté presente y tenga el formato esperado.

            access_token = auth_header.split(' ')[1]
            # Extrae el token de acceso del encabezado de autorización.

            if BlacklistedAccessToken.objects.filter(token=access_token).exists():
                # Consulta la base de datos para verificar si el token de acceso está en la lista negra.
                # Si el token está en la lista negra, se bloquea la solicitud.

                return JsonResponse(
                    {"detail": "Token is blacklisted", "code": "token_not_valid"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                # Devuelve una respuesta JSON con un mensaje de error y un código de estado 401 (no autorizado).
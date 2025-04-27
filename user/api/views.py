from rest_framework import generics, status
from django.contrib.auth.models import User
from .serializers import RegistroSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework.permissions import IsAdminUser
from user.models import BlacklistedAccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer



# Create your views here.

class RegistroView(generics.CreateAPIView):
    # Define el conjunto de datos que se utilizará para esta vista, en este caso, todos los usuarios.
    queryset = User.objects.all()
    # Especifica el serializador que se usará para validar y transformar los datos de entrada/salida.
    serializer_class = RegistroSerializer  
  
    def create(self, request, *args, **kwargs):
        # Aquí puedes realizar cualquier acción adicional antes de crear el usuario.
        response = super().create(request, *args, **kwargs)

        return response
    
# Esta vista permite a un usuario autenticado cerrar sesión en el sistema.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        # Obtiene el token de refresco del cuerpo de la solicitud.
        refresh_token = request.data.get("refresh")
        # Obtiene el encabezado de autorización de la solicitud.
        auth_header = request.headers.get("Authorization")

        # Verifica que ambos tokens (refresh y access) estén presentes en la solicitud.
        if refresh_token is None or auth_header is None:
            return Response({"error": "Faltan tokens en la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        # Extrae el token de acceso del encabezado de autorización.
        access_token = auth_header.split(" ")[1]

        # Marca el token de refresco como inválido (lo agrega a la lista negra).
        token = RefreshToken(refresh_token)
        token.blacklist()

        # Marca el token de acceso como inválido almacenándolo en la base de datos.
        BlacklistedAccessToken.objects.create(token=access_token)

        # Devuelve una respuesta con el código de estado 205 (contenido restablecido).
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        # Captura cualquier excepción y devuelve un mensaje de error con el detalle de la excepción.
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# Esta vista permite a un usuario administrador eliminar un usuario específico del sistema.
# Utiliza `DestroyAPIView` del framework Django REST, que proporciona
# la funcionalidad para eliminar una instancia de un modelo.
class UserDeleteView(generics.DestroyAPIView):
    # Define el conjunto de datos que se utilizará para esta vista, en este caso, todos los usuarios.
    queryset = User.objects.all()
    # Especifica el serializador que se usará para validar y transformar los datos de entrada/salida.
    serializer_class = UserSerializer
    # Especifica los permisos requeridos para acceder a esta vista.
    permission_classes = [IsAdminUser]
    


# Esta vista extiende TokenObtainPairView para personalizar el proceso de generación de tokens.
class CustomTokenObtainPairView(TokenObtainPairView):
    # Especifica el serializador personalizado que se usará para la generación de tokens.
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Intenta obtener los tokens de acceso y refresco utilizando el serializador.
        serializer = self.get_serializer(data=request.data)
        try:
            # Valida los datos de entrada y genera los tokens.
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            # Si ocurre un error durante la validación, devuelve una respuesta con el detalle del error.
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        # Si la validación es exitosa, se generan los tokens y se devuelven en la respuesta.
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
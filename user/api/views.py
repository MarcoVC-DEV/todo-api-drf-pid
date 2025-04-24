from django.shortcuts import render
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
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from todo_api.pagination import DefaultPaginationLOS


# Create your views here.

class RegistroView(generics.CreateAPIView):  
    queryset = User.objects.all()  
    serializer_class = RegistroSerializer  
  
    def create(self, request, *args, **kwargs):  
        response = super().create(request, *args, **kwargs)  
        # user = User.objects.get(username=response.data['username'])
        # refresh = RefreshToken.for_user(user)
        # response.data['token'] = {
        #     'refresh': str(refresh),
        #     'access': str(refresh.access_token)
        # }
        return response
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        auth_header = request.headers.get("Authorization")

        if refresh_token is None or auth_header is None:
            return Response({"error": "Faltan tokens en la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        # Extract the access token from the Authorization header
        access_token = auth_header.split(" ")[1]

        # Blacklist the refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()

        # Blacklist the access token
        BlacklistedAccessToken.objects.create(token=access_token)

        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email


class RegistroSerializer(serializers.ModelSerializer):
    #password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)  
  
    class Meta:  
        model = User  
        fields = ['username', 'email', 'first_name', 'last_name' , 'password' ]#, 'password2']  
        extra_kwargs = {  
            'password': {'write_only': True}  
        }  
  
    def validate(self, data):  
        # Verificar que las contraseñas coincidan
        # if data['password'] != data['password2']:  
        #     raise serializers.ValidationError({'password': 'Las contraseñas no coinciden.'})  

        # Verificar que el correo electrónico no esté en uso
        if User.objects.filter(email=data['email']).exists():  
            raise serializers.ValidationError({'email': 'El email ya está registrado.'})  

        # Verificar que el nombre de usuario no esté en uso
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': 'El nombre de usuario ya está en uso.'})

        # Validar el formato del correo electrónico
        try:
            validate_email(data['email'])
        except DjangoValidationError:
            raise serializers.ValidationError({'email': 'El formato del email no es válido.'})

        # Validar la longitud de la contraseña
        if len(data['password']) < 8:
            raise serializers.ValidationError({'password': 'La contraseña debe tener al menos 8 caracteres.'})

        return data

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return UserSerializer(user).data
    
    
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email','full_name']

    def get_full_name(self, object):
        return f"{object.first_name} {object.last_name}"

    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        user_data = UserSerializer(user).data
        data.update({"user": user_data})
        return data
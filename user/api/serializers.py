from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email


class RegistroSerializer(serializers.ModelSerializer):
    # Clase Meta para definir el modelo y los campos que se utilizarán
    class Meta:  
        model = User  
        fields = ['username', 'email', 'first_name', 'last_name' , 'password' ]
        extra_kwargs = {  
            'password': {'write_only': True}  
        }

    # Metodo para validar los datos de entrada
    def validate(self, data):  


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
    # Campo calculado para obtener el nombre completo del usuario
    full_name = serializers.SerializerMethodField()

    class Meta:
        # Modelo asociado al serializador
        model = User
        # Campos que se incluirán en la representación del usuario
        fields = ['id', 'username', 'email','full_name']

    # Metodo para calcular el nombre completo del usuario
    def get_full_name(self, object):
        return f"{object.first_name} {object.last_name}"

    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        user_data = UserSerializer(user).data
        data.update({"user": user_data})
        return data
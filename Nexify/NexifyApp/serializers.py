from rest_framework import serializers
from . import models
from .models import Evento, Chat, Mensaje, Usuario

class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = '__all__'  # O especifica los campos que quieras

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = '__all__'
        
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['username', 'password', 'email', 'rol', 'telefono']
        extra_kwargs = {
            'password': {'write_only': True},  # No devolver la contraseña en las respuestas
        }

    def validate(self, data):
        # Validar que todos los campos requeridos estén presentes
        if not data.get('username') or not data.get('password') or not data.get('email') or not data.get('rol'):
            raise serializers.ValidationError("Todos los campos son obligatorios.")
        return data

    def create(self, validated_data):
        # Crear el usuario y asegurar que la contraseña esté hasheada
        user = Usuario(
            username=validated_data['username'],
            email=validated_data['email'],
            rol=validated_data['rol'],
            telefono=validated_data.get('telefono', None),  # Campo opcional
        )
        user.set_password(validated_data['password'])  # Hashear la contraseña
        user.save()
        return user


class CategoriaEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CategoriaEvento
        fields = '__all__'
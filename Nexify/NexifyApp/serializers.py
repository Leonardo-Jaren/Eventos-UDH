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
        fields = ['username', 'password', 'email', 'rol', 'telefono', 'foto_perfil']
        extra_kwargs = {
            'password': {'write_only': True},  # No devolver la contraseña en las respuestas
            'foto_perfil': {'required': False},  # Campo opcional
        }

    def validate(self, data):
        if not data.get('username') or not data.get('password') or not data.get('email'):
            raise serializers.ValidationError("Todos los campos son obligatorios.")
        return data

    def create(self, validated_data):
        # Establecer rol por defecto como "Participante"
        validated_data['rol'] = 'Participante'
        user = Usuario(
            username=validated_data['username'],
            email=validated_data['email'],
            rol=validated_data['rol'],
            telefono=validated_data.get('telefono', None),
            foto_perfil=validated_data.get('foto_perfil', None),
        )
        user.set_password(validated_data['password'])  # Hashear la contraseña
        user.save()
        return user


class CoordinadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Coordinador
        fields = '__all__'

class PonenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ponente
        fields = '__all__'

class ParticipanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Participante
        fields = '__all__'

class CategoriaEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CategoriaEvento
        fields = '__all__'
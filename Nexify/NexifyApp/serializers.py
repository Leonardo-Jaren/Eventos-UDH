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
        fields = '__all__'
        read_only_fields = ['id','last_login','is_superuser','is_staff','is_active','date_joined','groups','user_permissions','first_name','last_name']
    def create(self, validated_data):
        user = models.Usuario(
            email = validated_data['email'],
            username = validated_data['username'],
            rol=validated_data['rol']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class CategoriaEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CategoriaEvento
        fields = '__all__'
from django.shortcuts import render
from rest_framework import viewsets
from . import models, serializers
from .serializers import EventoSerializer, ChatSerializer, MensajeSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Chat, Mensaje, Evento
from rest_framework.permissions import IsAuthenticated
from .pusher import pusher_client
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth import authenticate

# Vista para manejar los eventos
class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Aquí puedes personalizar la creación del evento
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

############
class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, evento_id):
        usuario = request.user
        mensaje = request.data.get('mensaje')
        
        # Crear un nuevo chat
        chat = Chat.objects.create(evento_id=evento_id, usuario=usuario, mensaje=mensaje)

        return Response({'id': chat.id, 'mensaje': chat.mensaje})

    def get(self, request, evento_id):
        chats = Chat.objects.filter(evento_id=evento_id).order_by('-fecha_mensaje')
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)
 ###   
class MensajeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        contenido = request.data.get('contenido')

        # Crear un nuevo mensaje
        mensaje = Mensaje.objects.create(chat_id=chat_id, contenido=contenido)

        return Response({'id': mensaje.id, 'contenido': mensaje.contenido})

    def get(self, request, chat_id):
        mensajes = Mensaje.objects.filter(chat_id=chat_id)
        serializer = MensajeSerializer(mensajes, many=True)
        return Response(serializer.data)
############


class MesageAPIView(APIView):

    def post(self, request, evento_id):
        # Obtener el evento correspondiente, asumiendo que se pasa el ID del evento en la URL
        chat = get_object_or_404(Chat, evento_id=evento_id, usuario=request.user)

        # Crear un nuevo mensaje
        mensaje = Mensaje.objects.create(chat=chat, contenido=request.data['message'])

        # Enviar el mensaje a través de Pusher
        pusher_client.trigger('chat', 'message', {
            'username': request.data['username'],
            'message': mensaje.contenido
        })

        return Response({'id': mensaje.id, 'contenido': mensaje.contenido}, status=status.HTTP_201_CREATED)
    
    
###    
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = models.Usuario.objects.all()
    serializer_class = serializers.UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

#CategoriaEventoViewSet
class CategoriaEventoViewSet(viewsets.ModelViewSet):
    queryset = models.CategoriaEvento.objects.all()
    serializer_class = serializers.CategoriaEventoSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        api_key = request.headers.get('API-KEY')
        if api_key != settings.API_KEY:
            return Response({'error': 'Invalid API Key'}, status=401)
        
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=400)
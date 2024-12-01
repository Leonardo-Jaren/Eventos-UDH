from django.shortcuts import render
from rest_framework import viewsets
from . import models, serializers
from .serializers import EventoSerializer, ChatSerializer, MensajeSerializer, UsuarioSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Chat, Mensaje, Evento, Usuario
from rest_framework.permissions import IsAuthenticated
from .pusher import pusher_client
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import update_last_login
from django.contrib.auth.hashers import make_password

# ! Vista para manejar los eventos
class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()  # Atributo necesario para el router
    serializer_class = EventoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Ordenar los eventos por la fecha de creación descendente
        return Evento.objects.all().order_by('-fecha_evento')

    def create(self, request, *args, **kwargs):
        # Personalizar la creación del evento si es necesario
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        # Si necesitas realizar algún procesamiento adicional en la lista
        return super().list(request, *args, **kwargs)

# ! Usuarios APIview   
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = models.Usuario.objects.all()
    serializer_class = serializers.UsuarioSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]  # * Para manejar imágenes y formularios

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # * Crear el usuario y guardar la contraseña hasheada
        us = serializer.save()
        userer.set_password(serializer.validated_data['password'])
        user.save()

        # * Construir respuesta
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def partial_update(self, request, *args, **kwargs):
        """
        Permite la actualización parcial de usuarios, incluyendo la foto de perfil.
        """
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if 'password' in serializer.validated_data:
            user.set_password(serializer.validated_data['password'])
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

# ! ChatAPIView
class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, evento_id):
        usuario = request.user
        mensaje = request.data.get('mensaje')
        
        # * Crear un nuevo chat
        chat = Chat.objects.create(evento_id=evento_id, usuario=usuario, mensaje=mensaje)

        return Response({'id': chat.id, 'mensaje': chat.mensaje})

    def get(self, request, evento_id):
        chats = Chat.objects.filter(evento_id=evento_id).order_by('-fecha_mensaje')
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)

# ! ChatAPIView 
class MensajeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        contenido = request.data.get('contenido')

        # * Crear un nuevo mensaje
        mensaje = Mensaje.objects.create(chat_id=chat_id, contenido=contenido)

        return Response({'id': mensaje.id, 'contenido': mensaje.contenido})

    def get(self, request, chat_id):
        mensajes = Mensaje.objects.filter(chat_id=chat_id)
        serializer = MensajeSerializer(mensajes, many=True)
        return Response(serializer.data)

# ! MensajeAPIView
class MesageAPIView(APIView):

    def post(self, request, evento_id):
        # * Obtener el evento correspondiente, asumiendo que se pasa el ID del evento en la URL
        chat = get_object_or_404(Chat, evento_id=evento_id, usuario=request.user)

        # * Crear un nuevo mensaje
        mensaje = Mensaje.objects.create(chat=chat, contenido=request.data['message'])

        # * Enviar el mensaje a través de Pusher
        pusher_client.trigger('chat', 'message', {
            'username': request.data['username'],
            'message': mensaje.contenido
        })

        return Response({'id': mensaje.id, 'contenido': mensaje.contenido}, status=status.HTTP_201_CREATED)
    
# ! CategoriaEventoViewSet
class CategoriaEventoViewSet(viewsets.ModelViewSet):
    queryset = models.CategoriaEvento.objects.all()
    serializer_class = serializers.CategoriaEventoSerializer
    permission_classes = [AllowAny] # IsAuthenticated

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

# ! LoginView
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Obtener las credenciales (correo electrónico y contraseña)
        email = request.data.get('email')
        password = request.data.get('password')

        # Validar datos de entrada
        if not email or not password:
            return Response({'error': 'Se requiere correo electrónico y contraseña'}, status=status.HTTP_400_BAD_REQUEST)

        # Autenticar al usuario usando el correo electrónico
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response({'error': 'El correo electrónico no está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)
        if user is not None:
            # Generar o recuperar el token
            token, _ = Token.objects.get_or_create(user=user)

            # Actualizar la última fecha de inicio de sesión
            update_last_login(None, user)

            return Response({
                'token': token.key,
                'rol': user.rol,  # Devolver el rol del usuario
                'username': user.username
            })
        else:
            return Response({'error': 'Credenciales incorrectas'}, status=status.HTTP_400_BAD_REQUEST)
        
# ! RegisterView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password
from .models import Usuario
from .serializers import UsuarioSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Usar el serializer para validar y crear el usuario
        serializer = UsuarioSerializer(data=request.data)
        
        if serializer.is_valid():
            # Sobrescribir el rol para mayor seguridad
            serializer.validated_data['rol'] = 'Participante'
            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])  # Hashear la contraseña
            serializer.save()
            
            return Response({'message': 'Usuario registrado con éxito.'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def coordinadores(request):
    coordinadores = Usuario.objects.filter(rol='Coordinador')
    serializer = UsuarioSerializer(coordinadores, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def ponentes(request):
    ponentes = Usuario.objects.filter(rol='Ponente')
    serializer = UsuarioSerializer(ponentes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def moderadores(request):
    moderadores = Usuario.objects.filter(rol='Moderador_Solicitud')
    serializer = UsuarioSerializer(moderadores, many=True)
    return Response(serializer.data)
    
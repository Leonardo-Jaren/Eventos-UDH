from django.shortcuts import render
from rest_framework import viewsets
from . import models, serializers
from .serializers import EventoSerializer, ChatSerializer, MensajeSerializer, UsuarioSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Chat, Mensaje, Evento
from rest_framework.permissions import IsAuthenticated
from .pusher import pusher_client
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from .models import Usuario
from rest_framework.parsers import MultiPartParser, FormParser


# ! Vista para manejar los eventos
class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [AllowAny] #  AllowAny

    def create(self, request, *args, **kwargs):
        # * Aquí puedes personalizar la creación del evento
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
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
        user = serializer.save()
        user.set_password(serializer.validated_data['password'])
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
        # * Obtiene el nombre de usuario y la contraseña de la solicitud
        username = request.data.get('username')
        password = request.data.get('password')

        # * Valida los datos de entrada
        if not username or not password:
            return Response({'error': 'Se requiere nombre de usuario y contraseña'}, status=status.HTTP_400_BAD_REQUEST)

        # * Autentica al usuario
        user = authenticate(username=username, password=password)
        if user is not None:
            # * Si la autenticación es exitosa, genera o recupera el token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            # * Si la autenticación falla, retorna un error
            return Response({'error': 'Credenciales incorrectas'}, status=status.HTTP_400_BAD_REQUEST)
        
# ! RegisterView
class RegisterView(APIView): # 
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Usuario registrado con éxito."}, status=status.HTTP_201_CREATED)
        # * Devolver errores específicos
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
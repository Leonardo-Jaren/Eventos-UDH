from rest_framework import routers
from . import views
from django.urls import path, include
from .views import (
    EventoViewSet, ChatAPIView, MensajeAPIView,
    CategoriaEventoViewSet, usuarios_por_rol
)
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register('eventos', views.EventoViewSet)
router.register('usuario', views.UsuarioViewSet)
router.register('categoria', views.CategoriaEventoViewSet)

urlpatterns = [ 

    
    # Endpoints principales
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('messages', MensajeAPIView.as_view()),  # Desactivar si es solo para pruebas
    path('chat/<int:evento_id>/', ChatAPIView.as_view(), name='chat'),
    path('mensaje/<int:chat_id>/', MensajeAPIView.as_view(), name='mensaje'),
    
    # Ruta para obtener el perfil del usuario autenticado
    path('perfil/', views.PerfilUsuarioAPIView.as_view(), name='perfil-usuario'),
    
    # Rutas para roles específicos
    path('usuarios/<str:rol>/', usuarios_por_rol, name='usuarios-por-rol'),
    path('coordinadores/', views.coordinadores, name='coordinadores'),
    path('ponentes/', views.ponentes, name='ponentes'),
    path('moderadores/', views.moderadores, name='moderadores'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

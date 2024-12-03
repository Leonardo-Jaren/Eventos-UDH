from rest_framework import routers
from . import views
from django.urls import path, include
from .views import EventoViewSet, ChatAPIView, MensajeAPIView, InscripcionEventoAPIView
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register('eventos', views.EventoViewSet)
router.register('usuario', views.UsuarioViewSet)
router.register('categoria', views.CategoriaEventoViewSet)
router.register('Participantes', views.InscripcionViewSet)


urlpatterns = [ 
    path('messages', MensajeAPIView.as_view()), #desactivar para dejar de hacer pruebas
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('inscripcion/<int:evento_id>/', InscripcionEventoAPIView.as_view(), name='inscripcion_evento'),
    path('chat/<int:evento_id>/', ChatAPIView.as_view(), name='chat'),
    path('mensaje/<int:chat_id>/', MensajeAPIView.as_view(), name='mensaje'),

    # Rutas para los roles:
    path('coordinadores/', views.coordinadores, name='coordinadores'),
    path('ponentes/', views.ponentes, name='ponentes'),
    path('moderadores/', views.moderadores, name='moderadores'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

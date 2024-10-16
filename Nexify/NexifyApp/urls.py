from rest_framework import routers
from . import views
from django.urls import path, include
from .views import EventoViewSet, ChatAPIView, MensajeAPIView, CategoriaEventoViewSet

router = routers.DefaultRouter()
router.register('eventos', views.EventoViewSet)
router.register('usuario', views.UsuarioViewSet)
router.register('categoria', views.CategoriaEventoViewSet)

urlpatterns = [ 
    path('messages', MensajeAPIView.as_view()), #desactivar para dejar de hacer pruebas
    path('', include(router.urls)),
    path('token-auth/', views.CustomAuthToken.as_view(),name='token-auth'),
    path('chat/<int:evento_id>/', ChatAPIView.as_view(), name='chat'),
    path('mensaje/<int:chat_id>/', MensajeAPIView.as_view(), name='mensaje'),
]

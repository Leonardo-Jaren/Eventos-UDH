from rest_framework import routers
from . import views
from django.urls import path, include

router = routers.DefaultRouter()

urlpatterns = [ 
    path('', include(router.urls))
]
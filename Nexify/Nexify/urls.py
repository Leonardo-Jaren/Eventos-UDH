from django.contrib import admin
from django.urls import path, include
from NexifyApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('NexifyApp.urls')),
    path('login', views.LoginView.as_view(), name='login'),
]

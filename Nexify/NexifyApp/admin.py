from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Usuario)
admin.site.register(models.Evento)
admin.site.register(models.Chat)
admin.site.register(models.Mensaje)
admin.site.register(models.CategoriaEvento)
admin.site.register(models.Coordinador)

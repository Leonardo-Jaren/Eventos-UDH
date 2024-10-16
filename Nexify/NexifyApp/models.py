from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

# Modelo Usuario, base para otros roles
class Usuario(AbstractUser):
    TIPO_ROL_CHOICES =[
        ('Coordinador', 'Coordinador'),
        ('Participante', 'Participante'),
        ('Ponente', 'Ponente'),
        ('Moderador_Solicitud', 'Moderador_Solicitud'),
    ]
    telefono = models.CharField(max_length=9,null=True,blank=True)
    url_linkedin = models.CharField(max_length=40, null=True, blank=True)
    ##foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)
    rol =models.CharField(max_length=50,choices=TIPO_ROL_CHOICES,null=True,blank=True)
    rango =models.IntegerField(default=1)
    eventos_asistidos = models.IntegerField(default=0)

    def __str__(self):
        return self.username  # De AbstractUser

# Modelo Coordinador, hereda de Usuario
class Coordinador(Usuario):
    def __str__(self):
        return f'Coordinador: {self.username}'

# Modelo Ponente, hereda de Usuario
class Ponente(Usuario):
    def __str__(self):
        return f'Ponente: {self.username}'

# Modelo Participante, hereda de Usuario
class Participante(Usuario):
    def __str__(self):
        return f'Participante: {self.username}'

# Modelo Moderador_Solicitud, hereda de Usuario
class ModeradorSolicitud(Usuario):
    moderador_necesario = models.BooleanField(default=False)

    def __str__(self):
        return f'Moderador Solicitud: {self.username}'

#Modelo de categoria de evento una tabla conectada a eventos para que eventos herede una categoria
class CategoriaEvento(models.Model):
    nombre_categoria = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre_categoria

# Modelo Evento
class Evento(models.Model):
    nombre_evento = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_evento = models.DateTimeField()
    categoria_evento = models.ForeignKey(CategoriaEvento, on_delete=models.CASCADE, null=True, blank=True)
    TIPO_EVENTO_CHOICES = [
        ('Virtual', 'Virtual'),
        ('Presencial', 'Presencial'),
    ]
    tipo_evento = models.CharField(max_length=10, choices=TIPO_EVENTO_CHOICES, default='Virtual')
    
    ubicacion = models.CharField(max_length=255, null=True, blank=True)
    coordinador = models.ForeignKey(Usuario, limit_choices_to={'rol': 'Coordinador'}, on_delete=models.CASCADE, related_name='eventos_coordinados')
    ponente = models.ForeignKey(Usuario, limit_choices_to={'rol': 'Ponente'}, on_delete=models.CASCADE, related_name='eventos_ponentes')
    moderador_necesario = models.BooleanField(default=False)
    moderador = models.ForeignKey(Usuario, limit_choices_to={'rol': 'Moderador_Solicitud'}, on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos_moderados')
    participantes = models.ManyToManyField(Participante, through='Participantes', related_name='eventos')

    @property
    def estado_evento(self):
        now = timezone.now()  # Obtener la fecha y hora actual según la zona horaria configurada
        diferencia_tiempo = timezone.timedelta(hours=1)  # Definir una ventana de 1 hora para considerar "En Vivo"

        # Próximo evento
        if self.fecha_evento > now:
            return "Próximo"
        
        # En Vivo si el evento está dentro del margen de 1 hora
        elif self.fecha_evento <= now <= (self.fecha_evento + diferencia_tiempo):
            return "En Vivo"
        
        # Evento culminado
        else:
            return "Culminado"

    def clean(self):
        # Validar que si moderador_necesario es True, moderador debe ser requerido
        if self.moderador_necesario and self.moderador is None:
            raise ValidationError("Debe asignar un moderador si el campo 'moderador_necesario' está activado.")
        if self.tipo_evento == 'Presencial' and not self.ubicacion:
            raise ValidationError("La ubicación es requerida si el evento es presencial.")

    def save(self, *args, **kwargs):
        self.clean()  # Llamar a la validación antes de guardar
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_evento
    
# Modelo Participantes, tabla intermedia entre Evento y Participante
class Participantes(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='participantes_relacionados')
    usuario = models.ForeignKey(Participante, on_delete=models.CASCADE)
    fecha_asistencia = models.DateField()

    def __str__(self):
        return f'{self.usuario.username} en {self.evento.nombre_evento}'

# Modelo Premios_Rangos
class PremiosRangos(models.Model):
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    tipo_premio = models.CharField(max_length=100)
    fecha_premio = models.DateField()

    def __str__(self):
        return f'{self.tipo_premio} otorgado a {self.participante.username}'

# Modelo Chat
class Chat(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha_mensaje = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Mensaje en {self.evento.nombre_evento}'

# Modelo Mensaje
class Mensaje(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='mensajes')
    contenido = models.TextField()

    def __str__(self):
        return f'Mensaje: {self.contenido[:30]}'

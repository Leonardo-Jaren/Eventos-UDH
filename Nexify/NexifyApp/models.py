from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo Usuario, base para otros roles
class Usuario(AbstractUser):
    rango = models.CharField(max_length=50, null=True, blank=True)
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

# Modelo Evento
class Evento(models.Model):
    nombre_evento = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_evento = models.DateField()
    coordinador = models.ForeignKey(Coordinador, on_delete=models.CASCADE)
    ponente = models.ForeignKey(Ponente, on_delete=models.CASCADE)
    moderador = models.ForeignKey(ModeradorSolicitud, on_delete=models.SET_NULL, null=True, blank=True)
    estado_evento = models.CharField(max_length=50)
    participantes = models.ManyToManyField(Participante, through='Participantes', related_name='eventos')

    def __str__(self):
        return self.nombre_evento

# Modelo Participantes, tabla intermedia
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

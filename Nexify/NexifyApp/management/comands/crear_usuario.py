from django.core.management.base import BaseCommand, CommandParser
from NexifyApp.models import Usuario

class Command(BaseCommand):
    help = 'Crea un usuario'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('email', type=str)

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        password = kwargs['password']
        email = kwargs['email']

        Usuario.objects.create_user(
            username=username, 
            password=password, 
            email=email
        )

        Usuario.save()
        
        self.stdout.write(self.style.SUCCESS('Usuario creado exitosamente'))


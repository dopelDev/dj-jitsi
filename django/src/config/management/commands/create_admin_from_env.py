from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea superusuario admin desde variables de entorno'

    def handle(self, *args, **options):
        # Obtener variables de entorno
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        admin_first_name = os.getenv('ADMIN_FIRST_NAME', 'Admin')
        admin_last_name = os.getenv('ADMIN_LAST_NAME', 'User')
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=admin_username).exists():
            self.stdout.write(
                self.style.WARNING(f'El usuario {admin_username} ya existe')
            )
            return
        
        # Crear superusuario
        try:
            user = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                first_name=admin_first_name,
                last_name=admin_last_name
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superusuario {admin_username} creado exitosamente')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creando superusuario: {e}')
            )

"""
Comando de Django para configurar administradores desde variables de entorno
"""
from django.core.management.base import BaseCommand
from config.admin_setup import create_admins_from_env, list_admins


class Command(BaseCommand):
    help = 'Configura administradores desde variables de entorno DJANGO_ADMINS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--list',
            action='store_true',
            help='Lista los administradores actuales',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la actualización de contraseñas existentes',
        )

    def handle(self, *args, **options):
        if options['list']:
            self.stdout.write(
                self.style.SUCCESS('Listando administradores actuales...')
            )
            count = list_admins()
            self.stdout.write(
                self.style.SUCCESS(f'Total: {count} administradores')
            )
            return

        self.stdout.write(
            self.style.SUCCESS('Configurando administradores...')
        )
        
        try:
            count = create_admins_from_env()
            self.stdout.write(
                self.style.SUCCESS(f'✓ {count} administradores configurados exitosamente')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error configurando administradores: {e}')
            )

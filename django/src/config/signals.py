from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import os

User = get_user_model()


@receiver(post_migrate)
def create_admin_user(sender, **kwargs):
    """Crear superusuario admin automáticamente después de las migraciones"""
    import sys
    
    # Solo ejecutar si no estamos ejecutando tests
    if sender.name == 'models' and 'test' not in sys.argv:
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'change-me-in-production')
        admin_first_name = os.getenv('ADMIN_FIRST_NAME', 'Admin')
        admin_last_name = os.getenv('ADMIN_LAST_NAME', 'User')
        
        # Verificar si el usuario ya existe
        if not User.objects.filter(username=admin_username).exists():
            try:
                user = User.objects.create_superuser(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password,
                    first_name=admin_first_name,
                    last_name=admin_last_name
                )
                
                # Crear perfil con rol de ENV_ADMIN
                from models.models import UserProfile
                UserProfile.objects.create(
                    user=user,
                    role=UserProfile.ROLE_ENV_ADMIN
                )
                
                print(f'✅ Superusuario {admin_username} creado automáticamente con rol ENV_ADMIN')
            except Exception as e:
                print(f'❌ Error creando superusuario: {e}')
        else:
            # Verificar si el usuario existente tiene perfil con rol correcto
            user = User.objects.get(username=admin_username)
            if not hasattr(user, 'profile'):
                from models.models import UserProfile
                UserProfile.objects.create(
                    user=user,
                    role=UserProfile.ROLE_ENV_ADMIN
                )
                print(f'✅ Perfil ENV_ADMIN creado para usuario existente {admin_username}')
            else:
                print(f'ℹ️  El usuario {admin_username} ya existe con perfil')

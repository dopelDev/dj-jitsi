"""
Módulo para configuración de administradores desde variables de entorno
"""
import os
from django.contrib.auth import get_user_model


def create_admins_from_env():
    """
    Crea administradores basado en las variables de entorno DJANGO_ADMINS
    Formato: username:email:password,username2:email2:password2
    """
    User = get_user_model()
    admins_config = os.getenv("DJANGO_ADMINS", "")
    
    if not admins_config:
        return create_legacy_admin()
    
    created_count = 0
    updated_count = 0
    
    print(f"Configurando administradores desde DJANGO_ADMINS...")
    
    for admin_config in admins_config.split(","):
        admin_config = admin_config.strip()
        if not admin_config:
            continue
            
        try:
            # Formato: username:email:password
            parts = admin_config.split(":")
            if len(parts) != 3:
                print(f"Error: Formato inválido para admin '{admin_config}'. Usar: username:email:password")
                continue
                
            username, email, password = parts
            
            # Crear o actualizar usuario
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True
                }
            )
            
            if created:
                user.set_password(password)
                user.save()
                print(f"✓ Administrador creado: {username} ({email})")
                created_count += 1
            else:
                # Actualizar datos si el usuario ya existe
                user.email = email
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.set_password(password)
                user.save()
                print(f"✓ Administrador actualizado: {username} ({email})")
                updated_count += 1
                
        except Exception as e:
            print(f"Error creando administrador '{admin_config}': {e}")
    
    print(f"Resumen: {created_count} creados, {updated_count} actualizados")
    return created_count + updated_count


def create_legacy_admin():
    """
    Crea administrador usando las variables de entorno legacy
    """
    User = get_user_model()
    
    username = os.getenv("DJANGO_SUPERUSER_USERNAME")
    email = os.getenv("DJANGO_SUPERUSER_EMAIL")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
    
    if not all([username, email, password]):
        print("No se encontraron credenciales de administrador")
        return 0
    
    try:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            print(f"✓ Administrador legacy creado: {username} ({email})")
        else:
            # Actualizar datos si el usuario ya existe
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(password)
            user.save()
            print(f"✓ Administrador legacy actualizado: {username} ({email})")
            
        return 1
        
    except Exception as e:
        print(f"Error creando administrador legacy: {e}")
        return 0


def list_admins():
    """
    Lista todos los administradores actuales
    """
    User = get_user_model()
    admins = User.objects.filter(is_superuser=True, is_active=True)
    
    print("Administradores actuales:")
    for admin in admins:
        print(f"  - {admin.username} ({admin.email})")
    
    return admins.count()


if __name__ == "__main__":
    # Para uso directo del script
    import django
    from django.conf import settings
    
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
    
    create_admins_from_env()
    list_admins()

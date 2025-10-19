#!/usr/bin/env python3
"""
Script para generar datos mock basado en el esquema SQL
"""
import os
import sys
import django
from pathlib import Path
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from models.models import SignupRequest, Meeting, UserProfile
from django.utils import timezone
from datetime import timezone as dt_timezone

User = get_user_model()
fake = Faker('es_ES')  # Usar datos en español

class MockDataGenerator:
    """Generador de datos mock para el sistema Django-Jitsi"""
    
    def __init__(self):
        self.users_created = 0
        self.signup_requests_created = 0
        self.meetings_created = 0
        self.profiles_created = 0
    
    def generate_users(self, count=20):
        """Generar usuarios mock con diferentes roles"""
        print(f"🔄 Generando {count} usuarios...")
        
        roles = [
            (UserProfile.ROLE_ENV_ADMIN, 1),
            (UserProfile.ROLE_WEB_ADMIN, 2), 
            (UserProfile.ROLE_USER, 15),
            (UserProfile.ROLE_GUEST, 2)
        ]
        
        for role, role_count in roles:
            for i in range(role_count):
                # Crear usuario
                username = fake.user_name() + str(random.randint(100, 999))
                email = fake.email()
                first_name = fake.first_name()
                last_name = fake.last_name()
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='testpass123',
                    first_name=first_name,
                    last_name=last_name,
                    is_active=True
                )
                
                # Configurar permisos según el rol
                if role == UserProfile.ROLE_ENV_ADMIN:
                    user.is_staff = True
                    user.is_superuser = True
                elif role == UserProfile.ROLE_WEB_ADMIN:
                    user.is_staff = True
                
                user.save()
                
                # Crear perfil
                profile = UserProfile.objects.create(
                    user=user,
                    role=role
                )
                
                self.users_created += 1
                self.profiles_created += 1
                
                print(f"  ✅ Usuario creado: {username} ({role})")
    
    def generate_signup_requests(self, count=30):
        """Generar solicitudes de registro mock"""
        print(f"🔄 Generando {count} solicitudes de registro...")
        
        statuses = ['pending', 'approved', 'rejected']
        status_weights = [0.4, 0.4, 0.2]  # 40% pendientes, 40% aprobadas, 20% rechazadas
        
        for i in range(count):
            status = random.choices(statuses, weights=status_weights)[0]
            
            # Crear solicitud
            signup_request = SignupRequest.objects.create(
                email=fake.email(),
                full_name=fake.name(),
                password_hash=fake.sha256(),
                note=fake.text(max_nb_chars=200),
                status=status,
                created_at=fake.date_time_between(start_date='-30d', end_date='now', tzinfo=dt_timezone.utc)
            )
            
            # Si está decidida, agregar información de decisión
            if status in ['approved', 'rejected']:
                # Asignar un admin como decisor
                admin_users = User.objects.filter(profile__role__in=[
                    UserProfile.ROLE_ENV_ADMIN, 
                    UserProfile.ROLE_WEB_ADMIN
                ])
                
                if admin_users.exists():
                    signup_request.decided_by = random.choice(admin_users)
                    signup_request.decided_at = fake.date_time_between(
                        start_date=signup_request.created_at, 
                        end_date='now', 
                        tzinfo=dt_timezone.utc
                    )
                    signup_request.decision_note = fake.text(max_nb_chars=100)
                    signup_request.save()
            
            self.signup_requests_created += 1
            print(f"  ✅ Solicitud creada: {signup_request.email} ({status})")
    
    def generate_meetings(self, count=25):
        """Generar meetings mock"""
        print(f"🔄 Generando {count} meetings...")
        
        # Obtener usuarios que pueden crear meetings (no guests)
        users = User.objects.filter(profile__role__in=[
            UserProfile.ROLE_ENV_ADMIN,
            UserProfile.ROLE_WEB_ADMIN, 
            UserProfile.ROLE_USER
        ])
        
        if not users.exists():
            print("  ⚠️  No hay usuarios disponibles para crear meetings")
            return
        
        for i in range(count):
            owner = random.choice(users)
            
            # Generar room ID único
            room_id = f"room-{fake.word()}-{random.randint(1000, 9999)}"
            
            meeting = Meeting.objects.create(
                room=room_id,
                owner=owner,
                created_at=fake.date_time_between(start_date='-15d', end_date='now', tzinfo=dt_timezone.utc)
            )
            
            self.meetings_created += 1
            print(f"  ✅ Meeting creado: {room_id} (propietario: {owner.username})")
    
    def generate_realistic_scenarios(self):
        """Generar escenarios realistas de uso"""
        print("🔄 Generando escenarios realistas...")
        
        # Escenario 1: Usuario que crea múltiples meetings
        user = User.objects.filter(profile__role=UserProfile.ROLE_USER).first()
        if user:
            for i in range(3):
                room_id = f"project-meeting-{i+1}-{random.randint(100, 999)}"
                Meeting.objects.create(
                    room=room_id,
                    owner=user,
                    created_at=fake.date_time_between(start_date='-7d', end_date='now', tzinfo=dt_timezone.utc)
                )
            print(f"  ✅ Usuario {user.username} tiene 3 meetings de proyecto")
        
        # Escenario 2: Solicitudes recientes pendientes
        recent_requests = SignupRequest.objects.filter(status='pending')[:5]
        for request in recent_requests:
            request.created_at = fake.date_time_between(start_date='-2d', end_date='now', tzinfo=dt_timezone.utc)
            request.save()
        print(f"  ✅ {len(recent_requests)} solicitudes recientes pendientes")
        
        # Escenario 3: Admin que ha decidido muchas solicitudes
        admin = User.objects.filter(profile__role=UserProfile.ROLE_ENV_ADMIN).first()
        if admin:
            approved_requests = SignupRequest.objects.filter(status='approved')[:10]
            for request in approved_requests:
                request.decided_by = admin
                request.decided_at = fake.date_time_between(
                    start_date=request.created_at, 
                    end_date='now', 
                    tzinfo=dt_timezone.utc
                )
                request.decision_note = "Solicitud aprobada automáticamente"
                request.save()
            print(f"  ✅ Admin {admin.username} ha aprobado {len(approved_requests)} solicitudes")
    
    def print_statistics(self):
        """Imprimir estadísticas finales"""
        print("\n📊 ESTADÍSTICAS FINALES:")
        print(f"  👤 Usuarios creados: {self.users_created}")
        print(f"  👤 Perfiles creados: {self.profiles_created}")
        print(f"  📝 Solicitudes creadas: {self.signup_requests_created}")
        print(f"  🎥 Meetings creados: {self.meetings_created}")
        
        print(f"\n📈 ESTADÍSTICAS DEL SISTEMA:")
        print(f"  - Total usuarios: {User.objects.count()}")
        print(f"  - Total solicitudes: {SignupRequest.objects.count()}")
        print(f"  - Total meetings: {Meeting.objects.count()}")
        print(f"  - Total perfiles: {UserProfile.objects.count()}")
        
        print(f"\n📊 DISTRIBUCIÓN POR ROLES:")
        for role in ['ENV_ADMIN', 'WEB_ADMIN', 'USER', 'GUEST']:
            count = UserProfile.objects.filter(role=role).count()
            print(f"  - {role}: {count}")
        
        print(f"\n📊 ESTADOS DE SOLICITUDES:")
        for status in ['pending', 'approved', 'rejected']:
            count = SignupRequest.objects.filter(status=status).count()
            print(f"  - {status.upper()}: {count}")

def main():
    """Función principal"""
    print("🚀 GENERADOR DE DATOS MOCK PARA DJANGO-JITSI")
    print("=" * 50)
    
    generator = MockDataGenerator()
    
    try:
        # Generar datos
        generator.generate_users(20)
        generator.generate_signup_requests(30)
        generator.generate_meetings(25)
        generator.generate_realistic_scenarios()
        
        # Mostrar estadísticas
        generator.print_statistics()
        
        print("\n✅ ¡Datos mock generados exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error generando datos mock: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generador de datos mock para el sistema Django-Jitsi
Respetando la jerarquía de permisos: ENV_ADMIN > WEB_ADMIN > USER > GUEST
"""
import os
import sys
import django
import random
from faker import Faker
from datetime import timezone as dt_timezone

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from models.models import SignupRequest, Meeting, UserProfile

User = get_user_model()
fake = Faker('es_ES')  # Usar datos en español

class MockDataGeneratorV2:
    def __init__(self):
        self.fake = fake
        
    def clear_existing_data(self):
        """Limpiar datos existentes (excepto ENV_ADMIN)"""
        print("🧹 Limpiando datos existentes...")
        
        # Eliminar usuarios que no sean ENV_ADMIN
        User.objects.exclude(profile__role=UserProfile.ROLE_ENV_ADMIN).delete()
        SignupRequest.objects.all().delete()
        Meeting.objects.all().delete()
        
        print("✅ Datos limpiados")
    
    def generate_web_admins(self, count=2):
        """Generar WEB_ADMIN (solo ENV_ADMIN puede crear estos)"""
        print(f"👑 Generando {count} WEB_ADMIN...")
        
        env_admin = User.objects.filter(profile__role=UserProfile.ROLE_ENV_ADMIN).first()
        if not env_admin:
            print("❌ No se encontró ENV_ADMIN")
            return
        
        for i in range(count):
            try:
                user = User.objects.create_user(
                    username=f"webadmin_{i+1}",
                    email=f"webadmin{i+1}@example.com",
                    password='webadmin123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    is_staff=True
                )
                
                UserProfile.objects.create(user=user, role=UserProfile.ROLE_WEB_ADMIN)
                print(f"  ✅ WEB_ADMIN {i+1} creado")
                
            except Exception as e:
                print(f"  ❌ Error creando WEB_ADMIN {i+1}: {e}")
    
    def generate_regular_users(self, count=15):
        """Generar usuarios regulares (USER)"""
        print(f"👤 Generando {count} usuarios regulares...")
        
        for i in range(count):
            try:
                user = User.objects.create_user(
                    username=f"user_{i+1}",
                    email=f"user{i+1}@example.com",
                    password='user123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )
                
                UserProfile.objects.create(user=user, role=UserProfile.ROLE_USER)
                
                if i % 5 == 0:
                    print(f"  ✅ Usuario {i+1}/{count} creado")
                    
            except Exception as e:
                print(f"  ❌ Error creando usuario {i+1}: {e}")
    
    def generate_guests(self, count=10):
        """Generar usuarios invitados (GUEST)"""
        print(f"👻 Generando {count} usuarios invitados...")
        
        for i in range(count):
            try:
                user = User.objects.create_user(
                    username=f"guest_{i+1}",
                    email=f"guest{i+1}@example.com",
                    password='guest123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )
                
                UserProfile.objects.create(user=user, role=UserProfile.ROLE_GUEST)
                
                if i % 5 == 0:
                    print(f"  ✅ Invitado {i+1}/{count} creado")
                    
            except Exception as e:
                print(f"  ❌ Error creando invitado {i+1}: {e}")
    
    def generate_signup_requests(self, count=20):
        """Generar solicitudes de registro"""
        print(f"📝 Generando {count} solicitudes de registro...")
        
        statuses = ['pending', 'approved', 'rejected']
        weights = [0.4, 0.4, 0.2]  # 40% pendientes, 40% aprobadas, 20% rechazadas
        
        for i in range(count):
            try:
                status = random.choices(statuses, weights=weights)[0]
                
                signup_request = SignupRequest.objects.create(
                    email=fake.email(),
                    full_name=fake.name(),
                    password_hash=fake.sha256(),
                    note=fake.text(max_nb_chars=200),
                    status=status,
                    created_at=fake.date_time_between(start_date='-30d', end_date='now', tzinfo=dt_timezone.utc)
                )
                
                # Si está aprobada o rechazada, asignar decisor
                if status in ['approved', 'rejected']:
                    # Asignar decisor aleatorio (ENV_ADMIN o WEB_ADMIN)
                    deciders = User.objects.filter(profile__role__in=[
                        UserProfile.ROLE_ENV_ADMIN, 
                        UserProfile.ROLE_WEB_ADMIN
                    ])
                    if deciders.exists():
                        signup_request.decided_by = random.choice(deciders)
                        signup_request.decided_at = fake.date_time_between(
                            start_date=signup_request.created_at, 
                            end_date='now', 
                            tzinfo=dt_timezone.utc
                        )
                        signup_request.decision_note = fake.text(max_nb_chars=100)
                        signup_request.save()
                
                if i % 5 == 0:
                    print(f"  ✅ Solicitud {i+1}/{count} creada")
                    
            except Exception as e:
                print(f"  ❌ Error creando solicitud {i+1}: {e}")
    
    def generate_meetings(self, count=25):
        """Generar meetings para usuarios"""
        print(f"🎥 Generando {count} meetings...")
        
        # Obtener usuarios que pueden crear meetings (USER y admins)
        meeting_owners = User.objects.filter(
            profile__role__in=[
                UserProfile.ROLE_USER,
                UserProfile.ROLE_WEB_ADMIN,
                UserProfile.ROLE_ENV_ADMIN
            ]
        )
        
        if not meeting_owners.exists():
            print("❌ No hay usuarios que puedan crear meetings")
            return
        
        for i in range(count):
            try:
                owner = random.choice(meeting_owners)
                
                meeting = Meeting.objects.create(
                    room=f"room-{fake.word()}-{random.randint(1000, 9999)}",
                    owner=owner,
                    created_at=fake.date_time_between(start_date='-15d', end_date='now', tzinfo=dt_timezone.utc)
                )
                
                if i % 5 == 0:
                    print(f"  ✅ Meeting {i+1}/{count} creado")
                    
            except Exception as e:
                print(f"  ❌ Error creando meeting {i+1}: {e}")
    
    def generate_all(self):
        """Generar todos los datos mock"""
        print("🚀 INICIANDO GENERACIÓN DE DATOS MOCK V2")
        print("=" * 50)
        
        # Limpiar datos existentes
        self.clear_existing_data()
        
        # Generar datos respetando jerarquía
        self.generate_web_admins(2)
        self.generate_regular_users(15)
        self.generate_guests(10)
        self.generate_signup_requests(20)
        self.generate_meetings(25)
        
        # Mostrar estadísticas finales
        self.show_statistics()
        
        print("\n🎉 ¡GENERACIÓN DE DATOS COMPLETADA!")
    
    def show_statistics(self):
        """Mostrar estadísticas de los datos generados"""
        print("\n📊 ESTADÍSTICAS FINALES:")
        print("-" * 30)
        
        # Usuarios por rol
        for role, _ in UserProfile.ROLE_CHOICES:
            count = UserProfile.objects.filter(role=role).count()
            print(f"  {role}: {count} usuarios")
        
        # Solicitudes por estado
        for status, _ in SignupRequest.STATUS_CHOICES:
            count = SignupRequest.objects.filter(status=status).count()
            print(f"  Solicitudes {status}: {count}")
        
        # Meetings
        meetings_count = Meeting.objects.count()
        print(f"  Meetings: {meetings_count}")
        
        # Total usuarios
        total_users = User.objects.count()
        print(f"  Total usuarios: {total_users}")

if __name__ == "__main__":
    generator = MockDataGeneratorV2()
    generator.generate_all()

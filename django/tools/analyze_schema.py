#!/usr/bin/env python3
"""
Script para analizar el esquema de la base de datos Django
"""
import os
import sys
import django
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from models.models import SignupRequest, Meeting, UserProfile

def analyze_schema():
    """Analizar el esquema de la base de datos"""
    print("=== ANÁLISIS DEL ESQUEMA DE BASE DE DATOS ===\n")
    
    # Obtener información de las tablas
    with connection.cursor() as cursor:
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📋 TABLAS ENCONTRADAS:")
        for table in tables:
            print(f"  - {table[0]}")
        print()
        
        # Analizar cada tabla importante
        important_tables = [
            'auth_user',
            'models_signuprequest', 
            'models_meeting',
            'models_userprofile'
        ]
        
        for table_name in important_tables:
            if any(table[0] == table_name for table in tables):
                print(f"🔍 ANÁLISIS DE LA TABLA: {table_name}")
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                print("  Columnas:")
                for col in columns:
                    col_id, name, type_name, not_null, default_value, pk = col
                    pk_marker = " (PRIMARY KEY)" if pk else ""
                    null_marker = " NOT NULL" if not_null else ""
                    default_marker = f" DEFAULT {default_value}" if default_value else ""
                    print(f"    - {name}: {type_name}{null_marker}{default_marker}{pk_marker}")
                
                # Obtener algunos registros de ejemplo
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"  Total de registros: {count}")
                
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                    sample_data = cursor.fetchall()
                    print("  Datos de ejemplo:")
                    for row in sample_data:
                        print(f"    {row}")
                print()
    
    # Análisis de modelos Django
    print("🐍 ANÁLISIS DE MODELOS DJANGO:")
    
    # User model
    User = get_user_model()
    print(f"\n👤 MODELO USER:")
    print(f"  - Campos: {[field.name for field in User._meta.fields]}")
    print(f"  - Total usuarios: {User.objects.count()}")
    
    # SignupRequest model
    print(f"\n📝 MODELO SIGNUPREQUEST:")
    print(f"  - Campos: {[field.name for field in SignupRequest._meta.fields]}")
    print(f"  - Total solicitudes: {SignupRequest.objects.count()}")
    
    # Meeting model
    print(f"\n🎥 MODELO MEETING:")
    print(f"  - Campos: {[field.name for field in Meeting._meta.fields]}")
    print(f"  - Total meetings: {Meeting.objects.count()}")
    
    # UserProfile model
    print(f"\n👤 MODELO USERPROFILE:")
    print(f"  - Campos: {[field.name for field in UserProfile._meta.fields]}")
    print(f"  - Total perfiles: {UserProfile.objects.count()}")
    
    # Análisis de relaciones
    print(f"\n🔗 ANÁLISIS DE RELACIONES:")
    print(f"  - Usuarios con perfil: {User.objects.filter(profile__isnull=False).count()}")
    print(f"  - Usuarios sin perfil: {User.objects.filter(profile__isnull=True).count()}")
    print(f"  - Meetings por usuario: {Meeting.objects.values('owner').distinct().count()}")
    
    # Estados de solicitudes
    print(f"\n📊 ESTADOS DE SOLICITUDES:")
    for status in ['pending', 'approved', 'rejected']:
        count = SignupRequest.objects.filter(status=status).count()
        print(f"  - {status.upper()}: {count}")
    
    # Roles de usuarios
    print(f"\n🎭 ROLES DE USUARIOS:")
    for role in ['ENV_ADMIN', 'WEB_ADMIN', 'USER', 'GUEST']:
        count = UserProfile.objects.filter(role=role).count()
        print(f"  - {role}: {count}")

if __name__ == "__main__":
    analyze_schema()

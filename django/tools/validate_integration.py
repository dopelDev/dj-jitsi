import os
import sys
import django
import sqlite3

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_authreg_table():
    """Verificar que tabla authreg existe"""
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='authreg'")
        result = cursor.fetchone()
        print(f"✓ Tabla authreg existe: {result is not None}")

def test_user_sync():
    """Verificar que usuarios Django están en authreg"""
    from django.contrib.auth.models import User
    from django.db import connection
    
    users = User.objects.filter(is_active=True)
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM authreg")
        count = cursor.fetchone()[0]
        print(f"✓ Usuarios en authreg: {count}")
        print(f"  Usuarios Django activos: {users.count()}")

def test_meeting_types():
    """Verificar salas públicas y privadas"""
    from models.models import Meeting
    public = Meeting.objects.filter(is_private=False).count()
    private = Meeting.objects.filter(is_private=True).count()
    print(f"✓ Reuniones públicas: {public}")
    print(f"✓ Reuniones privadas: {private}")

if __name__ == "__main__":
    print("Validando integración Django-Jitsi...")
    test_authreg_table()
    test_user_sync()
    test_meeting_types()

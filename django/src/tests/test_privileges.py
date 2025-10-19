#!/usr/bin/env python3
"""
Tests para verificar la jerarquía de privilegios del sistema
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from models.models import UserProfile, SignupRequest, Meeting

User = get_user_model()

class TestPrivilegeHierarchy(TestCase):
    """Tests para verificar la jerarquía de privilegios"""
    
    def setUp(self):
        """Configurar usuarios de prueba"""
        self.client = Client()
        
        # Crear ENV_ADMIN
        self.env_admin = User.objects.create_user(
            username="env_admin",
            email="env@admin.com",
            password="env123",
            is_staff=True,
            is_superuser=True
        )
        UserProfile.objects.create(user=self.env_admin, role=UserProfile.ROLE_ENV_ADMIN)
        
        # Crear WEB_ADMIN
        self.web_admin = User.objects.create_user(
            username="web_admin",
            email="web@admin.com",
            password="web123",
            is_staff=True
        )
        UserProfile.objects.create(user=self.web_admin, role=UserProfile.ROLE_WEB_ADMIN)
        
        # Crear USER
        self.regular_user = User.objects.create_user(
            username="regular_user",
            email="user@example.com",
            password="user123"
        )
        UserProfile.objects.create(user=self.regular_user, role=UserProfile.ROLE_USER)
        
        # Crear GUEST
        self.guest_user = User.objects.create_user(
            username="guest_user",
            email="guest@example.com",
            password="guest123"
        )
        UserProfile.objects.create(user=self.guest_user, role=UserProfile.ROLE_GUEST)
    
    def test_env_admin_cannot_create_env_admin(self):
        """ENV_ADMIN NO puede crear otro ENV_ADMIN desde la aplicación"""
        self.assertFalse(
            UserProfile.can_create_role(
                self.env_admin.profile, 
                UserProfile.ROLE_ENV_ADMIN
            )
        )
    
    def test_env_admin_can_create_web_admin(self):
        """ENV_ADMIN puede crear WEB_ADMIN"""
        self.assertTrue(
            UserProfile.can_create_role(
                self.env_admin.profile, 
                UserProfile.ROLE_WEB_ADMIN
            )
        )
    
    def test_web_admin_cannot_create_web_admin(self):
        """WEB_ADMIN NO puede crear otro WEB_ADMIN"""
        self.assertFalse(
            UserProfile.can_create_role(
                self.web_admin.profile, 
                UserProfile.ROLE_WEB_ADMIN
            )
        )
    
    def test_web_admin_can_create_user(self):
        """WEB_ADMIN puede crear USER"""
        self.assertTrue(
            UserProfile.can_create_role(
                self.web_admin.profile, 
                UserProfile.ROLE_USER
            )
        )
    
    def test_web_admin_can_create_guest(self):
        """WEB_ADMIN puede crear GUEST"""
        self.assertTrue(
            UserProfile.can_create_role(
                self.web_admin.profile, 
                UserProfile.ROLE_GUEST
            )
        )
    
    def test_user_cannot_create_any_role(self):
        """USER no puede crear ningún rol"""
        self.assertFalse(
            UserProfile.can_create_role(
                self.regular_user.profile, 
                UserProfile.ROLE_USER
            )
        )
        self.assertFalse(
            UserProfile.can_create_role(
                self.regular_user.profile, 
                UserProfile.ROLE_WEB_ADMIN
            )
        )
    
    def test_guest_cannot_create_any_role(self):
        """GUEST no puede crear ningún rol"""
        self.assertFalse(
            UserProfile.can_create_role(
                self.guest_user.profile, 
                UserProfile.ROLE_USER
            )
        )
    
    def test_env_admin_can_delete_web_admin(self):
        """ENV_ADMIN puede eliminar WEB_ADMIN"""
        self.assertTrue(
            UserProfile.can_delete_user(
                self.env_admin.profile,
                self.web_admin.profile
            )
        )
    
    def test_env_admin_cannot_delete_env_admin(self):
        """ENV_ADMIN NO puede eliminar otro ENV_ADMIN"""
        # Crear otro ENV_ADMIN
        another_env_admin = User.objects.create_user(
            username="another_env_admin",
            email="another@env.com",
            password="another123"
        )
        UserProfile.objects.create(user=another_env_admin, role=UserProfile.ROLE_ENV_ADMIN)
        
        self.assertFalse(
            UserProfile.can_delete_user(
                self.env_admin.profile,
                another_env_admin.profile
            )
        )
    
    def test_cannot_delete_env_admin_from_app(self):
        """Nadie puede eliminar ENV_ADMIN desde la aplicación"""
        self.assertFalse(
            UserProfile.can_delete_user(
                self.env_admin.profile,
                self.env_admin.profile
            )
        )
        
        self.assertFalse(
            UserProfile.can_delete_user(
                self.web_admin.profile,
                self.env_admin.profile
            )
        )
    
    def test_web_admin_can_delete_user(self):
        """WEB_ADMIN puede eliminar USER"""
        self.assertTrue(
            UserProfile.can_delete_user(
                self.web_admin.profile,
                self.regular_user.profile
            )
        )
    
    def test_web_admin_can_delete_guest(self):
        """WEB_ADMIN puede eliminar GUEST"""
        self.assertTrue(
            UserProfile.can_delete_user(
                self.web_admin.profile,
                self.guest_user.profile
            )
        )
    
    def test_web_admin_cannot_delete_env_admin(self):
        """WEB_ADMIN NO puede eliminar ENV_ADMIN"""
        self.assertFalse(
            UserProfile.can_delete_user(
                self.web_admin.profile,
                self.env_admin.profile
            )
        )
    
    def test_user_cannot_delete_anyone(self):
        """USER no puede eliminar a nadie"""
        self.assertFalse(
            UserProfile.can_delete_user(
                self.regular_user.profile,
                self.guest_user.profile
            )
        )
    
    def test_guest_cannot_delete_anyone(self):
        """GUEST no puede eliminar a nadie"""
        self.assertFalse(
            UserProfile.can_delete_user(
                self.guest_user.profile,
                self.regular_user.profile
            )
        )

class TestPrivilegeViews(TestCase):
    """Tests para verificar privilegios en las vistas"""
    
    def setUp(self):
        """Configurar usuarios de prueba"""
        self.client = Client()
        
        # Crear ENV_ADMIN
        self.env_admin = User.objects.create_user(
            username="env_admin",
            email="env@admin.com",
            password="env123",
            is_staff=True,
            is_superuser=True
        )
        UserProfile.objects.create(user=self.env_admin, role=UserProfile.ROLE_ENV_ADMIN)
        
        # Crear WEB_ADMIN
        self.web_admin = User.objects.create_user(
            username="web_admin",
            email="web@admin.com",
            password="web123",
            is_staff=True
        )
        UserProfile.objects.create(user=self.web_admin, role=UserProfile.ROLE_WEB_ADMIN)
        
        # Crear USER para ser modificado
        self.target_user = User.objects.create_user(
            username="target_user",
            email="target@example.com",
            password="target123"
        )
        UserProfile.objects.create(user=self.target_user, role=UserProfile.ROLE_USER)
    
    def test_env_admin_can_change_role_to_web_admin(self):
        """ENV_ADMIN puede cambiar rol a WEB_ADMIN"""
        self.client.login(username="env_admin", password="env123")
        
        response = self.client.post(
            reverse('change_user_role', kwargs={'pk': self.target_user.pk}),
            {'role': UserProfile.ROLE_WEB_ADMIN}
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.profile.role, UserProfile.ROLE_WEB_ADMIN)
    
    def test_web_admin_cannot_change_role_to_web_admin(self):
        """WEB_ADMIN NO puede cambiar rol a WEB_ADMIN"""
        self.client.login(username="web_admin", password="web123")
        
        response = self.client.post(
            reverse('change_user_role', kwargs={'pk': self.target_user.pk}),
            {'role': UserProfile.ROLE_WEB_ADMIN}
        )
        
        # Debería redirigir con error
        self.assertEqual(response.status_code, 302)
        self.target_user.refresh_from_db()
        # El rol no debería haber cambiado
        self.assertEqual(self.target_user.profile.role, UserProfile.ROLE_USER)
    
    def test_web_admin_can_change_role_to_user(self):
        """WEB_ADMIN puede cambiar rol a USER"""
        self.client.login(username="web_admin", password="web123")
        
        response = self.client.post(
            reverse('change_user_role', kwargs={'pk': self.target_user.pk}),
            {'role': UserProfile.ROLE_GUEST}
        )
        
        self.assertEqual(response.status_code, 302)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.profile.role, UserProfile.ROLE_GUEST)
    
    def test_env_admin_can_delete_web_admin(self):
        """ENV_ADMIN puede eliminar WEB_ADMIN"""
        self.client.login(username="env_admin", password="env123")
        
        response = self.client.post(
            reverse('delete_user', kwargs={'pk': self.web_admin.pk})
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(pk=self.web_admin.pk).exists())
    
    def test_web_admin_cannot_delete_env_admin(self):
        """WEB_ADMIN NO puede eliminar ENV_ADMIN"""
        self.client.login(username="web_admin", password="web123")
        
        response = self.client.get(
            reverse('delete_user', kwargs={'pk': self.env_admin.pk})
        )
        
        # Debería redirigir con error
        self.assertEqual(response.status_code, 302)
        # El ENV_ADMIN debería seguir existiendo
        self.assertTrue(User.objects.filter(pk=self.env_admin.pk).exists())
    
    def test_cannot_assign_env_admin_role(self):
        """Nadie puede asignar rol ENV_ADMIN desde la aplicación"""
        self.client.login(username="env_admin", password="env123")
        
        response = self.client.post(
            reverse('change_user_role', kwargs={'pk': self.target_user.pk}),
            {'role': UserProfile.ROLE_ENV_ADMIN}
        )
        
        # Debería redirigir con error
        self.assertEqual(response.status_code, 302)
        self.target_user.refresh_from_db()
        # El rol no debería haber cambiado
        self.assertEqual(self.target_user.profile.role, UserProfile.ROLE_USER)
    
    def test_cannot_change_env_admin_role(self):
        """Nadie puede cambiar el rol de ENV_ADMIN"""
        self.assertFalse(
            UserProfile.can_change_user_role(
                self.env_admin.profile,
                self.env_admin.profile,
                UserProfile.ROLE_WEB_ADMIN
            )
        )
        
        self.assertFalse(
            UserProfile.can_change_user_role(
                self.web_admin.profile,
                self.env_admin.profile,
                UserProfile.ROLE_USER
            )
        )
    
    def test_cannot_delete_env_admin_from_view(self):
        """Nadie puede eliminar ENV_ADMIN desde la vista"""
        self.client.login(username="env_admin", password="env123")
        
        response = self.client.get(
            reverse('delete_user', kwargs={'pk': self.env_admin.pk})
        )
        
        # Debería redirigir con error
        self.assertEqual(response.status_code, 302)
        # El ENV_ADMIN debería seguir existiendo
        self.assertTrue(User.objects.filter(pk=self.env_admin.pk).exists())
    
    def test_cannot_change_env_admin_role_from_view(self):
        """Nadie puede cambiar el rol de ENV_ADMIN desde la vista"""
        self.client.login(username="env_admin", password="env123")
        
        response = self.client.post(
            reverse('change_user_role', kwargs={'pk': self.env_admin.pk}),
            {'role': UserProfile.ROLE_WEB_ADMIN}
        )
        
        # Debería redirigir con error
        self.assertEqual(response.status_code, 302)
        self.env_admin.refresh_from_db()
        # El rol no debería haber cambiado
        self.assertEqual(self.env_admin.profile.role, UserProfile.ROLE_ENV_ADMIN)
    
    def test_web_admin_can_delete_user(self):
        """WEB_ADMIN puede eliminar USER"""
        self.client.login(username="web_admin", password="web123")
        
        response = self.client.post(
            reverse('delete_user', kwargs={'pk': self.target_user.pk})
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(pk=self.target_user.pk).exists())

def run_privilege_tests():
    """Ejecutar todos los tests de privilegios"""
    print("🔐 EJECUTANDO TESTS DE PRIVILEGIOS")
    print("=" * 40)
    
    # Ejecutar tests usando Django test runner
    import subprocess
    import sys
    
    command = [
        sys.executable, 
        "src/manage.py", 
        "test", 
        "tools.test_privileges",
        "--verbosity=2"
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ ¡TODOS LOS TESTS DE PRIVILEGIOS PASARON!")
            return True
        else:
            print("\n❌ ALGUNOS TESTS DE PRIVILEGIOS FALLARON")
            return False
            
    except Exception as e:
        print(f"Error ejecutando tests: {e}")
        return False

if __name__ == "__main__":
    success = run_privilege_tests()
    sys.exit(0 if success else 1)

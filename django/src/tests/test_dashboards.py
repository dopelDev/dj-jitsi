from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from models.models import UserProfile, SignupRequest, Meeting
from django.urls import reverse

User = get_user_model()


class TestDashboardRedirects(TestCase):
    """Tests para verificar que los dashboards redirijan correctamente según el rol"""
    
    def setUp(self):
        self.client = Client()
        
        # Limpiar cache antes de cada test
        from django.core.cache import cache
        cache.clear()
        
        # Crear usuarios con diferentes roles
        self.env_admin = User.objects.create_user("env_admin", "env@example.com", "pass123")
        self.web_admin = User.objects.create_user("web_admin", "web@example.com", "pass123")
        self.regular_user = User.objects.create_user("user", "user@example.com", "pass123")
        self.guest_user = User.objects.create_user("guest", "guest@example.com", "pass123")
        
        # Crear perfiles con roles específicos
        UserProfile.objects.create(user=self.env_admin, role=UserProfile.ROLE_ENV_ADMIN)
        UserProfile.objects.create(user=self.web_admin, role=UserProfile.ROLE_WEB_ADMIN)
        UserProfile.objects.create(user=self.regular_user, role=UserProfile.ROLE_USER)
        UserProfile.objects.create(user=self.guest_user, role=UserProfile.ROLE_GUEST)
    
    def test_env_admin_dashboard_content(self):
        """Test que ENV_ADMIN vea el contenido correcto en dashboard"""
        self.client.login(username="env_admin", password="pass123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard ENV Admin")
        self.assertContains(response, "ENV_ADMIN")
    
    def test_web_admin_dashboard_content(self):
        """Test que WEB_ADMIN vea el contenido correcto en dashboard"""
        self.client.login(username="web_admin", password="pass123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard Web Admin")
        self.assertContains(response, "WEB_ADMIN")
    
    def test_user_dashboard_content(self):
        """Test que USER vea el contenido correcto en dashboard"""
        self.client.login(username="user", password="pass123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mi Dashboard")
        self.assertContains(response, "USER")
    
    def test_guest_dashboard_content(self):
        """Test que GUEST vea el contenido correcto en dashboard"""
        self.client.login(username="guest", password="pass123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard Invitado")
        self.assertContains(response, "GUEST")


class TestDashboardRoleContent(TestCase):
    """Tests para verificar que cada rol ve el contenido correcto"""
    
    def setUp(self):
        self.client = Client()
        
        # Limpiar cache antes de cada test
        from django.core.cache import cache
        cache.clear()
        
        # Crear usuarios con diferentes roles
        self.env_admin = User.objects.create_user("env_admin", "env@example.com", "pass123")
        self.web_admin = User.objects.create_user("web_admin", "web@example.com", "pass123")
        self.regular_user = User.objects.create_user("user", "user@example.com", "pass123")
        self.guest_user = User.objects.create_user("guest", "guest@example.com", "pass123")
        
        # Crear perfiles con roles específicos
        UserProfile.objects.create(user=self.env_admin, role=UserProfile.ROLE_ENV_ADMIN)
        UserProfile.objects.create(user=self.web_admin, role=UserProfile.ROLE_WEB_ADMIN)
        UserProfile.objects.create(user=self.regular_user, role=UserProfile.ROLE_USER)
        UserProfile.objects.create(user=self.guest_user, role=UserProfile.ROLE_GUEST)
    
    def test_env_admin_sees_admin_content(self):
        """Test que ENV_ADMIN ve contenido de administrador"""
        self.client.login(username="env_admin", password="pass123")
        response = self.client.get(reverse("dashboard"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard ENV Admin")
        self.assertContains(response, "Total Usuarios")
        self.assertContains(response, "Panel Django Admin")
    
    def test_web_admin_sees_web_admin_content(self):
        """Test que WEB_ADMIN ve contenido de web admin"""
        self.client.login(username="web_admin", password="pass123")
        response = self.client.get(reverse("dashboard"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard Web Admin")
        self.assertContains(response, "Solicitudes Pendientes")
    
    def test_user_sees_user_content(self):
        """Test que USER ve contenido de usuario"""
        self.client.login(username="user", password="pass123")
        response = self.client.get(reverse("dashboard"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mi Dashboard")
        self.assertContains(response, "Mis Meetings")
    
    def test_guest_sees_guest_content(self):
        """Test que GUEST ve contenido limitado"""
        self.client.login(username="guest", password="pass123")
        response = self.client.get(reverse("dashboard"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard Invitado")
        self.assertContains(response, "Acceso Limitado")


class TestDashboardDataContent(TestCase):
    """Tests para verificar que el dashboard muestra datos correctos según el rol"""
    
    def setUp(self):
        self.client = Client()
        
        # Limpiar cache antes de cada test
        from django.core.cache import cache
        cache.clear()
        
        # Crear ENV_ADMIN
        self.env_admin = User.objects.create_user("env_admin", "env@example.com", "pass123")
        UserProfile.objects.create(user=self.env_admin, role=UserProfile.ROLE_ENV_ADMIN)
        
        # Crear algunos datos de prueba
        self.user1 = User.objects.create_user("user1", "user1@example.com", "pass123")
        self.user2 = User.objects.create_user("user2", "user2@example.com", "pass123")
        
        # Crear solicitudes
        SignupRequest.objects.create(
            email="test1@example.com",
            full_name="Test User 1",
            password_hash="hash1",
            status=SignupRequest.PENDING
        )
        SignupRequest.objects.create(
            email="test2@example.com",
            full_name="Test User 2",
            password_hash="hash2",
            status=SignupRequest.APPROVED
        )
        
        # Crear meetings
        Meeting.objects.create(room="room1", owner=self.user1)
        Meeting.objects.create(room="room2", owner=self.user2)
    
    def test_env_admin_dashboard_shows_statistics(self):
        """Test que ENV_ADMIN ve estadísticas del sistema"""
        self.client.login(username="env_admin", password="pass123")
        response = self.client.get(reverse("dashboard"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard ENV Admin")
        self.assertContains(response, "Total Usuarios")
        self.assertContains(response, "Solicitudes Pendientes")
        self.assertContains(response, "Solicitudes Aprobadas")
        self.assertContains(response, "Total Meetings")
        self.assertContains(response, "Panel Django Admin")
    
    def test_user_dashboard_shows_meetings(self):
        """Test que USER ve sus meetings"""
        UserProfile.objects.create(user=self.user1, role=UserProfile.ROLE_USER)
        self.client.login(username="user1", password="pass123")
        
        response = self.client.get(reverse("dashboard"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mi Dashboard")
        self.assertContains(response, "Mis Meetings")
        self.assertContains(response, "Crear Meeting")

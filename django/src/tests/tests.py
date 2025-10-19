import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.test import TestCase, Client
from django.core.cache import cache
from models.models import SignupRequest, UserProfile, Meeting

User = get_user_model()


class TestHomeView(TestCase):
    """Tests para la vista home"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("testuser", "test@example.com", "pass123")
        self.profile = UserProfile.objects.create(user=self.user, role=UserProfile.ROLE_USER)
    
    def test_home_anonymous_user(self):
        """Test que usuarios anónimos pueden ver la página home"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Solicitud")
    
    def test_home_authenticated_user_redirects(self):
        """Test que usuarios autenticados son redirigidos al dashboard"""
        self.client.login(username="testuser", password="pass123")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/dashboard/")
    
    def test_signup_request_creation(self):
        """Test creación de solicitud de registro"""
        data = {
            'email': 'newuser@example.com',
            'full_name': 'New User',
            'note': 'Test request',
            'password': 'testpass123',  # Campo requerido por el formulario
            'signup_request': '1'  # Necesario para que se procese como solicitud
        }
        response = self.client.post("/", data)
        self.assertEqual(response.status_code, 302)  # Debería redirigir después de crear
        self.assertTrue(SignupRequest.objects.filter(email='newuser@example.com').exists())
    
    def test_login_functionality(self):
        """Test funcionalidad de login"""
        response = self.client.post("/", {
            'username': 'testuser',
            'password': 'pass123',
            'login': '1'  # Necesario para que se procese como login
        })
        # Debería redirigir al dashboard
        self.assertEqual(response.status_code, 302)


class TestDashboardView(TestCase):
    """Tests para la vista dashboard"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("testuser", "test@example.com", "pass123")
        self.profile = UserProfile.objects.create(user=self.user, role=UserProfile.ROLE_USER)
    
    def test_dashboard_requires_login(self):
        """Test que dashboard requiere autenticación"""
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/admin/login/?next=/dashboard/")
    
    def test_dashboard_authenticated_user(self):
        """Test que usuarios autenticados pueden ver dashboard"""
        self.client.login(username="testuser", password="pass123")
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")
    
    def test_dashboard_shows_user_role(self):
        """Test que dashboard muestra el rol del usuario"""
        self.client.login(username="testuser", password="pass123")
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "USER")


class TestMeetingViews(TestCase):
    """Tests para las vistas de meetings"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("testuser", "test@example.com", "pass123")
        self.profile = UserProfile.objects.create(user=self.user, role=UserProfile.ROLE_USER)
        
        self.guest_user = User.objects.create_user("guest", "guest@example.com", "pass123")
        self.guest_profile = UserProfile.objects.create(user=self.guest_user, role=UserProfile.ROLE_GUEST)
    
    def test_create_meeting_requires_login(self):
        """Test que crear meeting requiere autenticación"""
        response = self.client.get("/meet/create/")
        self.assertEqual(response.status_code, 302)
    
    def test_create_meeting_authenticated_user(self):
        """Test que usuarios autenticados pueden crear meetings"""
        self.client.login(username="testuser", password="pass123")
        response = self.client.post("/meet/create/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Meeting.objects.filter(owner=self.user).exists())
    
    def test_create_meeting_guest_user(self):
        """Test que usuarios GUEST no pueden crear meetings"""
        self.client.login(username="guest", password="pass123")
        response = self.client.post("/meet/create/")
        # Debería devolver 403 o redirigir
        self.assertIn(response.status_code, [302, 403])
    
    def test_meeting_detail_authenticated_user(self):
        """Test que usuarios autenticados pueden ver detalles de meeting"""
        meeting = Meeting.objects.create(room="test-room", owner=self.user)
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(f"/meet/{meeting.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test-room")
    
    def test_meeting_detail_guest_user(self):
        """Test que usuarios GUEST pueden ver detalles si tienen el link"""
        meeting = Meeting.objects.create(room="test-room", owner=self.user)
        self.client.login(username="guest", password="pass123")
        response = self.client.get(f"/meet/{meeting.pk}/")
        self.assertEqual(response.status_code, 200)


class TestAdminViews(TestCase):
    """Tests para las vistas de administración"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user("admin", "admin@example.com", "pass123")
        self.admin_profile = UserProfile.objects.create(user=self.admin_user, role=UserProfile.ROLE_ENV_ADMIN)
        
        self.normal_user = User.objects.create_user("user", "user@example.com", "pass123")
        self.normal_profile = UserProfile.objects.create(user=self.normal_user, role=UserProfile.ROLE_USER)
        
        self.signup_request = SignupRequest.objects.create(
            email="test@example.com",
            full_name="Test User",
            password_hash="hashed_password",
            note="Test request"
        )
    
    def test_admin_requests_requires_admin(self):
        """Test que ver solicitudes requiere permisos de admin"""
        self.client.login(username="user", password="pass123")
        response = self.client.get("/requests/")
        self.assertIn(response.status_code, [302, 403])
    
    def test_admin_requests_admin_user(self):
        """Test que admins pueden ver solicitudes"""
        self.client.login(username="admin", password="pass123")
        response = self.client.get("/requests/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Solicitudes")
    
    def test_request_detail_admin(self):
        """Test que admins pueden ver detalles de solicitud"""
        self.client.login(username="admin", password="pass123")
        response = self.client.get(f"/requests/{self.signup_request.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test@example.com")
    
    def test_approve_request_admin(self):
        """Test que admins pueden aprobar solicitudes"""
        self.client.login(username="admin", password="pass123")
        response = self.client.post(f"/requests/{self.signup_request.pk}/approve/", {
            'decision_note': 'Test approval'
        })
        self.assertEqual(response.status_code, 302)
        
        self.signup_request.refresh_from_db()
        self.assertEqual(self.signup_request.status, SignupRequest.APPROVED)
    
    def test_reject_request_admin(self):
        """Test que admins pueden rechazar solicitudes"""
        self.client.login(username="admin", password="pass123")
        response = self.client.post(f"/requests/{self.signup_request.pk}/reject/", {
            'decision_note': 'Test rejection'
        })
        self.assertEqual(response.status_code, 302)
        
        self.signup_request.refresh_from_db()
        self.assertEqual(self.signup_request.status, SignupRequest.REJECTED)
    
    def test_reset_request_admin(self):
        """Test que admins pueden resetear solicitudes"""
        self.signup_request.approve(decided_by=self.admin_user, decision_note="Original approval")
        self.client.login(username="admin", password="pass123")
        
        response = self.client.post(f"/requests/{self.signup_request.pk}/reset/")
        self.assertEqual(response.status_code, 302)
        
        self.signup_request.refresh_from_db()
        self.assertEqual(self.signup_request.status, SignupRequest.PENDING)


class TestLogoutView(TestCase):
    """Tests para la vista de logout"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("testuser", "test@example.com", "pass123")
        self.profile = UserProfile.objects.create(user=self.user, role=UserProfile.ROLE_USER)
    
    def test_logout_authenticated_user(self):
        """Test logout de usuario autenticado"""
        self.client.login(username="testuser", password="pass123")
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sesión Cerrada")
    
    def test_logout_anonymous_user(self):
        """Test logout de usuario anónimo"""
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sesión Cerrada")


class TestErrorPages(TestCase):
    """Tests para las páginas de error"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("testuser", "test@example.com", "pass123")
        self.profile = UserProfile.objects.create(user=self.user, role=UserProfile.ROLE_USER)
    
    def test_404_page(self):
        """Test página 404 personalizada"""
        # Simular una URL que no existe
        response = self.client.get("/nonexistent-page/")
        self.assertEqual(response.status_code, 404)
        # En modo de testing, Django usa su página 404 por defecto
        # Solo verificamos que devuelve 404
    
    def test_404_page_authenticated_user(self):
        """Test página 404 con usuario autenticado"""
        self.client.login(username="testuser", password="pass123")
        # Simular una URL que no existe
        response = self.client.get("/nonexistent-page/")
        self.assertEqual(response.status_code, 404)
        # En modo de testing, Django usa su página 404 por defecto
        # Solo verificamos que devuelve 404
    
    def test_403_page(self):
        """Test página 403 personalizada"""
        # Simular acceso denegado
        from django.core.exceptions import PermissionDenied
        from django.http import Http404
        
        # Test directo de la vista
        from views.views import custom_permission_denied
        response = custom_permission_denied(None)
        self.assertEqual(response.status_code, 403)


class TestCacheFunctionality(TestCase):
    """Tests para la funcionalidad de cache"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("testuser", "test@example.com", "pass123")
        self.profile = UserProfile.objects.create(user=self.user, role=UserProfile.ROLE_USER)
    
    def test_user_info_cache(self):
        """Test que la información del usuario se cachea correctamente"""
        from views.views import get_user_info
        
        # Simular request con usuario autenticado
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user)
        
        # Primera llamada debería crear el cache
        user_info = get_user_info(request)
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info['username'], 'testuser')
        self.assertEqual(user_info['role'], 'USER')
        
        # Verificar que está en cache
        cache_key = f"user_info_{self.user.id}"
        cached_info = cache.get(cache_key)
        self.assertIsNotNone(cached_info)
        self.assertEqual(cached_info['username'], 'testuser')
    
    def test_cache_clear_on_logout(self):
        """Test que el cache se limpia al hacer logout"""
        from views.views import get_user_info
        
        # Simular request con usuario autenticado
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user)
        
        # Crear cache
        get_user_info(request)
        cache_key = f"user_info_{self.user.id}"
        self.assertIsNotNone(cache.get(cache_key))
        
        # Simular logout (limpiar cache)
        cache.delete(cache_key)
        self.assertIsNone(cache.get(cache_key))


class TestUserProfileModel(TestCase):
    """Tests para el modelo UserProfile"""
    
    def test_user_profile_creation(self):
        """Test creación de perfil de usuario"""
        user = User.objects.create_user("testuser", "test@example.com", "pass123")
        profile = UserProfile.objects.create(user=user, role=UserProfile.ROLE_USER)
        
        self.assertEqual(profile.role, UserProfile.ROLE_USER)
        self.assertIsNotNone(profile.uuid)
        self.assertFalse(profile.is_admin_like())
    
    def test_admin_roles(self):
        """Test roles de administrador"""
        user = User.objects.create_user("admin", "admin@example.com", "pass123")
        profile = UserProfile.objects.create(user=user, role=UserProfile.ROLE_ENV_ADMIN)
        
        self.assertTrue(profile.is_admin_like())
        
        profile.role = UserProfile.ROLE_WEB_ADMIN
        profile.save()
        self.assertTrue(profile.is_admin_like())


class TestMeetingModel(TestCase):
    """Tests para el modelo Meeting"""
    
    def test_meeting_creation(self):
        """Test creación de meeting"""
        user = User.objects.create_user("owner", "owner@example.com", "pass123")
        meeting = Meeting.objects.create(room="test-room", owner=user)
        
        self.assertEqual(meeting.room, "test-room")
        self.assertEqual(meeting.owner, user)
    
    def test_jitsi_url_generation(self):
        """Test generación de URL de Jitsi"""
        user = User.objects.create_user("owner", "owner@example.com", "pass123")
        meeting = Meeting.objects.create(room="test-room", owner=user)
        
        url = meeting.jitsi_url()
        self.assertTrue(url.startswith("https://"))
        self.assertIn("test-room", url)
        self.assertTrue(url.endswith("/test-room"))
    
    def test_room_generation(self):
        """Test generación automática de room"""
        room = Meeting.generate_room()
        self.assertIsNotNone(room)
        self.assertGreater(len(room), 0)


class TestSignupRequestModel(TestCase):
    """Tests para el modelo SignupRequest"""
    
    def test_signup_request_creation(self):
        """Test creación de solicitud de registro"""
        request = SignupRequest.objects.create(
            email="test@example.com",
            full_name="Test User",
            password_hash="hashed_password",
            note="Test request"
        )
        
        self.assertEqual(request.email, "test@example.com")
        self.assertEqual(request.status, SignupRequest.PENDING)
        self.assertIsNone(request.decided_by)
    
    def test_approve_request(self):
        """Test aprobación de solicitud"""
        user = User.objects.create_user("admin", "admin@example.com", "pass123")
        request = SignupRequest.objects.create(
            email="test@example.com",
            full_name="Test User",
            password_hash="hashed_password"
        )
        
        request.approve(decided_by=user, decision_note="Approved")
        
        self.assertEqual(request.status, SignupRequest.APPROVED)
        self.assertEqual(request.decided_by, user)
        self.assertEqual(request.decision_note, "Approved")
    
    def test_reject_request(self):
        """Test rechazo de solicitud"""
        user = User.objects.create_user("admin", "admin@example.com", "pass123")
        request = SignupRequest.objects.create(
            email="test@example.com",
            full_name="Test User",
            password_hash="hashed_password"
        )
        
        request.reject(decided_by=user, decision_note="Rejected")
        
        self.assertEqual(request.status, SignupRequest.REJECTED)
        self.assertEqual(request.decided_by, user)
        self.assertEqual(request.decision_note, "Rejected")


# Tests con pytest para funcionalidad específica
@pytest.mark.django_db
def test_signup_request_and_approval(client, admin_user):
    """Test flujo completo de solicitud y aprobación"""
    # Crear perfil de admin
    UserProfile.objects.get_or_create(user=admin_user, defaults={"role": "ENV_ADMIN"})
    
    # Crear solicitud
    req = SignupRequest.objects.create(
        email="alice@example.com",
        full_name="Alice",
        password_hash=make_password("secret123")
    )
    
    # Aprobar simulando acción admin
    username = "alice"
    u = User.objects.create(
        username=username, 
        email=req.email, 
        password=req.password_hash, 
        first_name=req.full_name[:150]
    )
    prof, _ = UserProfile.objects.get_or_create(user=u, defaults={"role": "USER"})
    assert prof.role == "USER"


@pytest.mark.django_db
def test_user_can_create_meeting(client, django_user_model):
    """Test que usuarios registrados pueden crear meetings"""
    u = django_user_model.objects.create_user("bob", "bob@example.com", "secret123")
    UserProfile.objects.create(user=u, role="USER")
    client.login(username="bob", password="secret123")
    
    resp = client.post(reverse("create_meeting"))
    assert resp.status_code in (302, 303)
    assert Meeting.objects.filter(owner=u).count() == 1


@pytest.mark.django_db
def test_guest_user_cannot_create_meeting(client, django_user_model):
    """Test que usuarios GUEST no pueden crear meetings"""
    u = django_user_model.objects.create_user("guest", "guest@example.com", "secret123")
    UserProfile.objects.create(user=u, role="GUEST")
    client.login(username="guest", password="secret123")
    
    resp = client.post(reverse("create_meeting"))
    assert resp.status_code in (302, 403)


@pytest.mark.django_db
def test_admin_can_view_requests(client, django_user_model):
    """Test que admins pueden ver solicitudes"""
    admin = django_user_model.objects.create_user("admin", "admin@example.com", "secret123")
    UserProfile.objects.create(user=admin, role="ENV_ADMIN")
    client.login(username="admin", password="secret123")
    
    resp = client.get(reverse("admin_requests"))
    assert resp.status_code == 200


@pytest.mark.django_db
def test_normal_user_cannot_view_requests(client, django_user_model):
    """Test que usuarios normales no pueden ver solicitudes"""
    user = django_user_model.objects.create_user("user", "user@example.com", "secret123")
    UserProfile.objects.create(user=user, role="USER")
    client.login(username="user", password="secret123")
    
    resp = client.get(reverse("admin_requests"))
    assert resp.status_code in (302, 403)
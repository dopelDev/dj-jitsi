import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from .models import SignupRequest, Meeting
from .jitsi import jitsi_jwt, generate_meeting_link, create_secure_room


User = get_user_model()


class SignupRequestModelTest(TestCase):
    """Tests para el modelo SignupRequest"""
    
    def setUp(self):
        self.signup_request = SignupRequest.objects.create(
            email="test@example.com",
            full_name="Test User",
            note="Test note"
        )
    
    def test_signup_request_creation(self):
        """Test que se puede crear una solicitud"""
        self.assertEqual(self.signup_request.email, "test@example.com")
        self.assertEqual(self.signup_request.full_name, "Test User")
        self.assertEqual(self.signup_request.status, SignupRequest.PENDING)
        self.assertIsNotNone(self.signup_request.created_at)
    
    def test_signup_request_str(self):
        """Test del método __str__"""
        expected = "Test User <test@example.com> [pending]"
        self.assertEqual(str(self.signup_request), expected)
    
    def test_approve_method(self):
        """Test del método approve"""
        self.signup_request.approve()
        self.assertEqual(self.signup_request.status, SignupRequest.APPROVED)
        
        # Verificar que se creó el usuario
        username = "test"
        self.assertTrue(User.objects.filter(username=username).exists())
    
    def test_reject_method(self):
        """Test del método reject"""
        self.signup_request.reject()
        self.assertEqual(self.signup_request.status, SignupRequest.REJECTED)
    
    def test_unique_email_constraint(self):
        """Test que el email debe ser único"""
        with self.assertRaises(Exception):
            SignupRequest.objects.create(
                email="test@example.com",
                full_name="Another User"
            )


class SignupRequestAdminTest(TestCase):
    """Tests para las acciones del admin"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        self.client = Client()
        self.client.login(username="admin", password="admin123")
        
        # Crear solicitudes de prueba
        self.pending_request = SignupRequest.objects.create(
            email="pending@example.com",
            full_name="Pending User"
        )
        self.approved_request = SignupRequest.objects.create(
            email="approved@example.com",
            full_name="Approved User",
            status=SignupRequest.APPROVED
        )
    
    def test_admin_approve_action(self):
        """Test de la acción de aprobar en admin"""
        from django.contrib.admin.sites import AdminSite
        from .admin import SignupRequestAdmin
        
        admin_site = AdminSite()
        admin_instance = SignupRequestAdmin(SignupRequest, admin_site)
        
        # Ejecutar acción de aprobar
        queryset = SignupRequest.objects.filter(status=SignupRequest.PENDING)
        admin_instance.approve_requests(self.admin_user, queryset)
        
        # Verificar que se aprobó
        self.pending_request.refresh_from_db()
        self.assertEqual(self.pending_request.status, SignupRequest.APPROVED)
        
        # Verificar que se creó el usuario
        self.assertTrue(User.objects.filter(username="pending").exists())
    
    def test_admin_reject_action(self):
        """Test de la acción de rechazar en admin"""
        from django.contrib.admin.sites import AdminSite
        from .admin import SignupRequestAdmin
        
        admin_site = AdminSite()
        admin_instance = SignupRequestAdmin(SignupRequest, admin_site)
        
        # Ejecutar acción de rechazar
        queryset = SignupRequest.objects.filter(status=SignupRequest.PENDING)
        admin_instance.reject_requests(self.admin_user, queryset)
        
        # Verificar que se rechazó
        self.pending_request.refresh_from_db()
        self.assertEqual(self.pending_request.status, SignupRequest.REJECTED)


class ViewsTest(TestCase):
    """Tests para las vistas"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        self.regular_user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="user123"
        )
        self.client = Client()
        
        # Crear solicitudes de prueba
        SignupRequest.objects.create(
            email="test1@example.com",
            full_name="Test User 1"
        )
        SignupRequest.objects.create(
            email="test2@example.com",
            full_name="Test User 2",
            status=SignupRequest.APPROVED
        )
    
    def test_dashboard_requires_staff(self):
        """Test que el dashboard requiere usuario staff"""
        # Usuario no autenticado
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect a login
        
        # Usuario regular (no staff)
        self.client.login(username="user", password="user123")
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Usuario staff
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_context(self):
        """Test que el dashboard tiene el contexto correcto"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('pending', response.context)
        self.assertIn('approved', response.context)
        self.assertIn('rejected', response.context)
        self.assertIn('recent', response.context)
    
    def test_request_list_requires_staff(self):
        """Test que la lista de solicitudes requiere usuario staff"""
        self.client.login(username="user", password="user123")
        response = self.client.get(reverse('request_list'))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_request_detail_requires_staff(self):
        """Test que el detalle de solicitud requiere usuario staff"""
        request_obj = SignupRequest.objects.first()
        self.client.login(username="user", password="user123")
        response = self.client.get(reverse('request_detail', args=[request_obj.pk]))
        self.assertEqual(response.status_code, 403)  # Forbidden


class JitsiIntegrationTest(TestCase):
    """Tests para la integración con Jitsi"""
    
    def setUp(self):
        import os
        # Configurar variables de entorno para testing
        os.environ['JITSI_BASE_URL'] = 'https://meet.example.com'
        os.environ['JITSI_JWT_SECRET'] = 'test_secret'
        os.environ['JITSI_APP_ID'] = 'test_app'
    
    def test_generate_meeting_link_without_jwt(self):
        """Test generar link sin JWT"""
        import os
        del os.environ['JITSI_JWT_SECRET']  # Remover secret para este test
        
        link = generate_meeting_link("test-room", "test-user")
        expected = "https://meet.example.com/test-room"
        self.assertEqual(link, expected)
    
    def test_generate_meeting_link_with_jwt(self):
        """Test generar link con JWT"""
        link = generate_meeting_link("test-room", "test-user")
        self.assertTrue(link.startswith("https://meet.example.com/test-room?jwt="))
    
    def test_create_secure_room(self):
        """Test crear sala segura"""
        room_info = create_secure_room("test-room", "test-user")
        
        self.assertEqual(room_info['room_name'], "test-room")
        self.assertEqual(room_info['user_name'], "test-user")
        self.assertTrue(room_info['is_secure'])
        self.assertIn('meeting_link', room_info)


class MeetingModelTest(TestCase):
    """Tests para el modelo Meeting"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="test123"
        )
        self.meeting = Meeting.objects.create(
            room_name="test-room",
            owner=self.user,
            start_time=timezone.now()
        )
    
    def test_meeting_creation(self):
        """Test que se puede crear una reunión"""
        self.assertEqual(self.meeting.room_name, "test-room")
        self.assertEqual(self.meeting.owner, self.user)
        self.assertTrue(self.meeting.is_active)
    
    def test_meeting_str(self):
        """Test del método __str__"""
        expected = "Reunión test-room - testuser"
        self.assertEqual(str(self.meeting), expected)
    
    def test_generate_jitsi_link(self):
        """Test generar link de Jitsi para la reunión"""
        # Mock del método generate_meeting_link
        def mock_generate_link(room_name, user_name):
            return f"https://meet.example.com/{room_name}"
        
        # Reemplazar temporalmente el método
        from accounts import jitsi
        original_method = jitsi.generate_meeting_link
        jitsi.generate_meeting_link = mock_generate_link
        
        try:
            link = self.meeting.generate_jitsi_link()
            expected = "https://meet.example.com/test-room"
            self.assertEqual(link, expected)
        finally:
            # Restaurar método original
            jitsi.generate_meeting_link = original_method


@pytest.mark.django_db
class PytestIntegrationTest:
    """Tests usando pytest para integración"""
    
    def test_signup_request_creation_pytest(self):
        """Test de creación usando pytest"""
        request = SignupRequest.objects.create(
            email="pytest@example.com",
            full_name="Pytest User"
        )
        assert request.email == "pytest@example.com"
        assert request.status == SignupRequest.PENDING
    
    def test_user_creation_on_approval_pytest(self):
        """Test de creación de usuario al aprobar usando pytest"""
        request = SignupRequest.objects.create(
            email="approve@example.com",
            full_name="Approve User"
        )
        
        # Verificar que no existe el usuario
        assert not User.objects.filter(username="approve").exists()
        
        # Aprobar solicitud
        request.approve()
        
        # Verificar que se creó el usuario
        assert User.objects.filter(username="approve").exists()
        assert request.status == SignupRequest.APPROVED

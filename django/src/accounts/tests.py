import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.test import TestCase
from .models import SignupRequest, UserProfile, Meeting

User = get_user_model()


@pytest.mark.django_db
def test_signup_request_and_approval(client, admin_user):
    """Test signup request flow and approval"""
    # ENV_ADMIN profile
    UserProfile.objects.get_or_create(user=admin_user, defaults={"role": "ENV_ADMIN"})
    
    # crear solicitud
    req = SignupRequest.objects.create(
        email="alice@example.com",
        full_name="Alice",
        password_hash=make_password("secret123")
    )
    
    # aprobar simulando acción admin
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
    """Test that registered users can create meetings"""
    u = django_user_model.objects.create_user("bob", "bob@example.com", "secret123")
    UserProfile.objects.create(user=u, role="USER")
    client.login(username="bob", password="secret123")
    
    resp = client.post(reverse("create_meeting"))
    assert resp.status_code in (302, 303)
    assert Meeting.objects.filter(owner=u).count() == 1


class UserProfileTest(TestCase):
    def test_user_profile_creation(self):
        """Test UserProfile creation with UUID"""
        user = User.objects.create_user("testuser", "test@example.com", "pass123")
        profile = UserProfile.objects.create(user=user, role=UserProfile.ROLE_USER)
        
        self.assertEqual(profile.role, UserProfile.ROLE_USER)
        self.assertIsNotNone(profile.uuid)
        self.assertTrue(profile.is_admin_like() == False)
        
    def test_admin_roles(self):
        """Test admin role detection"""
        user = User.objects.create_user("admin", "admin@example.com", "pass123")
        profile = UserProfile.objects.create(user=user, role=UserProfile.ROLE_ENV_ADMIN)
        
        self.assertTrue(profile.is_admin_like())
        
        profile.role = UserProfile.ROLE_WEB_ADMIN
        profile.save()
        self.assertTrue(profile.is_admin_like())


class MeetingTest(TestCase):
    def test_meeting_creation(self):
        """Test meeting creation and room generation"""
        user = User.objects.create_user("owner", "owner@example.com", "pass123")
        meeting = Meeting.objects.create(room="test-room", owner=user)
        
        self.assertEqual(meeting.room, "test-room")
        self.assertEqual(meeting.owner, user)
        
    def test_jitsi_url_generation(self):
        """Test Jitsi URL generation"""
        user = User.objects.create_user("owner", "owner@example.com", "pass123")
        meeting = Meeting.objects.create(room="test-room", owner=user)
        
        url = meeting.jitsi_url()
        self.assertTrue(url.startswith("https://"))
        self.assertIn("test-room", url)
        self.assertTrue(url.endswith("/test-room"))


class AdminRequestTests(TestCase):
    def setUp(self):
        # Crear usuario admin
        self.admin_user = User.objects.create_user("admin", "admin@example.com", "pass123")
        self.admin_profile = UserProfile.objects.create(user=self.admin_user, role=UserProfile.ROLE_ENV_ADMIN)
        
        # Crear usuario normal
        self.normal_user = User.objects.create_user("user", "user@example.com", "pass123")
        self.normal_profile = UserProfile.objects.create(user=self.normal_user, role=UserProfile.ROLE_USER)
        
        # Crear solicitud de prueba
        self.signup_request = SignupRequest.objects.create(
            email="test@example.com",
            full_name="Test User",
            password_hash="hashed_password",
            note="Test request"
        )

    def test_admin_can_view_request_detail(self):
        """Test que admin puede ver detalles de solicitud"""
        self.client.login(username="admin", password="pass123")
        response = self.client.get(f"/requests/{self.signup_request.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test@example.com")

    def test_normal_user_cannot_view_request_detail(self):
        """Test que usuario normal no puede ver detalles de solicitud"""
        self.client.login(username="user", password="pass123")
        response = self.client.get(f"/requests/{self.signup_request.pk}/")
        # Debería redirigir a login o devolver 403
        self.assertIn(response.status_code, [302, 403])

    def test_admin_can_approve_request(self):
        """Test que admin puede aprobar solicitud"""
        self.client.login(username="admin", password="pass123")
        
        # Aprobar solicitud
        response = self.client.post(f"/requests/{self.signup_request.pk}/approve/", {
            'decision_note': 'Test approval'
        })
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la solicitud fue aprobada
        self.signup_request.refresh_from_db()
        self.assertEqual(self.signup_request.status, SignupRequest.APPROVED)
        self.assertEqual(self.signup_request.decided_by, self.admin_user)
        self.assertEqual(self.signup_request.decision_note, 'Test approval')

    def test_admin_can_reject_request(self):
        """Test que admin puede rechazar solicitud"""
        self.client.login(username="admin", password="pass123")
        
        # Rechazar solicitud
        response = self.client.post(f"/requests/{self.signup_request.pk}/reject/", {
            'decision_note': 'Test rejection'
        })
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la solicitud fue rechazada
        self.signup_request.refresh_from_db()
        self.assertEqual(self.signup_request.status, SignupRequest.REJECTED)
        self.assertEqual(self.signup_request.decided_by, self.admin_user)
        self.assertEqual(self.signup_request.decision_note, 'Test rejection')

    def test_admin_can_reset_request(self):
        """Test que admin puede resetear solicitud"""
        # Primero aprobar la solicitud
        self.signup_request.approve(decided_by=self.admin_user, decision_note="Original approval")
        
        self.client.login(username="admin", password="pass123")
        
        # Resetear solicitud
        response = self.client.post(f"/requests/{self.signup_request.pk}/reset/")
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la solicitud fue reseteada
        self.signup_request.refresh_from_db()
        self.assertEqual(self.signup_request.status, SignupRequest.PENDING)
        self.assertIsNone(self.signup_request.decided_by)
        self.assertEqual(self.signup_request.decision_note, "")

    def test_normal_user_cannot_approve_request(self):
        """Test que usuario normal no puede aprobar solicitud"""
        self.client.login(username="user", password="pass123")
        response = self.client.post(f"/requests/{self.signup_request.pk}/approve/")
        # Debería redirigir a login o devolver 403
        self.assertIn(response.status_code, [302, 403])

    def test_request_list_shows_stats(self):
        """Test que la lista de solicitudes muestra estadísticas"""
        self.client.login(username="admin", password="pass123")
        response = self.client.get("/requests/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total Solicitudes")
        self.assertContains(response, "Pendientes")

    def test_request_list_filtering(self):
        """Test que los filtros de la lista funcionan"""
        self.client.login(username="admin", password="pass123")
        response = self.client.get("/requests/?status=pending")
        self.assertEqual(response.status_code, 200)
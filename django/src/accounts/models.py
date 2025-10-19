from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
import uuid

User = get_user_model()

class SignupRequest(models.Model):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected")
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200)
    password_hash = models.CharField(max_length=255)  # guarda make_password(...)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="decisions")
    decision_note = models.TextField(blank=True, help_text="Nota del administrador sobre la decisión")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Solicitud de Registro"
        verbose_name_plural = "Solicitudes de Registro"

    def __str__(self):
        return f"{self.full_name} <{self.email}> [{self.status}]"

    def approve(self, decided_by=None, decision_note=""):
        """Aprobar la solicitud y crear usuario si no existe"""
        from django.utils.timezone import now
        
        self.status = self.APPROVED
        self.decided_at = now()
        self.decided_by = decided_by
        self.decision_note = decision_note
        self.save()
        
        # Crear usuario si no existe
        username = self.email.split("@")[0]
        if not User.objects.filter(username=username).exists():
            user = User.objects.create(
                username=username,
                email=self.email,
                password=self.password_hash,  # ya hashed
                first_name=self.full_name[:150]
            )
            # Crear perfil con rol USER
            UserProfile.objects.get_or_create(user=user, defaults={"role": UserProfile.ROLE_USER})

    def reject(self, decided_by=None, decision_note=""):
        """Rechazar la solicitud"""
        from django.utils.timezone import now
        self.status = self.REJECTED
        self.decided_at = now()
        self.decided_by = decided_by
        self.decision_note = decision_note
        self.save()


class UserProfile(models.Model):
    ROLE_ENV_ADMIN = "ENV_ADMIN"
    ROLE_WEB_ADMIN = "WEB_ADMIN"
    ROLE_USER = "USER"
    ROLE_GUEST = "GUEST"
    ROLE_CHOICES = [
        (ROLE_ENV_ADMIN, "Env Admin"),
        (ROLE_WEB_ADMIN, "Web Admin"),
        (ROLE_USER, "User"),
        (ROLE_GUEST, "Guest"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER)

    def is_admin_like(self):
        return self.role in {self.ROLE_ENV_ADMIN, self.ROLE_WEB_ADMIN}

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Meeting(models.Model):
    """Modelo para gestionar reuniones Jitsi"""
    room = models.CharField(max_length=120, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meetings")
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_room():
        return "room-" + get_random_string(8)

    def jitsi_url(self):
        # MVP sin JWT
        from django.conf import settings
        base = getattr(settings, "JITSI_BASE_URL", "https://meet.jit.si")
        return f"{base}/{self.room}"

    def __str__(self):
        return f"{self.room} by {self.owner.username}"
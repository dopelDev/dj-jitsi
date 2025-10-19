from django.db import models
from django.contrib.auth import get_user_model


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
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Solicitud de Registro"
        verbose_name_plural = "Solicitudes de Registro"

    def __str__(self):
        return f"{self.full_name} <{self.email}> [{self.status}]"

    def approve(self):
        """Aprobar la solicitud y crear usuario si no existe"""
        from django.contrib.auth.models import User
        
        self.status = self.APPROVED
        self.save()
        
        # Crear usuario si no existe
        username = self.email.split("@")[0]
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(
                username=username, 
                email=self.email, 
                password=User.objects.make_random_password()
            )

    def reject(self):
        """Rechazar la solicitud"""
        self.status = self.REJECTED
        self.save()


class Meeting(models.Model):
    """Modelo para gestionar reuniones Jitsi (Fase 8+)"""
    room_name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    jwt_token = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Reunión"
        verbose_name_plural = "Reuniones"

    def __str__(self):
        return f"Reunión {self.room_name} - {self.owner.username}"

    def generate_jitsi_link(self):
        """Genera el link de Jitsi para esta reunión"""
        from .jitsi import generate_meeting_link
        return generate_meeting_link(self.room_name, self.owner.username)
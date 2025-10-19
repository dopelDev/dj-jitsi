from django.contrib import admin
from django.utils.timezone import now
from django.contrib.auth.models import User
from .models import SignupRequest


@admin.register(SignupRequest)
class SignupRequestAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "status", "created_at", "decided_at")
    list_filter = ("status", "created_at")
    search_fields = ("email", "full_name", "note")
    readonly_fields = ("created_at",)
    actions = ["approve_requests", "reject_requests", "reset_to_pending"]

    @admin.action(description="Aprobar solicitudes seleccionadas y crear usuarios")
    def approve_requests(self, request, queryset):
        count = 0
        for req in queryset.filter(status=SignupRequest.PENDING):
            # Crear usuario si no existe
            username = req.email.split("@")[0]
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username, 
                    email=req.email, 
                    password=User.objects.make_random_password()
                )
            req.status = SignupRequest.APPROVED
            req.decided_at = now()
            req.save()
            count += 1
        
        self.message_user(request, f"{count} solicitudes aprobadas exitosamente.")

    @admin.action(description="Rechazar solicitudes seleccionadas")
    def reject_requests(self, request, queryset):
        updated = queryset.filter(status=SignupRequest.PENDING).update(
            status=SignupRequest.REJECTED, 
            decided_at=now()
        )
        self.message_user(request, f"{updated} solicitudes rechazadas.")

    @admin.action(description="Resetear a pendiente")
    def reset_to_pending(self, request, queryset):
        updated = queryset.update(
            status=SignupRequest.PENDING, 
            decided_at=None
        )
        self.message_user(request, f"{updated} solicitudes reseteadas a pendiente.")

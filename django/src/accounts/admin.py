from django.contrib import admin
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .models import SignupRequest, UserProfile, Meeting

User = get_user_model()


@admin.register(SignupRequest)
class SignupRequestAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "status", "created_at", "decided_at")
    list_filter = ("status",)
    search_fields = ("email", "full_name", "note")
    actions = ["approve_requests", "reject_requests", "reset_to_pending"]

    @admin.action(description="Approve and create users")
    def approve_requests(self, request, queryset):
        for req in queryset.filter(status=SignupRequest.PENDING):
            username = req.email.split("@")[0]
            if User.objects.filter(email=req.email).exists():
                user = User.objects.get(email=req.email)
            else:
                user = User.objects.create(
                    username=username,
                    email=req.email,
                    password=req.password_hash,  # ya hashed
                    first_name=req.full_name[:150]
                )
            UserProfile.objects.get_or_create(user=user, defaults={"role": UserProfile.ROLE_USER})
            req.status = SignupRequest.APPROVED
            req.decided_at = now()
            req.save()

    @admin.action(description="Reject")
    def reject_requests(self, request, queryset):
        queryset.update(status=SignupRequest.REJECTED, decided_at=now())

    @admin.action(description="Reset to pending")
    def reset_to_pending(self, request, queryset):
        queryset.update(status=SignupRequest.PENDING, decided_at=None)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "uuid")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email", "uuid")


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("room", "owner", "created_at")

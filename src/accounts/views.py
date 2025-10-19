from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import SignupRequest


is_staff = user_passes_test(lambda u: u.is_staff)


@login_required
@is_staff
def dashboard(request):
    """Dashboard principal con métricas y solicitudes recientes"""
    ctx = {
        "pending": SignupRequest.objects.filter(status="pending").count(),
        "approved": SignupRequest.objects.filter(status="approved").count(),
        "rejected": SignupRequest.objects.filter(status="rejected").count(),
        "recent": SignupRequest.objects.order_by("-created_at")[:10],
    }
    return render(request, "accounts/dashboard.html", ctx)


@login_required
@is_staff
def request_list(request):
    """Lista todas las solicitudes"""
    qs = SignupRequest.objects.order_by("-created_at")
    return render(request, "accounts/request_list.html", {"requests": qs})


@login_required
@is_staff
def request_detail(request, pk):
    """Detalle de una solicitud específica"""
    obj = get_object_or_404(SignupRequest, pk=pk)
    return render(request, "accounts/request_detail.html", {"obj": obj})

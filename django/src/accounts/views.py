from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from .models import SignupRequest, Meeting, UserProfile
from .forms import SignupRequestForm
from .permissions import require_admin, require_registered

User = get_user_model()


def home(request):
    """Homepage pública: formulario de solicitud + login"""
    if request.method == "POST" and "signup_request" in request.POST:
        form = SignupRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Solicitud enviada. Te avisaremos cuando sea aprobada.")
            return redirect("home")
    else:
        form = SignupRequestForm()
    
    login_form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and "login" in request.POST and login_form.is_valid():
        user = login_form.get_user()
        login(request, user)
        return redirect("dashboard")
    
    return render(request, "accounts/home.html", {"form": form, "login_form": login_form})


@login_required
def dashboard(request):
    """Dashboard del usuario con meetings y rol"""
    if hasattr(request.user, "profile"):
        role = request.user.profile.role
    else:
        role = "GUEST"
    
    meetings = Meeting.objects.filter(owner=request.user).order_by("-created_at")[:10]
    return render(request, "accounts/dashboard.html", {"role": role, "meetings": meetings})


@login_required
def create_meeting(request):
    """Crear un nuevo meeting (solo usuarios registrados)"""
    require_registered(request.user)  # USER / WEB_ADMIN / ENV_ADMIN
    
    if request.method == "POST":
        room = Meeting.generate_room()
        m = Meeting.objects.create(room=room, owner=request.user)
        messages.success(request, "Meeting creado.")
        return redirect("meeting_detail", pk=m.pk)
    
    return render(request, "accounts/create_meeting.html")


@login_required
def meeting_detail(request, pk):
    """Detalle de un meeting con link de Jitsi"""
    m = get_object_or_404(Meeting, pk=pk)
    # Unirse: todos los roles autenticados; GUEST no puede crear, pero sí unirse si tiene link
    return render(request, "accounts/meeting_detail.html", {"meeting": m})


@login_required
def admin_requests(request):
    """Lista de solicitudes para admins"""
    require_admin(request.user)
    
    # Filtros
    status_filter = request.GET.get('status', '')
    qs = SignupRequest.objects.all()
    
    if status_filter:
        qs = qs.filter(status=status_filter)
    
    qs = qs.order_by("-created_at")
    
    # Estadísticas
    stats = {
        'total': SignupRequest.objects.count(),
        'pending': SignupRequest.objects.filter(status=SignupRequest.PENDING).count(),
        'approved': SignupRequest.objects.filter(status=SignupRequest.APPROVED).count(),
        'rejected': SignupRequest.objects.filter(status=SignupRequest.REJECTED).count(),
    }
    
    return render(request, "accounts/request_list.html", {
        "requests": qs,
        "stats": stats,
        "current_filter": status_filter
    })


@login_required
def request_detail(request, pk):
    """Detalle de una solicitud específica para admins"""
    require_admin(request.user)
    request_obj = get_object_or_404(SignupRequest, pk=pk)
    return render(request, "accounts/request_detail.html", {"request_obj": request_obj})


@login_required
def approve_request(request, pk):
    """Aprobar una solicitud"""
    require_admin(request.user)
    request_obj = get_object_or_404(SignupRequest, pk=pk)
    
    if request.method == 'POST':
        decision_note = request.POST.get('decision_note', '')
        request_obj.approve(decided_by=request.user, decision_note=decision_note)
        messages.success(request, f"Solicitud de {request_obj.email} aprobada exitosamente.")
        return redirect('admin_requests')
    
    return redirect('request_detail', pk=pk)


@login_required
def reject_request(request, pk):
    """Rechazar una solicitud"""
    require_admin(request.user)
    request_obj = get_object_or_404(SignupRequest, pk=pk)
    
    if request.method == 'POST':
        decision_note = request.POST.get('decision_note', '')
        request_obj.reject(decided_by=request.user, decision_note=decision_note)
        messages.success(request, f"Solicitud de {request_obj.email} rechazada.")
        return redirect('admin_requests')
    
    return redirect('request_detail', pk=pk)


@login_required
def reset_request(request, pk):
    """Resetear una solicitud a pendiente"""
    require_admin(request.user)
    request_obj = get_object_or_404(SignupRequest, pk=pk)
    
    if request.method == 'POST':
        request_obj.status = SignupRequest.PENDING
        request_obj.decided_at = None
        request_obj.decided_by = None
        request_obj.decision_note = ""
        request_obj.save()
        messages.success(request, f"Solicitud de {request_obj.email} reseteada a pendiente.")
        return redirect('admin_requests')
    
    return redirect('request_detail', pk=pk)

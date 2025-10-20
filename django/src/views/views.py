from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from models.models import SignupRequest, Meeting, UserProfile
from .forms import SignupRequestForm
from models.permissions import require_admin, require_registered

User = get_user_model()


def home(request):
    """Homepage pública: formulario de solicitud + login"""
    # Si el usuario ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated:
        return redirect("dashboard")
    
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
        # Limpiar cache del usuario al hacer login
        cache_key = f"user_info_{user.id}"
        cache.delete(cache_key)
        return redirect("dashboard")
    
    return render(request, "home.html", {"form": form, "login_form": login_form})


@login_required
def dashboard(request):
    """Dashboard principal que muestra contenido según el rol del usuario"""
    user_info = get_user_info(request)
    if user_info:
        role = user_info['role']
    else:
        role = "GUEST"
    
    # Mostrar contenido según el rol
    if role == "ENV_ADMIN":
        return env_admin_dashboard(request)
    elif role == "WEB_ADMIN":
        return web_admin_dashboard(request)
    elif role == "USER":
        return user_dashboard(request)
    else:
        return guest_dashboard(request)


@login_required
def env_admin_dashboard(request):
    """Dashboard para ENV_ADMIN - Control total del sistema"""
    require_admin(request.user)
    
    # Estadísticas del sistema
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    total_users = User.objects.count()
    pending_requests = SignupRequest.objects.filter(status=SignupRequest.PENDING).count()
    approved_requests = SignupRequest.objects.filter(status=SignupRequest.APPROVED).count()
    total_meetings = Meeting.objects.count()
    
    # Últimas solicitudes
    recent_requests = SignupRequest.objects.all().order_by("-created_at")[:5]
    
    return render(request, "dashboards/env_admin_dashboard.html", {
        "total_users": total_users,
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
        "total_meetings": total_meetings,
        "recent_requests": recent_requests,
        "user_info": get_user_info(request)
    })


@login_required
def web_admin_dashboard(request):
    """Dashboard para WEB_ADMIN - Gestión de usuarios y solicitudes"""
    require_admin(request.user)
    
    # Solo solicitudes pendientes para web admin
    pending_requests = SignupRequest.objects.filter(status=SignupRequest.PENDING).order_by("-created_at")
    recent_requests = SignupRequest.objects.all().order_by("-created_at")[:10]
    
    return render(request, "dashboards/web_admin_dashboard.html", {
        "pending_requests": pending_requests,
        "recent_requests": recent_requests,
        "user_info": get_user_info(request)
    })


@login_required
def user_dashboard(request):
    """Dashboard para USER - Sus meetings y funcionalidades básicas"""
    require_registered(request.user)
    
    # Meetings del usuario
    meetings = Meeting.objects.filter(owner=request.user).order_by("-created_at")
    
    return render(request, "dashboards/user_dashboard.html", {
        "meetings": meetings,
        "user_info": get_user_info(request)
    })


@login_required
def guest_dashboard(request):
    """Dashboard para GUEST - Información limitada"""
    return render(request, "dashboards/guest_dashboard.html", {
        "user_info": get_user_info(request)
    })


@login_required
def create_meeting(request):
    """Crear un nuevo meeting (solo usuarios registrados)"""
    require_registered(request.user)  # USER / WEB_ADMIN / ENV_ADMIN
    
    if request.method == "POST":
        is_private = request.POST.get('is_private') == '1'
        room = Meeting.generate_room()
        m = Meeting.objects.create(
            room=room, 
            owner=request.user,
            is_private=is_private
        )
        messages.success(request, f"Reunión {'privada' if is_private else 'pública'} creada.")
        return redirect("meeting_detail", pk=m.pk)
    
    return render(request, "create_meeting.html")


@login_required
def meeting_detail(request, pk):
    """Detalle de un meeting con link de Jitsi"""
    m = get_object_or_404(Meeting, pk=pk)
    # Unirse: todos los roles autenticados; GUEST no puede crear, pero sí unirse si tiene link
    return render(request, "meeting_detail.html", {"meeting": m})


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
    
    return render(request, "request_list.html", {
        "requests": qs,
        "stats": stats,
        "current_filter": status_filter
    })


@login_required
def request_detail(request, pk):
    """Detalle de una solicitud específica para admins"""
    require_admin(request.user)
    request_obj = get_object_or_404(SignupRequest, pk=pk)
    return render(request, "request_detail.html", {"request_obj": request_obj})


@login_required
def approve_request(request, pk):
    """Aprobar una solicitud"""
    require_admin(request.user)
    request_obj = get_object_or_404(SignupRequest, pk=pk)
    
    if request.method == 'POST':
        decision_note = request.POST.get('decision_note', '')
        
        # Generar contraseña temporal
        temp_password = 'temp' + get_random_string(8)
        
        # Guardar en _plain_password para signal
        username = request_obj.email.split("@")[0]
        User = get_user_model()
        user = User(username=username, email=request_obj.email)
        user._plain_password = temp_password
        user.set_password(temp_password)
        user.save()
        
        request_obj.approve(decided_by=request.user, decision_note=decision_note)
        messages.success(request, f"Usuario {username} creado con contraseña: {temp_password}")
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


@login_required
def admin_users(request):
    """Lista de usuarios para administradores con paginación"""
    require_admin(request.user)
    
    from django.core.paginator import Paginator
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Obtener todos los usuarios con sus perfiles
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    
    # Paginación
    paginator = Paginator(users, 10)  # 10 usuarios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()
    
    # Estadísticas por rol
    from models.models import UserProfile
    role_stats = {}
    for role, _ in UserProfile.ROLE_CHOICES:
        role_stats[role] = UserProfile.objects.filter(role=role).count()
    
    return render(request, "admin_users.html", {
        "page_obj": page_obj,
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "role_stats": role_stats,
        "user_info": get_user_info(request)
    })


@login_required
def toggle_user_status(request, pk):
    """Activar/desactivar usuario"""
    require_admin(request.user)
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        
        status = "activado" if user.is_active else "desactivado"
        messages.success(request, f"Usuario {user.username} {status} exitosamente.")
        
        return redirect('admin_users')
    
    return redirect('admin_users')


@login_required
def delete_user(request, pk):
    """Eliminar usuario"""
    require_admin(request.user)
    
    from django.contrib.auth import get_user_model
    from models.models import UserProfile
    
    User = get_user_model()
    user = get_object_or_404(User, pk=pk)
    current_user_profile = request.user.profile
    
    # Verificar permisos de eliminación
    if hasattr(user, 'profile'):
        target_profile = user.profile
    else:
        # Si no tiene perfil, crear uno temporal para verificar permisos
        target_profile = UserProfile(user=user, role=UserProfile.ROLE_GUEST)
    
    if not UserProfile.can_delete_user(current_user_profile, target_profile):
        if target_profile.role == UserProfile.ROLE_ENV_ADMIN:
            messages.error(request, "No se puede eliminar ENV_ADMIN desde la aplicación.")
        else:
            messages.error(request, f"No tienes permisos para eliminar a {user.username}.")
        return redirect('admin_users')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"Usuario {username} eliminado exitosamente.")
        return redirect('admin_users')
    
    return render(request, "confirm_delete_user.html", {
        "user": user,
        "user_info": get_user_info(request)
    })


@login_required
def change_user_role(request, pk):
    """Cambiar rol de usuario"""
    require_admin(request.user)
    
    from django.contrib.auth import get_user_model
    from models.models import UserProfile
    
    User = get_user_model()
    user = get_object_or_404(User, pk=pk)
    current_user_profile = request.user.profile
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        
        # Verificar si se puede cambiar el rol del usuario
        if not UserProfile.can_change_user_role(current_user_profile, user.profile, new_role):
            if user.profile.role == UserProfile.ROLE_ENV_ADMIN:
                messages.error(request, "No se puede cambiar el rol de ENV_ADMIN desde la aplicación.")
            elif new_role == UserProfile.ROLE_ENV_ADMIN:
                messages.error(request, "No se puede asignar el rol ENV_ADMIN desde la aplicación. Solo se crea por deploy con env_simple.")
            else:
                messages.error(request, f"No tienes permisos para asignar el rol {new_role}.")
            return redirect('admin_users')
        
        if new_role in [choice[0] for choice in UserProfile.ROLE_CHOICES]:
            if hasattr(user, 'profile'):
                user.profile.role = new_role
                user.profile.save()
            else:
                UserProfile.objects.create(user=user, role=new_role)
            
            messages.success(request, f"Rol de {user.username} cambiado a {new_role}.")
        else:
            messages.error(request, "Rol inválido.")
        
        return redirect('admin_users')
    
    # Filtrar roles disponibles según permisos (NUNCA incluir ENV_ADMIN)
    available_roles = []
    for role_value, role_name in UserProfile.ROLE_CHOICES:
        # NUNCA permitir ENV_ADMIN desde la aplicación
        if role_value == UserProfile.ROLE_ENV_ADMIN:
            continue
        if UserProfile.can_create_role(current_user_profile, role_value):
            available_roles.append((role_value, role_name))
    
    return render(request, "change_user_role.html", {
        "user": user,
        "role_choices": available_roles,
        "user_info": get_user_info(request)
    })


def logout_view(request):
    """Página de logout con confirmación"""
    if request.user.is_authenticated:
        # Limpiar cache del usuario antes del logout
        cache_key = f"user_info_{request.user.id}"
        cache.delete(cache_key)
        logout(request)
        messages.success(request, "Has cerrado sesión exitosamente.")
    return render(request, "logout.html")


def custom_404(request, exception=None):
    """Página 404 personalizada"""
    return render(request, "404.html", status=404)


def custom_permission_denied(request, exception=None):
    """Página de permisos denegados"""
    return render(request, "permission_denied.html", status=403)


def get_user_info(request):
    """Función helper para obtener información del usuario con cache"""
    if not request.user.is_authenticated:
        return None
    
    cache_key = f"user_info_{request.user.id}"
    user_info = cache.get(cache_key)
    
    if user_info is None:
        # Obtener el rol del usuario
        try:
            role = request.user.profile.role
        except:
            role = 'GUEST'
        
        user_info = {
            'is_authenticated': True,
            'username': request.user.username,
            'email': request.user.email,
            'role': role
        }
        # Cache por 5 minutos
        cache.set(cache_key, user_info, 300)
    
    return user_info

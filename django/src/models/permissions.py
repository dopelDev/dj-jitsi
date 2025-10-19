from django.core.exceptions import PermissionDenied


def require_admin(user):
    """Requiere que el usuario sea ENV_ADMIN o WEB_ADMIN"""
    if not user.is_authenticated or not hasattr(user, "profile") or not user.profile.is_admin_like():
        raise PermissionDenied()


def require_registered(user):
    """Requiere que el usuario sea ENV_ADMIN, WEB_ADMIN o USER (no GUEST)"""
    if not user.is_authenticated or not hasattr(user, "profile") or user.profile.role not in {"ENV_ADMIN", "WEB_ADMIN", "USER"}:
        raise PermissionDenied()

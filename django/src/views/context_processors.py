from django.core.cache import cache


def user_info(request):
    """Context processor para información del usuario con cache"""
    # Verificar que request tiene el atributo user
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {'user_info': None}
    
    cache_key = f"user_info_{request.user.id}"
    user_info = cache.get(cache_key)
    
    if user_info is None:
        user_info = {
            'is_authenticated': True,
            'username': request.user.username,
            'email': request.user.email,
            'role': getattr(request.user.profile, 'role', 'GUEST') if hasattr(request.user, 'profile') else 'GUEST'
        }
        # Cache por 5 minutos
        cache.set(cache_key, user_info, 300)
    
    return {'user_info': user_info}

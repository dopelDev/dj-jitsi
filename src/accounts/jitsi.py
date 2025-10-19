"""
Módulo para integración con Jitsi Meet
Funcionalidades para generar JWT y links de reunión
"""
import os
import time
from typing import Optional


def jitsi_jwt(sub: str = "meet", room: str = "*", user_name: str = "Guest") -> Optional[str]:
    """
    Genera un JWT para autenticación con Jitsi Meet
    
    Args:
        sub: Subject del token
        room: Nombre de la sala (usar "*" para acceso general)
        user_name: Nombre del usuario
    
    Returns:
        Token JWT codificado o None si hay error
    """
    try:
        import jwt
        
        secret = os.getenv("JITSI_JWT_SECRET")
        appid = os.getenv("JITSI_APP_ID", "django-jitsi")
        
        if not secret:
            print("Warning: JITSI_JWT_SECRET no configurado")
            return None
            
        now = int(time.time())
        payload = {
            "aud": appid,
            "iss": appid,
            "sub": sub,
            "room": room,
            "exp": now + 60 * 30,  # 30 minutos
            "nbf": now - 5,
            "context": {"user": {"name": user_name}},
        }
        
        return jwt.encode(payload, secret, algorithm="HS256")
        
    except ImportError:
        print("Error: pyjwt no instalado. Instalar con: pip install pyjwt")
        return None
    except Exception as e:
        print(f"Error generando JWT: {e}")
        return None


def generate_meeting_link(room_name: str, user_name: str = "Guest") -> str:
    """
    Genera un link de reunión de Jitsi con JWT
    
    Args:
        room_name: Nombre de la sala
        user_name: Nombre del usuario
    
    Returns:
        URL completa de la reunión
    """
    base_url = os.getenv("JITSI_BASE_URL", "https://meet.jit.si")
    
    # Generar JWT si está configurado
    jwt_token = jitsi_jwt(room=room_name, user_name=user_name)
    
    if jwt_token:
        return f"{base_url}/{room_name}?jwt={jwt_token}"
    else:
        return f"{base_url}/{room_name}"


def create_secure_room(room_name: str, user_name: str) -> dict:
    """
    Crea una sala segura con JWT
    
    Args:
        room_name: Nombre de la sala
        user_name: Nombre del usuario
    
    Returns:
        Diccionario con información de la sala
    """
    meeting_link = generate_meeting_link(room_name, user_name)
    
    return {
        "room_name": room_name,
        "meeting_link": meeting_link,
        "is_secure": bool(os.getenv("JITSI_JWT_SECRET")),
        "user_name": user_name,
        "created_at": time.time()
    }


# Funciones para integración futura con Prosody
def sync_user_with_prosody(username: str, email: str) -> bool:
    """
    Sincroniza usuario con Prosody (implementación futura)
    
    Args:
        username: Nombre de usuario
        email: Email del usuario
    
    Returns:
        True si la sincronización fue exitosa
    """
    # TODO: Implementar sincronización con Prosody
    # Esto requeriría configuración específica del servidor Prosody
    print(f"TODO: Sincronizar usuario {username} ({email}) con Prosody")
    return False


def create_prosody_room(room_name: str, moderator: str) -> bool:
    """
    Crea una sala en Prosody (implementación futura)
    
    Args:
        room_name: Nombre de la sala
        moderator: Usuario moderador
    
    Returns:
        True si la sala fue creada exitosamente
    """
    # TODO: Implementar creación de salas en Prosody
    print(f"TODO: Crear sala {room_name} en Prosody con moderador {moderator}")
    return False

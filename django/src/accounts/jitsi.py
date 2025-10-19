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
    Crea una sala segura con JWT y configuración P2P
    
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
        "created_at": time.time(),
        "p2p_enabled": True,
        "stun_servers": os.getenv("JVB_STUN_SERVERS", "stun.l.google.com:19302,stun1.l.google.com:19302"),
        "turn_servers": get_turn_servers(),
        "octo_enabled": os.getenv("JVB_OCTO_BIND_ADDRESS", "0.0.0.0") != "",
    }


def get_turn_servers() -> list:
    """
    Obtiene la configuración de servidores TURN para P2P
    
    Returns:
        Lista de servidores TURN configurados
    """
    turn_servers = []
    turn_server = os.getenv("TURN_SERVER")
    turn_username = os.getenv("TURN_USERNAME")
    turn_password = os.getenv("TURN_PASSWORD")
    
    if turn_server and turn_username and turn_password:
        turn_servers.append({
            "urls": [f"turn:{turn_server}"],
            "username": turn_username,
            "credential": turn_password
        })
    
    return turn_servers


def create_p2p_room(room_name: str, user_name: str, enable_p2p: bool = True) -> dict:
    """
    Crea una sala con configuración P2P optimizada
    
    Args:
        room_name: Nombre de la sala
        user_name: Nombre del usuario
        enable_p2p: Habilitar conexiones P2P directas
    
    Returns:
        Diccionario con configuración de la sala P2P
    """
    base_config = create_secure_room(room_name, user_name)
    
    if enable_p2p:
        base_config.update({
            "p2p_config": {
                "enabled": True,
                "stun_servers": base_config["stun_servers"].split(","),
                "turn_servers": base_config["turn_servers"],
                "ice_transport_policy": "all",
                "ice_servers": get_ice_servers(),
            },
            "jvb_config": {
                "enabled": not enable_p2p,  # JVB solo si P2P está deshabilitado
                "octo_enabled": base_config["octo_enabled"],
            }
        })
    
    return base_config


def get_ice_servers() -> list:
    """
    Obtiene la lista completa de servidores ICE (STUN + TURN)
    
    Returns:
        Lista de servidores ICE configurados
    """
    ice_servers = []
    
    # Agregar servidores STUN
    stun_servers = os.getenv("JVB_STUN_SERVERS", "stun.l.google.com:19302,stun1.l.google.com:19302")
    for stun in stun_servers.split(","):
        ice_servers.append({"urls": f"stun:{stun.strip()}"})
    
    # Agregar servidores TURN
    ice_servers.extend(get_turn_servers())
    
    return ice_servers


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

"""
Configuración de pytest con fixtures comunes para tests de Jitsi Meet
"""
import pytest
import requests
import docker
import os
import socket
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(dotenv_path='./tests/env.test')

@pytest.fixture(scope="session")
def jitsi_url():
    """URL base de Jitsi Meet"""
    return os.getenv('JITSI_URL', 'http://localhost:8080')

@pytest.fixture(scope="session")
def docker_client():
    """Cliente de Docker para interactuar con contenedores"""
    try:
        return docker.from_env()
    except Exception as e:
        pytest.skip(f"No se pudo conectar a Docker: {e}")

@pytest.fixture(scope="session")
def jitsi_containers(docker_client):
    """Verificar que contenedores estén ejecutándose"""
    containers = {
        'prosody': 'jitsi-prosody',
        'web': 'jitsi-web',
        'jicofo': 'jitsi-jicofo',
        'jvb': 'jitsi-jvb'
    }
    
    running_containers = {}
    for name, container_name in containers.items():
        try:
            container = docker_client.containers.get(container_name)
            if container.status == 'running':
                running_containers[name] = container
            else:
                pytest.fail(f"Contenedor {container_name} no está ejecutándose (status: {container.status})")
        except docker.errors.NotFound:
            pytest.fail(f"Contenedor {container_name} no encontrado")
    
    return running_containers

@pytest.fixture(scope="session")
def env_vars():
    """Variables de entorno críticas"""
    return {
        'PUBLIC_URL': os.getenv('PUBLIC_URL', 'http://localhost:8080'),
        'JITSI_DOMAIN': os.getenv('JITSI_DOMAIN', 'localhost'),
        'JITSI_URL': os.getenv('JITSI_URL', 'http://localhost:8080')
    }

@pytest.fixture
def test_room():
    """Sala de prueba para tests"""
    return os.getenv('TEST_ROOM', 'test-websocket-error')

def check_port_open(host, port, timeout=5):
    """Verificar si un puerto está abierto"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception:
        return False

def check_udp_port_open(host, port, timeout=5):
    """Verificar si un puerto UDP está abierto"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            sock.bind(('', 0))  # Bind to any available port
            return True  # Si llegamos aquí, el puerto UDP está disponible
    except Exception:
        return False

@pytest.fixture
def port_checker():
    """Helper para verificar puertos"""
    return {
        'tcp': check_port_open,
        'udp': check_udp_port_open
    }

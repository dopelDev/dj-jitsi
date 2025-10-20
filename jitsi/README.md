# Jitsi Meet - Contenedor Único

Jitsi Meet dockerizado en un solo contenedor para desarrollo, incluyendo todos los componentes necesarios para videoconferencias.

## 🎯 Propósito

Este proyecto proporciona una solución completa de Jitsi Meet en un solo contenedor Docker, ideal para desarrollo y testing. Incluye todos los componentes necesarios: servidor XMPP (Prosody), componente de enfoque (Jicofo), puente de video (JVB) y la interfaz web de Jitsi Meet.

## 🏗️ Componentes Incluidos

- **Prosody**: Servidor XMPP para mensajería y presencia
- **Jicofo**: Componente de enfoque que coordina las sesiones
- **JVB**: Puente de video para streaming de video/audio
- **Jitsi Meet**: Interfaz web para videoconferencias
- **Nginx**: Servidor web y proxy reverso
- **Supervisor**: Gestor de procesos para ejecutar todos los servicios

## 📁 Estructura del Proyecto

```
jitsi/
├── README.md                    # Este archivo
├── Dockerfile                   # Imagen Docker con todos los componentes
├── entrypoint.sh               # Script de inicio y configuración
├── docker-compose.yml          # Configuración para ejecutar el contenedor
├── .env.example               # Variables de entorno de ejemplo
├── .dockerignore              # Archivos a ignorar en la construcción
├── config/                     # Configuraciones
│   ├── supervisor/
│   │   └── supervisord.conf   # Configuración de supervisor
│   └── jitsi/
│       └── meet-config.js     # Configuración de Jitsi Meet
└── logs/                      # Logs generados en runtime
```

## 🚀 Inicio Rápido

### 1. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 2. Construir y Ejecutar

```bash
# Construir la imagen
docker-compose build

# Ejecutar el contenedor
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f
```

### 3. Acceder a Jitsi Meet

- **URL**: `https://localhost` (o tu dominio configurado)
- **Puerto HTTP**: 80
- **Puerto HTTPS**: 443
- **Puerto JVB**: 10000/udp

## ⚙️ Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `JITSI_DOMAIN` | Dominio principal de Jitsi | `localhost` |
| `PUBLIC_URL` | URL pública de acceso | `https://localhost` |
| `JVB_PORT` | Puerto del puente de video | `10000` |
| `ENABLE_AUTH` | Habilitar autenticación | `false` |

### Puertos Expuestos

- **80**: HTTP (redirige a HTTPS)
- **443**: HTTPS (Jitsi Meet web)
- **10000/udp**: JVB (puente de video)
- **4443**: JVB TCP

## 🔧 Desarrollo

### Sin Autenticación

Por defecto, el contenedor está configurado para desarrollo sin autenticación:
- Los usuarios pueden unirse a cualquier sala
- No se requiere registro
- Ideal para testing y desarrollo

### Logs

Los logs se almacenan en el directorio `logs/` y también se muestran en la consola:
- `logs/prosody.log` - Servidor XMPP
- `logs/jicofo.log` - Componente de enfoque
- `logs/jvb.log` - Puente de video
- `logs/nginx.log` - Servidor web

### Comandos Útiles

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f jitsi

# Reiniciar el contenedor
docker-compose restart

# Detener el contenedor
docker-compose down

# Acceder al shell del contenedor
docker-compose exec jitsi bash
```

## 🔗 Integración con Django

Este contenedor está diseñado para integrarse con el proyecto Django principal:

### Configuración en Django

```python
# settings.py
JITSI_CONFIG = {
    'DOMAIN': 'localhost',
    'PUBLIC_URL': 'https://localhost',
    'JWT_SECRET': 'tu-secreto-jwt',
    'ENABLE_AUTH': False,  # Para desarrollo
}
```

### Generación de URLs de Reunión

```python
def create_meeting_url(room_name, user_name):
    base_url = "https://localhost"
    return f"{base_url}/{room_name}#userInfo.displayName={user_name}"
```

## 🛠️ Troubleshooting

### Problemas Comunes

#### 1. El contenedor no inicia
```bash
# Verificar logs
docker-compose logs

# Verificar configuración
docker-compose config
```

#### 2. No se puede acceder a Jitsi Meet
- Verificar que el puerto 443 esté disponible
- Comprobar que el certificado SSL se haya generado
- Revisar logs de nginx

#### 3. Problemas de video/audio
- Verificar que el puerto 10000/udp esté abierto
- Comprobar configuración de STUN servers
- Revisar logs de JVB

### Regenerar Certificados

```bash
# Detener el contenedor
docker-compose down

# Eliminar certificados existentes
rm -rf ssl/*

# Reiniciar (se generarán nuevos certificados)
docker-compose up -d
```

## 📚 Documentación Adicional

- [Documentación oficial de Jitsi](https://jitsi.org/docs/)
- [Configuración de Prosody](https://prosody.im/doc/configuration)
- [Jitsi Meet API](https://github.com/jitsi/jitsi-meet/blob/master/doc/api.md)

## 🤝 Contribución

Para contribuir a este proyecto:

1. Modificar archivos de configuración según necesidades
2. Probar cambios en entorno de desarrollo
3. Documentar cambios en este README
4. Crear pull request con descripción detallada

## 📝 Notas de Desarrollo

- Los certificados SSL se generan automáticamente al iniciar
- Los logs se mantienen persistentes en el directorio `logs/`
- La configuración se puede personalizar modificando archivos en `config/`
- Para producción, cambiar `ENABLE_AUTH=true` y configurar autenticación JWT
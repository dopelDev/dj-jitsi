# Jitsi Meet - Configuración Segura con Docker Compose

Jitsi Meet configurado con Docker Compose siguiendo las mejores prácticas de seguridad, incluyendo todos los componentes necesarios para videoconferencias con autenticación interna segura.

## 🎯 Propósito

Este proyecto proporciona una solución completa de Jitsi Meet con Docker Compose, siguiendo las mejores prácticas de seguridad documentadas en `esential.md`. Incluye todos los componentes necesarios con configuración segura: servidor XMPP (Prosody), componente de enfoque (Jicofo), puente de video (JVB) y la interfaz web de Jitsi Meet.

## 🔐 Configuración de Seguridad

**⚠️ IMPORTANTE**: Este proyecto implementa las mejores prácticas de seguridad documentadas en `esential.md`:

- **Contraseñas seguras obligatorias**: No se pueden usar contraseñas vacías o por defecto
- **Generación automática**: Script `gen-passwords.sh` genera contraseñas seguras automáticamente
- **Validación de configuración**: Script `validate-config.sh` verifica que todo esté configurado correctamente
- **Variables de entorno completas**: Todas las credenciales internas están documentadas y configuradas

### Documentación de Seguridad

- 📋 **[DEPLOYMENT.md](DEPLOYMENT.md)** - Guía paso a paso para despliegue seguro
- 🔧 **[esential.md](../esential.md)** - Documentación técnica completa de configuración
- ✅ **[validate-config.sh](validate-config.sh)** - Script de validación automática

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
# Copiar archivo de plantilla
cp env.example .env

# Generar contraseñas seguras automáticamente
bash gen-passwords.sh
```

### 2. Validar Configuración

```bash
# Verificar que todo esté configurado correctamente
bash validate-config.sh
```

### 3. Ejecutar Servicios

```bash
# Levantar todos los servicios
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f
```

### 4. Acceder a Jitsi Meet

- **URL**: `http://localhost:8080` (o tu dominio configurado)
- **Puerto Web**: 8080
- **Puerto JVB**: 10000/udp

### 5. Verificar Despliegue

```bash
# Verificar que no hay errores FATAL
docker compose logs prosody | grep -i "fatal"

# Verificar conexiones XMPP
docker compose logs jicofo | grep "Connected to XMPP"
docker compose logs jvb | grep "Joined MUC"
```

## ⚙️ Configuración

### Variables de Entorno Críticas

| Variable | Descripción | Generada por |
|----------|-------------|--------------|
| `JICOFO_COMPONENT_SECRET` | Secreto del componente Jicofo | `gen-passwords.sh` |
| `JICOFO_AUTH_PASSWORD` | Contraseña del usuario focus | `gen-passwords.sh` |
| `JVB_AUTH_PASSWORD` | Contraseña del usuario jvb | `gen-passwords.sh` |
| `XMPP_DOMAIN` | Dominio XMPP principal | Manual |
| `XMPP_AUTH_DOMAIN` | Dominio XMPP de autenticación | Manual |

### Variables Públicas

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `JITSI_DOMAIN` | Dominio principal de Jitsi | `localhost` |
| `PUBLIC_URL` | URL pública de acceso | `http://localhost:8080` |
| `JVB_PORT` | Puerto del puente de video | `10000` |
| `ENABLE_AUTH` | Habilitar autenticación | `false` |

### ⚠️ Importante sobre Seguridad

- **NUNCA** uses contraseñas vacías o por defecto
- **SIEMPRE** ejecuta `bash gen-passwords.sh` antes del primer despliegue
- **VERIFICA** la configuración con `bash validate-config.sh`
- **CONSULTA** `esential.md` para detalles técnicos completos

### Puertos Expuestos

- **8080**: HTTP (Jitsi Meet web)
- **10000/udp**: JVB (puente de video)

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

#### 1. Error: "FATAL ERROR: Jicofo component secret and auth password must be set"
```bash
# Causa: Contraseñas vacías en .env
# Solución: Regenerar contraseñas
bash gen-passwords.sh
docker compose restart
```

#### 2. Error: "XMPP failed authentication"
```bash
# Causa: Desincronización entre .env y cuentas Prosody
# Solución: Recrear volúmenes de configuración
docker compose down
docker volume rm jitsi_prosody-config jitsi_jicofo-config jitsi_jvb-config
docker compose up -d
```

#### 3. Los servicios no se conectan
```bash
# Verificar configuración
bash validate-config.sh

# Verificar logs
docker compose logs prosody | grep -i "fatal"
docker compose logs jicofo | grep "Connected to XMPP"
docker compose logs jvb | grep "Joined MUC"
```

#### 4. No se puede acceder a Jitsi Meet
- Verificar que el puerto 8080 esté disponible
- Comprobar que todos los contenedores estén ejecutándose
- Revisar logs de todos los servicios

### Scripts de Diagnóstico

```bash
# Validación completa
bash validate-config.sh

# Verificar estado de contenedores
docker compose ps

# Ver logs de todos los servicios
docker compose logs --tail=50
```

## 📚 Documentación Adicional

### Documentación del Proyecto
- 📋 **[DEPLOYMENT.md](DEPLOYMENT.md)** - Guía completa de despliegue
- 🔧 **[esential.md](../esential.md)** - Documentación técnica detallada
- ✅ **[validate-config.sh](validate-config.sh)** - Script de validación

### Documentación Externa
- [Documentación oficial de Jitsi](https://jitsi.org/docs/)
- [Configuración de Prosody](https://prosody.im/doc/configuration)
- [Jitsi Meet API](https://github.com/jitsi/jitsi-meet/blob/master/doc/api.md)
- [Docker Jitsi Meet](https://github.com/jitsi/docker-jitsi-meet)

## 🤝 Contribución

Para contribuir a este proyecto:

1. Modificar archivos de configuración según necesidades
2. Probar cambios en entorno de desarrollo
3. Documentar cambios en este README
4. Crear pull request con descripción detallada

## 📝 Notas de Desarrollo

- **Contraseñas seguras**: Se generan automáticamente con `gen-passwords.sh`
- **Validación**: Usar `validate-config.sh` para verificar configuración
- **Logs**: Se mantienen persistentes en el directorio `logs/`
- **Volúmenes**: Las configuraciones se persisten en volúmenes Docker
- **Seguridad**: Para producción, cambiar `ENABLE_AUTH=true` y configurar autenticación JWT
- **Documentación**: Consultar `esential.md` para detalles técnicos completos
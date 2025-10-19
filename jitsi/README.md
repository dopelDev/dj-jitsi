# Jitsi Meet Server

Servidor Jitsi Meet containerizado con Docker para videoconferencias seguras.

## Requisitos

- Docker
- Docker Compose
- Puertos disponibles: 80, 443, 8443, 5222, 5269, 5280, 5281, 10000, 4443

## Setup

### 1. Configurar Variables de Entorno

```bash
cd jitsi
cp .env.example .env
# Editar .env con tus valores
```

### 2. Iniciar Servicios

```bash
docker-compose up -d
```

### 3. Verificar Estado

```bash
docker-compose ps
docker-compose logs
```

## Servicios Incluidos

- **Prosody**: Servidor XMPP para comunicación
- **Jicofo**: Componente de enfoque para conferencias
- **JVB**: Jitsi Videobridge para streaming de video
- **Nginx**: Proxy reverso y servidor web

## Acceso

- **Jitsi Meet**: `https://localhost:8443`
- **Nginx**: `http://localhost` (puerto 80)
- **HTTPS**: `https://localhost` (puerto 443)

## Configuración

### Dominios

Configura los dominios en `.env`:

```bash
JITSI_DOMAIN=meet.jitsi
JITSI_AUTH_DOMAIN=auth.meet.jitsi
JITSI_GUEST_DOMAIN=guest.meet.jitsi
```

### JWT (Opcional)

Para autenticación segura:

```bash
JWT_APP_ID=django-jitsi
JWT_APP_SECRET=tu_secreto_seguro
```

### P2P

Configuración para conexiones peer-to-peer:

```bash
JVB_STUN_SERVERS=stun.l.google.com:19302,stun1.l.google.com:19302
JVB_OCTO_BIND_ADDRESS=0.0.0.0
```

## Comandos Útiles

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar servicios
docker-compose down

# Reiniciar un servicio
docker-compose restart prosody

# Ver estado
docker-compose ps
```

## Integración con Django

El servidor Jitsi se integra con la aplicación Django:

1. Django se conecta a `https://localhost:8443`
2. Las reuniones se crean con JWT para autenticación
3. Los usuarios pueden acceder a salas seguras

## Estructura

```
jitsi/
├── docker-compose.yml    # Configuración Docker
├── config/              # Configuraciones de servicios
│   ├── prosody/         # Configuración XMPP
│   ├── jicofo/          # Configuración Jicofo
│   ├── jvb/             # Configuración Videobridge
│   └── nginx/           # Configuración Nginx
├── logs/                # Logs de servicios
├── ssl/                 # Certificados SSL
└── .env.example        # Variables de entorno
```

## Troubleshooting

### Problemas de Conexión

1. Verificar que todos los puertos estén disponibles
2. Revisar logs: `docker-compose logs`
3. Verificar configuración de red

### Problemas de SSL

1. Generar certificados en `ssl/`
2. Verificar configuración de Nginx
3. Revisar permisos de archivos

### Problemas de P2P

1. Verificar configuración STUN/TURN
2. Revisar firewall
3. Verificar conectividad de red
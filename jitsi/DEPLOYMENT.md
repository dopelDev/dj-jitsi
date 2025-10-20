# Guía de Despliegue - Jitsi Meet con Django

Esta guía te llevará paso a paso para desplegar Jitsi Meet con todas las configuraciones de seguridad necesarias.

## 📋 Prerrequisitos

- Docker y Docker Compose instalados
- Acceso a terminal/consola
- Permisos para ejecutar scripts

## 🚀 Proceso de Despliegue

### Paso 1: Preparar el Entorno

```bash
# Navegar al directorio de Jitsi
cd /home/dopel/projects/jitsi-django/jitsi

# Verificar que los archivos necesarios existen
ls -la env.example gen-passwords.sh docker-compose.yml
```

### Paso 2: Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp env.example .env

# Generar contraseñas seguras automáticamente
bash gen-passwords.sh
```

**¿Qué hace `gen-passwords.sh`?**
- Genera contraseñas seguras para `JICOFO_COMPONENT_SECRET`, `JICOFO_AUTH_PASSWORD`, `JVB_AUTH_PASSWORD`
- Actualiza automáticamente el archivo `.env`
- Crea un backup de `.env` en `.env.bak`

### Paso 3: Personalizar Configuración (Opcional)

Edita el archivo `.env` si necesitas cambiar:

```bash
# Para desarrollo local (por defecto)
JITSI_DOMAIN=localhost
PUBLIC_URL=http://localhost:8080

# Para producción, cambiar a tu dominio
# JITSI_DOMAIN=meet.tudominio.com
# PUBLIC_URL=https://meet.tudominio.com
```

### Paso 4: Desplegar los Servicios

```bash
# Levantar todos los servicios
docker compose up -d

# Verificar que todos los contenedores estén ejecutándose
docker compose ps
```

### Paso 5: Verificar el Despliegue

```bash
# Verificar logs de Prosody (no debe haber errores FATAL)
docker compose logs prosody | grep -i "fatal\|error"

# Verificar conexión de Jicofo
docker compose logs jicofo | grep "Connected to XMPP"

# Verificar conexión de JVB
docker compose logs jvb | grep "Joined MUC"

# Verificar estado general
docker compose logs --tail=20
```

## ✅ Verificación de Éxito

Si todo está funcionando correctamente, deberías ver:

1. **Prosody**: Sin errores FATAL, escuchando en puertos XMPP
2. **Jicofo**: "Connected to XMPP server" y "Focus role: authorized"
3. **JVB**: "Connected to XMPP server" y "Joined MUC: jvbbrewery@internal-muc.meet.jitsi"
4. **Web**: Accesible en http://localhost:8080

## 🔧 Comandos Útiles

### Ver logs en tiempo real
```bash
# Todos los servicios
docker compose logs -f

# Servicio específico
docker compose logs -f prosody
docker compose logs -f jicofo
docker compose logs -f jvb
```

### Reiniciar servicios
```bash
# Reiniciar todo
docker compose restart

# Reiniciar servicio específico
docker compose restart prosody
```

### Detener servicios
```bash
# Detener todo
docker compose down

# Detener y eliminar volúmenes (¡CUIDADO! Borra configuraciones)
docker compose down -v
```

## 🚨 Solución de Problemas

### Error: "FATAL ERROR: Jicofo component secret and auth password must be set"

**Causa**: Contraseñas vacías en `.env`

**Solución**:
```bash
# Regenerar contraseñas
bash gen-passwords.sh

# Reiniciar servicios
docker compose restart
```

### Error: "XMPP failed authentication"

**Causa**: Desincronización entre `.env` y cuentas en Prosody

**Solución**:
```bash
# Detener servicios
docker compose down

# Eliminar volúmenes de configuración (¡CUIDADO!)
docker volume rm jitsi_prosody-config jitsi_jicofo-config jitsi_jvb-config

# Volver a levantar
docker compose up -d
```

### Los servicios no se conectan entre sí

**Verificar**:
1. Que el archivo `.env` existe y tiene contraseñas
2. Que todos los contenedores están ejecutándose
3. Que no hay errores en los logs

```bash
# Verificar archivo .env
cat .env | grep -E "(JICOFO|JVB).*PASSWORD"

# Verificar contenedores
docker compose ps

# Verificar logs
docker compose logs --tail=50
```

## 📁 Estructura de Archivos

Después del despliegue exitoso, tendrás:

```
jitsi/
├── .env                    # Variables de entorno (con contraseñas)
├── .env.bak               # Backup del .env original
├── gen-passwords.sh       # Script de generación de contraseñas
├── docker-compose.yml     # Configuración de servicios
├── env.example           # Plantilla de variables
├── DEPLOYMENT.md         # Esta guía
├── validate-config.sh    # Script de validación
└── logs/                 # Logs de los servicios
```

## 🔐 Seguridad

- **Nunca** compartas el archivo `.env` (contiene contraseñas)
- **Siempre** usa `gen-passwords.sh` para generar contraseñas seguras
- **Mantén** el backup `.env.bak` en un lugar seguro
- **Revisa** los logs regularmente para detectar problemas

## 📚 Referencias

- `esential.md` - Documentación técnica completa
- `validate-config.sh` - Script de validación automática
- [Docker Jitsi Meet](https://github.com/jitsi/docker-jitsi-meet) - Documentación oficial

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker compose logs`
2. Ejecuta el validador: `bash validate-config.sh`
3. Consulta `esential.md` para detalles técnicos
4. Verifica que todas las contraseñas estén configuradas en `.env`

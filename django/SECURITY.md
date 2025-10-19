# 🔒 Guía de Seguridad

## ⚠️ Credenciales y Variables de Entorno

### Archivos de Configuración

**NUNCA** commitees archivos con credenciales reales:
- ❌ `env_simple`
- ❌ `.env`
- ❌ `env.local`
- ❌ `env.production`

### Archivos Seguros (Sí commiteear)
- ✅ `env.example` - Plantilla con valores de ejemplo
- ✅ `.gitignore` - Configurado para excluir archivos sensibles

### Configuración de Desarrollo

1. **Copia el archivo de ejemplo:**
   ```bash
   cp env.example env_simple
   ```

2. **Edita `env_simple` con tus credenciales reales:**
   ```bash
   # Configuración de Admin
   ADMIN_USERNAME=tu_admin
   ADMIN_EMAIL=tu_email@example.com
   ADMIN_PASSWORD=tu_password_seguro
   ADMIN_FIRST_NAME=Tu
   ADMIN_LAST_NAME=Nombre
   
   # Django
   DJANGO_SECRET_KEY=tu-secret-key-muy-largo-y-seguro
   DJANGO_DEBUG=1
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
   
   # Jitsi
   JITSI_DOMAIN=tu-dominio.com
   JITSI_APP_ID=tu-app-id
   JITSI_APP_SECRET=tu-app-secret
   JITSI_BASE_URL=https://tu-jitsi.com
   ```

3. **NUNCA commitees `env_simple`** - está en `.gitignore`

### Configuración de Producción

1. **Usa variables de entorno del sistema:**
   ```bash
   export ADMIN_USERNAME=admin
   export ADMIN_PASSWORD=password_super_seguro
   export DJANGO_SECRET_KEY=secret_key_muy_largo_y_seguro
   ```

2. **O usa un archivo `.env` local** (no commiteado)

### Verificación de Seguridad

Para verificar que no hay credenciales expuestas:

```bash
# Buscar posibles credenciales
grep -r "password\|secret\|key\|token" . --exclude-dir=venv --exclude-dir=.git
```

### Valores por Defecto Seguros

Los valores por defecto en el código son seguros:
- `ADMIN_PASSWORD=change-me-in-production`
- `DJANGO_SECRET_KEY=insecure` (solo para desarrollo)

### Jerarquía de Privilegios

- **ENV_ADMIN**: Solo creado desde deploy con variables de entorno
- **WEB_ADMIN**: Creado por ENV_ADMIN
- **USER/GUEST**: Creados por administradores

### Recomendaciones

1. **Cambia todas las contraseñas por defecto**
2. **Usa contraseñas fuertes y únicas**
3. **Rota las credenciales regularmente**
4. **Nunca uses credenciales de producción en desarrollo**
5. **Revisa el historial de Git si se expusieron credenciales**

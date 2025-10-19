# Herramientas de Django-Jitsi

Este directorio contiene herramientas útiles para la gestión del proyecto django-jitsi.

## Scripts Disponibles

### cleanup_docker.sh

Script para limpiar completamente el entorno Docker del proyecto.

**Funcionalidades:**
- Detiene y elimina todos los contenedores del proyecto
- Elimina volúmenes del proyecto y volúmenes huérfanos
- Elimina redes del proyecto
- Elimina imágenes del proyecto
- Limpia el directorio de base de datos local
- Limpia archivos temporales de Docker

**Uso:**
```bash
./tools/cleanup_docker.sh
```

**Cuándo usar:**
- Antes de hacer cambios importantes en la configuración Docker
- Cuando quieres empezar con un entorno completamente limpio
- Para liberar espacio en disco
- Para resolver problemas de contenedores o volúmenes

**Precauciones:**
- Este script elimina TODOS los datos del proyecto
- Se perderán las bases de datos y configuraciones
- Asegúrate de hacer backup si tienes datos importantes

### backup_database.sh

Script para hacer backup de la base de datos SQLite.

**Funcionalidades:**
- Crea backup de la base de datos con timestamp
- Limpia automáticamente backups antiguos (mantiene los últimos 10)
- Soporte para backup completo del directorio db/
- Información detallada del backup creado

**Uso:**
```bash
./tools/backup_database.sh
```

**Cuándo usar:**
- Antes de hacer cambios importantes en la base de datos
- Como parte de rutinas de mantenimiento
- Antes de actualizar el sistema

### restore_database.sh

Script para restaurar backup de la base de datos SQLite.

**Funcionalidades:**
- Lista todos los backups disponibles
- Interfaz interactiva para seleccionar backup
- Crea backup de la base de datos actual antes de restaurar
- Verifica integridad de la base de datos restaurada

**Uso:**
```bash
./tools/restore_database.sh
```

**Cuándo usar:**
- Para recuperar datos después de un error
- Para volver a un estado anterior conocido
- Para migrar datos entre entornos

### monitor_containers.sh

Script para monitorear contenedores de django-jitsi.

**Funcionalidades:**
- Estado de contenedores en tiempo real
- Logs recientes de la aplicación
- Uso de recursos (CPU, memoria, red)
- Estado de la base de datos
- Estadísticas de la aplicación web
- Modo de monitoreo continuo

**Uso:**
```bash
# Monitoreo único
./tools/monitor_containers.sh

# Monitoreo continuo
./tools/monitor_containers.sh --continuous
```

**Cuándo usar:**
- Para diagnosticar problemas de rendimiento
- Para monitorear el estado de la aplicación
- Para verificar que todo funciona correctamente

## Herramientas Planificadas

### Herramientas Futuras:

1. **deploy_production.sh** - Script de despliegue a producción
2. **setup_ssl.sh** - Configuración de SSL/TLS
3. **jitsi_config_generator.sh** - Generador de configuración Jitsi
4. **health_check.sh** - Verificación de salud del sistema
5. **performance_test.sh** - Tests de rendimiento

## Contribución

Para agregar nuevas herramientas:

1. Crea el script en el directorio `tools/`
2. Hazlo ejecutable con `chmod +x`
3. Documenta su uso en este README
4. Agrega tests si es necesario
5. Actualiza este archivo con la nueva funcionalidad

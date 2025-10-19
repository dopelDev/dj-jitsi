#!/bin/bash
# Script para hacer backup de la base de datos SQLite

set -e

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Backup de Base de Datos Django-Jitsi ===${NC}"

# Crear directorio de backups si no existe
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"

# Generar nombre de archivo con timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/django_jitsi_backup_$TIMESTAMP.sqlite3"

# Verificar si la base de datos existe
if [ ! -f "db/db.sqlite3" ]; then
    echo -e "${YELLOW}[WARNING]${NC} No se encontró la base de datos en db/db.sqlite3"
    echo "¿Deseas continuar con el backup del directorio db/ completo? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        BACKUP_FILE="$BACKUP_DIR/django_jitsi_full_backup_$TIMESTAMP.tar.gz"
        tar -czf "$BACKUP_FILE" db/
        echo -e "${GREEN}[SUCCESS]${NC} Backup completo creado: $BACKUP_FILE"
    else
        echo "Backup cancelado"
        exit 1
    fi
else
    # Hacer backup de la base de datos
    cp "db/db.sqlite3" "$BACKUP_FILE"
    echo -e "${GREEN}[SUCCESS]${NC} Backup de base de datos creado: $BACKUP_FILE"
fi

# Mostrar información del backup
echo ""
echo -e "${BLUE}=== Información del Backup ===${NC}"
echo "Archivo: $BACKUP_FILE"
echo "Tamaño: $(du -h "$BACKUP_FILE" | cut -f1)"
echo "Fecha: $(date)"

# Limpiar backups antiguos (mantener solo los últimos 10)
echo ""
echo -e "${BLUE}=== Limpiando backups antiguos ===${NC}"
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/django_jitsi_backup_*.sqlite3 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 10 ]; then
    ls -1t "$BACKUP_DIR"/django_jitsi_backup_*.sqlite3 | tail -n +11 | xargs rm -f
    echo -e "${GREEN}[SUCCESS]${NC} Backups antiguos eliminados (mantenidos los últimos 10)"
fi

echo ""
echo -e "${GREEN}=== Backup completado exitosamente ===${NC}"

#!/bin/bash
# Script para restaurar backup de la base de datos SQLite

set -e

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Restaurar Backup de Base de Datos Django-Jitsi ===${NC}"

# Verificar si existen backups
BACKUP_DIR="backups"
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}[ERROR]${NC} No se encontró el directorio de backups"
    exit 1
fi

# Listar backups disponibles
echo -e "${BLUE}=== Backups Disponibles ===${NC}"
BACKUPS=$(ls -1 "$BACKUP_DIR"/django_jitsi_backup_*.sqlite3 2>/dev/null || true)
if [ -z "$BACKUPS" ]; then
    echo -e "${RED}[ERROR]${NC} No se encontraron backups de base de datos"
    echo "Backups disponibles en $BACKUP_DIR:"
    ls -la "$BACKUP_DIR/" 2>/dev/null || echo "Directorio vacío"
    exit 1
fi

# Mostrar backups con números
echo "Backups disponibles:"
counter=1
for backup in $BACKUPS; do
    filename=$(basename "$backup")
    size=$(du -h "$backup" | cut -f1)
    date=$(stat -c %y "$backup" | cut -d' ' -f1)
    echo "  $counter) $filename (${size}, $date)"
    ((counter++))
done

echo ""
echo -e "${YELLOW}Selecciona el número del backup a restaurar (1-$((counter-1))):${NC}"
read -r selection

# Validar selección
if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt $((counter-1)) ]; then
    echo -e "${RED}[ERROR]${NC} Selección inválida"
    exit 1
fi

# Obtener el archivo seleccionado
selected_backup=$(echo "$BACKUPS" | sed -n "${selection}p")

echo ""
echo -e "${YELLOW}¿Estás seguro de que quieres restaurar el backup:${NC}"
echo "  $selected_backup"
echo -e "${YELLOW}Esto sobrescribirá la base de datos actual. (y/N):${NC}"
read -r confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Restauración cancelada"
    exit 0
fi

# Crear backup de la base de datos actual antes de restaurar
if [ -f "db/db.sqlite3" ]; then
    echo -e "${BLUE}[INFO]${NC} Creando backup de la base de datos actual..."
    CURRENT_BACKUP="backups/current_backup_$(date +"%Y%m%d_%H%M%S").sqlite3"
    cp "db/db.sqlite3" "$CURRENT_BACKUP"
    echo -e "${GREEN}[SUCCESS]${NC} Backup actual creado: $CURRENT_BACKUP"
fi

# Crear directorio db si no existe
mkdir -p db

# Restaurar backup
echo -e "${BLUE}[INFO]${NC} Restaurando backup..."
cp "$selected_backup" "db/db.sqlite3"
echo -e "${GREEN}[SUCCESS]${NC} Backup restaurado exitosamente"

# Verificar que la base de datos es válida
echo -e "${BLUE}[INFO]${NC} Verificando integridad de la base de datos..."
if docker compose ps | grep -q "Up"; then
    docker compose exec web python manage.py check --database default
    echo -e "${GREEN}[SUCCESS]${NC} Base de datos verificada"
else
    echo -e "${YELLOW}[WARNING]${NC} No se pudo verificar la base de datos (contenedor no corriendo)"
fi

echo ""
echo -e "${GREEN}=== Restauración completada exitosamente ===${NC}"
echo "Archivo restaurado: $(basename "$selected_backup")"
echo ""
echo -e "${YELLOW}Para aplicar los cambios, reinicia los contenedores:${NC}"
echo -e "${BLUE}  docker compose restart${NC}"

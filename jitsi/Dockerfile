# Dockerfile para Jitsi Meet - Contenedor Único
FROM jitsi/web:stable

# Instalar dependencias para mod_auth_sql
RUN apt-get update && apt-get install -y \
    lua-dbi-sqlite3 \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio para base de datos compartida
RUN mkdir -p /config/sqlite

# Crear directorio para plugins personalizados
RUN mkdir -p /prosody-plugins-custom

# Variables de entorno
ENV JITSI_DOMAIN=localhost
ENV PUBLIC_URL=http://localhost:8080
ENV JVB_PORT=10000
ENV ENABLE_AUTH=true

# Crear directorios necesarios
RUN mkdir -p /var/log/jitsi \
    && mkdir -p /etc/jitsi/meet

# Copiar archivos de configuración
COPY config/ /etc/
COPY entrypoint.sh /entrypoint.sh

# Hacer ejecutable el script de entrada
RUN chmod +x /entrypoint.sh

# Crear directorio para logs
RUN mkdir -p /var/log/supervisor

# Exponer puertos
EXPOSE 80 443 10000/udp

# Configurar entrypoint
ENTRYPOINT ["/entrypoint.sh"]

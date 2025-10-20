# Dockerfile para Jitsi Meet - Contenedor Único
FROM jitsi/web:latest

# Variables de entorno
ENV JITSI_DOMAIN=localhost
ENV PUBLIC_URL=http://localhost:8080
ENV JVB_PORT=10000
ENV ENABLE_AUTH=false

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
EXPOSE 80 443

# Configurar entrypoint
ENTRYPOINT ["/entrypoint.sh"]

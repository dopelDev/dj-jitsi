-- Archivo de configuración principal de Prosody
-- Este archivo es requerido por los tests en /etc/prosody/prosody.cfg.lua

-- Configuración global mínima
daemonize = false
pidfile = "/var/run/prosody/prosody.pid"

-- Rutas de módulos
plugin_paths = { "/usr/share/jitsi-meet/prosody-plugins/" }

-- Logging
log = {
    { levels = { min = "info" }, to = "console" };
}

-- Network settings
interfaces = { "*", "::" }

-- Incluir configuraciones específicas del sitio
Include "conf.d/*.cfg.lua"

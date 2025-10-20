-- Configuración de Prosody para Jitsi Meet
-- Este archivo se monta en /etc/prosody/conf.d/jitsi-meet.cfg.lua

-- Configuración global
admins = { "admin@meet.jitsi" }

-- VirtualHost para Jitsi Meet
VirtualHost "meet.jitsi"
    -- Autenticación deshabilitada para desarrollo
    authentication = "anonymous"
    
    -- Configuración de módulos
    modules_enabled = {
        "bosh";
        "websocket";
        "pubsub";
        "ping";
        "speakerstats";
        "conference_duration";
        "muc_lobby_rooms";
        "muc_breakout_rooms";
    }
    
    -- Configuración de BOSH y WebSocket
    bosh_ports = { 5280 }
    bosh_interfaces = { "*" }
    
    -- Configuración de WebSocket
    cross_domain_websocket = true
    cross_domain_bosh = true
    
    -- Configuración de salas MUC
    muc_mapper_domain_base = "meet.jitsi"
    
    -- Configuración de lobby
    lobby_muc = "lobby.meet.jitsi"
    
    -- Configuración de breakout rooms
    breakout_rooms_muc = "breakout.meet.jitsi"

-- Componente para conferencias
Component "conference.meet.jitsi" "muc"
    modules_enabled = {
        "muc_mam";
    }
    storage = "memory"
    muc_room_locking = false
    muc_room_default_public_jids = true

-- Componente para lobby
Component "lobby.meet.jitsi" "muc"
    storage = "memory"
    muc_room_locking = false
    muc_room_default_public_jids = true

-- Componente para breakout rooms
Component "breakout.meet.jitsi" "muc"
    storage = "memory"
    muc_room_locking = false
    muc_room_default_public_jids = true

-- Configuración de puertos
c2s_ports = { 5222 }
c2s_interfaces = { "*" }

-- Configuración de logs
log = {
    { levels = { min = "info" }, to = "console" };
    { levels = { min = "info" }, to = "file", filename = "/var/log/prosody/prosody.log" };
}

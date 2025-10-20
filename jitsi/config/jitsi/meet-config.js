var config = {
    hosts: {
        domain: 'localhost',
        muc: 'conference.localhost'
    },
    
    bosh: 'http://localhost:8080/http-bind',
    
    // WebSocket URL explícita para evitar construcción incorrecta
    // IMPORTANTE: Usar ws:// para HTTP, wss:// para HTTPS
    // El WebSocket debe apuntar al puerto 8080 donde está el frontend de Jitsi Meet
    websocket: 'ws://localhost:8080/xmpp-websocket',
    
    // Forzar configuración de WebSocket para evitar construcción automática incorrecta
    useStunTurn: true,
    enableLayerSuspension: true,
    
    // Sin autenticación para desarrollo
    enableUserRolesBasedOnToken: false,
    
    // P2P habilitado
    p2p: {
        enabled: true,
        stunServers: [
            { urls: 'stun:stun.l.google.com:19302' },
            { urls: 'stun:stun1.l.google.com:19302' }
        ]
    },
    
    // Configuración de video
    resolution: 720,
    constraints: {
        video: {
            height: {
                ideal: 720,
                max: 720,
                min: 240
            }
        }
    },
    
    // Desactivar estadísticas
    disableThirdPartyRequests: true,
    
    // UI simplificada
    enableWelcomePage: true,
    enableClosePage: false,
    
    // Features para desarrollo
    prejoinPageEnabled: false,
    disableDeepLinking: true,
    
    // Configuración de URLs para evitar errores de construcción
    // IMPORTANTE: Estas URLs deben coincidir con PUBLIC_URL del .env
    // Formato correcto: http://localhost:8080 (no http//localhost:8080)
    // WebSocket debe usar wss:// para HTTPS o ws:// para HTTP
    enableWelcomePage: true,
    
    // Configuración específica para forzar URLs correctas
    // Evitar construcción automática incorrecta de URLs
    disableDeepLinking: true,
    disableThirdPartyRequests: true,
    
    // Configuración de dominio para evitar construcción incorrecta
    // Forzar uso de localhost:8080 para todas las conexiones
    domain: 'localhost',
    muc: 'conference.localhost',
    
    // Forzar URLs específicas para evitar construcción automática incorrecta
    // Estas URLs deben ser absolutas para evitar concatenación incorrecta
    useStunTurn: true,
    enableLayerSuspension: true,
    
    // Configuración adicional para evitar construcción automática de URLs
    // Deshabilitar detección automática de protocolo
    disableThirdPartyRequests: true,
    disableDeepLinking: true,
    
    // Configuración de dominio dinámico (se puede sobrescribir con variables de entorno)
    // Para usar dominio dinámico, cambiar 'localhost' por window.location.hostname
    // hosts: {
    //     domain: window.location.hostname,
    //     muc: 'conference.' + window.location.hostname
    // }
};


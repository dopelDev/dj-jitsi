var config = {
    hosts: {
        domain: 'localhost',
        muc: 'conference.localhost'
    },
    
    bosh: '//localhost/http-bind',
    
    // WebSocket URL explícita para evitar construcción incorrecta
    websocket: 'wss://localhost/xmpp-websocket',
    
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
    
    // Configuración de dominio dinámico (se puede sobrescribir con variables de entorno)
    // Para usar dominio dinámico, cambiar 'localhost' por window.location.hostname
    // hosts: {
    //     domain: window.location.hostname,
    //     muc: 'conference.' + window.location.hostname
    // }
};


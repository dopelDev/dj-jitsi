var config = {
    hosts: {
        domain: 'localhost',
        muc: 'conference.localhost'
    },
    
    bosh: '//localhost/http-bind',
    
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
    disableDeepLinking: true
};


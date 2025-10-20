-- Configuración de autenticación SQL para Prosody
VirtualHost "meet.localhost"
    authentication = "sql"
    sql = {
        driver = "SQLite3";
        database = "/config/sqlite/jitsi-django.sqlite3";
    }
    
    -- Query personalizado para authreg
    sql_auth_query = "SELECT password FROM authreg WHERE username=? AND realm=?";

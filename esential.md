# Archivos de configuración esenciales para Prosody, Jicofo y JVB en Docker (Jitsi-Django)

En un entorno Docker basado en la imagen oficial de Jitsi Meet, los servicios Prosody (XMPP), Jicofo (Focus) y Jitsi Videobridge (JVB) requieren varios archivos de configuración para funcionar correctamente. 

A continuación se detallan, por cada servicio, los archivos clave, su función, ejemplos mínimos de contenido, su relación con las variables definidas en docker-compose.yml/.env y dónde residen (dentro del contenedor o en volúmenes). Se incluyen también recomendaciones para evitar problemas (como contraseñas faltantes).

## Prosody (Servidor XMPP)

### Archivo .env – Variables de entorno globales (Prosody)

Este archivo (ubicado en la raíz del proyecto, fuera de los contenedores) contiene las variables de entorno que configuran todo Jitsi. En particular, Prosody toma de aquí los nombres de dominio XMPP internos y las credenciales para los componentes internos:

**Dominio XMPP interno:** Variables como `XMPP_DOMAIN` (por defecto meet.jitsi) y `XMPP_AUTH_DOMAIN` (por defecto auth.meet.jitsi) definen el dominio principal de conferencias y el subdominio para usuarios autenticados. Estas se reflejan en la configuración de Prosody (ver más abajo).

**Credenciales internas (secrets):** Prosody necesita valores para:
- `JICOFO_COMPONENT_SECRET` (secreto del componente Focus)
- `JICOFO_AUTH_PASSWORD` (contraseña del usuario focus de Jicofo) 
- `JVB_AUTH_PASSWORD` (contraseña del usuario jvb del Videobridge)

Estos se definen en .env y no deben quedar vacíos, ya que los contenedores no iniciarán si faltan contraseñas seguras para estas cuentas internas. En versiones recientes, las contraseñas por defecto fueron eliminadas deliberadamente para obligar a proporcionarlas; si no se establecen, se verá un error fatal en los logs (por ejemplo, "FATAL ERROR: Jicofo component secret and auth password must be set" en Prosody) y los servicios reiniciarán constantemente.

**Ejemplo (fragmento de .env):**

```bash
# Dominio XMPP interno
XMPP_DOMAIN=meet.jitsi
XMPP_AUTH_DOMAIN=auth.meet.jitsi

# Credenciales internas (ejemplos generados aleatoriamente)
JICOFO_COMPONENT_SECRET=JHbPUIpU65Q
JICOFO_AUTH_USER=focus
JICOFO_AUTH_PASSWORD=snjfku289fjk
JVB_AUTH_USER=jvb
JVB_AUTH_PASSWORD=a8snmLK80a
```

**Función:** Este archivo suministra al docker-compose.yml las variables de entorno que serán inyectadas en los contenedores. Por ejemplo, `JICOFO_COMPONENT_SECRET` y `JICOFO_AUTH_PASSWORD` se pasan al contenedor Prosody para configurar el componente focus y crear el usuario focus, respectivamente. De igual forma, `JVB_AUTH_PASSWORD` se usará para el usuario jvb.

**Relación con Docker:** En el docker-compose.yml del proyecto Jitsi-Django (basado en la imagen oficial), suele incluir líneas `env_file: .env` o definiciones de entorno para cada servicio (prosody, jicofo, jvb), de modo que estas variables se apliquen dentro de los contenedores correspondientes.

**Ubicación:** .env es un archivo externo (en el host) – no dentro de un contenedor. Se debe editar antes de levantar los contenedores.

**Recomendación:** Utiliza el script provisto `gen-passwords.sh` para generar contraseñas seguras automáticamente en .env. Este script rellenará opciones como `JICOFO_COMPONENT_SECRET`, `JICOFO_AUTH_PASSWORD`, `JVB_AUTH_PASSWORD`, etc., con valores aleatorios robustos (usando `openssl rand -hex 16`). Asegúrate de ejecutarlo después de copiar el archivo de ejemplo (`cp env.example .env`) y antes de `docker compose up`. De esta manera, Prosody, Jicofo y JVB arrancarán con contraseñas válidas y únicas, evitando el error crítico por credenciales faltantes.

### Archivo prosody.cfg.lua – Configuración principal de Prosody

Este es el archivo de configuración de Prosody (formato Lua) que define los host virtuales XMPP, módulos y autenticación. En la imagen Docker oficial, se encuentra dentro del contenedor en `/config/prosody.cfg.lua` y se monta en un volumen externo para persistencia (por ejemplo en `~/.jitsi-meet-cfg/prosody/config/prosody.cfg.lua` en el host). Si no existe al iniciar, el contenedor lo genera a partir de plantillas por defecto, incorporando las variables de entorno.

**Función:** Establece cómo Prosody opera. Define los VirtualHost (dominios XMPP) usados en Jitsi Meet, los Componentes (como "focus" para Jicofo) y métodos de autenticación. Por defecto (sin habilitar auth para usuarios), el dominio principal permite invitados anónimos y el subdominio auth.meet.jitsi usa autenticación interna para las cuentas de servicio (focus, jvb, etc.). Este archivo también configura los componentes especiales de conferencia (salas MUC) y la integración con Jicofo.

**Ejemplo mínimo de contenido relevante (prosody.cfg.lua):**

```lua
-- Dominio principal de reuniones (con acceso anónimo por defecto)
VirtualHost "meet.jitsi"
authentication = "anonymous"
-- ... módulos por defecto, etc.

-- Dominio de autenticación para usuarios internos (focus, jvb)
VirtualHost "auth.meet.jitsi"
authentication = "internal_hashed"
admins = { "focus@auth.meet.jitsi" }

-- Componentes MUC (salas de conferencia)
Component "muc.meet.jitsi" "muc"
storage = "memory"
muc_room_default_public_jids = true

Component "internal-muc.meet.jitsi" "muc"
storage = "memory"
muc_room_default_public_jids = true

-- Componente Focus (Jicofo) con contraseña de componente
Component "focus.meet.jitsi"
component_secret = "JHbPUIpU65Q"
```

**En este ejemplo:**

- Se define el host principal "meet.jitsi" donde los usuarios se conectan (aquí con autenticación anónima).
- Se define el host "auth.meet.jitsi" para autenticación interna, donde se crearán usuarios de servicio. La línea `admins = { "focus@auth.meet.jitsi" }` asegura que el usuario focus (de Jicofo) tenga privilegios administrativos en Prosody.
- Se configuran dos componentes tipo MUC: uno público (muc.meet.jitsi para salas de conferencia) y uno interno (internal-muc.meet.jitsi) que suele usarse para la sala oculta donde Jicofo y JVB se comunican (por ej., JvbBrewery).
- El componente focus (focus.meet.jitsi) se declara con un `component_secret` – este secreto debe coincidir con el que Jicofo usa para autenticarse como componente.

**Relación con variables de entorno:** Los valores en este archivo provienen de las variables en .env:

- Los nombres de dominio meet.jitsi, auth.meet.jitsi, etc., derivan de `XMPP_DOMAIN`, `XMPP_AUTH_DOMAIN`, `XMPP_MUC_DOMAIN`, `XMPP_INTERNAL_MUC_DOMAIN` y similares (que por defecto son meet.jitsi). Si en .env se cambia a un dominio real (ej. meet.midominio.com), aquí aparecerá ese FQDN.

- El `component_secret` para focus es insertado desde la variable `JICOFO_COMPONENT_SECRET`. En el ejemplo, "JHbPUIpU65Q" corresponde a la clave definida en .env para Jicofo.

- La directiva `admins = { "focus@auth.meet.jitsi" }` incluye al usuario focus; este nombre de usuario proviene de `JICOFO_AUTH_USER` (que por defecto es "focus").

**Registro de usuarios internos:** Notablemente, Prosody necesita tener cuentas creadas para focus@auth.meet.jitsi (Jicofo) y jvb@auth.meet.jitsi (Videobridge) con las contraseñas definidas. En el contenedor Prosody, un script de inicialización usa prosodyctl para registrar automáticamente estos usuarios la primera vez que arranca el servicio, tomando `JICOFO_AUTH_PASSWORD` y `JVB_AUTH_PASSWORD` de las variables de entorno. Es decir, si las contraseñas están en .env, Prosody creará las cuentas internas necesarias (no es necesario editarlas manualmente en el archivo de config).

**Ubicación:** Dentro del contenedor Prosody (`/config/prosody.cfg.lua`). Está en un volumen persistente mapeado a una ruta del host (normalmente en la carpeta de configuración, por ejemplo jitsi-meet-cfg/prosody). Esto permite editarlo si fuera necesario o conservar cambios tras recrear contenedores. 

> **Nota:** Cualquier ajuste manual debe hacerse con precaución; la imagen oficial reescribe partes de este archivo en cada arranque para alinear con las variables (por ejemplo, si cambias dominios o activas autentificación JWT/LDAP vía env). En general, es preferible utilizar las variables de entorno provistas en lugar de editar este archivo directamente.

## Jicofo (Conferencia Focus)

### Archivo .env – Variables de entorno para Jicofo

Jicofo (Jitsi Conference Focus) utiliza varias variables definidas en .env (ya listadas anteriormente) para sus credenciales XMPP y ajustes:

**Usuario y contraseña Focus:** `JICOFO_AUTH_USER` (normalmente "focus") y `JICOFO_AUTH_PASSWORD` son las credenciales de Jicofo para iniciar sesión en Prosody como usuario XMPP cliente. Deben coincidir con la cuenta focus@auth.meet.jitsi registrada en Prosody. Por defecto, el usuario es "focus" y la contraseña no tiene valor por defecto (debe proporcionarse en .env).

**Secreto de componente:** `JICOFO_COMPONENT_SECRET` es la contraseña que Jicofo usará para autenticarse como componente externo focus.meet.jitsi. También debe ser la misma definida en Prosody (`component_secret` en el archivo Lua). En versiones recientes este valor por defecto era "s3cr37", pero se debe cambiar en producción (o generar automáticamente). Si falta, Prosody no permitirá la conexión del componente focus.

**Otros flags:** Opcionalmente, `ENABLE_AUTH`, `AUTH_TYPE` etc. se propagan a Jicofo (`JICOFO_ENABLE_AUTH`, etc.), pero estos afectan más al comportamiento (autenticación de usuarios Jitsi) que a la conectividad interna.

Estas variables se pasan al contenedor jicofo vía Docker Compose. Asegúrate de que `JICOFO_COMPONENT_SECRET` y `JICOFO_AUTH_PASSWORD` tengan valores definidos (no vacíos) en .env antes de iniciar. Si no, el contenedor de Prosody fallará al iniciar indicando que faltan credenciales (como vimos) y Jicofo tampoco podrá conectarse.

**Ejemplo (fragmento de .env ya mostrado):**

```bash
JICOFO_COMPONENT_SECRET=JHbPUIpU65Q
JICOFO_AUTH_USER=focus
JICOFO_AUTH_PASSWORD=snjfku289fjk
```

> (Estas credenciales deben ser consistentes con las configuraciones de Prosody y Jicofo).

### Archivo de configuración de Jicofo (cliente XMPP)

En la configuración Docker, Jicofo puede usar dos formatos de archivo según la versión: el legado `sip-communicator.properties` (propiedades Java) o el nuevo `jicofo.conf` (formato HOCON). Ambos cumplen la misma función: proporcionar a Jicofo parámetros de conexión y operación. La imagen oficial incluye plantillas para este archivo; al lanzar el contenedor Jicofo por primera vez, si el archivo no existe en el volumen, se genera automáticamente usando las variables de entorno. Por defecto, se almacena en el volumen montado en `/config` del contenedor (ej. en el host `~/.jitsi-meet-cfg/jicofo/sip-communicator.properties` o `jicofo.conf`).

**Función:** Este archivo indica a Jicofo cómo conectarse al servidor XMPP (Prosody) y qué salas utilizar para coordinar videobridges, autenticar, etc. Entre otras cosas, contiene: el JID de la sala "brewery" donde Jicofo descubre los JVB (videobridges), la URL de autenticación XMPP, y credenciales del usuario focus (si no se pasan por otros medios). También puede contener ajustes de health checks, tiempo de expiración de auth, etc., pero nos centraremos en lo esencial para la conectividad.

**Ejemplo mínimo (formato legacy sip-communicator.properties):**

```properties
# Jicofo: configuración de XMPP

org.jitsi.jicofo.BRIDGE_MUC=jvbbrewery@internal-muc.meet.jitsi
org.jitsi.jicofo.auth.URL=XMPP:meet.jitsi

# Credenciales del usuario focus (cliente XMPP de Jicofo)

org.jitsi.jicofo.auth.DOMAIN=auth.meet.jitsi
org.jitsi.jicofo.auth.USERNAME=focus
org.jitsi.jicofo.auth.PASSWORD=snjfku289fjk
```

**En este ejemplo:**

- `BRIDGE_MUC` indica la sala MUC que Jicofo supervisa para detectar videobridges. Por defecto es jvbbrewery@internal-muc.meet.jitsi, lo que significa que Jicofo esperará a los JVB en la sala "jvbbrewery" del dominio internal-muc.meet.jitsi (el MUC interno). Este valor combina la variable `JVB_BREWERY_MUC` (nombre de la sala, por defecto jvbbrewery) y `XMPP_INTERNAL_MUC_DOMAIN` (por defecto internal-muc.meet.jitsi).

- `org.jitsi.jicofo.auth.URL=XMPP:meet.jitsi` activa el Secure Domain para reuniones: le dice a Jicofo que solo permita crear salas a usuarios autenticados en el dominio principal (esto se usa cuando ENABLE_AUTH=1 con auth interna o JWT). Si no se usa autenticación segura, esta línea puede quedarse con XMPP:meet.jitsi o no estar presente.

- Bajo "Credenciales del usuario focus", se configuran el dominio, nombre de usuario y contraseña que Jicofo usará para autenticarse como cliente XMPP. Deben coincidir exactamente con la cuenta configurada en Prosody (en nuestro ejemplo, focus@auth.meet.jitsi con su password). Jicofo usará estas propiedades para iniciar sesión automáticamente. (Nota: En algunas configuraciones legacy, en lugar de auth.DOMAIN/USERNAME/PASSWORD, se usaba una sola propiedad FOCUS_USER_PASSWORD. Las versiones recientes utilizan los campos mostrados arriba.)

**Ejemplo equivalente (formato nuevo jicofo.conf):** Este archivo, ubicado típicamente en `/config/jicofo.conf`, tiene sintaxis tipo HOCON. Un bloque relevante luciría así:

```hocon
jicofo {
  xmpp: {
    client: {
      client-proxy: "focus.meet.jitsi"
      xmpp-domain: "meet.jitsi"
      username: "focus"
      password: "snjfku289fjk"
      domain: "auth.meet.jitsi"
    }
    bridge: {
      brewery-jid: "jvbbrewery@internal-muc.meet.jitsi"
    }
  }
}
```

Aquí vemos análogamente que `brewery-jid` indica la sala de bridges, y en `client` se configuran usuario (focus), contraseña y dominios. La propiedad `client-proxy` (focus.meet.jitsi) corresponde al componente XMPP – Jicofo lo usa para no requerir registrarse como componente manualmente (en Prosody, este ajuste va de la mano con el módulo client_proxy en vez del componente tradicional; es una variación técnica, pero en Docker oficial normalmente se sigue usando el componente secreto). Este formato nuevo es soportado por Jicofo y la imagen Docker lo poblará usando las mismas variables de entorno. En cualquier caso, solo uno de los archivos (properties o conf) será usado según la versión; no es necesario mantener ambos.

**Relación con variables de entorno:** Todos los parámetros anteriores provienen de .env y de las variables predeterminadas de la imagen:

- `BRIDGE_MUC` se construye con `$JVB_BREWERY_MUC@$XMPP_INTERNAL_MUC_DOMAIN`. Por defecto en .env: `JVB_BREWERY_MUC=jvbbrewery` y `XMPP_INTERNAL_MUC_DOMAIN=internal-muc.meet.jitsi`, dando lugar a jvbbrewery@internal-muc.meet.jitsi. Si se cambiaron estos valores (por ejemplo, para escenarios de alta disponibilidad con múltiples JVB, se podría usar otro nombre de sala), debe reflejarse aquí.

- El `auth.DOMAIN` (auth.meet.jitsi) y `xmpp-domain` (meet.jitsi) corresponden directamente a `XMPP_AUTH_DOMAIN` y `XMPP_DOMAIN`.

- El `USERNAME=focus` viene de `JICOFO_AUTH_USER` (normalmente no se modifica, permanece "focus").

- La `PASSWORD` es la definida en `JICOFO_AUTH_PASSWORD`. **Importante:** Si cambias manualmente la contraseña en .env, también deberás recrear la cuenta en Prosody o asegurarte de borrar el volumen de prosody para que se regenere, ya que Prosody almacena la contraseña original.

La imagen oficial maneja estos valores automáticamente: durante el arranque, un script inserta las env vars en la plantilla. Por ejemplo, en la configuración predeterminada de Docker se usaba sip-communicator.properties con placeholders:

```properties
org.jitsi.jicofo.BRIDGE_MUC={{ .Env.JVB_BREWERY_MUC }}@{{ .Env.XMPP_INTERNAL_MUC_DOMAIN }}
org.jitsi.jicofo.auth.URL={{ if .Env.ENABLE_AUTH | and (eq .Env.AUTH_TYPE "internal") }}XMPP:{{ .Env.XMPP_DOMAIN }}{{ end }}
```

y así sucesivamente, sustituyendo `{{ .Env.VARIABLE }}` por el valor. (En jicofo.conf ocurre algo similar, pero con sintaxis HOCON). Esto significa que no necesitas editar a mano este archivo en la mayoría de los casos; basta con que .env sea correcto.

**Ubicación:** Dentro del contenedor Jicofo, en el directorio `/config`. Está montado en un volumen externo (p. ej. `~/.jitsi-meet-cfg/jicofo/` en el host). Si necesitas revisar o modificar este archivo, puedes editar la copia en el host (o entrar al contenedor). Recuerda reiniciar el contenedor después de cualquier cambio para que Jicofo lo recargue.

**Recomendaciones:**

- Asegura que `JICOFO_AUTH_PASSWORD` y `JICOFO_COMPONENT_SECRET` estén establecidos en .env antes de la primera ejecución. Si olvidaste hacerlo y los contenedores fallaron, detén todo, añade las contraseñas al .env (puedes generar nuevas seguras) y vuelve a levantar los servicios. Prosody deberá crear la cuenta focus con la nueva contraseña.

- Verifica los logs de Jicofo (`docker compose logs jicofo`) y Prosody si hay problemas de conexión XMPP. Mensajes sobre auth failed indican contraseñas no coincidentes entre Jicofo y Prosody. En tal caso, puedes forzar la recreación de la cuenta en Prosody (borrando la entrada en `~/.jitsi-meet-cfg/prosody` correspondiente, o ejecutando manualmente en el contenedor Prosody un `prosodyctl --config /config/prosody.cfg.lua register focus auth.meet.jitsi NUEVAPASS`). No olvides mantener sincronizado ese NUEVAPASS en .env y reiniciar Jicofo.

- Habitualmente no es necesario tocar `JICOFO_AUTH_USER` (déjalo en "focus" a menos que sepas lo que haces y hayas cambiado configuraciones acordemente).

## Jitsi Videobridge (JVB)

### Archivo .env – Variables de entorno para JVB

El componente Jitsi Videobridge usa variables definidas en .env para poder autenticarse ante Prosody y anunciarse en el sistema:

**Usuario JVB y contraseña:** `JVB_AUTH_USER` (por defecto "jvb") y `JVB_AUTH_PASSWORD` representan las credenciales del cliente XMPP que cada instancia de videobridge usará. Igual que con focus, esta cuenta se crea en Prosody (jvb@auth.meet.jitsi) con la contraseña proporcionada. No hay un valor por defecto para la contraseña (debe definirse); si se deja <unset> el contenedor no iniciará correctamente. En producción se genera un valor aleatorio.

**Nombre de MUC de Bridges:** `JVB_BREWERY_MUC` define el nombre de la sala de conferencia (Multi-User Chat) interna donde se registran los JVB. Por defecto es jvbbrewery. Jicofo se unirá a esta sala (en el domain interno) para coordinar los bridges. Normalmente no es necesario cambiarlo, salvo escenarios avanzados (por ejemplo, tener grupos de bridges separados).

**Dominio interno MUC:** `XMPP_INTERNAL_MUC_DOMAIN` es el subdominio XMPP reservado para la MUC interna de bridges. Por defecto internal-muc.meet.jitsi. Prosody configura un host componente para este subdominio, como vimos. Este valor raramente cambia, a menos que hayas personalizado todos los subdominios XMPP en .env.

**Otros:** Hay más variables JVB (puerto UDP, STUN servers, etc.), pero no afectan la autenticación interna. Un valor a destacar es `JVB_ADVERTISE_IPS` si estás en NAT, pero es independiente de Prosody.

Asegúrate de haber establecido `JVB_AUTH_PASSWORD` en .env antes de iniciar. Si falta, el arranque fallará: el contenedor Prosody espera ese valor para registrar la cuenta jvb y, al no tenerlo, abortará con error (similar al caso de Jicofo).

**Ejemplo (fragmento de .env):**

```bash
JVB_AUTH_USER=jvb
JVB_AUTH_PASSWORD=a8snmLK80a
JVB_BREWERY_MUC=jvbbrewery

# XMPP_INTERNAL_MUC_DOMAIN=internal-muc.meet.jitsi (usa el valor por defecto)
```

> (Si se usa el dominio XMPP por defecto, no es necesario especificar `XMPP_INTERNAL_MUC_DOMAIN` ya que la imagen lo deriva como internal-muc.meet.jitsi. Está incluido en el .env de ejemplo por claridad.)

### Archivo de configuración de JVB (sip-communicator.properties)

El Videobridge utiliza un archivo de propiedades para saber cómo conectarse al servidor XMPP. En Docker, se encuentra en `/config/sip-communicator.properties` dentro del contenedor jvb (y mapeado a `~/.jitsi-meet-cfg/jvb/sip-communicator.properties` en el host). La imagen oficial provee este archivo con valores plantilla que se rellenan a partir de las variables de entorno mencionadas. (En versiones nuevas, JVB admite un archivo jvb.conf en formato YAML; sin embargo, la imagen sigue soportando y utilizando el archivo de propiedades para compatibilidad. Así que nos centraremos en éste.)

**Función:** Este archivo configura los parámetros de conexión XMPP del videobridge: principalmente el host XMPP, el dominio de autenticación, el usuario/contraseña y la sala MUC a la que debe unirse el JVB para anunciarse. También se pueden configurar aquí otros ajustes (por ejemplo deshabilitar la verificación de cert, activar APIs REST/Colibri, etc.). Por defecto, Docker lo configura en modo "MUC", es decir, el JVB se conecta como un cliente XMPP regular (usuario "jvb") en lugar de como componente externo, y se une a una room MUC (jvbbrewery) para ser gestionado por Jicofo.

**Ejemplo de contenido (sip-communicator.properties del JVB):**

```properties
# Config XMPP del Videobridge (JVB)

org.jitsi.videobridge.xmpp.user.shard.HOSTNAME=xmpp.meet.jitsi
org.jitsi.videobridge.xmpp.user.shard.DOMAIN=auth.meet.jitsi
org.jitsi.videobridge.xmpp.user.shard.USERNAME=jvb
org.jitsi.videobridge.xmpp.user.shard.PASSWORD=a8snmLK80a
org.jitsi.videobridge.xmpp.user.shard.MUC_JIDS=jvbbrewery@internal-muc.meet.jitsi
org.jitsi.videobridge.xmpp.user.shard.MUC_NICKNAME=jvb-01
org.jitsi.videobridge.xmpp.user.shard.DISABLE_CERTIFICATE_VERIFICATION=true
```

**Explicación:**

Las propiedades bajo `xmpp.user.shard` configuran una conexión XMPP tipo cliente (llamada shard en la config).

- `HOSTNAME=xmpp.meet.jitsi` – Es la dirección del servidor XMPP al que debe conectarse el JVB. En Docker, se usa el nombre de host interno del contenedor Prosody (xmpp.meet.jitsi) que resuelve dentro de la red de Docker. No es necesario cambiarlo a menos que hayas renombrado el servicio o el dominio interno.

- `DOMAIN=auth.meet.jitsi` – El dominio XMPP al que se autentica el JVB. Aquí es el dominio de autenticación interna, lo que indica que JVB inicia sesión como jvb@auth.meet.jitsi. Corresponde a `XMPP_AUTH_DOMAIN` en .env.

- `USERNAME=jvb` – Nombre del usuario XMPP (parte local del JID). Viene de `JVB_AUTH_USER`.

- `PASSWORD=a8snmLK80a` – Contraseña para ese usuario. Viene de `JVB_AUTH_PASSWORD`. Debe coincidir con la registrada en Prosody para jvb@auth.meet.jitsi (que, como mencionamos, se crea automáticamente usando este valor la primera vez).

- `MUC_JIDS=jvbbrewery@internal-muc.meet.jitsi` – Es el JID de la sala MUC donde el JVB se unirá para anunciarse. Compuesto por el nombre de sala (jvbbrewery, de `JVB_BREWERY_MUC`) y el dominio MUC interno (internal-muc.meet.jitsi). JVB entrará a esta sala al conectarse; Jicofo, a su vez, estará suscrito a ella para detectar los bridges disponibles. Si cambiaste `JVB_BREWERY_MUC` o `XMPP_INTERNAL_MUC_DOMAIN` en .env, aquí verás reflejado el cambio. En entornos escalados, cada JVB puede usar la misma MUC (aparecerán múltiples "jvb" en la sala) o en casos avanzados se pueden usar MUC separadas por grupos.

- `MUC_NICKNAME=jvb-01` – Apodo único con el que el JVB se registra en la sala. Puede ser generado (la plantilla oficial usa el hostname del contenedor como nickname por defecto). Es importante que cada JVB tenga un nick distinto en la MUC para evitar colisiones. Si tienes un solo JVB, el valor no es crítico. En el ejemplo "jvb-01" podría venir de la variable de entorno `$HOSTNAME` del contenedor (p. ej., si el contenedor JVB se llama jvb-1).

- `DISABLE_CERTIFICATE_VERIFICATION=true` – Indica al JVB que no verifique el certificado TLS del servidor XMPP. Esto es necesario en Docker porque Prosody utiliza certificados internos/autofirmados para sus virtualhosts XMPP. La plantilla lo pone en true para evitar problemas de SSL. (En despliegues fuera de Docker, a veces se deja false si se confía en el cert, pero aquí es intencionalmente true).

**Relación con variables de entorno:** Como se indicó, este archivo es esencialmente una plantilla rellenada con las env vars: la configuración por defecto de la imagen define estas propiedades usando los valores de .env. Referenciando la plantilla original:

```properties
org.jitsi.videobridge.xmpp.user.shard.HOSTNAME={{ .Env.XMPP_SERVER }}
org.jitsi.videobridge.xmpp.user.shard.DOMAIN={{ .Env.XMPP_AUTH_DOMAIN }}
org.jitsi.videobridge.xmpp.user.shard.USERNAME={{ .Env.JVB_AUTH_USER }}
org.jitsi.videobridge.xmpp.user.shard.PASSWORD={{ .Env.JVB_AUTH_PASSWORD }}
org.jitsi.videobridge.xmpp.user.shard.MUC_JIDS={{ .Env.JVB_BREWERY_MUC }}@{{ .Env.XMPP_INTERNAL_MUC_DOMAIN }}
org.jitsi.videobridge.xmpp.user.shard.MUC_NICKNAME={{ .Env.HOSTNAME }}
org.jitsi.videobridge.xmpp.user.shard.DISABLE_CERTIFICATE_VERIFICATION=true
```

Así, por ejemplo, `.Env.JVB_AUTH_PASSWORD` se reemplaza por el valor real definido. Mientras hayas configurado correctamente .env, no necesitas modificar este archivo manualmente.

**Ubicación:** Dentro del contenedor JVB (`/config/sip-communicator.properties`); persistido en el volumen jvb montado en el host (ejemplo: `~/.jitsi-meet-cfg/jvb/sip-communicator.properties`). Puedes verificar su contenido en tu sistema de archivos host después del primer arranque para confirmar que las contraseñas se insertaron.

**Recomendaciones:**

- **Contraseñas seguras:** Al igual que con Jicofo, asegúrate de generar una contraseña robusta para `JVB_AUTH_PASSWORD`. El script `gen-passwords.sh` lo hace automáticamente. Esto evitará usar valores débiles o por defecto que podrían ser conocidos públicamente (en versiones antiguas de docker-jitsi-meet, el default era `JVB_AUTH_PASSWORD=passw0rd`, lo cual ya no es el caso, ahora se exige que definas uno tú mismo).

- **Usuario JVB:** Por defecto "jvb" es adecuado; no es necesario cambiarlo. Si lo hicieras, recuerda cambiarlo también en Prosody (en prosody.cfg.lua y recreando la cuenta XMPP).

- **Múltiples JVB:** Si tu despliegue escala horizontalmente con varios contenedores JVB, todos usarán las mismas credenciales para conectarse (mismo user/pass jvb@auth.meet.jitsi). Esto es normal. Lo único que distinguirá a cada uno en la MUC es el `MUC_NICKNAME`. La imagen Docker le asignará el nombre del contenedor, pero puedes especificar manualmente un sufijo usando la variable `JVB_INSTANCE_ID` (ésta se antepone al nick). No obstante, en la mayoría de casos no hace falta tocarlo.

- **Verificación de certificados:** Se deja deshabilitada porque Prosody usa certificados autofirmados para sus dominios internos (meet.jitsi, etc.). No activar la verificación a menos que implementes certificados válidos para esos dominios internos (lo cual es poco común en Docker).

## Notas finales y buenas prácticas

### Generar todas las contraseñas antes de desplegar

Como se ha reiterado, utilizar `gen-passwords.sh` u otros medios para rellenar la sección de seguridad de .env es crítico. Este paso crea contraseñas aleatorias para `JICOFO_COMPONENT_SECRET`, `JICOFO_AUTH_PASSWORD`, `JVB_AUTH_PASSWORD` y otros (Jigasi, Jibri si aplicasen). Un .env completo y seguro garantiza que Prosody, Jicofo y JVB arranquen a la primera sin rechazar conexiones por credenciales faltantes. (El script hace un backup de tu .env original en .env.bak por seguridad).

### Crear los volúmenes de configuración apropiados

El proyecto Jitsi-Django parece seguir la estructura estándar de docker-jitsi-meet, donde se recomienda crear directorios de config en el host para cada servicio antes de levantar los contenedores. Por ejemplo: `~/.jitsi-meet-cfg/prosody`, `~/.jitsi-meet-cfg/jicofo`, `~/.jitsi-meet-cfg/jvb`, etc. Asegúrate de que dichos volúmenes estén declarados en el docker-compose.yml (la plantilla oficial ya lo hace) y de crear las carpetas con permisos adecuados en el host. Esto permite que los archivos .cfg.lua y .properties que hemos descrito se guarden en tu sistema host, donde puedes revisarlos y respaldarlos.

### Comprobación de inicio correcto

Una vez configurado todo, ejecuta `docker compose up -d` e inspecciona los logs:

- **Prosody** debe mostrar que carga la configuración sin errores y eventualmente que está escuchando en los puertos XMPP. Si hay un error FATAL relacionado con auth password o component secret, significa que aún falta alguna contraseña en .env.

- **Jicofo** en sus logs debería registrar mensajes como "Connected to XMPP server" y "Focus role: authorized" en la MUC jvbbrewery. Si hay un error de autenticación XMPP (Focus), revisa la contraseña.

- **JVB** debería loguear "Connected to XMPP server" y unirse a jvbbrewery (busca en el log del JVB algo como Joined MUC: jvbbrewery@internal-muc.meet.jitsi). Cualquier excepción indicando XMPP failed authentication sugiere credenciales jvb incorrectas – en tal caso, verificar Prosody y .env.

### Creación de un usuario administrador (opcional)

Si has habilitado la autenticación interna para las reuniones (`ENABLE_AUTH=1`, `AUTH_TYPE=internal` en .env), además de estas cuentas internas necesitas crear cuentas XMPP para los usuarios humanos (p. ej., un admin que inicie las reuniones). Esto se hace con prosodyctl dentro del contenedor Prosody. Por ejemplo: `docker compose exec prosody prosodyctl --config /config/prosody.cfg.lua register admin meet.jitsi MiContraseñ4` crea admin@meet.jitsi. 

Este proceso es independiente de las contraseñas de focus/jvb descritas (las cuales ya fueron creadas automáticamente). No confundas ambas cosas: focus/jvb son cuentas internas de servicio, mientras que las cuentas de usuario final van en el dominio principal (meet.jitsi o el que hayas usado) si usas "internal_hashed" como método. Para propósitos de levantar la infraestructura, las cuentas internas son las críticas (focus, jvb). Los usuarios finales se pueden crear después si se habilita auth para usar la aplicación.

### Consistencia de configuración

El proyecto Jitsi-Django debe mantener sincronizados .env y los archivos de config. Lo usual es que .env sea la fuente de la verdad y los contenedores sincronizan sus archivos automáticamente en cada arranque. Si realizas cambios manuales en, por ejemplo, prosody.cfg.lua o sip-communicator.properties, ten en cuenta que podrían ser sobreescritos en el próximo reinicio si no reflejas esos cambios en .env. Siempre que sea posible, usa las variables de entorno disponibles (la documentación oficial lista numerosas variables para personalizar comportamientos sin editar archivos a mano).

Por último, apoyarse en la documentación oficial de Docker-Jitsi-Meet es muy útil. La configuración descrita aquí corresponde a la imagen oficial, por lo que sigue las convenciones de ese proyecto. En caso de duda, puedes consultar el repositorio oficial y su manual para ver las descripciones de cada variable y archivo. Priorizando estas buenas prácticas, lograrás que Prosody, Jicofo y JVB inicien correctamente en Docker y el sistema Jitsi esté listo para videoconferencias.

## Fuentes

La explicación se basa en la documentación oficial de Jitsi Meet (docker), en guías de despliegue (por ejemplo, Scaleway Docs), y en la propia configuración por defecto de la imagen Docker (archivos de plantilla y código fuente). Se han incluido ejemplos derivados de estas fuentes para ilustrar cada archivo. Cada referencia corresponde al fragmento específico indicado para mayor detalle. ¡Configuración exitosa!

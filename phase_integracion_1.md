Gracias por compartir este análisis detallado del proyecto. Con base en el estado actual —fase de integración, componentes separados funcionando, y con SQLite como base común— he adaptado el plan de integración Django–Jitsi para que encaje perfectamente con tu stack actual y necesidades inmediatas.

---

# ✅ Plan Adaptado de Integración Django–Jitsi con Base SQLite Compartida

**Estado base actual:**

- Django (puerto 8000) ya funcional, con sistema de roles y autenticación.
- Jitsi Meet (puerto 8080) funcionando en Docker, imagen oficial.
- SQLite como base de datos.
- JWT en preparación, pero sin autenticación activa aún.
- En fase de integración de funcionalidades.

---

## 🎯 Objetivo

Permitir que **Jitsi Meet** utilice directamente la base de datos de **Django** (SQLite) para autenticar usuarios, de modo que no se requiera duplicar datos. La autenticación debe ejecutarse en Prosody a través de SQL (`mod_auth_sql`), sincronizando contra una tabla `authreg` gestionada desde Django.

---

## 🧩 Adaptación Estratégica al Proyecto

| Área                      | Adaptación                                                              |
| ------------------------- | ----------------------------------------------------------------------- |
| 🔐 Autenticación Jitsi    | `mod_auth_sql` apuntando al `db.sqlite3` de Django.                     |
| 🧠 Modelo de datos Django | Tabla `authreg` creada adicionalmente a `auth_user`.                    |
| ⚙️ Docker Jitsi           | Montar volumen con SQLite; Prosody con `lua-dbi-sqlite3`.               |
| 🛠️ Gestión de usuarios    | Desde Django Admin, sincronizado con `authreg` vía signals.             |
| 🚫 Contraseñas            | En texto plano (solo para desarrollo).                                  |
| ⚠️ JWT                    | Postergado hasta que esté todo funcional; no interferirá con este paso. |

---

## 🛠️ Pasos Técnicos Adaptados

### 1. Configurar `mod_auth_sql` en Prosody

- Habilita `mod_auth_sql` descargado a `~/.jitsi-meet-cfg/prosody/prosody-plugins-custom`.
- Agrega al VirtualHost en `~/.jitsi-meet-cfg/prosody/config/conf.d/jitsi-meet.cfg.lua`:

```lua
VirtualHost "meet.localhost"
    authentication = "sql"
    sql = {
        driver = "SQLite3";
        database = "/config/sqlite/jitsi-django.sqlite3";
    }
```

- Asegúrate de que el archivo `db.sqlite3` de Django esté montado como volumen Docker en `/config/sqlite/jitsi-django.sqlite3`.

```yaml
# docker-compose.override.yml
services:
  prosody:
    volumes:
      - ./django/db/db.sqlite3:/config/sqlite/jitsi-django.sqlite3
      - ./jitsi/prosody-plugins-custom:/prosody-plugins-custom
```

### 2. Crear tabla `authreg` en Django (si no existe aún)

Ejecutar una migración o manualmente desde Django shell:

```sql
CREATE TABLE authreg (
    username TEXT NOT NULL,
    realm TEXT NOT NULL,
    password TEXT,
    PRIMARY KEY(username, realm)
);
```

### 3. Extender Django para poblar `authreg`

En `signals.py` o dentro de la app `users`:

```python
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
import sqlite3
import os

SQLITE_PATH = os.path.join(BASE_DIR, "db", "db.sqlite3")
XMPP_REALM = "meet.localhost"

@receiver(post_save, sender=User)
def sync_user_to_authreg(sender, instance, **kwargs):
    if hasattr(instance, "_raw_password"):
        conn = sqlite3.connect(SQLITE_PATH)
        c = conn.cursor()
        c.execute("""
            REPLACE INTO authreg (username, realm, password)
            VALUES (?, ?, ?)""",
            (instance.username, XMPP_REALM, instance._raw_password))
        conn.commit()
        conn.close()
```

Luego, donde uses `set_password()` (por ejemplo, en un formulario de registro o admin personalizado):

```python
user._raw_password = form.cleaned_data['password1']
user.set_password(user._raw_password)
user.save()
```

> ⚠️ Solo para desarrollo. Nunca uses esta lógica en producción sin cifrado.

---

## 🧪 Checklist Adaptado al Estado Actual

| Tarea                                                | Estado         |
| ---------------------------------------------------- | -------------- |
| Prosody configurado para `mod_auth_sql`              | 🔄 En progreso |
| Tabla `authreg` creada en base SQLite                | ✅ Listo       |
| Docker monta volumen de SQLite al contenedor Prosody | 🔄 En progreso |
| Django inserta usuarios en `authreg` vía signals     | 🔄 En progreso |
| Usuario admin de prueba creado y probado             | ⏳ Pendiente   |
| Jitsi solicita login y autentica desde SQLite        | ⏳ Pendiente   |
| JWT funcional en entorno de producción               | ⏳ A definir   |

---

## ⚙️ Recomendaciones Próximos Pasos (alinea con tu roadmap)

### Esta Semana

- [ ] Montar correctamente SQLite como volumen en contenedor Jitsi.
- [ ] Probar que Prosody lea tabla `authreg` desde esa base.
- [ ] Crear 1 usuario desde Django con contraseña simple y verificar login desde interfaz Jitsi.
- [ ] Añadir logs en Prosody para ver fallos de autenticación.

### Corto Plazo

- [ ] Consolidar sincronización automática vía signals.
- [ ] Implementar login/registro con contraseña doble (una para Django, otra para XMPP si se desea separar).
- [ ] Preparar migración a base PostgreSQL (escalable).

### Opcional

- [ ] Si quieres fusionar esto con el sistema de roles: crea una columna `role` en `authreg` (aunque Prosody no la use) para trazabilidad desde Django.

---

## 📌 Conclusión Adaptada

Tu proyecto tiene una arquitectura modular y bien organizada. Esta estrategia de integración mantiene esa modularidad:

✅ Aísla Prosody pero lo conecta por una base compartida.
✅ Permite que Django administre toda la lógica de usuarios.
✅ Compatible con el entorno Docker y SQLite de desarrollo actual.
⚠️ Necesita migrarse a un backend más robusto (PostgreSQL) para producción.

¿Quieres que te genere directamente el código de sincronización en Django o el fragmento de docker-compose para el volumen de SQLite?

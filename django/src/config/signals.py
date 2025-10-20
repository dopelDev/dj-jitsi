from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db import connection
from django.conf import settings

XMPP_REALM = getattr(settings, 'JITSI_XMPP_REALM', 'meet.localhost')

@receiver(post_save, sender=User)
def sync_user_to_authreg(sender, instance, created, **kwargs):
    """Sincronizar usuarios Django con tabla authreg para Jitsi"""
    # Solo sincronizar si hay contraseña en texto plano guardada temporalmente
    if hasattr(instance, '_plain_password'):
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO authreg (username, realm, password)
                VALUES (%s, %s, %s)
            """, [instance.username, XMPP_REALM, instance._plain_password])
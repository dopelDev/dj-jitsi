from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('models', '0002_signuprequest_decided_by_signuprequest_decision_note'),
    ]
    
    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS authreg (
                username TEXT NOT NULL,
                realm TEXT NOT NULL,
                password TEXT,
                PRIMARY KEY(username, realm)
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS authreg;"
        ),
    ]

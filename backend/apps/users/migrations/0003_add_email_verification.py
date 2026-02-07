import uuid
from django.db import migrations, models


def generate_unique_tokens(apps, schema_editor):
    """Give every existing user a unique verification_token."""
    User = apps.get_model('users', 'User')
    for user in User.objects.all():
        user.verification_token = uuid.uuid4()
        user.save(update_fields=['verification_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        # Step 1: add field WITHOUT unique constraint
        migrations.AddField(
            model_name='user',
            name='verification_token',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
        # Step 2: backfill unique values for existing rows
        migrations.RunPython(
            generate_unique_tokens,
            migrations.RunPython.noop,
        ),
        # Step 3: add unique constraint
        migrations.AlterField(
            model_name='user',
            name='verification_token',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]

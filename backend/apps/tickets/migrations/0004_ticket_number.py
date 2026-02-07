from django.db import migrations, models


def assign_ticket_numbers(apps, schema_editor):
    """Assign sequential ticket numbers per organization."""
    Ticket = apps.get_model('tickets', 'Ticket')
    orgs = (
        Ticket.objects
        .values_list('organization_id', flat=True)
        .distinct()
    )
    for org_id in orgs:
        tickets = (
            Ticket.objects
            .filter(organization_id=org_id)
            .order_by('created_at')
        )
        for i, ticket in enumerate(tickets, start=1):
            ticket.ticket_number = i
            ticket.save(update_fields=['ticket_number'])


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_ticket_organization_ticket_idx_ticket_org'),
    ]

    operations = [
        # Step 1: add field nullable, no constraint
        migrations.AddField(
            model_name='ticket',
            name='ticket_number',
            field=models.PositiveIntegerField(
                null=True,
                help_text='Sequential number per organization.',
            ),
        ),
        # Step 2: backfill existing tickets
        migrations.RunPython(
            assign_ticket_numbers,
            migrations.RunPython.noop,
        ),
        # Step 3: make non-nullable
        migrations.AlterField(
            model_name='ticket',
            name='ticket_number',
            field=models.PositiveIntegerField(
                editable=False,
                help_text='Sequential number per organization.',
            ),
        ),
        # Step 4: add unique constraint
        migrations.AddConstraint(
            model_name='ticket',
            constraint=models.UniqueConstraint(
                fields=['organization', 'ticket_number'],
                name='uq_ticket_org_number',
            ),
        ),
    ]

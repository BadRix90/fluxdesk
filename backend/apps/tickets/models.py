from django.conf import settings
from django.db import models
from django.db.models import Max
from django.utils import timezone

from apps.core.models import SoftDeleteModel, TimestampedModel


class TicketQuerySet(models.QuerySet):
    """Custom QuerySet for Ticket filtering."""

    def for_org(self, organization):
        return self.filter(organization=organization)

    def active(self):
        return self.filter(deleted_at__isnull=True)

    def open_tickets(self):
        return self.active().exclude(status=Ticket.Status.CLOSED)

    def unassigned(self):
        return self.active().filter(
            assignee__isnull=True,
            status=Ticket.Status.NEW,
        )

    def escalation_candidates(self):
        """Tickets open > 24h without response."""
        cutoff = timezone.now() - timezone.timedelta(hours=24)
        return self.active().filter(
            status=Ticket.Status.OPEN,
            updated_at__lt=cutoff,
        )

    def auto_close_candidates(self):
        """Resolved tickets older than FLUX_AUTO_CLOSE_DAYS."""
        days = getattr(settings, 'FLUX_AUTO_CLOSE_DAYS', 7)
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.active().filter(
            status=Ticket.Status.RESOLVED,
            resolved_at__lt=cutoff,
        )


class Ticket(TimestampedModel, SoftDeleteModel):
    """Core ticket model."""

    class Status(models.TextChoices):
        NEW = 'NEW', 'New'
        OPEN = 'OPEN', 'Open'
        WAITING = 'WAITING', 'Waiting'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    class Priority(models.IntegerChoices):
        LOW = 1, 'Low'
        NORMAL = 2, 'Normal'
        HIGH = 3, 'High'
        CRITICAL = 4, 'Critical'

    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='tickets',
        null=True,
        blank=True,
    )
    ticket_number = models.PositiveIntegerField(
        editable=False,
        help_text='Sequential number per organization.',
    )
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.NEW,
    )
    priority = models.IntegerField(
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tickets',
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    objects = TicketQuerySet.as_manager()

    class Meta:
        db_table = 'flux_tickets'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'ticket_number'],
                name='uq_ticket_org_number',
            ),
        ]
        indexes = [
            models.Index(
                fields=['status'],
                condition=models.Q(deleted_at__isnull=True),
                name='idx_ticket_status_active',
            ),
            models.Index(
                fields=['assignee'],
                condition=models.Q(deleted_at__isnull=True),
                name='idx_ticket_assignee_active',
            ),
            models.Index(
                fields=['priority', '-created_at'],
                name='idx_ticket_priority',
            ),
            models.Index(
                fields=['organization', '-created_at'],
                name='idx_ticket_org',
            ),
        ]

    def __str__(self) -> str:
        return f'#{self.ticket_number} {self.subject}'

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self._next_number()
        super().save(*args, **kwargs)

    def _next_number(self) -> int:
        """Get the next ticket number for this organization."""
        result = Ticket.objects.filter(
            organization=self.organization,
        ).aggregate(max_num=Max('ticket_number'))
        return (result['max_num'] or 0) + 1

    def assign_to(self, agent) -> None:
        """Assign ticket to an agent."""
        self.assignee = agent
        if self.status == self.Status.NEW:
            self.status = self.Status.OPEN
        self.save(update_fields=['assignee', 'status', 'updated_at'])

    def resolve(self) -> None:
        """Mark ticket as resolved."""
        self.status = self.Status.RESOLVED
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolved_at', 'updated_at'])

    def close(self) -> None:
        """Close the ticket."""
        self.status = self.Status.CLOSED
        self.closed_at = timezone.now()
        self.save(update_fields=['status', 'closed_at', 'updated_at'])

    def escalate(self) -> bool:
        """Increase priority by 1. Returns False if already critical."""
        if self.priority >= self.Priority.CRITICAL:
            return False
        old_priority = self.priority
        self.priority = min(self.priority + 1, self.Priority.CRITICAL)
        self.save(update_fields=['priority', 'updated_at'])
        Escalation.objects.create(
            ticket=self,
            from_priority=old_priority,
            to_priority=self.priority,
            reason='auto',
        )
        return True

    @property
    def age_hours(self) -> float:
        """Hours since ticket creation."""
        delta = timezone.now() - self.created_at
        return delta.total_seconds() / 3600


class Comment(TimestampedModel):
    """Comment on a ticket (public or internal note)."""

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField()
    is_internal = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'flux_comments'
        ordering = ['created_at']

    def __str__(self) -> str:
        return f'Comment on #{self.ticket_id} by {self.author}'


class Attachment(TimestampedModel):
    """File attachment on a ticket."""

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    file = models.FileField(upload_to='attachments/%Y/%m/')
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploads',
    )

    class Meta:
        db_table = 'flux_attachments'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.file_name


class Escalation(TimestampedModel):
    """Audit log for ticket escalations."""

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='escalations',
    )
    from_priority = models.IntegerField(choices=Ticket.Priority.choices)
    to_priority = models.IntegerField(choices=Ticket.Priority.choices)
    reason = models.CharField(max_length=50, default='auto')

    class Meta:
        db_table = 'flux_escalations'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'#{self.ticket_id}: {self.from_priority} -> {self.to_priority}'

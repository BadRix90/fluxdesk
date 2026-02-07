import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """Abstract base model with created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Abstract base model with soft-delete support."""

    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self) -> None:
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class Organization(TimestampedModel):
    """A company or team using FluxDesk."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80, unique=True)
    support_email = models.EmailField()
    website = models.URLField(blank=True)
    logo = models.ImageField(
        upload_to='org_logos/',
        blank=True,
        null=True,
    )
    signature_html = models.TextField(
        blank=True,
        help_text='HTML signature appended to outgoing emails.',
    )
    is_active = models.BooleanField(default=True)

    # SMTP (outbound email per org)
    smtp_host = models.CharField(max_length=255, blank=True)
    smtp_port = models.IntegerField(default=587)
    smtp_use_tls = models.BooleanField(default=True)
    smtp_user = models.CharField(max_length=255, blank=True)
    smtp_password = models.CharField(max_length=255, blank=True)

    # IMAP (inbound email polling per org)
    imap_host = models.CharField(max_length=255, blank=True)
    imap_user = models.CharField(max_length=255, blank=True)
    imap_password = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'flux_organizations'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Invitation(TimestampedModel):
    """Pending invitation for a new agent/admin."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        EXPIRED = 'EXPIRED', 'Expired'

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='invitations',
    )
    email = models.EmailField()
    role = models.CharField(max_length=10, default='AGENT')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_invitations',
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'flux_invitations'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.email} -> {self.organization}'

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def accept(self) -> None:
        self.status = self.Status.ACCEPTED
        self.accepted_at = timezone.now()
        self.save(update_fields=['status', 'accepted_at'])

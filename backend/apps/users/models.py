import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Flux user - extends Django's AbstractUser."""

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        AGENT = 'AGENT', 'Agent'
        CUSTOMER = 'CUSTOMER', 'Customer'

    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='members',
        null=True,
        blank=True,
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
    )
    email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
    )

    class Meta:
        db_table = 'flux_users'
        ordering = ['username']

    def __str__(self) -> str:
        return self.get_full_name() or self.username

    @property
    def is_agent(self) -> bool:
        return self.role in (self.Role.AGENT, self.Role.ADMIN)

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def check_escalations():
    """Escalate tickets open > 24h without response."""
    from apps.tickets.models import Ticket

    candidates = Ticket.objects.escalation_candidates()
    escalated = 0
    for ticket in candidates:
        if ticket.escalate():
            escalated += 1
    logger.info('Escalated %d tickets', escalated)
    return escalated


@shared_task
def auto_close_resolved():
    """Close resolved tickets after FLUX_AUTO_CLOSE_DAYS."""
    from apps.tickets.models import Ticket

    candidates = Ticket.objects.auto_close_candidates()
    now = timezone.now()
    count = candidates.update(
        status=Ticket.Status.CLOSED,
        closed_at=now,
    )
    logger.info('Auto-closed %d tickets', count)
    return count

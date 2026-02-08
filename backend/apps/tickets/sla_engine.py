"""SLA deadline calculation engine.

Orchestrates SLA matching, deadline computation, pause/resume.
Called by ViewSets and Celery tasks on ticket lifecycle events.
"""

import logging

from django.utils import timezone

logger = logging.getLogger(__name__)


# ── Public API ───────────────────────────────────────────────


def match_sla_for_ticket(ticket):
    """Find the first active SLA matching the ticket's priority."""
    from apps.tickets.models import SLA

    return SLA.objects.filter(
        organization=ticket.organization,
        is_active=True,
        priority_filter__contains=[ticket.priority],
    ).order_by('position').first()


def assign_sla_and_deadlines(ticket):
    """Assign SLA on ticket creation and compute initial deadlines."""
    sla = match_sla_for_ticket(ticket)
    if not sla:
        return
    ticket.sla = sla
    calendar = _get_calendar(ticket.organization)
    if not calendar:
        return
    now = ticket.created_at or timezone.now()
    _set_initial_deadlines(ticket, sla, calendar, now)
    _update_escalation_at(ticket)
    ticket.save(update_fields=_sla_update_fields())


def on_agent_response(ticket, is_first):
    """Handle SLA when an agent posts a public comment."""
    now = timezone.now()
    ticket.last_agent_response_at = now
    if is_first and not ticket.first_response_at:
        ticket.first_response_at = now
        ticket.first_response_deadline = None
    ticket.next_response_deadline = None
    _update_escalation_at(ticket)
    ticket.save(update_fields=_sla_update_fields())


def on_customer_response(ticket):
    """Handle SLA when a customer posts a comment."""
    now = timezone.now()
    ticket.last_customer_response_at = now
    sla = ticket.sla
    calendar = _get_calendar(ticket.organization)
    if sla and calendar and sla.next_response_minutes:
        ticket.next_response_deadline = _add_biz_minutes(
            now, sla.next_response_minutes, calendar,
        )
    _update_escalation_at(ticket)
    ticket.save(update_fields=_sla_update_fields())


def pause_sla(ticket):
    """Pause SLA when ticket goes to WAITING status."""
    now = timezone.now()
    calendar = _get_calendar(ticket.organization)
    if calendar:
        ticket.sla_remaining_first_response = _remaining_biz(
            ticket.first_response_deadline, now, calendar,
        )
        ticket.sla_remaining_next_response = _remaining_biz(
            ticket.next_response_deadline, now, calendar,
        )
        ticket.sla_remaining_resolution = _remaining_biz(
            ticket.resolution_deadline, now, calendar,
        )
    _clear_deadlines(ticket)
    ticket.save(update_fields=_sla_update_fields())


def resume_sla(ticket):
    """Resume SLA when ticket moves from WAITING back to OPEN."""
    calendar = _get_calendar(ticket.organization)
    if not calendar or not ticket.sla:
        return
    now = timezone.now()
    _restore_deadlines(ticket, calendar, now)
    _clear_remaining(ticket)
    _update_escalation_at(ticket)
    ticket.save(update_fields=_sla_update_fields())


# ── Private helpers ──────────────────────────────────────────


def _get_calendar(organization):
    """Load the organization's business calendar or None."""
    from apps.core.models import BusinessCalendar

    if not organization:
        return None
    try:
        return organization.business_calendar
    except BusinessCalendar.DoesNotExist:
        return None


def _set_initial_deadlines(ticket, sla, calendar, now):
    """Compute first_response and resolution deadlines."""
    if sla.first_response_minutes:
        ticket.first_response_deadline = _add_biz_minutes(
            now, sla.first_response_minutes, calendar,
        )
    if sla.resolution_minutes:
        ticket.resolution_deadline = _add_biz_minutes(
            now, sla.resolution_minutes, calendar,
        )


def _add_biz_minutes(start, minutes, calendar):
    """Wrapper around pure business_time.add_business_minutes."""
    from apps.core.business_time import add_business_minutes

    return add_business_minutes(
        start, minutes,
        calendar.business_hours, calendar.holidays, calendar.timezone,
    )


def _remaining_biz(deadline, now, calendar):
    """Compute remaining business minutes until deadline."""
    from apps.core.business_time import remaining_business_minutes

    if not deadline:
        return None
    mins = remaining_business_minutes(
        deadline, now,
        calendar.business_hours, calendar.holidays, calendar.timezone,
    )
    return max(mins, 0) if mins else None


def _update_escalation_at(ticket):
    """Set escalation_at to the earliest active deadline."""
    deadlines = [
        ticket.first_response_deadline,
        ticket.next_response_deadline,
        ticket.resolution_deadline,
    ]
    active = [d for d in deadlines if d is not None]
    ticket.escalation_at = min(active) if active else None


def _clear_deadlines(ticket):
    """Null all three deadlines and escalation_at."""
    ticket.first_response_deadline = None
    ticket.next_response_deadline = None
    ticket.resolution_deadline = None
    ticket.escalation_at = None


def _restore_deadlines(ticket, calendar, now):
    """Recalculate deadlines from saved remaining minutes."""
    if ticket.sla_remaining_first_response:
        ticket.first_response_deadline = _add_biz_minutes(
            now, ticket.sla_remaining_first_response, calendar,
        )
    if ticket.sla_remaining_next_response:
        ticket.next_response_deadline = _add_biz_minutes(
            now, ticket.sla_remaining_next_response, calendar,
        )
    if ticket.sla_remaining_resolution:
        ticket.resolution_deadline = _add_biz_minutes(
            now, ticket.sla_remaining_resolution, calendar,
        )


def _clear_remaining(ticket):
    """Null the paused remaining-minute fields."""
    ticket.sla_remaining_first_response = None
    ticket.sla_remaining_next_response = None
    ticket.sla_remaining_resolution = None


def _sla_update_fields():
    """Fields to include in save(update_fields=...) for SLA changes."""
    return [
        'sla', 'first_response_at', 'last_agent_response_at',
        'last_customer_response_at', 'first_response_deadline',
        'next_response_deadline', 'resolution_deadline',
        'escalation_at', 'sla_remaining_first_response',
        'sla_remaining_next_response', 'sla_remaining_resolution',
        'updated_at',
    ]

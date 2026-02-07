from django.conf import settings
from django.core.mail import EmailMessage, get_connection


def _org_connection(org):
    """Build SMTP connection from organization credentials."""
    return get_connection(
        host=org.smtp_host,
        port=org.smtp_port,
        username=org.smtp_user,
        password=org.smtp_password,
        use_tls=org.smtp_use_tls,
    )


def _ticket_message_id(ticket):
    """Generate a stable Message-ID for a ticket thread."""
    org_domain = ticket.organization.support_email.split('@')[1]
    return f'<ticket-{ticket.id}@{org_domain}>'


def _set_thread_headers(email_msg, ticket):
    """Set In-Reply-To and References for email threading."""
    thread_id = _ticket_message_id(ticket)
    email_msg.extra_headers['In-Reply-To'] = thread_id
    email_msg.extra_headers['References'] = thread_id


def send_ticket_created_email(ticket) -> None:
    """Notify the customer that a ticket was created."""
    org = ticket.organization
    msg_id = _ticket_message_id(ticket)
    email = EmailMessage(
        subject=f'[#{ticket.ticket_number}] {ticket.subject}',
        body=(
            f'Hallo {ticket.customer.first_name or ""},\n\n'
            f'deine Anfrage ist bei uns eingegangen.\n\n'
            f'Ticketnummer: #{ticket.ticket_number}\n'
            f'Betreff: {ticket.subject}\n\n'
            f'Wir melden uns schnellstmöglich bei dir.\n\n'
            f'Viele Grüße,\n{org.name}'
        ),
        from_email=f'{org.name} <{org.support_email}>',
        to=[ticket.customer.email],
        reply_to=[org.support_email],
        connection=_org_connection(org),
        headers={'Message-ID': msg_id},
    )
    email.send()


def send_comment_email(comment) -> None:
    """Notify the customer about a new agent reply."""
    if comment.is_internal:
        return
    ticket = comment.ticket
    org = ticket.organization
    email = EmailMessage(
        subject=f'Re: [#{ticket.ticket_number}] {ticket.subject}',
        body=(
            f'Hallo {ticket.customer.first_name or ""},\n\n'
            f'{comment.text}\n\n'
            f'Viele Grüße,\n{org.name}'
        ),
        from_email=f'{org.name} <{org.support_email}>',
        to=[ticket.customer.email],
        reply_to=[org.support_email],
        connection=_org_connection(org),
    )
    _set_thread_headers(email, ticket)
    email.send()


def send_auto_reply_email(ticket) -> None:
    """Send automatic receipt confirmation for inbound emails."""
    org = ticket.organization
    email = EmailMessage(
        subject=f'Re: [#{ticket.ticket_number}] {ticket.subject}',
        body=(
            f'Moin {ticket.customer.first_name or ""},\n\n'
            f'deine Anfrage ist bei uns eingegangen mit der '
            f'Ticketnummer #{ticket.ticket_number}.\n\n'
            f'Wir melden uns schnellstmöglich bei dir.\n\n'
            f'Viele Grüße,\n{org.name}'
        ),
        from_email=f'{org.name} <{org.support_email}>',
        to=[ticket.customer.email],
        reply_to=[org.support_email],
        connection=_org_connection(org),
    )
    _set_thread_headers(email, ticket)
    email.send()


def send_ticket_resolved_email(ticket) -> None:
    """Notify the customer that their ticket was resolved."""
    org = ticket.organization
    email = EmailMessage(
        subject=f'Re: [#{ticket.ticket_number}] {ticket.subject}',
        body=(
            f'Hallo {ticket.customer.first_name or ""},\n\n'
            f'dein Ticket #{ticket.ticket_number} wurde gelöst.\n\n'
            f'Falls du noch Fragen hast, antworte einfach '
            f'auf diese Mail.\n\n'
            f'Viele Grüße,\n{org.name}'
        ),
        from_email=f'{org.name} <{org.support_email}>',
        to=[ticket.customer.email],
        reply_to=[org.support_email],
        connection=_org_connection(org),
    )
    _set_thread_headers(email, ticket)
    email.send()


def send_verification_email(user) -> None:
    """Send email verification link to a newly registered user."""
    link = f'{settings.FRONTEND_URL}/verify/{user.verification_token}'
    email = EmailMessage(
        subject='FluxDesk - E-Mail bestätigen',
        body=(
            f'Hallo {user.first_name},\n\n'
            f'bitte bestätige deine E-Mail-Adresse:\n\n'
            f'{link}\n\n'
            f'Der Link ist 48 Stunden gültig.\n\n'
            f'Viele Grüße,\nFluxDesk'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.send()


def send_invitation_email(invitation) -> None:
    """Send invitation link to a new agent."""
    link = f'{settings.FRONTEND_URL}/invite/{invitation.token}'
    org = invitation.organization
    email = EmailMessage(
        subject=f'FluxDesk - Einladung von {org.name}',
        body=(
            f'Hallo,\n\n'
            f'du wurdest eingeladen, dem Team von '
            f'"{org.name}" auf FluxDesk beizutreten.\n\n'
            f'Klicke hier, um dein Konto einzurichten:\n\n'
            f'{link}\n\n'
            f'Der Link ist 7 Tage gültig.\n\n'
            f'Viele Grüße,\nFluxDesk'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[invitation.email],
        reply_to=[org.support_email],
    )
    email.send()

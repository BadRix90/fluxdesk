import email
import hashlib
import imaplib
import logging
import re

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)

TICKET_PATTERN = re.compile(r'\[#(\d+)\]')

REPLY_MARKERS = [
    re.compile(r'^(Am|On) .+ schrieb .+:'),
    re.compile(r'^(Am|On) .+ wrote:'),
    re.compile(r'^-{2,}'),
    re.compile(r'^_{2,}'),
    re.compile(r'^>'),
    re.compile(r'^Gesendet von Outlook', re.IGNORECASE),
    re.compile(r'^Sent from (Outlook|my iPhone|Mail)', re.IGNORECASE),
    re.compile(r'^Von:.*@'),
    re.compile(r'^From:.*@'),
]

LOOP_HEADERS = {
    'Auto-Submitted': ['auto-replied', 'auto-generated'],
    'X-Auto-Response-Suppress': ['all'],
    'Precedence': ['bulk', 'list', 'junk'],
    'X-Loop': ['yes', 'true'],
}


# ── Celery Tasks ─────────────────────────────────────────────

@shared_task
def check_escalations():
    """Escalate tickets open > 24h without response."""
    from apps.tickets.models import Ticket

    candidates = Ticket.objects.escalation_candidates()
    escalated = sum(1 for t in candidates if t.escalate())
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


@shared_task
def poll_all_inboxes():
    """Poll IMAP inbox for every org with credentials."""
    from apps.core.models import Organization

    orgs = Organization.objects.filter(
        is_active=True,
        imap_host__gt='',
        imap_user__gt='',
    )
    total = 0
    for org in orgs:
        total += _poll_org_inbox(org)
    logger.info('Total inbound: %d', total)
    return total


# ── IMAP Connection ──────────────────────────────────────────

def _poll_org_inbox(org):
    """Poll one organization's IMAP inbox."""
    conn = None
    try:
        conn = _connect_imap(org.imap_host, org.imap_user, org.imap_password)
        uids = _search_unseen(conn)
        processed = _process_uids(conn, uids, org)
        logger.info('%s: %d/%d processed', org.name, processed, len(uids))
        return processed
    except Exception:
        logger.exception('IMAP failed for %s', org.name)
        return 0
    finally:
        if conn:
            _safe_logout(conn)


def _connect_imap(host, user, password):
    """Open IMAP SSL connection and select INBOX."""
    conn = imaplib.IMAP4_SSL(host)
    conn.login(user, password)
    conn.select('INBOX')
    return conn


def _search_unseen(conn):
    """Return list of UIDs for unseen messages."""
    _, data = conn.uid('search', None, 'UNSEEN')
    raw = data[0]
    if not raw:
        return []
    return raw.split()


def _process_uids(conn, uids, org):
    """Fetch each UID with PEEK, process, mark SEEN."""
    processed = 0
    for uid in uids:
        try:
            msg = _fetch_peek(conn, uid)
            if not msg:
                _mark_seen(conn, uid)
                continue
            created = _handle_message(msg, org)
            _mark_seen(conn, uid)
            if created:
                processed += 1
        except Exception:
            logger.exception('Failed UID %s for %s', uid, org.name)
    return processed


def _fetch_peek(conn, uid):
    """Fetch email without marking as SEEN."""
    _, data = conn.uid('fetch', uid, '(BODY.PEEK[])')
    if not data or not data[0]:
        return None
    raw = data[0][1]
    return email.message_from_bytes(raw)


def _mark_seen(conn, uid):
    """Explicitly mark a message as SEEN."""
    conn.uid('store', uid, '+FLAGS', '\\Seen')


# ── Message Routing ──────────────────────────────────────────

def _handle_message(msg, org):
    """Route: skip loops, find ticket or create new."""
    if _is_loop(msg):
        logger.debug('Loop detected, skipping')
        return False

    sender = _extract_sender_email(msg.get('From', ''))
    if not sender:
        return False
    if sender.lower() == org.support_email.lower():
        return False

    subject = _decode_header(msg.get('Subject', ''))
    body = _extract_body(msg)
    if not body:
        return False

    message_id = msg.get('Message-ID', '')
    references = _extract_references(msg)

    ticket = _find_ticket_by_subject(subject, org)
    if not ticket:
        ticket = _find_ticket_by_references(references, org)

    if ticket:
        return _add_comment(ticket, sender, body, message_id)
    return _create_ticket(subject, sender, body, message_id, org)


def _is_loop(msg):
    """Detect auto-responses and mailing list bounces."""
    for header, values in LOOP_HEADERS.items():
        raw = (msg.get(header) or '').lower().strip()
        if any(v in raw for v in values):
            return True
    if msg.get('List-Unsubscribe'):
        return True
    return False


# ── Ticket Lookup (3-layer like Zammad) ──────────────────────

def _find_ticket_by_subject(subject, org):
    """Layer 1: ticket number in subject [#123]."""
    match = TICKET_PATTERN.search(subject)
    if not match:
        return None
    return _get_ticket(int(match.group(1)), org)


def _find_ticket_by_references(references, org):
    """Layer 2: Message-ID references in DB."""
    from apps.tickets.models import Comment

    for ref in references:
        ref_md5 = hashlib.md5(ref.encode()).hexdigest()
        comment = Comment.objects.filter(
            message_id_md5=ref_md5,
            ticket__organization=org,
        ).select_related('ticket').first()
        if comment:
            return comment.ticket
    return None


def _get_ticket(ticket_number, org):
    """Find ticket by number within organization."""
    from apps.tickets.models import Ticket

    try:
        return Ticket.objects.select_related(
            'customer', 'organization',
        ).get(
            ticket_number=ticket_number,
            organization=org,
        )
    except Ticket.DoesNotExist:
        return None


def _extract_references(msg):
    """Get all Message-IDs from References + In-Reply-To."""
    refs = []
    for header in ('References', 'In-Reply-To'):
        raw = msg.get(header, '')
        refs.extend(re.findall(r'<[^>]+>', raw))
    return refs


# ── Actions ──────────────────────────────────────────────────

def _add_comment(ticket, sender, body, message_id):
    """Add comment to existing ticket, reopen if closed."""
    from apps.tickets.models import Comment

    author = _find_or_create_customer(sender, ticket.organization)
    msg_md5 = hashlib.md5(message_id.encode()).hexdigest()

    if Comment.objects.filter(message_id_md5=msg_md5).exists():
        logger.debug('Duplicate message_id, skipping')
        return False

    Comment.objects.create(
        ticket=ticket,
        author=author,
        text=body,
        message_id=message_id,
        message_id_md5=msg_md5,
    )
    _reopen_if_closed(ticket)
    logger.info('Comment on #%d from %s', ticket.ticket_number, sender)
    return True


def _create_ticket(subject, sender, body, message_id, org):
    """Create new ticket from inbound email."""
    from apps.core.email import send_auto_reply_email
    from apps.tickets.models import Ticket

    customer = _find_or_create_customer(sender, org)
    ticket = Ticket.objects.create(
        organization=org,
        customer=customer,
        subject=subject or 'Kein Betreff',
        description=body,
    )
    _store_message_id(ticket, message_id)
    send_auto_reply_email(ticket)
    logger.info('New ticket #%d from %s', ticket.ticket_number, sender)
    return True


def _store_message_id(ticket, message_id):
    """Store the original email Message-ID on the ticket."""
    if not message_id:
        return
    from apps.tickets.models import Comment

    msg_md5 = hashlib.md5(message_id.encode()).hexdigest()
    Comment.objects.create(
        ticket=ticket,
        author=ticket.customer,
        text=ticket.description,
        message_id=message_id,
        message_id_md5=msg_md5,
        is_internal=True,
    )


def _reopen_if_closed(ticket):
    """Reopen a closed/resolved ticket on customer reply."""
    from apps.tickets.models import Ticket

    if ticket.status in (Ticket.Status.CLOSED, Ticket.Status.RESOLVED):
        ticket.status = Ticket.Status.OPEN
        ticket.closed_at = None
        ticket.resolved_at = None
        ticket.save(update_fields=[
            'status', 'closed_at', 'resolved_at', 'updated_at',
        ])
        logger.info('Reopened ticket #%d', ticket.ticket_number)


# ── Customer Lookup ──────────────────────────────────────────

def _find_or_create_customer(sender_email, org):
    """Find existing customer or create a new one."""
    from apps.users.models import User

    user, created = User.objects.get_or_create(
        email=sender_email,
        organization=org,
        defaults={
            'username': sender_email.split('@')[0],
            'role': User.Role.CUSTOMER,
            'email_verified': True,
        },
    )
    if created:
        user.set_unusable_password()
        user.save(update_fields=['password'])
        logger.info('Created customer %s for %s', sender_email, org.name)
    return user


# ── Email Parsing ────────────────────────────────────────────

def _decode_header(raw):
    """Decode a MIME-encoded email header."""
    parts = email.header.decode_header(raw)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(
                part.decode(charset or 'utf-8', errors='replace'),
            )
        else:
            decoded.append(part)
    return ''.join(decoded)


def _extract_sender_email(from_header):
    """Extract plain email from 'Name <email>' format."""
    match = re.search(r'<(.+?)>', from_header)
    if match:
        return match.group(1).lower()
    return from_header.strip().lower()


def _extract_body(msg):
    """Extract plain text body from email message."""
    body = _get_text_payload(msg)
    if not body:
        return ''
    return _strip_quoted_reply(body).strip()


def _get_text_payload(msg):
    """Walk message parts and return first text/plain."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or 'utf-8'
                return payload.decode(charset, errors='replace')
        return ''
    payload = msg.get_payload(decode=True)
    charset = msg.get_content_charset() or 'utf-8'
    return payload.decode(charset, errors='replace')


def _strip_quoted_reply(text):
    """Remove quoted original message from reply text."""
    lines = text.split('\n')
    clean = []
    for line in lines:
        if _is_reply_marker(line):
            break
        clean.append(line)
    return '\n'.join(clean)


def _is_reply_marker(line):
    """Check if a line starts a quoted reply section."""
    for pattern in REPLY_MARKERS:
        if pattern.match(line.strip()):
            return True
    return False


def _safe_logout(conn):
    """Logout from IMAP, ignoring errors."""
    try:
        conn.close()
        conn.logout()
    except Exception:
        pass

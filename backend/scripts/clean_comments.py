"""One-time script to strip signature remnants from existing comments."""

import os
import re
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from apps.tickets.models import Comment  # noqa: E402

MARKERS = [
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


def is_marker(line):
    """Check if a line is a reply/signature marker."""
    for pattern in MARKERS:
        if pattern.match(line.strip()):
            return True
    return False


def strip_reply(text):
    """Strip quoted reply and signature from text."""
    lines = text.split('\n')
    clean = []
    for line in lines:
        if is_marker(line):
            break
        clean.append(line)
    return '\n'.join(clean).strip()


def main():
    """Clean all comments with signature remnants."""
    for comment in Comment.objects.all():
        cleaned = strip_reply(comment.text)
        if cleaned != comment.text:
            print(f'Cleaned comment {comment.id}: '
                  f'"{comment.text[:40]}" -> "{cleaned[:40]}"')
            comment.text = cleaned
            comment.save(update_fields=['text'])
        else:
            print(f'Comment {comment.id} OK: "{comment.text[:40]}"')


if __name__ == '__main__':
    main()

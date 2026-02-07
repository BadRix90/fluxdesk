from django.conf import settings
from django.core.mail import send_mail


def send_verification_email(user) -> None:
    """Send email verification link to a newly registered user."""
    link = f'{settings.FRONTEND_URL}/verify/{user.verification_token}'
    send_mail(
        subject='FluxDesk - E-Mail bestätigen',
        message=(
            f'Hallo {user.first_name},\n\n'
            f'bitte bestätige deine E-Mail-Adresse:\n\n'
            f'{link}\n\n'
            f'Der Link ist 48 Stunden gültig.\n\n'
            f'Viele Grüße,\nFluxDesk'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


def send_invitation_email(invitation) -> None:
    """Send invitation link to a new agent."""
    link = f'{settings.FRONTEND_URL}/invite/{invitation.token}'
    org_name = invitation.organization.name
    send_mail(
        subject=f'FluxDesk - Einladung von {org_name}',
        message=(
            f'Hallo,\n\n'
            f'du wurdest eingeladen, dem Team von '
            f'"{org_name}" auf FluxDesk beizutreten.\n\n'
            f'Klicke hier, um dein Konto einzurichten:\n\n'
            f'{link}\n\n'
            f'Der Link ist 7 Tage gültig.\n\n'
            f'Viele Grüße,\nFluxDesk'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invitation.email],
    )

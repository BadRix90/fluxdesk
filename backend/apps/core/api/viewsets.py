from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from apps.core.email import send_invitation_email, send_verification_email
from apps.core.models import BusinessCalendar, Invitation, Organization
from apps.users.api.serializers import UserSerializer

from .serializers import (
    AcceptInvitationSerializer,
    BusinessCalendarSerializer,
    InvitationCreateSerializer,
    InvitationSerializer,
    OrganizationSerializer,
    RegisterSerializer,
    VerifyEmailSerializer,
)


class MeView(viewsets.ViewSet):
    """Return current authenticated user info."""

    def list(self, request):
        return Response(UserSerializer(request.user).data)


class RegisterView(viewsets.ViewSet):
    """Register a new organization + admin user."""

    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        send_verification_email(result['user'])
        return Response(
            {'message': 'Bestätigungs-E-Mail wurde gesendet.'},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(viewsets.ViewSet):
    """Verify email address via token."""

    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'E-Mail erfolgreich bestätigt.'},
        )


class OrganizationViewSet(viewsets.ModelViewSet):
    """Manage the current user's organization."""

    serializer_class = OrganizationSerializer
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        return Organization.objects.filter(
            pk=self.request.user.organization_id,
        )

    def get_object(self):
        return self.request.user.organization

    def list(self, request):
        org = request.user.organization
        if not org:
            return Response(
                {'detail': 'Keine Organisation zugeordnet.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(OrganizationSerializer(org).data)


class InvitationViewSet(viewsets.ModelViewSet):
    """Manage invitations for the organization."""

    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return Invitation.objects.filter(
            organization=self.request.user.organization,
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return InvitationCreateSerializer
        return InvitationSerializer

    def perform_create(self, serializer):
        invitation = serializer.save(
            organization=self.request.user.organization,
            invited_by=self.request.user,
        )
        send_invitation_email(invitation)


class AcceptInvitationView(viewsets.ViewSet):
    """Accept an invitation and create a user account."""

    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = AcceptInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Konto erstellt. Du kannst dich jetzt anmelden.'},
            status=status.HTTP_201_CREATED,
        )


class BusinessCalendarViewSet(viewsets.ModelViewSet):
    """GET/PATCH for the organization's business calendar."""

    serializer_class = BusinessCalendarSerializer
    http_method_names = ['get', 'patch']

    def get_object(self):
        cal, _created = BusinessCalendar.objects.get_or_create(
            organization=self.request.user.organization,
        )
        return cal

    def list(self, request):
        cal = self.get_object()
        return Response(BusinessCalendarSerializer(cal).data)

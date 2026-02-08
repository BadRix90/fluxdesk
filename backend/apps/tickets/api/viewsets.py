from django.db.models import Count
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.email import (
    send_comment_email,
    send_ticket_created_email,
    send_ticket_resolved_email,
)
from apps.tickets.models import Comment, SLA, Ticket
from apps.tickets.sla_engine import (
    assign_sla_and_deadlines,
    on_agent_response,
    on_customer_response,
)

from .serializers import (
    CommentSerializer,
    SLASerializer,
    TicketCreateSerializer,
    TicketDetailSerializer,
    TicketListSerializer,
)


class IsOrgAdmin(permissions.BasePermission):
    """Only allow organization admins."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class TicketViewSet(viewsets.ModelViewSet):
    """CRUD + custom actions for tickets."""

    filterset_fields = ['status', 'priority', 'assignee']
    search_fields = ['subject', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Ticket.objects.active()
        org = getattr(self.request.user, 'organization', None)
        if org:
            qs = qs.for_org(org)
        return (
            qs.select_related('customer', 'assignee', 'sla')
            .annotate(comment_count=Count('comments'))
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        if self.action in ('retrieve',):
            return TicketDetailSerializer
        return TicketListSerializer

    def perform_create(self, serializer):
        serializer.save()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.action == 'create':
            ctx['organization'] = self.request.user.organization
        return ctx

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()
        assign_sla_and_deadlines(ticket)
        send_ticket_created_email(ticket)
        return Response(
            TicketDetailSerializer(ticket).data,
            status=status.HTTP_201_CREATED,
        )

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=['get'])
    def my_queue(self, request):
        """Tickets assigned to current user."""
        qs = self.get_queryset().filter(assignee=request.user)
        page = self.paginate_queryset(qs)
        serializer = TicketListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def unassigned(self, request):
        """Tickets without an assignee."""
        qs = self.get_queryset().filter(
            assignee__isnull=True,
            status=Ticket.Status.NEW,
        )
        page = self.paginate_queryset(qs)
        serializer = TicketListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def escalated(self, request):
        """Tickets with breached or high-priority SLAs."""
        qs = self.get_queryset().filter(priority__gte=Ticket.Priority.HIGH)
        page = self.paginate_queryset(qs)
        serializer = TicketListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign_to_me(self, request, pk=None):
        """Assign ticket to current user."""
        ticket = self.get_object()
        ticket.assign_to(request.user)
        return Response(TicketDetailSerializer(ticket).data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark ticket as resolved."""
        ticket = self.get_object()
        ticket.resolve()
        send_ticket_resolved_email(ticket)
        return Response(TicketDetailSerializer(ticket).data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close the ticket."""
        ticket = self.get_object()
        ticket.close()
        return Response(TicketDetailSerializer(ticket).data)

    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        """Manually escalate ticket priority."""
        ticket = self.get_object()
        if not ticket.escalate():
            return Response(
                {'detail': 'Already at maximum priority.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(TicketDetailSerializer(ticket).data)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore a soft-deleted ticket."""
        ticket = Ticket.objects.get(pk=pk)
        ticket.restore()
        return Response(TicketDetailSerializer(ticket).data)

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        """Add a comment to the ticket."""
        ticket = self.get_object()
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_comment = serializer.save(
            ticket=ticket,
            author=request.user,
        )
        _handle_sla_on_comment(ticket, new_comment, request.user)
        send_comment_email(new_comment)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


def _handle_sla_on_comment(ticket, comment, user):
    """Trigger SLA recalculation based on who commented."""
    if comment.is_internal:
        return
    if user.is_agent:
        is_first = ticket.first_response_at is None
        on_agent_response(ticket, is_first)
    else:
        on_customer_response(ticket)


class CommentViewSet(viewsets.ModelViewSet):
    """Comments on tickets."""

    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SLAViewSet(viewsets.ModelViewSet):
    """CRUD for SLA policies (admin only)."""

    serializer_class = SLASerializer
    permission_classes = [IsOrgAdmin]

    def get_queryset(self):
        return SLA.objects.filter(
            organization=self.request.user.organization,
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
        )

from rest_framework import serializers

from apps.tickets.models import Attachment, Comment, Escalation, SLA, Ticket
from apps.users.api.serializers import UserMinimalSerializer
from apps.users.models import User


class CommentSerializer(serializers.ModelSerializer):
    author = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'ticket', 'author', 'text',
            'is_internal', 'created_at', 'edited_at',
        ]
        read_only_fields = ['id', 'ticket', 'author', 'created_at', 'edited_at']


class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Attachment
        fields = [
            'id', 'ticket', 'file', 'file_name',
            'file_size', 'mime_type', 'uploaded_by', 'created_at',
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at']


class EscalationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Escalation
        fields = [
            'id', 'ticket', 'from_priority',
            'to_priority', 'reason', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class SLAMinimalSerializer(serializers.ModelSerializer):
    """Compact SLA for nesting inside ticket responses."""

    class Meta:
        model = SLA
        fields = ['id', 'name']


class SLASerializer(serializers.ModelSerializer):
    """Full SLA serializer for CRUD."""

    class Meta:
        model = SLA
        fields = [
            'id', 'name', 'position', 'is_active',
            'priority_filter', 'first_response_minutes',
            'next_response_minutes', 'resolution_minutes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TicketListSerializer(serializers.ModelSerializer):
    """Compact ticket for list views."""

    customer = UserMinimalSerializer(read_only=True)
    assignee = UserMinimalSerializer(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'subject', 'status', 'priority',
            'customer', 'assignee', 'created_at', 'updated_at',
            'comment_count', 'escalation_at',
        ]


class TicketDetailSerializer(serializers.ModelSerializer):
    """Full ticket with comments and SLA info."""

    customer = UserMinimalSerializer(read_only=True)
    assignee = UserMinimalSerializer(read_only=True)
    sla = SLAMinimalSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'subject', 'description',
            'status', 'priority', 'customer', 'assignee',
            'created_at', 'updated_at', 'resolved_at', 'closed_at',
            'sla', 'first_response_at', 'last_agent_response_at',
            'last_customer_response_at', 'first_response_deadline',
            'next_response_deadline', 'resolution_deadline',
            'escalation_at', 'comments', 'attachments',
        ]
        read_only_fields = [
            'id', 'ticket_number', 'customer',
            'created_at', 'updated_at',
            'resolved_at', 'closed_at',
            'sla', 'first_response_at', 'last_agent_response_at',
            'last_customer_response_at', 'first_response_deadline',
            'next_response_deadline', 'resolution_deadline',
            'escalation_at',
        ]


class TicketCreateSerializer(serializers.Serializer):
    """Create a ticket on behalf of a customer (by email)."""

    customer_email = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    description = serializers.CharField()
    priority = serializers.IntegerField(default=2)

    def create(self, validated_data):
        org = self.context['organization']
        email = validated_data['customer_email']
        customer = self._resolve_customer(email, org)
        return Ticket.objects.create(
            organization=org,
            customer=customer,
            subject=validated_data['subject'],
            description=validated_data['description'],
            priority=validated_data['priority'],
        )

    def _resolve_customer(self, email, org):
        """Find existing customer or create a new one."""
        try:
            return User.objects.get(email=email, organization=org)
        except User.DoesNotExist:
            return User.objects.create_user(
                username=email,
                email=email,
                organization=org,
                role=User.Role.CUSTOMER,
                is_active=False,
            )

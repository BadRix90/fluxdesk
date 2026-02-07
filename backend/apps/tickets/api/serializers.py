from rest_framework import serializers

from apps.tickets.models import Attachment, Comment, Escalation, Ticket
from apps.users.api.serializers import UserMinimalSerializer


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
            'comment_count',
        ]


class TicketDetailSerializer(serializers.ModelSerializer):
    """Full ticket with comments."""

    customer = UserMinimalSerializer(read_only=True)
    assignee = UserMinimalSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'subject', 'description',
            'status', 'priority', 'customer', 'assignee',
            'created_at', 'updated_at', 'resolved_at', 'closed_at',
            'comments', 'attachments',
        ]
        read_only_fields = [
            'id', 'ticket_number', 'customer',
            'created_at', 'updated_at',
            'resolved_at', 'closed_at',
        ]


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'ticket_number', 'subject', 'description', 'priority']
        read_only_fields = ['id', 'ticket_number']

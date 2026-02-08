from django.contrib import admin

from .models import Attachment, Comment, Escalation, SLA, Ticket


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['created_at']


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'subject', 'organization', 'status', 'priority',
        'customer', 'assignee', 'sla', 'escalation_at', 'created_at',
    ]
    list_filter = ['status', 'priority', 'organization']
    search_fields = ['subject', 'description']
    inlines = [CommentInline, AttachmentInline]


@admin.register(SLA)
class SLAAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'organization', 'position', 'is_active',
        'priority_filter', 'first_response_minutes',
        'next_response_minutes', 'resolution_minutes',
    ]
    list_filter = ['organization', 'is_active']
    ordering = ['organization', 'position']


@admin.register(Escalation)
class EscalationAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'from_priority', 'to_priority', 'reason', 'created_at']
    readonly_fields = ['created_at']

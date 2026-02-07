from django.contrib import admin

from .models import Attachment, Comment, Escalation, Ticket


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
        'customer', 'assignee', 'created_at',
    ]
    list_filter = ['status', 'priority', 'organization']
    search_fields = ['subject', 'description']
    inlines = [CommentInline, AttachmentInline]


@admin.register(Escalation)
class EscalationAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'from_priority', 'to_priority', 'reason', 'created_at']
    readonly_fields = ['created_at']

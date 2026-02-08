from django.contrib import admin

from .models import BusinessCalendar, Invitation, Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'support_email', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'support_email']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'organization', 'role',
        'status', 'created_at', 'expires_at',
    ]
    list_filter = ['status', 'role']
    search_fields = ['email']
    readonly_fields = ['token', 'created_at']


@admin.register(BusinessCalendar)
class BusinessCalendarAdmin(admin.ModelAdmin):
    list_display = ['organization', 'timezone', 'created_at']
    list_filter = ['timezone']

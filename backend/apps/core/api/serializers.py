from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers

from apps.core.models import BusinessCalendar, Invitation, Organization
from apps.users.models import User


class BusinessCalendarSerializer(serializers.ModelSerializer):
    """Business hours and holidays for an organization."""

    class Meta:
        model = BusinessCalendar
        fields = [
            'id', 'timezone', 'business_hours', 'holidays',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_business_hours(self, value):
        valid_days = {'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'}
        if not isinstance(value, dict):
            raise serializers.ValidationError('Must be a dict.')
        for key in value:
            if key not in valid_days:
                raise serializers.ValidationError(f'Invalid day: {key}')
        return value


class OrganizationSerializer(serializers.ModelSerializer):
    smtp_password = serializers.CharField(
        write_only=True, required=False, allow_blank=True,
    )
    smtp_has_password = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'support_email',
            'website', 'logo', 'signature_html',
            'is_active', 'created_at',
            'smtp_host', 'smtp_port', 'smtp_use_tls',
            'smtp_user', 'smtp_password', 'smtp_has_password',
            'imap_host', 'imap_user',
        ]
        read_only_fields = [
            'id', 'slug', 'is_active', 'created_at',
        ]

    def get_smtp_has_password(self, obj) -> bool:
        return bool(obj.smtp_password)

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        pwd = validated_data.get('smtp_password', None)
        if pwd == '':
            validated_data.pop('smtp_password', None)
        return super().update(instance, validated_data)


def validate_no_disposable_email(email: str) -> str:
    """Reject disposable / throwaway email domains."""
    domain = email.rsplit('@', 1)[-1].lower()
    blocked = settings.FLUX_BLOCKED_EMAIL_DOMAINS
    if domain in blocked:
        raise serializers.ValidationError(
            'Wegwerf-E-Mail-Adressen sind nicht erlaubt.'
        )
    return email


class RegisterSerializer(serializers.Serializer):
    """Register a new organization + admin user."""

    org_name = serializers.CharField(max_length=200)
    support_email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Benutzername bereits vergeben.'
            )
        return value

    def validate_email(self, value):
        return validate_no_disposable_email(value)

    def validate_support_email(self, value):
        return validate_no_disposable_email(value)

    def validate_org_name(self, value):
        slug = slugify(value)
        if Organization.objects.filter(slug=slug).exists():
            raise serializers.ValidationError(
                'Organisation existiert bereits.'
            )
        return value

    def create(self, validated_data):
        org = Organization.objects.create(
            name=validated_data['org_name'],
            slug=slugify(validated_data['org_name']),
            support_email=validated_data['support_email'],
        )
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            organization=org,
            role=User.Role.ADMIN,
            is_active=False,
        )
        return {'organization': org, 'user': user}


class VerifyEmailSerializer(serializers.Serializer):
    """Verify a user's email via token."""

    token = serializers.UUIDField()

    def validate_token(self, value):
        try:
            user = User.objects.get(
                verification_token=value,
                email_verified=False,
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Ungültiger oder bereits verwendeter Token.'
            )
        self._user = user
        return value

    def save(self, **kwargs):
        self._user.email_verified = True
        self._user.is_active = True
        self._user.save(update_fields=['email_verified', 'is_active'])
        return self._user


class InvitationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['email', 'role']

    def validate_email(self, value):
        return validate_no_disposable_email(value)

    def create(self, validated_data):
        validated_data['expires_at'] = (
            timezone.now() + timezone.timedelta(days=7)
        )
        return super().create(validated_data)


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = [
            'id', 'email', 'role', 'status',
            'created_at', 'expires_at', 'accepted_at',
        ]
        read_only_fields = [
            'id', 'status', 'created_at',
            'expires_at', 'accepted_at',
        ]


class AcceptInvitationSerializer(serializers.Serializer):
    """Accept an invitation and create a user account."""

    token = serializers.UUIDField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    def validate_token(self, value):
        try:
            invitation = Invitation.objects.get(
                token=value,
                status=Invitation.Status.PENDING,
            )
        except Invitation.DoesNotExist:
            raise serializers.ValidationError(
                'Einladung nicht gefunden oder bereits verwendet.'
            )
        if invitation.is_expired:
            raise serializers.ValidationError(
                'Einladung ist abgelaufen.'
            )
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Benutzername bereits vergeben.'
            )
        return value

    def create(self, validated_data):
        invitation = Invitation.objects.get(
            token=validated_data['token'],
        )
        User.objects.create_user(
            username=validated_data['username'],
            email=invitation.email,
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            organization=invitation.organization,
            role=invitation.role,
            is_active=True,
            email_verified=True,
        )
        invitation.accept()
        return invitation

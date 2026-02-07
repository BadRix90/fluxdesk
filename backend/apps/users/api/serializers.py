from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id']


class UserMinimalSerializer(serializers.ModelSerializer):
    """Compact user representation for nested use."""

    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'role']

    def get_display_name(self, obj: User) -> str:
        return obj.get_full_name() or obj.username

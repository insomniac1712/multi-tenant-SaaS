from rest_framework import serializers
from .models import Organization, Membership

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "created_by", "created_at", "updated_at"]
        read_only_fields = ["id", "slug", "created_by", "created_at", "updated_at"]

class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    
    class Meta:
        model = Membership
        fields = [
            "id",
            "organization",
            "user",
            "user_email",
            "username",
            "role",
            "is_active",
            "joined_at",
        ]
        read_only_fields = ["id", "organization", "user", "user_email", "username", "joined_at"]


class MembershipRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ["role"]

    def validate_role(self, value):
        if value == Membership.Role.OWNER:
            raise serializers.ValidationError("Use ownership transfer flow to set owner role.")
        return value
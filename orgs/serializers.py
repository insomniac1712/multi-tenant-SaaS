from rest_framework import serializers
from .models import Organization, Membership

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "created_by", "created_at", "updated_at"]
        read_only_fields = ["id", "slug", "created_by", "created_at", "updated_at"]

class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    
    class Meta:
        model = Membership
        fields = ["id", "organization", "user", "user_email", "role", "is_active", "joined_at"]
        read_only_fields = ["id", "joined_at", "user_email"]
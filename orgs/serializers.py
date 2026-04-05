from rest_framework import serializers
from .models import Organization, Membership, Invitation
from datetime import timedelta
import secrets
from django.utils import timezone

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
    
class InvitationSerializer(serializers.ModelSerializer):
    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True)
    
    class Meta:
        model = Invitation
        fields = ["id", "organization","invited_by", "email", "role", "token", "expires_at", "status", "created_at", "updated_at", "invited_by_email"]
        read_only_fields = ["id","organization","invited_by","invited_by_email","token","status","expires_at","created_at","updated_at"]
        

class InvitationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ["email","role"]
        
    def validate_email(self, value):
        normalized_email = value.lower().strip()
        organization = self.context['organization']
        
        if Membership.objects.filter(
            organization = organization,
            user__email = normalized_email,
            is_active = True,
        ).exists():
            raise serializers.ValidationError("This user is already an active member.")
        
        if Invitation.objects.filter(
            organization = organization,
            email = normalized_email,
            status = Invitation.Status.PENDING,
        ).exists():
            raise serializers.ValidationError("User already has a pending request.")
        
        return normalized_email
    
    def create(self, validated_data):
        return Invitation.objects.create(
            organization=self.context["organization"],  # lowercase field name
            invited_by=self.context["request"].user,
            email=validated_data["email"],
            role=validated_data.get("role", Invitation.Role.MEMBER),
            token=secrets.token_hex(32),
            expires_at=timezone.now() + timedelta(days=7),
        )

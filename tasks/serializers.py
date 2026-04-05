from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)
    class Meta:
        model = Task
        fields = ["id","project","title","description","status","created_by","created_by_email","assigned_to","assigned_to_email","is_deleted","created_at","updated_at",]
        read_only_fields = ["id","project","created_by","created_by_email","is_deleted","created_at","updated_at",]
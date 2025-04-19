from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from workspace.models import Workspace, Tag, Task
from django.contrib.auth.models import User

class WorkspaceSerializer(serializers.ModelSerializer):
    admin = serializers.StringRelatedField(read_only=True)
    members = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Workspace
        fields = ['id', 'title', 'description', 'admin', 'members']


class TagSerializer(serializers.ModelSerializer):
    workspace = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'workspace']


class TaskSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of tag IDs to assign to the task."
    )
    assigned_to = serializers.StringRelatedField(read_only=True)
    workspace = serializers.StringRelatedField(read_only=True)
    tags_detail = TagSerializer(many=True, read_only=True, source='tags')

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'created_at', 'final_at',
            'assigned_to', 'workspace', 'tags', 'tags_detail'
        ]

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        task = super().create(validated_data)

        # Validate and assign tags
        tags = Tag.objects.filter(id__in=tags_data, workspace=task.workspace)
        if len(tags) != len(tags_data):
            raise ValidationError("One or more tags do not exist or do not belong to the workspace.")
        task.tags.set(tags)

        return task


class AddUserToWorkspaceSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="Username of the user to add to the workspace.")

    def validate_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this username does not exist.")
        return user
from rest_framework import serializers
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
    assigned_to = serializers.StringRelatedField(read_only=True)
    workspace = serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'created_at', 'final_at',
            'assigned_to', 'workspace', 'tags'
        ]

class AddUserToWorkspaceSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="Username of the user to add to the workspace.")

    def validate_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this username does not exist.")
        return user
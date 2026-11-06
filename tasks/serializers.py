from rest_framework import serializers
from .models import Project, Task, Tag, TaskEvent


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ProjectSerializer(serializers.ModelSerializer):
    tasks_count = serializers.IntegerField(source='tasks.count', read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'tasks_count']


class TaskEventSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = TaskEvent
        fields = ['id', 'event_type', 'old_status', 'new_status', 'user_name', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    tags = TagSerializer(many=True, read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    owner_name = serializers.SerializerMethodField()
    events = TaskEventSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'project', 'project_name', 'priority_display',
            'tags', 'owner', 'owner_name', 'events', 'created_at',
        ]

    def get_owner_name(self, obj):
        return obj.owner.username if obj.owner else None

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Название задачи должно быть не короче 3 символов.')
        return value


class ChangeStatusSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(
        choices=['todo', 'in_progress', 'done'],
        required=True,
    )
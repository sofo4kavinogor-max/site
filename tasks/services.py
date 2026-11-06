from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Task, TaskEvent, Project


ALLOWED_TRANSITIONS = {
    'todo': ['in_progress'],
    'in_progress': ['done'],
    'done': ['todo'],
}


def change_status(task, new_status, user):
    old_status = task.status

    if new_status not in ALLOWED_TRANSITIONS.get(old_status, []):
        raise ValidationError(
            f'Недопустимый переход: {old_status} → {new_status}'
        )

    if task.owner_id and task.owner_id != user.id and not user.is_staff:
        raise PermissionError('Вы не можете менять чужую задачу')

    with transaction.atomic():
        task.status = new_status
        task.save()

        if new_status == 'done':
            project = Project.objects.select_for_update().get(id=task.project_id)
            project.completed_count += 1
            project.save()

        TaskEvent.objects.create(
            task=task,
            event_type='status_changed',
            old_status=old_status,
            new_status=new_status,
            user=user,
        )
    return task
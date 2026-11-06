import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from .models import Task, Project, Tag


def task_list(request):
    tasks = Task.objects.select_related('project').all()
    projects = Project.objects.all()
    return render(request, 'task_list.html', {
        'tasks': tasks,
        'projects': projects,
    })


def board(request):
    tasks = Task.objects.select_related('project').all()
    return render(request, 'board.html', {
        'columns': [
            ('todo', 'К выполнению', tasks.filter(status='todo')),
            ('in_progress', 'В работе', tasks.filter(status='in_progress')),
            ('done', 'Выполнено', tasks.filter(status='done')),
        ],
        'projects': Project.objects.all(),
    })


def projects(request):
    projects_qs = Project.objects.annotate(
        total=Count('tasks'),
        done=Count('tasks', filter=Q(tasks__status='done')),
    )
    return render(request, 'projects.html', {'projects': projects_qs})


def stats(request):
    total = Task.objects.count()
    done = Task.objects.filter(status='done').count()
    in_progress = Task.objects.filter(status='in_progress').count()
    todo = Task.objects.filter(status='todo').count()

    by_project = Project.objects.annotate(cnt=Count('tasks')).order_by('-cnt')
    by_priority = (
        Task.objects.values('priority')
        .annotate(cnt=Count('id'))
        .order_by('-cnt')
    )
    for item in by_priority:
        item['priority_display'] = dict(Task.PRIORITY_CHOICES).get(item['priority'], item['priority'])

    return render(request, 'stats.html', {
        'total': total,
        'done': done,
        'in_progress': in_progress,
        'todo': todo,
        'by_project': by_project,
        'by_priority': by_priority,
    })



@require_POST
def create_task(request):
    data = json.loads(request.body)
    task = Task.objects.create(
        project_id=data['project'],
        title=data['title'],
        status='todo',
    )
    return JsonResponse({
        'id': task.id,
        'title': task.title,
        'status': task.status,
        'project': task.project.name,
        'priority': task.get_priority_display(),
    })


@require_POST
def update_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    data = json.loads(request.body)
    task.status = data['status']
    task.save()
    return JsonResponse({'ok': True, 'status': task.status})


@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return JsonResponse({'ok': True})

def control_center(request):
    return render(request, 'control_center.html')
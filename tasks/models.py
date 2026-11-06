from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    completed_count = models.IntegerField(default=0, verbose_name='Выполнено задач')

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'К выполнению'),
        ('in_progress', 'В работе'),
        ('done', 'Выполнено'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Проект',
    )
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
        verbose_name='Статус',
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Приоритет',
    )
    due_date = models.DateField(null=True, blank=True, verbose_name='Срок')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Теги')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')

    owner = models.ForeignKey(
    'auth.User', on_delete=models.CASCADE,
    null=True, blank=True, related_name='tasks',
    verbose_name='Владелец',
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return self.title

class TaskEvent(models.Model):
    EVENT_CHOICES = [
        ('created', 'Создана'),
        ('status_changed', 'Статус изменён'),
        ('deleted', 'Удалена'),
    ]
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES)
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Событие задачи'
        verbose_name_plural = 'История событий'

    def __str__(self):
        return f'{self.task.title} — {self.get_event_type_display()}'
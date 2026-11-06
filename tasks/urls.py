from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('board/', views.board, name='board'),
    path('projects/', views.projects, name='projects'),
    path('stats/', views.stats, name='stats'),
    path('api/task/create/', views.create_task, name='create_task'),
    path('api/task/<int:task_id>/status/', views.update_status, name='update_status'),
    path('api/task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('control/', views.control_center, name='control_center'),
]
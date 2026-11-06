from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tasks.api_views import ProjectViewSet, TaskViewSet

admin.site.site_header = 'Управление задачами'
admin.site.site_title = 'Task Manager'
admin.site.index_title = 'Панель управления'

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='api-projects')
router.register(r'tasks', TaskViewSet, basename='api-tasks')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), 
    path('', include('tasks.urls')), 
]
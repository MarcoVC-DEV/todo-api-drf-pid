from django.urls import path
from workspace.api.views import (
    WorkspaceListCreateView,
    WorkspaceDetailView,
    TaskListCreateView,
    TaskDetailView,
    TagListCreateView, AddUserToWorkspaceView, AddUserToTaskView,
)

urlpatterns = [
    # Workspace URLs
    path('', WorkspaceListCreateView.as_view(), name='workspace-list-create'),
    path('add-user/<int:workspace_id>/', AddUserToWorkspaceView.as_view(), name='add-user-to-workspace'),

path('tasks/<int:task_id>/add-user/', AddUserToTaskView.as_view(), name='add-user-to-task'),

    path('<int:pk>/', WorkspaceDetailView.as_view(), name='workspace-detail'),

    # Task URLs
    path('tasks/<int:workspace_id>/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),

    # Tag URLs
    path('tags/<int:workspace_id>/', TagListCreateView.as_view(), name='tag-list-create'),
]
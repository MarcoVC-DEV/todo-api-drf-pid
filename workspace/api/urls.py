from django.urls import path
from workspace.api.views import (
    WorkspaceListCreateView,
    WorkspaceDetailView,
    TaskListCreateView,
    TaskDetailView,
    TagListCreateView,
    AddUserToWorkspaceView,
    AddUserToTaskView,
    UserTagListCreateView,
    UserTaskListCreateView,
)

urlpatterns = [
    # User-specific URLs
    path('user/tags/', UserTagListCreateView.as_view(), name='user-tag-list-create'),
    path('user/tasks/', UserTaskListCreateView.as_view(), name='user-task-list-create'),

    # Workspace URLs
    path('workspaces/', WorkspaceListCreateView.as_view(), name='workspace-list-create'),
    path('workspaces/<int:pk>/', WorkspaceDetailView.as_view(), name='workspace-detail'),
    path('workspaces/<int:workspace_id>/add-user/', AddUserToWorkspaceView.as_view(), name='add-user-to-workspace'),

    # Task URLs (Workspace-specific)
    path('workspaces/<int:workspace_id>/tasks/', TaskListCreateView.as_view(), name='workspace-task-list-create'),
    path('workspace/tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('workspace/tasks/<int:task_id>/add-user/', AddUserToTaskView.as_view(), name='add-user-to-task'),

    # Tag URLs (Workspace-specific)
    path('workspaces/<int:workspace_id>/tags/', TagListCreateView.as_view(), name='workspace-tag-list-create'),
]
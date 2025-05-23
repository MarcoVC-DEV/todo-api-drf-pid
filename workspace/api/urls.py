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
    UserTaskListCreateView, CompleteTaskView, CompleteUserTaskView,
    UserTagDeleteView, UserTaskDeleteView, UserTaskDetailView, RemoveUserFromWorkspaceView, RemoveTagFromWorkspaceView,
    NonWorkspaceUsersView
)

urlpatterns = [
    # User-specific URLs
    path('user/tags/', UserTagListCreateView.as_view(), name='user-tag-list-create'),
    path('user/tags/<int:tag_id>/delete/', UserTagDeleteView.as_view(), name='delete-user-tag'),
    path('user/tasks/', UserTaskListCreateView.as_view(), name='user-task-list-create'),
    path('user/tasks/<int:task_id>/complete/', CompleteUserTaskView.as_view(), name='complete-user-task'),
    path('user/tasks/<int:task_id>/delete/', UserTaskDeleteView.as_view(), name='delete-user-task'),
    path('user/tasks/<int:task_id>/', UserTaskDetailView.as_view(), name='user-task-detail'),



    # Workspace URLs
    path('workspaces/', WorkspaceListCreateView.as_view(), name='workspace-list-create'),
    path('workspaces/<int:pk>/', WorkspaceDetailView.as_view(), name='workspace-detail'),
    path('workspaces/<int:workspace_id>/add-user/', AddUserToWorkspaceView.as_view(), name='add-user-to-workspace'),
    path('workspaces/<int:workspace_id>/remove-user/', RemoveUserFromWorkspaceView.as_view(), name='remove-user-from-workspace'),

    # Task URLs (Workspace-specific)
    path('workspaces/<int:workspace_id>/tasks/', TaskListCreateView.as_view(), name='workspace-task-list-create'),
    path('workspace/tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('workspace/tasks/<int:task_id>/add-user/', AddUserToTaskView.as_view(), name='add-user-to-task'),
    path('workspaces/<int:workspace_id>/non-members/', NonWorkspaceUsersView.as_view(), name='non-workspace-users'),
    path('workspace/tasks/<int:task_id>/complete/', CompleteTaskView.as_view(), name='complete-task'),

    # Tag URLs (Workspace-specific)
    path('workspaces/<int:workspace_id>/tags/', TagListCreateView.as_view(), name='workspace-tag-list-create'),
    path('workspaces/<int:workspace_id>/tags/<int:tag_id>/delete/', RemoveTagFromWorkspaceView.as_view(), name='remove-tag-from-workspace'),
]
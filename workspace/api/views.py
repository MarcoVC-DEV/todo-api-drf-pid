from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from workspace.models import Workspace
from workspace.api.serializers import WorkspaceSerializer, AddUserToWorkspaceSerializer
from workspace.models import Task
from workspace.api.serializers import TaskSerializer
from workspace.models import Tag
from workspace.api.serializers import TagSerializer
from todo_api.pagination import DefaultPaginationLOS
from rest_framework import filters


class AddUserToWorkspaceView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Add a user to a workspace. Only the admin of the workspace can perform this action.",
        request_body=AddUserToWorkspaceSerializer,
        responses={
            200: openapi.Response(
                description="User added successfully.",
                examples={
                    "application/json": {
                        "message": "User added successfully."
                    }
                }
            ),
            400: "Bad Request",
            403: "You do not have permission to add users to this workspace.",
            404: "Workspace not found."
        }
    )
    def post(self, request, workspace_id):
        # Verificar si el espacio de trabajo existe y si el usuario es el administrador
        try:
            workspace = Workspace.objects.get(id=workspace_id)
            if workspace.admin != request.user:
                return Response({"error": "You do not have permission to add users to this workspace."},
                                status=status.HTTP_403_FORBIDDEN)
        except Workspace.DoesNotExist:
            return Response({"error": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validar el usuario a agregar
        serializer = AddUserToWorkspaceSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['username']
            if user in workspace.members.all():
                return Response({"error": "User is already a member of this workspace."},
                                status=status.HTTP_400_BAD_REQUEST)
            workspace.members.add(user)
            return Response({"message": "User added successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WorkspaceListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPaginationLOS
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['admin__username']
    search_fields = ['members__username', 'title']
    ordering_fields = ['title']

    @swagger_auto_schema(
        operation_description="Retrieve a list of workspaces where the user is a member or admin.",
        manual_parameters=[
            openapi.Parameter(
                'admin__username', openapi.IN_QUERY, description="Filter workspaces by admin username.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'search', openapi.IN_QUERY, description="Search workspaces by title or member username.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'ordering', openapi.IN_QUERY, description="Order workspaces by title.",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                description="Paginated list of workspaces.",
                examples={
                    "application/json": {
                        "count": 2,
                        "next": None,
                        "previous": None,
                        "results": [
                            {"id": 1, "title": "Workspace 1", "description": "Description 1", "admin": "admin_user",
                             "members": ["member1", "member2"]},
                            {"id": 2, "title": "Workspace 2", "description": "Description 2", "admin": "another_admin",
                             "members": ["member3"]}
                        ]
                    }
                }
            )
        }
    )

    def get(self, request):
        workspaces = Workspace.objects.filter(members=request.user)
        serializer = WorkspaceSerializer(workspaces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new workspace. The user will be set as the admin.",
        request_body=WorkspaceSerializer,
        responses={
            201: openapi.Response(
                description="Workspace created successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Workspace 1",
                        "description": "Description 1",
                        "admin": "admin_user",
                        "members": []
                    }
                }
            ),
            400: "Bad Request"
        }
    )

    def post(self, request):
        serializer = WorkspaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(admin=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkspaceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific workspace by ID.",
        responses={
            200: openapi.Response(
                description="Workspace details retrieved successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Workspace 1",
                        "description": "Description 1",
                        "admin": "admin_user",
                        "members" : []
                    }
                }
            ),
            404: "Workspace not found or access denied."
        }
    )

    def get_object(self, pk, user):
        try:
            workspace = Workspace.objects.get(pk=pk)
            if user not in workspace.members.all() and workspace.admin != user:
                return None
            return workspace
        except Workspace.DoesNotExist:
            return None

    def get(self, request, pk):
        workspace = self.get_object(pk, request.user)
        if not workspace:
            return Response({"error": "Workspace not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
        serializer = WorkspaceSerializer(workspace)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete a workspace by id. Only the admin can delete it.",
        responses={
            204: "Workspace deleted successfully.",
            403: "You do not have permission to delete this workspace.",
            404: "Workspace not found or access denied."
        }
    )

    def delete(self, request, pk):
        workspace = self.get_object(pk, request.user)
        if not workspace:
            return Response({"error": "Workspace not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
        if not workspace.can_delete(request.user):
            return Response({"error": "You do not have permission to delete this workspace."}, status=status.HTTP_403_FORBIDDEN)
        workspace.delete()
        return Response({"message": "Workspace deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class TaskListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPaginationLOS
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'assigned_to', 'tags__name']
    search_fields = ['title', 'created_at', 'final_at']
    ordering_fields = ['title', 'created_at']

    @swagger_auto_schema(
        operation_description="Retrieve a list of tasks in a workspace with optional filters.",
        manual_parameters=[
            openapi.Parameter(
                'status', openapi.IN_QUERY, description="Filter tasks by status (e.g., 'pending', 'completed').",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'assigned_to', openapi.IN_QUERY, description="Filter tasks by the user assigned to them.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'tags__name', openapi.IN_QUERY, description="Filter tasks by a tag name",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'search', openapi.IN_QUERY, description="Search tasks by title or date.",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'ordering', openapi.IN_QUERY, description="Order tasks by title or creation date.",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                description="Paginated list of tasks.",
                examples={
                    "application/json": {
                        "count": 2,
                        "next": None,
                        "previous": None,
                        "results": [
                            {"id": 1, "title": "Task 1", "status": "pending",
                             "workspace": {"id": 1, "title": "Workspace 1"}},
                            {"id": 2, "title": "Task 2", "status": "completed",
                             "workspace": {"id": 1, "title": "Workspace 1"}}
                        ]
                    }
                }
            )
        }
    )

    def get(self, request, workspace_id):
        tasks = Task.objects.filter(workspace__id=workspace_id, workspace__members=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new task in the specified workspace.",
        request_body=TaskSerializer,
        responses={
            201: openapi.Response(
                description="Task created successfully.",
                examples={
                    "application/json": {"id": 1, "title": "Task 1", "status": "pending",
                             "workspace": {"id": 1, "title": "Workspace 1"}},
                }
            ),
            400: "Bad Request",
            403: "Forbidden",
            404: "Workspace not found"
        }
    )

    def post(self, request, workspace_id):
        try:
            workspace = Workspace.objects.get(id=workspace_id)
            if request.user not in workspace.members.all():
                return Response({"error": "You do not have permission to create tasks in this workspace."},
                                status=status.HTTP_403_FORBIDDEN)
        except Workspace.DoesNotExist:
            return Response({"error": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(workspace=workspace)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]


    def get_object(self, pk, user):
        try:
            task = Task.objects.get(pk=pk)
            if user not in task.workspace.members.all() and task.workspace.admin != user:
                return None
            return task
        except Task.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific task by ID.",
        responses={
            200: openapi.Response(
                description="Task details retrieved successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Task 1",
                        "status": "pending",
                        "created_at": "2023-01-01T12:00:00Z",
                        "final_at": "2023-01-02T12:00:00Z",
                        "assigned_to": "user1",
                        "workspace": {"id": 1, "title": "Workspace 1"},
                        "tags": [{"id": 1, "name": "Tag 1", "color": "#FF5733"}]
                    }
                }
            ),
            404: "Task not found or access denied."
        }
    )

    def get(self, request, pk):
        task = self.get_object(pk, request.user)
        if not task:
            return Response({"error": "Task not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a task. Only members of the workspace can edit it.",
        request_body=TaskSerializer,
        responses={
            200: openapi.Response(
                description="Task updated successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Updated Task",
                        "status": "in_progress",
                        "created_at": "2023-01-01T12:00:00Z",
                        "final_at": "2023-01-03T12:00:00Z",
                        "assigned_to": "user1",
                        "workspace": {"id": 1, "title": "Workspace 1"},
                        "tags": [{"id": 1, "name": "Tag 1", "color": "#FF5733"}]
                    }
                }
            ),
            400: "Bad Request",
            403: "You do not have permission to edit this task.",
            404: "Task not found or access denied."
        }
    )

    def put(self, request, pk):
        task = self.get_object(pk, request.user)
        if not task:
            return Response({"error": "Task not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
        if not task.can_edit(request.user):
            return Response({"error": "You do not have permission to edit this task."}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a task. Only the admin of the workspace can delete it.",
        responses={
            204: "Task deleted successfully.",
            403: "You do not have permission to delete this task.",
            404: "Task not found or access denied."
        }
    )

    def delete(self, request, pk):
        task = self.get_object(pk, request.user)
        if not task:
            return Response({"error": "Task not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
        if not task.can_delete(request.user):
            return Response({"error": "You do not have permission to delete this task."}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response({"message": "Task deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class TagListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPaginationLOS

    @swagger_auto_schema(
        operation_description="Retrieve a list of tags in a workspace.",
        responses={
            200: openapi.Response(
                description="Paginated list of tags.",
                examples={
                    "application/json": {
                        "count": 2,
                        "next": None,
                        "previous": None,
                        "results": [
                            {"id": 1, "name": "Tag 1", "color": "#FF5733", "workspace": "Workspace 1"},
                            {"id": 2, "name": "Tag 2", "color": "#33FF57", "workspace": "Workspace 1"}
                        ]
                    }
                }
            )
        }
    )

    def get(self, request, workspace_id):
        tags = Tag.objects.filter(workspace__id=workspace_id, workspace__members=request.user)
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new tag in the specified workspace.",
        request_body=TagSerializer,
        responses={
            201: openapi.Response(
                description="Tag created successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "name": "New Tag",
                        "color": "#FF5733",
                        "workspace": "Workspace 1"
                    }
                }
            ),
            400: "Bad Request",
            403: "Forbidden",
            404: "Workspace not found"
        }
    )

    def post(self, request, workspace_id):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(workspace_id=workspace_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
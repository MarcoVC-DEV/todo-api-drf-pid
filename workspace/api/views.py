from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from workspace.models import Workspace, UserTask, UserTag
from workspace.api.serializers import WorkspaceSerializer, AddUserToWorkspaceSerializer, UserTagSerializer, \
    UserTaskSerializer
from workspace.models import Task
from workspace.api.serializers import TaskSerializer
from workspace.models import Tag
from workspace.api.serializers import TagSerializer
from todo_api.pagination import DefaultPaginationLOS
from rest_framework import filters



class UserTagListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of tags associated with the user.",
        responses={
            200: openapi.Response(
                description="List of user tags.",
                examples={
                    "application/json": [
                        {"id": 1, "name": "Personal", "color": "#FF5733"},
                        {"id": 2, "name": "Work", "color": "#33FF57"}
                    ]
                }
            )
        }
    )
    def get(self, request):
        tags = UserTag.objects.filter(user=request.user)
        serializer = UserTagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new tag associated with the user.",
        request_body=UserTagSerializer,
        responses={
            201: openapi.Response(
                description="User tag created successfully.",
                examples={
                    "application/json": {"id": 1, "name": "Personal", "color": "#FF5733"}
                }
            ),
            400: "Bad Request"
        }
    )
    def post(self, request):
        if UserTag.objects.filter(name=request.data.get('name'), user=request.user).exists():
            return Response({"error": "A tag with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserTagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserTaskListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of tasks associated with the user.",
        responses={
            200: openapi.Response(
                description="List of user tasks.",
                examples={
                    "application/json": [
                        {"id": 1, "title": "Buy groceries", "status": "pending"},
                        {"id": 2, "title": "Read a book", "status": "completed"}
                    ]
                }
            )
        }
    )
    def get(self, request):
        tasks = UserTask.objects.filter(user=request.user)
        serializer = UserTaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new task associated with the user.",
        request_body=UserTaskSerializer,
        responses={
            201: openapi.Response(
                description="User task created successfully.",
                examples={
                    "application/json": {"id": 1, "title": "Buy groceries", "status": "pending"}
                }
            ),
            400: "Bad Request"
        }
    )
    def post(self, request):
        serializer = UserTaskSerializer(data=request.data)
        if UserTask.objects.filter(title=request.data.get('title'), user=request.user).exists():
            return Response({"error": "A task with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AddUserToTaskView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Add a user to a task. Only the admin of the workspace can perform this action.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Username of the user to add to the task.",
                )
            },
            required=['username']
        ),
        responses={
            200: openapi.Response(
                description="User added to the task successfully.",
                examples={
                    "application/json": {
                        "message": "User added to the task successfully."
                    }
                }
            ),
            400: "Bad Request",
            403: "You do not have permission to add users to this task.",
            404: "Task or user not found."
        }
    )
    def post(self, request, task_id):
        try:
            # Get the task
            task = Task.objects.get(id=task_id)
            workspace = task.workspace

            # Check if the user is the admin of the workspace
            if workspace.admin != request.user:
                return Response({"error": "You do not have permission to add users to this task."},
                                status=status.HTTP_403_FORBIDDEN)

            # Get the username from the request body
            username = request.data.get('username')
            if not username:
                return Response({"error": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Get the user to add
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            # Check if the user is a member of the workspace
            if user not in workspace.members.all():
                return Response({"error": "User is not a member of this workspace."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Assign the user to the task
            task.assigned_to = user
            task.save()

            return Response({"message": "User added to the task successfully."}, status=status.HTTP_200_OK)

        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

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
        workspaces = Workspace.objects.filter(Q(members=request.user) | Q(admin=request.user)).distinct()

        for backend in self.filter_backends:
            workspaces = backend().filter_queryset(request, workspaces, self)

        paginator = self.pagination_class()
        paginated_workspaces = paginator.paginate_queryset(workspaces, request)

        serializer = WorkspaceSerializer(paginated_workspaces, many=True)
        return paginator.get_paginated_response(serializer.data)

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
        if Workspace.objects.filter(title=request.data.get('title')).exists():
            return Response({"error": "A workspace with this title already exists."},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = WorkspaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(admin=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkspaceDetailView(APIView):
    permission_classes = [IsAuthenticated]



    def get_object(self, pk, user):
        try:
            workspace = Workspace.objects.get(pk=pk)
            if user not in workspace.members.all() and workspace.admin != user:
                return None
            return workspace
        except Workspace.DoesNotExist:
            return None

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
                        "members": []
                    }
                }
            ),
            404: "Workspace not found or access denied."
        }
    )

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
        Task.delete_old_completed_tasks()
        try:
            workspace = Workspace.objects.get(id=workspace_id)
            if request.user != workspace.admin and request.user not in workspace.members.all():
                return Response({"error": "You do not have permission to view tasks in this workspace."},
                                status=status.HTTP_403_FORBIDDEN)
        except Workspace.DoesNotExist:
            return Response({"error": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND)

        tasks = Task.objects.filter(workspace=workspace)

        for backend in self.filter_backends:
            tasks = backend().filter_queryset(request, tasks, self)

        paginator = self.pagination_class()
        paginated_tasks = paginator.paginate_queryset(tasks, request)

        serializer = TaskSerializer(paginated_tasks, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new task in the specified workspace. Optionally, assign tags to the task.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description="Title of the task."),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description="Status of the task (e.g., 'pending')."),
                'final_at': openapi.Schema(type=openapi.FORMAT_DATETIME, description="Deadline for the task."),
                'tags': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),  # Fixed: Specify the type of array items
                    description="List of tag IDs to assign to the task."
                )
            },
            required=['title']
        ),
        responses={
            201: openapi.Response(
                description="Task created successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "Task 1",
                        "status": "pending",
                        "workspace": {"id": 1, "title": "Workspace 1"},
                        "tags": [{"id": 1, "name": "Tag 1", "color": "#FF5733"}]
                    }
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
            if request.user not in workspace.members.all() and request.user != workspace.admin:
                return Response({"error": "You do not have permission to create tasks in this workspace."},
                                status=status.HTTP_403_FORBIDDEN)
        except Workspace.DoesNotExist:
            return Response({"error": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND)

        if Task.objects.filter(title=request.data.get('title'), workspace=workspace).exists():
            return Response({"error": "A task with this title already exists in this workspace."},
                            status=status.HTTP_400_BAD_REQUEST)

        tags_data = request.data.get('tags', [])
        tags = Tag.objects.filter(id__in=tags_data, workspace=workspace)
        if len(tags) != len(tags_data):
            return Response({"error": "One or more tags do not exist or do not belong to the workspace."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save(workspace=workspace)
            task.tags.set(tags)  # Assign the tags to the task
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
        try:
            workspace = Workspace.objects.get(id=workspace_id)
            if request.user not in workspace.members.all() and request.user != workspace.admin:
                return Response({"error": "You do not have permission to read tags in this workspace."},
                                status=status.HTTP_403_FORBIDDEN)
        except Workspace.DoesNotExist:
            return Response({"error": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND)

        tags = Tag.objects.filter(Q(workspace__members=request.user) | Q(workspace__admin=request.user),
                                  workspace__id=workspace_id).distinct()

        paginator = self.pagination_class()
        paginated_tags = paginator.paginate_queryset(tags, request)

        serializer = TagSerializer(paginated_tags, many=True)
        return paginator.get_paginated_response(serializer.data)

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
        try:
            workspace = Workspace.objects.get(id=workspace_id)
            if request.user not in workspace.members.all() and request.user != workspace.admin:
                return Response({"error": "You do not have permission to create tags in this workspace."},
                                status=status.HTTP_403_FORBIDDEN)
        except Workspace.DoesNotExist:
            return Response({"error": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND)

        if Tag.objects.filter(name=request.data.get('name'), workspace=workspace).exists():
            return Response({"error": "A tag with this name already exists in this workspace."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(workspace=workspace)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteTaskView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Mark a task as completed. The user must be a member or admin of the workspace.",
        manual_parameters=[
            openapi.Parameter(
                'task_id', openapi.IN_PATH, description="ID of the task to complete.",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response(
                description="Task completed successfully.",
                examples={
                    "application/json": {"message": "Task completed successfully."}
                }
            ),
            403: openapi.Response(
                description="User does not have permission to complete the task.",
                examples={
                    "application/json": {"message": "You do not have permission to complete this task."}
                }
            ),
            404: openapi.Response(
                description="Task not found.",
                examples={
                    "application/json": {"message": "Task not found."}
                }
            ),
            400: openapi.Response(
                description="This task is already completed and cannot be completed again.",
                examples={
                    "application/json": {"message": "This task is already completed and cannot be completed again."}
                }
            )
        }
    )

    def post(self, request, task_id):
        try:
            # Obtener la tarea
            task = Task.objects.get(id=task_id)
            workspace = task.workspace

            # Verificar si el usuario es el miembro asignado a la task o administrador del workspace
            if request.user != workspace.admin and request.user != task.assigned_to:
                return Response({"message": "You do not have permission to complete this task."},
                                status=status.HTTP_403_FORBIDDEN)

            if task.status == 'completed':
                return Response({"message": "This task is already completed and cannot be completed again."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Cambiar el estado de la tarea a completada
            task.status = 'completed'
            task.final_at = now()
            task.save()

            return Response({"message": "Task completed successfully."}, status=status.HTTP_200_OK)

        except Task.DoesNotExist:
            return Response({"message": "Task not found."}, status=status.HTTP_404_NOT_FOUND)


class CompleteUserTaskView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Mark a user task as completed. The task must belong to the authenticated user.",
        manual_parameters=[
            openapi.Parameter(
                'task_id', openapi.IN_PATH, description="ID of the user task to complete.",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response(
                description="User task completed successfully.",
                examples={
                    "application/json": {"message": "User task completed successfully."}
                }
            ),
            403: openapi.Response(
                description="User does not have permission to complete this task.",
                examples={
                    "application/json": {"message": "You do not have permission to complete this task."}
                }
            ),
            404: openapi.Response(
                description="User task not found.",
                examples={
                    "application/json": {"message": "User task not found."}
                }
            ),
            400: openapi.Response(
                description="This task is already completed and cannot be completed again.",
                examples={
                    "application/json": {"message": "This task is already completed and cannot be completed again."}
                }
            )
        }
    )
    def post(self, request, task_id):
        try:
            # Obtener la tarea del usuario
            task = UserTask.objects.get(id=task_id)

            # Verificar que la tarea pertenece al usuario autenticado
            if task.user != request.user:
                return Response({"message": "You do not have permission to complete this task."},
                                status=status.HTTP_403_FORBIDDEN)

            # Verificar si la tarea ya está completada
            if task.status == 'completed':
                return Response({"message": "This task is already completed and cannot be completed again."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Cambiar el estado de la tarea a completada
            task.status = 'completed'
            task.final_at = now()
            task.save()

            return Response({"message": "User task completed successfully."}, status=status.HTTP_200_OK)

        except UserTask.DoesNotExist:
            return Response({"message": "User task not found."}, status=status.HTTP_404_NOT_FOUND)
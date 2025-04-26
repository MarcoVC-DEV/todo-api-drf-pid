from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


# Create your models here.
class Workspace(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_workspaces')
    members = models.ManyToManyField(User, related_name='member_workspaces', blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.members.filter(id=self.admin.id).exists():
            self.members.add(self.admin)

    def can_delete(self, user):
        return self.admin == user


class UserTag(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7)  # Hex color code
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tags')

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7)  # Hex color code
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='tags')

    def __str__(self):
        return self.name

class UserTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    final_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tasks')
    tags = models.ManyToManyField(UserTag, related_name='user_tasks', blank=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    final_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='tasks')
    tags = models.ManyToManyField(Tag, related_name='tasks', blank=True)

    def __str__(self):
        return self.title

    def can_edit(self, user):
        return user in self.workspace.members.all()

    def can_delete(self, user):
        return self.workspace.admin == user

    @classmethod
    def delete_old_completed_tasks(cls):
        three_months_ago = now() - timedelta(days=90)
        cls.objects.filter(status='completed', final_at__lte=three_months_ago).delete()
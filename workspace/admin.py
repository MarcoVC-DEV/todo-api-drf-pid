from django.contrib import admin
from .models import Workspace, Task, Tag

# Register your models here.
admin.site.register(Workspace)
admin.site.register(Task)
admin.site.register(Tag)
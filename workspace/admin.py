from django.contrib import admin
from .models import Workspace, Task, Tag, UserTag, UserTask

# Register your models here.
admin.site.register(Workspace)
admin.site.register(Task)
admin.site.register(Tag)
admin.site.register(UserTag)
admin.site.register(UserTask)

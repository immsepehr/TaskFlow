
from django.contrib import admin
from .models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    search_fields = ("name", "description")
    list_filter = ("created_at",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "status",
        "priority",
        "assigned_to",
        "due_date",
    )

    list_filter = ("status", "priority", "due_date")
    search_fields = ("title", "description")
    date_hierarchy = "created_at"
    list_per_page = 20

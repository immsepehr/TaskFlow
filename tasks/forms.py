
from django import forms

from .models import Project, Task


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ["name", "description"]

        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Enter project name",
                "class": "form-input",
            }),

            "description": forms.Textarea(attrs={
                "placeholder": "Describe your project...",
                "class": "form-input",
                "rows": 4,
            }),
        }


class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "project",
            "status",
            "priority",
            "due_date",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Enter task title",
                "class": "form-input",
            }),

            "description": forms.Textarea(attrs={
                "placeholder": "Describe your task...",
                "class": "form-input",
                "rows": 4,
            }),

            "project": forms.Select(attrs={
                "class": "form-input",
            }),

            "status": forms.Select(attrs={
                "class": "form-input",
            }),

            "priority": forms.Select(attrs={
                "class": "form-input",
            }),

            "due_date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-input",
            }),
        }

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["project"].queryset = Project.objects.filter(
            owner=user
        )

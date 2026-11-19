from .forms import ProjectForm, TaskForm
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Project, Task


@login_required
def dashboard(request):
    user_projects = Project.objects.filter(owner=request.user)

    user_tasks = Task.objects.filter(
        project__owner=request.user
    )

    context = {
        "total_projects": user_projects.count(),
        "total_tasks": user_tasks.count(),
        "todo_tasks": user_tasks.filter(
            status=Task.Status.TODO
        ).count(),
        "in_progress_tasks": user_tasks.filter(
            status=Task.Status.IN_PROGRESS
        ).count(),
        "completed_tasks": user_tasks.filter(
            status=Task.Status.DONE
        ).count(),
        "recent_tasks": user_tasks.select_related(
            "project"
        ).order_by("-created_at")[:5],
    }

    return render(request, "tasks/dashboard.html", context)


@login_required
def task_list(request):
    tasks = (
        Task.objects
        .filter(project__owner=request.user)
        .select_related(
            "project",
            "created_by",
            "assigned_to",
        )
        .order_by("-created_at")
    )

    # Search by task title
    search_query = request.GET.get("q", "").strip()

    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    # Filter by task status
    status_filter = request.GET.get("status", "")

    if status_filter in Task.Status.values:
        tasks = tasks.filter(status=status_filter)

    # Pagination
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get("page", 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(paginator.num_pages)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        "tasks": page_obj,
        "page_obj": page_obj,
        "total_tasks": paginator.count,
        "search_query": search_query,
        "status_filter": status_filter,
    }

    return render(request, "tasks/task_list.html", context)


@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()

            return redirect("task_list")

    else:
        form = TaskForm(user=request.user)

    context = {
        "form": form,
    }

    return render(request, "tasks/task_form.html", context)


@login_required
def task_update(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        project__owner=request.user,
    )

    if request.method == "POST":
        form = TaskForm(
            request.POST,
            instance=task,
            user=request.user,
        )

        if form.is_valid():
            form.save()
            return redirect("task_list")

    else:
        form = TaskForm(
            instance=task,
            user=request.user,
        )

    context = {
        "form": form,
        "task": task,
        "is_edit": True,
    }

    return render(request, "tasks/task_form.html", context)

@login_required
def task_delete(request, pk):
    task = get_object_or_404(
        Task,
        pk=pk,
        project__owner=request.user,
    )

    if request.method == "POST":
        task.delete()
        return redirect("task_list")

    context = {
        "task": task,
    }

    return render(
        request,
        "tasks/task_confirm_delete.html",
        context,
    )

@login_required
def project_list(request):
    projects = (
        Project.objects
        .filter(owner=request.user)
        .annotate(
            total_tasks=Count("tasks"),
            completed_tasks=Count(
                "tasks",
                filter=Q(tasks__status=Task.Status.DONE),
            ),
        )
        .order_by("-created_at")
    )

    context = {
        "projects": projects,
        "total_projects": projects.count(),
    }

    return render(request, "tasks/projects.html", context)


@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()

            return redirect("project_list")

    else:
        form = ProjectForm()

    context = {
        "form": form,
    }

    return render(request, "tasks/project_form.html", context)


@login_required
def project_update(request, pk):
    project = get_object_or_404(
        Project,
        pk=pk,
        owner=request.user,
    )

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            return redirect("project_list")

    else:
        form = ProjectForm(instance=project)

    context = {
        "form": form,
        "project": project,
        "is_edit": True,
    }

    return render(request, "tasks/project_form.html", context)

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    if request.method == "POST":
        project.delete()
        return redirect("project_list")

    context = {"project": project}
    return render(request, "tasks/project_confirm_delete.html", context)

@login_required
def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.filter(owner=request.user).annotate(
            total_tasks=Count("tasks"),
            completed_tasks=Count(
                "tasks",
                filter=Q(tasks__status=Task.Status.DONE),
            ),
        ),
        pk=pk,
    )

    tasks = (
        Task.objects
        .filter(project=project)
        .select_related("created_by", "assigned_to")
        .order_by("-created_at")
    )

    context = {
        "project": project,
        "tasks": tasks,
        "remaining_tasks": (
            project.total_tasks - project.completed_tasks
        ),
    }

    return render(request, "tasks/project_detail.html", context)
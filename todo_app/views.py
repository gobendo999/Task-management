from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Task
from .forms import TaskForm


@login_required(login_url='login')
def task_list(request):
    """
    List tasks strictly belonging to the currently logged in user,
    with search and status filters, personal user metrics, and pagination.
    """
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', 'all').lower()

    # User isolation: only fetch tasks for request.user
    tasks = Task.objects.filter(user=request.user)

    # Search filter
    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Status filter
    if status == 'completed':
        tasks = tasks.filter(completed=True)
    elif status == 'pending':
        tasks = tasks.filter(completed=False)

    # Statistics for the logged-in user
    user_all_tasks = Task.objects.filter(user=request.user)
    total_count = user_all_tasks.count()
    completed_count = user_all_tasks.filter(completed=True).count()
    pending_count = total_count - completed_count
    completion_rate = int((completed_count / total_count * 100)) if total_count > 0 else 0

    # Pagination: 8 tasks per page
    paginator = Paginator(tasks, 8)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    context = {
        'tasks': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'search_query': query,
        'current_status': status,
        'total_count': total_count,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'completion_rate': completion_rate,
    }
    return render(request, 'todo/task_list.html', context)


@login_required(login_url='login')
def task_create(request):
    """
    Create a new task assigned automatically to the authenticated user.
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('todo:task_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm()

    return render(request, 'todo/task_form.html', {'form': form, 'is_edit': False})


@login_required(login_url='login')
def task_update(request, pk):
    """
    Edit and update a task. Protected so a user can only edit their own tasks.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('todo:task_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm(instance=task)

    return render(request, 'todo/task_form.html', {'form': form, 'task': task, 'is_edit': True})


@login_required(login_url='login')
def task_delete(request, pk):
    """
    Delete a task. Protected so a user can only delete their own tasks.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.warning(request, f'Task "{task_title}" was deleted.')
        return redirect('todo:task_list')

    return render(request, 'todo/task_confirm_delete.html', {'task': task})


@login_required(login_url='login')
@require_POST
def task_toggle(request, pk):
    """
    Toggle task completion status for request.user's task.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()

    status_label = "completed" if task.completed else "pending"
    messages.info(request, f'Task marked as {status_label}.')
    return redirect('todo:task_list')
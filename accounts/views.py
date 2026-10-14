from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile
from todo_app.models import Task


def register_view(request):
    """
    Handle user registration and direct them to login upon success.
    """
    if request.user.is_authenticated:
        return redirect('todo:task_list')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created for {user.username}! Please sign in.')
            return redirect('login')
        else:
            messages.error(request, 'Registration failed. Please check the form errors below.')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handle user login, validate open redirect target, apply remember_me, and redirect.
    """
    if request.user.is_authenticated:
        return redirect('todo:task_list')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Remember Me session management
            remember_me = request.POST.get('remember_me')
            if remember_me:
                # 2 weeks session expiry
                request.session.set_expiry(1209600)
            else:
                # Session expires on browser close
                request.session.set_expiry(0)

            messages.success(request, f'Welcome back, {user.username}!')

            # Open Redirect protection: only allow same-origin redirects
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url and url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('todo:task_list')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Handle user logout and redirect to login page.
    """
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.info(request, f'You have been logged out, {username}.')
    return redirect('login')


# -------------------------------------------------------------
# Password Reset Views with Indigo + Slate Aesthetic
# -------------------------------------------------------------

class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


@login_required(login_url='login')
def profile_view(request):
    """
    View user information, task summary metrics, and edit profile details.
    """
    # Ensure profile exists for the user
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    # User task statistics
    user_tasks = Task.objects.filter(user=request.user)
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    completion_rate = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'completion_rate': completion_rate,
    }
    return render(request, 'accounts/profile.html', context)

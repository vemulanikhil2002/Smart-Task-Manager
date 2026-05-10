import json
import pandas as pd
import numpy as np

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Task


# ─────────────────────────────────────────────
#  Helper – broadcast via WebSocket
# ─────────────────────────────────────────────

def broadcast(event_type, payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'tasks',
        {'type': 'task_event', 'event': event_type, 'payload': payload}
    )


# ─────────────────────────────────────────────
#  Auth Views
# ─────────────────────────────────────────────

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not username or not email or not password:
            error = 'All fields are required.'
        elif User.objects.filter(username=username).exists():
            error = 'Username already taken.'
        elif User.objects.filter(email=email).exists():
            error = 'Email already registered.'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters.'
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('dashboard')

    return render(request, 'register.html', {'error': error})


def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user     = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            error = 'Invalid username or password.'

    return render(request, 'login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


# ─────────────────────────────────────────────
#  Dashboard
# ─────────────────────────────────────────────

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


# ─────────────────────────────────────────────
#  REST API – Tasks
# ─────────────────────────────────────────────

@login_required
@require_http_methods(['GET'])
def api_get_tasks(request):
    tasks = Task.objects.filter(user=request.user)
    return JsonResponse({'success': True, 'tasks': [t.to_dict() for t in tasks]})


@login_required
@csrf_exempt
@require_http_methods(['POST'])
def api_add_task(request):
    try:
        data        = json.loads(request.body)
        title       = data.get('title', '').strip()
        description = data.get('description', '').strip()
        priority    = data.get('priority', 'medium')
        status      = data.get('status', 'pending')

        if not title:
            return JsonResponse({'success': False, 'error': 'Title is required.'}, status=400)

        task = Task.objects.create(
            user=request.user, title=title,
            description=description, priority=priority, status=status
        )
        broadcast('task_added', task.to_dict())
        return JsonResponse({'success': True, 'task': task.to_dict()}, status=201)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(['PUT'])
def api_update_task(request, task_id):
    try:
        task = get_object_or_404(Task, id=task_id, user=request.user)
        data = json.loads(request.body)

        task.title       = data.get('title', task.title).strip()
        task.description = data.get('description', task.description).strip()
        task.priority    = data.get('priority', task.priority)
        task.status      = data.get('status', task.status)
        task.save()

        broadcast('task_updated', task.to_dict())
        return JsonResponse({'success': True, 'task': task.to_dict()})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(['DELETE'])
def api_delete_task(request, task_id):
    try:
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.delete()
        broadcast('task_deleted', {'id': task_id})
        return JsonResponse({'success': True, 'message': 'Task deleted.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ─────────────────────────────────────────────
#  Analytics API – Pandas & NumPy
# ─────────────────────────────────────────────

@login_required
@require_http_methods(['GET'])
def api_analytics(request):
    try:
        tasks = Task.objects.filter(user=request.user).values('status', 'priority')

        if not tasks:
            return JsonResponse({
                'success': True, 'total': 0, 'completed': 0,
                'pending': 0, 'in_progress': 0, 'completion_pct': 0.0,
                'priority_counts': {'high': 0, 'medium': 0, 'low': 0},
            })

        # Use Pandas & NumPy for analytics computation
        df = pd.DataFrame(list(tasks))

        total         = int(len(df))
        completed     = int(np.sum(df['status'] == 'completed'))
        pending       = int(np.sum(df['status'] == 'pending'))
        in_progress   = int(np.sum(df['status'] == 'in_progress'))
        completion_pct = round(float(np.mean(df['status'] == 'completed') * 100), 2)

        priority_counts = df['priority'].value_counts().to_dict()
        priority_counts = {k: int(v) for k, v in priority_counts.items()}
        for p in ['high', 'medium', 'low']:
            priority_counts.setdefault(p, 0)

        return JsonResponse({
            'success': True,
            'total': total, 'completed': completed,
            'pending': pending, 'in_progress': in_progress,
            'completion_pct': completion_pct,
            'priority_counts': priority_counts,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

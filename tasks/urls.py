from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('',            views.index,         name='index'),
    path('register/',   views.register_view, name='register'),
    path('login/',      views.login_view,    name='login'),
    path('logout/',     views.logout_view,   name='logout'),
    path('dashboard/',  views.dashboard,     name='dashboard'),

    # REST API endpoints
    path('api/tasks/',              views.api_get_tasks,   name='api_get_tasks'),
    path('api/tasks/add/',          views.api_add_task,    name='api_add_task'),
    path('api/tasks/<int:task_id>/update/', views.api_update_task, name='api_update_task'),
    path('api/tasks/<int:task_id>/delete/', views.api_delete_task, name='api_delete_task'),
    path('api/analytics/',          views.api_analytics,   name='api_analytics'),
]

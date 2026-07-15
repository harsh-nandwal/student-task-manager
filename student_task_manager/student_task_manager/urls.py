"""
URL configuration for student_task_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from task_manager.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('list', TaskListView.as_view(), name='task_list'),
    path('add/', TaskCreateView.as_view(), name='add_task'),
    path('detail/<int:pk>/', TaskDetailView.as_view(), name='detailed_task'),
    path('delete/<int:pk>/', TaskDeleteView.as_view(), name='delete_task'),
    path('edit/<int:pk>/', TaskUpdateView.as_view(), name='update_task'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('deleteAccount/', UserAccountDeleteView.as_view(), name='delete_account')
]

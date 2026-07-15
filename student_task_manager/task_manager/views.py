from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Task
from django.db.models import Q, Count
from django.db.models.functions import ExtractMonth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date

# Create your views here.

class UserRegisterView(View):
    def get(self, request):
        return render(request, 'register.html')
    
    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request,  'Username already exists.')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect("login")
    


class UserLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('task_list')
        return render(request, 'login.html')
    
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("task_list")
        else:
            messages.error(request, "Invalid username or password")
        
        return redirect("login")



class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
    


class UserAccountDeleteView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        user = request.user
        logout(request)
        user.delete()
        return redirect('register')



class TaskListView(LoginRequiredMixin, View):
    def get(self, request):
        task = Task.objects.filter(user=request.user).order_by('-created_at')
        priority = request.GET.get('priority')
        search = request.GET.get('search')
        status = request.GET.get('status')
        sort = request.GET.get('sort')
        today = request.GET.get('today')

        if priority:
            task = task.filter(priority=priority)

        if search:
            task = task.filter(Q(title__icontains=search) | Q(description__icontains=search))
        
        if status == 'completed':
            task = task.filter(completed=True)
        
        elif status == 'pending':
            task = task.filter(completed=False)

        if sort == 'created_at':
            task = task.order_by('-created_at')

        elif sort == 'title':
            task = task.order_by('title')

        if today:
            task = task.filter(deadline=date.today())

        total_task = task.count()
        completed_task = task.filter(completed=True).count()
        pending_task = task.filter(completed=False).count()

        context = {
            'task' : task, 
            'total_task' : total_task, 
            'completed_task' : completed_task, 
            'pending_task' : pending_task
        }

        return render(request, 'show.html', context)



class TaskCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'add.html')
    
    def post(self, request):
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')
        priority = request.POST.get('priority')
        completed = request.POST.get('completed') == 'on'

        Task.objects.create(
            user=request.user,
            title=title, 
            description=description, 
            deadline=deadline, 
            priority=priority, 
            completed=completed
        )

        messages.success(request, "Task created successfully.")
        return redirect('task_list')
    


class TaskDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        return render(request, 'detail.html', {'task' : task})
    



class TaskDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        
        if request.user == task.user or request.user.is_superuser:
            task.delete()
        
        messages.success(request, "Task deleted successfully.")
        return redirect('task_list')
    


class TaskUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        return render(request, 'edit.html', {'task' : task})

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)

        task.title = request.POST['title']
        task.description = request.POST['description']
        task.deadline = request.POST['deadline']
        task.priority = request.POST['priority']
        task.completed = request.POST.get('completed') == 'on'
        task.save()

        messages.success(request, "Task updated successfully.")
        return redirect('task_list')
    


class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        task = Task.objects.filter(user=request.user)

        total_task = task.count()
        completed_task = task.filter(completed=True).count()
        pending_task = task.filter(completed=False).count()
        high_priority = task.filter(priority='High').count()
        medium_priority = task.filter(priority='Medium').count()
        low_priority = task.filter(priority='Low').count()
        today_task = task.filter(deadline=date.today())

        if total_task > 0:
            completion_percentage = round((completed_task / total_task) * 100, 2)
        else:
            completion_percentage = 0

        recent_task = Task.objects.filter(user=request.user).order_by('-id')[:5]

        monthly_task = (
            task
            .annotate(month=ExtractMonth('created_at'))
            .values('month')
            .annotate(total=Count('id'))
            .order_by('month')
        )

        months = []
        counts = []

        month_names = {
            1: "Jan",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "Jul",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec",
        }

        for item in monthly_task:
            months.append(month_names[item["month"]])
            counts.append(item["total"])

        context = {
            'total_task' : total_task,
            'completed_task' : completed_task,
            'pending_task' : pending_task,
            'completion_percentage': completion_percentage,
            'recent_task' : recent_task,
            'months': months,
            'counts': counts,
            'high_priority' : high_priority,
            'medium_priority' : medium_priority,
            'low_priority' : low_priority,
            'today_task' : today_task
        }

        return render(request, 'dashboard.html', context)
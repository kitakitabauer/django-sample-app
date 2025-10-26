from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from .forms import TaskForm
from .models import Task


class TaskListView(ListView):
  model = Task
  template_name = 'tasks/task_list.html'
  context_object_name = 'tasks'


class TaskCreateView(CreateView):
  model = Task
  form_class = TaskForm
  template_name = 'tasks/task_form.html'
  success_url = reverse_lazy('tasks:list')


class TaskUpdateView(UpdateView):
  model = Task
  form_class = TaskForm
  template_name = 'tasks/task_form.html'
  success_url = reverse_lazy('tasks:list')


class TaskDeleteView(DeleteView):
  model = Task
  template_name = 'tasks/task_confirm_delete.html'
  success_url = reverse_lazy('tasks:list')


def toggle_done(request, pk):
  task = get_object_or_404(Task, pk=pk)
  task.is_done = not task.is_done
  task.save()
  return redirect('tasks:list')

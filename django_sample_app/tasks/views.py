from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import TaskForm
from .models import Task


class TaskListView(ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get("status")
        if status == "open":
            queryset = queryset.filter(is_done=False)
        elif status == "done":
            queryset = queryset.filter(is_done=True)

        query = (self.request.GET.get("q") or "").strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_status = self.request.GET.get("status", "all")
        query = (self.request.GET.get("q") or "").strip()
        context.update(
            {
                "current_status": current_status,
                "query": query,
                "active_filters": {"status": current_status, "query": query},
            }
        )
        return context


class TaskCreateView(SuccessMessageMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:list")
    success_message = "タスクを作成しました。"


class TaskUpdateView(SuccessMessageMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:list")
    success_message = "タスクを更新しました。"


class TaskDeleteView(DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("tasks:list")

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "タスクを削除しました。")
        return response


def toggle_done(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.is_done = not task.is_done
    task.save()
    messages.info(
        request,
        f"「{task.title}」を{'完了' if task.is_done else '未完了'}に切り替えました。",
    )
    return redirect("tasks:list")

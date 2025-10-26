from django.test import TestCase
from django.urls import reverse
from .models import Task


class TaskTests(TestCase):
  def test_create_and_list(self):
    Task.objects.create(title="Write docs")
    res = self.client.get(reverse('tasks:list'))
    self.assertContains(res, "Write docs")

  def test_toggle_done(self):
    t = Task.objects.create(title="Do it")
    self.client.get(reverse('tasks:toggle', args=[t.pk]))
    t.refresh_from_db()
    self.assertTrue(t.is_done)

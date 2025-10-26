from django.test import TestCase
from django.urls import reverse

from .models import Task


class TaskTests(TestCase):
    def test_create_and_list(self):
        Task.objects.create(title="Write docs")
        res = self.client.get(reverse("tasks:list"))
        self.assertContains(res, "Write docs")

    def test_toggle_done(self):
        t = Task.objects.create(title="Do it")
        self.client.get(reverse("tasks:toggle", args=[t.pk]))
        t.refresh_from_db()
        self.assertTrue(t.is_done)

    def test_list_filter_status_open(self):
        Task.objects.create(title="Open task")
        Task.objects.create(title="Closed task", is_done=True)
        res = self.client.get(reverse("tasks:list"), {"status": "open"})
        self.assertContains(res, "Open task")
        self.assertNotContains(res, "Closed task")

    def test_list_filter_status_done(self):
        Task.objects.create(title="Open task")
        Task.objects.create(title="Closed task", is_done=True)
        res = self.client.get(reverse("tasks:list"), {"status": "done"})
        self.assertContains(res, "Closed task")
        self.assertNotContains(res, "Open task")

    def test_list_search_filters_by_title_and_description(self):
        Task.objects.create(title="Write documentation")
        Task.objects.create(title="Plan sprint", description="Discuss docs")
        Task.objects.create(title="Random task")
        res = self.client.get(reverse("tasks:list"), {"q": "doc"})
        self.assertContains(res, "Write documentation")
        self.assertContains(res, "Plan sprint")
        self.assertNotContains(res, "Random task")

    def test_create_view_valid_submission(self):
        res = self.client.post(
            reverse("tasks:create"),
            {"title": "Write docs", "description": "Finish README", "is_done": False},
        )
        self.assertRedirects(res, reverse("tasks:list"))
        self.assertEqual(Task.objects.count(), 1)

    def test_create_view_rejects_short_title(self):
        res = self.client.post(
            reverse("tasks:create"),
            {"title": "Hi", "description": "Too short"},
        )
        self.assertEqual(res.status_code, 200)
        form = res.context["form"]
        self.assertIn("title", form.errors)
        self.assertEqual(
            form.errors["title"], ["タイトルは3文字以上で入力してください。"]
        )
        self.assertEqual(Task.objects.count(), 0)

    def test_create_view_rejects_duplicate_title(self):
        Task.objects.create(title="Duplicate")
        res = self.client.post(
            reverse("tasks:create"),
            {"title": "duplicate", "description": ""},
        )
        self.assertEqual(res.status_code, 200)
        form = res.context["form"]
        self.assertIn("title", form.errors)
        self.assertEqual(
            form.errors["title"], ["同じタイトルのタスクが既に存在します。"]
        )
        self.assertEqual(Task.objects.count(), 1)

    def test_description_cannot_match_title(self):
        res = self.client.post(
            reverse("tasks:create"),
            {"title": "Same value", "description": "Same Value"},
        )
        self.assertEqual(res.status_code, 200)
        form = res.context["form"]
        self.assertIn("description", form.errors)
        self.assertEqual(
            form.errors["description"], ["タイトルと説明を同じ内容にはできません。"]
        )
        self.assertEqual(Task.objects.count(), 0)

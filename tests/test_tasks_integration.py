import pytest
from django.urls import reverse

from django_sample_app.tasks.models import Task

pytestmark = pytest.mark.django_db


def test_homepage_lists_latest_tasks(client):
    Task.objects.create(title="First")
    Task.objects.create(title="Second")

    response = client.get(reverse("tasks:list"))

    content = response.content.decode()
    assert "Second" in content
    assert "First" in content
    assert content.index("Second") < content.index("First")


@pytest.mark.parametrize(
    "status,expected_titles,unexpected_titles",
    [
        ("open", {"Open task"}, {"Done task"}),
        ("done", {"Done task"}, {"Open task"}),
        ("all", {"Open task", "Done task"}, set()),
    ],
)
def test_status_filtering_via_query_param(
    client, status, expected_titles, unexpected_titles
):
    Task.objects.create(title="Open task")
    Task.objects.create(title="Done task", is_done=True)

    response = client.get(reverse("tasks:list"), {"status": status})
    content = response.content.decode()

    for title in expected_titles:
        assert title in content
    for title in unexpected_titles:
        assert title not in content


def test_search_finds_title_and_description(client):
    Task.objects.create(title="Write API docs")
    Task.objects.create(title="Plan sprint", description="Discuss docs handover")
    Task.objects.create(title="Random note")

    response = client.get(reverse("tasks:list"), {"q": "docs"})
    html = response.content.decode()

    assert "Write API docs" in html
    assert "Plan sprint" in html
    assert "Random note" not in html


def test_toggle_done_switches_state(client):
    task = Task.objects.create(title="Flip me")

    response = client.get(reverse("tasks:toggle", args=[task.pk]))

    assert response.status_code == 302
    task.refresh_from_db()
    assert task.is_done is True

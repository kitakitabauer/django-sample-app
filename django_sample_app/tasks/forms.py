from typing import Any

from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    """Task creation/update form with custom validation rules."""

    class Meta:
        model = Task
        fields = ["title", "description", "is_done"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "例: Write documentation",
                    "autofocus": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "補足があれば入力してください (任意)",
                }
            ),
            "is_done": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        help_texts = {
            "title": "3文字以上。既存タスクと同じタイトルは使えません。",
            "description": "タイトルと同一内容にはできません。",
        }
        labels = {
            "title": "タイトル",
            "description": "詳細",
            "is_done": "完了済みにする",
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css_class = field.widget.attrs.get("class", "")
            if (
                not isinstance(field.widget, forms.CheckboxInput)
                and "form-control" not in css_class.split()
            ):
                field.widget.attrs["class"] = f"{css_class} form-control".strip()
            if isinstance(field.widget, forms.CheckboxInput) and not css_class:
                field.widget.attrs["class"] = "form-check-input"

        if self.is_bound:
            for name, field in self.fields.items():
                if self.errors.get(name):
                    css_class = field.widget.attrs.get("class", "")
                    if "is-invalid" not in css_class.split():
                        field.widget.attrs["class"] = f"{css_class} is-invalid".strip()

    def clean_title(self) -> str:
        title = (self.cleaned_data.get("title") or "").strip()
        if len(title) < 3:
            raise forms.ValidationError("タイトルは3文字以上で入力してください。")

        qs = Task.objects.filter(title__iexact=title)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("同じタイトルのタスクが既に存在します。")

        return title

    def clean_description(self) -> str:
        description = (self.cleaned_data.get("description") or "").strip()
        return description

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean()
        title = cleaned.get("title") or ""
        description = cleaned.get("description") or ""
        if description and title.lower() == description.lower():
            self.add_error("description", "タイトルと説明を同じ内容にはできません。")
        return cleaned

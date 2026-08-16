from django.db import models

from .constants import ALLOWED_TRANSITIONS, TenderStatus


class Tender(models.Model):
    """Тендер с конечным набором статусов."""

    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=TenderStatus.choices,
        default=TenderStatus.DRAFT,
        db_index=True,
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        db_table = "tenders"
        ordering = ["-created_at"]
        verbose_name = "Тендер"
        verbose_name_plural = "Тендеры"

    def __str__(self):
        return f"{self.title} [{self.status}]"

    def can_transition_to(self, new_status: str) -> bool:
        """Разрешён ли переход из текущего статуса в new_status."""
        return new_status in ALLOWED_TRANSITIONS.get(self.status, set())


class TenderStatusHistory(models.Model):
    """
    Аудит-лог изменений статуса: кто, когда и почему.

    Таблица append-only — записи только добавляются,
    не обновляются и не удаляются.
    """

    tender = models.ForeignKey(
        Tender,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="Тендер",
    )
    old_status = models.CharField(
        "Предыдущий статус",
        max_length=20,
        choices=TenderStatus.choices,
    )
    new_status = models.CharField(
        "Новый статус",
        max_length=20,
        choices=TenderStatus.choices,
    )
    changed_by = models.CharField("Кем изменён", max_length=255)
    reason = models.TextField("Причина изменения")
    changed_at = models.DateTimeField("Когда изменён", auto_now_add=True)

    class Meta:
        db_table = "tender_status_history"
        ordering = ["-changed_at"]
        verbose_name = "История статуса тендера"
        verbose_name_plural = "История статусов тендеров"

    def __str__(self):
        return f"{self.tender_id}: {self.old_status} -> {self.new_status}"
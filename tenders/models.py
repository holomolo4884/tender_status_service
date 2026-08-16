import uuid

from django.db import models

from .constants import ALLOWED_TRANSITIONS, TenderStatus


class TimeStampedModel(models.Model):
    """Абстрактная база с таймстампами создания и обновления."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Tender(TimeStampedModel):
    """Тендер с конечным набором статусов."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=TenderStatus.choices,
        default=TenderStatus.DRAFT,
        db_index=True,
    )
    version = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "tenders"
        ordering = ["-created_at"]
        verbose_name = "Тендер"
        verbose_name_plural = "Тендеры"

    def __str__(self) -> str:
        return f"{self.title} [{self.status}]"

    def can_transition_to(self, new_status: str) -> bool:
        """Разрешён ли переход из текущего статуса в `new_status`."""
        return new_status in ALLOWED_TRANSITIONS.get(self.status, set())


class TenderStatusHistory(models.Model):
    """
    Аудит-лог изменений статуса тендера.

    Таблица append-only: записи только создаются, не обновляются
    и не удаляются. Каждое изменение фиксирует кто, когда и почему.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
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
        indexes = [
            models.Index(fields=["tender", "-changed_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.tender_id}: {self.old_status} → {self.new_status}"
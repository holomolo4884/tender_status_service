from django.db import models

class TenderStatus(models.TextChoices):
    """Статусы тендера."""

    DRAFT = "DRAFT", "Черновик"
    ACTIVE = "ACTIVE", "Активен"
    WON = "WON", "Выигран"
    LOST = "LOST", "Проигран"


# Матрица допустимых переходов.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    TenderStatus.DRAFT: {TenderStatus.ACTIVE},
    TenderStatus.ACTIVE: {TenderStatus.WON, TenderStatus.LOST},
    # Терминальные состояния: переходов нет.
    TenderStatus.WON: set(),
    TenderStatus.LOST: set(),
}
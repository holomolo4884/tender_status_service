# tenders/services.py
from django.db import transaction

from .constants import TenderStatus
from .exceptions import InvalidStatusTransitionError, TenderNotFoundError
from .models import Tender, TenderStatusHistory


def create_tender(*, title: str, description: str = "") -> Tender:
    """Создаёт тендер с начальным статусом DRAFT."""
    return Tender.objects.create(
        title=title,
        description=description,
        status=TenderStatus.DRAFT,
    )


def get_tender(tender_id: int) -> Tender:
    """Возвращает тендер или бросает TenderNotFoundError."""
    try:
        return Tender.objects.get(pk=tender_id)
    except Tender.DoesNotExist:
        raise TenderNotFoundError(f"Тендер с id={tender_id} не найден.")


def change_tender_status(
    *,
    tender_id: int,
    new_status: str,
    changed_by: str,
    reason: str,
) -> Tender:
    """
    Меняет статус тендера и пишет историю в одной транзакции.

    Алгоритм:
    1. Загрузить тендер (с блокировкой строки от гонки).
    2. Проверить допустимость перехода по матрице.
    3. Обновить статус.
    4. Создать запись истории (кто, когда, почему).
    """
    with transaction.atomic():
        try:
            tender = Tender.objects.select_for_update().get(pk=tender_id)
        except Tender.DoesNotExist:
            raise TenderNotFoundError(f"Тендер с id={tender_id} не найден.")

        # Проверка перехода через матрицу.
        if not tender.can_transition_to(new_status):
            raise InvalidStatusTransitionError(
                current_status=tender.status,
                requested_status=new_status,
            )

        old_status = tender.status
        tender.status = new_status
        tender.save(update_fields=["status", "updated_at"])

        # Запись истории в той же транзакции.
        TenderStatusHistory.objects.create(
            tender=tender,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            reason=reason,
        )

    return tender


def get_tender_history(tender_id: int):
    """История изменений статуса тендера (новые сверху)."""
    get_tender(tender_id)  # убедимся, что тендер существует
    return (
        TenderStatusHistory.objects
        .filter(tender_id=tender_id)
        .order_by("-changed_at")
    )
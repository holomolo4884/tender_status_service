import pytest

from tenders import services
from tenders.constants import TenderStatus
from tenders.exceptions import InvalidStatusTransitionError, TenderNotFoundError
from tenders.models import TenderStatusHistory

from .factories import create_tender


@pytest.mark.django_db
class TestTenderServices:
    """Тесты сервисного слоя."""

    def test_create_tender_sets_draft_status(self):
        """Сервис создания тендера устанавливает статус DRAFT."""
        tender = services.create_tender(title="Новый тендер", description="Описание")
        assert tender.status == TenderStatus.DRAFT
        assert tender.title == "Новый тендер"

    def test_change_status_draft_to_active(self):
        """Допустимый переход DRAFT -> ACTIVE."""
        tender = create_tender()
        updated = services.change_tender_status(
            tender_id=tender.id,
            new_status=TenderStatus.ACTIVE,
            changed_by="user1",
            reason="Опубликован",
        )
        assert updated.status == TenderStatus.ACTIVE

    def test_change_status_creates_history_record(self):
        """Смена статуса создаёт запись в истории."""
        tender = create_tender()
        services.change_tender_status(
            tender_id=tender.id,
            new_status=TenderStatus.ACTIVE,
            changed_by="user1",
            reason="Опубликован",
        )
        history = TenderStatusHistory.objects.filter(tender=tender)
        assert history.count() == 1
        record = history.first()
        assert record.old_status == TenderStatus.DRAFT
        assert record.new_status == TenderStatus.ACTIVE
        assert record.changed_by == "user1"
        assert record.reason == "Опубликован"

    def test_invalid_transition_raises_error(self):
        """Недопустимый переход бросает InvalidStatusTransitionError."""
        tender = create_tender()
        with pytest.raises(InvalidStatusTransitionError) as exc_info:
            services.change_tender_status(
                tender_id=tender.id,
                new_status=TenderStatus.WON,
                changed_by="user1",
                reason="Попытка",
            )
        assert exc_info.value.current_status == TenderStatus.DRAFT
        assert exc_info.value.requested_status == TenderStatus.WON

    def test_invalid_transition_does_not_change_status(self):
        """При недопустимом переходе статус не меняется."""
        tender = create_tender()
        original_status = tender.status
        with pytest.raises(InvalidStatusTransitionError):
            services.change_tender_status(
                tender_id=tender.id,
                new_status=TenderStatus.WON,
                changed_by="user1",
                reason="Попытка",
            )
        tender.refresh_from_db()
        assert tender.status == original_status

    def test_invalid_transition_does_not_create_history(self):
        """При недопустимом переходе запись в историю не создаётся."""
        tender = create_tender()
        with pytest.raises(InvalidStatusTransitionError):
            services.change_tender_status(
                tender_id=tender.id,
                new_status=TenderStatus.WON,
                changed_by="user1",
                reason="Попытка",
            )
        assert TenderStatusHistory.objects.filter(tender=tender).count() == 0

    def test_tender_not_found_raises_error(self):
        """Несуществующий тендер бросает TenderNotFoundError."""
        with pytest.raises(TenderNotFoundError):
            services.change_tender_status(
                tender_id=99999,
                new_status=TenderStatus.ACTIVE,
                changed_by="user1",
                reason="Попытка",
            )

    def test_full_lifecycle_draft_active_won(self):
        """Полный цикл: DRAFT -> ACTIVE -> WON."""
        tender = create_tender()
        # DRAFT -> ACTIVE
        tender = services.change_tender_status(
            tender_id=tender.id,
            new_status=TenderStatus.ACTIVE,
            changed_by="user1",
            reason="Шаг 1",
        )
        assert tender.status == TenderStatus.ACTIVE
        # ACTIVE -> WON
        tender = services.change_tender_status(
            tender_id=tender.id,
            new_status=TenderStatus.WON,
            changed_by="user2",
            reason="Шаг 2",
        )
        assert tender.status == TenderStatus.WON
        # Проверяем историю
        history = TenderStatusHistory.objects.filter(tender=tender).order_by("changed_at")
        assert history.count() == 2
        assert history[0].new_status == TenderStatus.ACTIVE
        assert history[1].new_status == TenderStatus.WON

    def test_get_tender_history_returns_chronological_order(self):
        """История возвращается в хронологическом порядке."""
        tender = create_tender()
        services.change_tender_status(
            tender_id=tender.id,
            new_status=TenderStatus.ACTIVE,
            changed_by="user1",
            reason="Шаг 1",
        )
        services.change_tender_status(
            tender_id=tender.id,
            new_status=TenderStatus.WON,
            changed_by="user2",
            reason="Шаг 2",
        )
        history = services.get_tender_history(tender.id)
        assert history.count() == 2
        # Новые записи сверху
        assert history[0].new_status == TenderStatus.WON
        assert history[1].new_status == TenderStatus.ACTIVE
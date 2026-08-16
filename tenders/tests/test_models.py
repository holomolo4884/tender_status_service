import pytest

from tenders.constants import TenderStatus

from .factories import create_tender


@pytest.mark.django_db
class TestTenderModel:
    """Тесты модели Tender и матрицы переходов."""

    def test_initial_status_is_draft(self):
        """Созданный тендер имеет статус DRAFT."""
        tender = create_tender()
        assert tender.status == TenderStatus.DRAFT

    def test_can_transition_draft_to_active(self):
        """Переход DRAFT -> ACTIVE разрешён."""
        tender = create_tender()
        assert tender.can_transition_to(TenderStatus.ACTIVE) is True

    def test_cannot_transition_draft_to_won(self):
        """Переход DRAFT -> WON запрещён (минуя ACTIVE)."""
        tender = create_tender()
        assert tender.can_transition_to(TenderStatus.WON) is False

    def test_cannot_transition_draft_to_lost(self):
        """Переход DRAFT -> LOST запрещён."""
        tender = create_tender()
        assert tender.can_transition_to(TenderStatus.LOST) is False

    def test_can_transition_active_to_won(self):
        """Переход ACTIVE -> WON разрешён."""
        tender = create_tender()
        tender.status = TenderStatus.ACTIVE
        tender.save()
        assert tender.can_transition_to(TenderStatus.WON) is True

    def test_can_transition_active_to_lost(self):
        """Переход ACTIVE -> LOST разрешён."""
        tender = create_tender()
        tender.status = TenderStatus.ACTIVE
        tender.save()
        assert tender.can_transition_to(TenderStatus.LOST) is True

    def test_cannot_transition_won_to_anything(self):
        """Из WON нельзя никуда перейти (терминальное состояние)."""
        tender = create_tender()
        tender.status = TenderStatus.WON
        tender.save()
        assert tender.can_transition_to(TenderStatus.DRAFT) is False
        assert tender.can_transition_to(TenderStatus.ACTIVE) is False
        assert tender.can_transition_to(TenderStatus.LOST) is False

    def test_cannot_transition_lost_to_anything(self):
        """Из LOST нельзя никуда перейти (терминальное состояние)."""
        tender = create_tender()
        tender.status = TenderStatus.LOST
        tender.save()
        assert tender.can_transition_to(TenderStatus.DRAFT) is False
        assert tender.can_transition_to(TenderStatus.ACTIVE) is False
        assert tender.can_transition_to(TenderStatus.WON) is False
from tenders.constants import TenderStatus
from tenders.models import Tender, TenderStatusHistory


def create_tender(title="Тестовый тендер", description=""):
    """Создаёт тендер с начальным статусом DRAFT."""
    return Tender.objects.create(
        title=title,
        description=description,
        status=TenderStatus.DRAFT,
    )


def create_history(tender, old_status, new_status, changed_by="test_user", reason="Тест"):
    """Создаёт запись истории."""
    return TenderStatusHistory.objects.create(
        tender=tender,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        reason=reason,
    )
import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from tenders.constants import TenderStatus

from .factories import create_tender


@pytest.mark.django_db
class TestTenderAPI:
    """Интеграционные тесты API."""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    def test_create_tender(self, api_client):
        """POST /api/v1/tenders/ создаёт тендер со статусом DRAFT."""
        url = reverse("tenders:tender-create")
        response = api_client.post(
            url,
            {"title": "Тендер 1", "description": "Описание"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == TenderStatus.DRAFT
        assert response.data["title"] == "Тендер 1"

    def test_get_tender_detail(self, api_client):
        """GET /api/v1/tenders/{id}/ возвращает детали."""
        tender = create_tender(title="Тест")
        url = reverse("tenders:tender-detail", kwargs={"tender_id": tender.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Тест"

    def test_get_nonexistent_tender_returns_404(self, api_client):
        """GET несуществующего тендера возвращает 404."""
        url = reverse("tenders:tender-detail", kwargs={"tender_id": 99999})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_change_status_valid_transition(self, api_client):
        """PATCH допустимого перехода возвращает 200."""
        tender = create_tender()
        url = reverse("tenders:tender-status", kwargs={"tender_id": tender.id})
        response = api_client.patch(
            url,
            {
                "status": TenderStatus.ACTIVE,
                "changed_by": "user1",
                "reason": "Опубликован",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == TenderStatus.ACTIVE

    def test_change_status_invalid_transition_returns_409(self, api_client):
        """PATCH недопустимого перехода возвращает 409."""
        tender = create_tender()
        url = reverse("tenders:tender-status", kwargs={"tender_id": tender.id})
        response = api_client.patch(
            url,
            {
                "status": TenderStatus.WON,
                "changed_by": "user1",
                "reason": "Попытка",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "current_status" in response.data
        assert "requested_status" in response.data

    def test_change_status_without_reason_returns_422(self, api_client):
        """PATCH без reason возвращает 422."""
        tender = create_tender()
        url = reverse("tenders:tender-status", kwargs={"tender_id": tender.id})
        response = api_client.patch(
            url,
            {
                "status": TenderStatus.ACTIVE,
                "changed_by": "user1",
                # reason отсутствует
            },
            format="json",
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_change_status_empty_reason_returns_422(self, api_client):
        """PATCH с пустым reason возвращает 422."""
        tender = create_tender()
        url = reverse("tenders:tender-status", kwargs={"tender_id": tender.id})
        response = api_client.patch(
            url,
            {
                "status": TenderStatus.ACTIVE,
                "changed_by": "user1",
                "reason": "",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_tender_history(self, api_client):
        """GET /api/v1/tenders/{id}/history/ возвращает историю."""
        tender = create_tender()
        # Создаём переход
        api_client.patch(
            reverse("tenders:tender-status", kwargs={"tender_id": tender.id}),
            {
                "status": TenderStatus.ACTIVE,
                "changed_by": "user1",
                "reason": "Опубликован",
            },
            format="json",
        )
        # Запрашиваем историю
        url = reverse("tenders:tender-history", kwargs={"tender_id": tender.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["new_status"] == TenderStatus.ACTIVE
        assert response.data[0]["changed_by"] == "user1"
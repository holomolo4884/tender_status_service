from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import (
    TenderCreateSerializer,
    TenderSerializer,
    TenderStatusChangeSerializer,
    TenderStatusHistorySerializer,
)


class TenderCreateView(APIView):
    """POST /api/v1/tenders/ — создать тендер."""

    def post(self, request):
        serializer = TenderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tender = services.create_tender(
            title=serializer.validated_data["title"],
            description=serializer.validated_data.get("description", ""),
        )
        return Response(TenderSerializer(tender).data, status=status.HTTP_201_CREATED)


class TenderDetailView(APIView):
    """GET /api/v1/tenders/{id}/ — детали тендера."""

    def get(self, request, tender_id):
        tender = services.get_tender(tender_id)
        return Response(TenderSerializer(tender).data)


class TenderStatusChangeView(APIView):
    """PATCH /api/v1/tenders/{id}/status/ — сменить статус."""

    def patch(self, request, tender_id):
        serializer = TenderStatusChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tender = services.change_tender_status(
            tender_id=tender_id,
            new_status=serializer.validated_data["status"],
            changed_by=serializer.validated_data["changed_by"],
            reason=serializer.validated_data["reason"],
        )
        return Response(TenderSerializer(tender).data)


class TenderStatusHistoryView(APIView):
    """GET /api/v1/tenders/{id}/history/ — история изменений статуса."""

    def get(self, request, tender_id):
        history = services.get_tender_history(tender_id)
        return Response(TenderStatusHistorySerializer(history, many=True).data)
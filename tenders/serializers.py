from rest_framework import serializers

from .constants import TenderStatus
from .models import Tender, TenderStatusHistory


class TenderCreateSerializer(serializers.Serializer):
    """Входные данные для создания тендера."""

    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")


class TenderSerializer(serializers.ModelSerializer):
    """Представление тендера (только чтение)."""

    class Meta:
        model = Tender
        fields = ("id", "title", "description", "status", "created_at", "updated_at")
        read_only_fields = fields


class TenderStatusChangeSerializer(serializers.Serializer):
    """Запрос на смену статуса. reason и changed_by обязательны."""

    status = serializers.ChoiceField(choices=TenderStatus.choices)
    changed_by = serializers.CharField(max_length=255)
    reason = serializers.CharField()


class TenderStatusHistorySerializer(serializers.ModelSerializer):
    """Запись истории (только чтение)."""

    class Meta:
        model = TenderStatusHistory
        fields = ("id", "old_status", "new_status", "changed_by", "reason", "changed_at")
        read_only_fields = fields
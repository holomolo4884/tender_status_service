from django.contrib import admin

from .models import Tender, TenderStatusHistory


class StatusHistoryInline(admin.TabularInline):
    model = TenderStatusHistory
    extra = 0
    readonly_fields = (
        "old_status",
        "new_status",
        "changed_by",
        "reason",
        "changed_at",
    )

    def has_add_permission(self, request, obj=None):
        # История неизменяема — ручное добавление запрещено.
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "version",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "status",
    )
    search_fields = (
        "title",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "version",
    )
    inlines = [
        StatusHistoryInline,
    ]


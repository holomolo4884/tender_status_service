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
        return False  # историю нельзя добавлять вручную

    def has_delete_permission(self, request, obj=None):
        return False  # историю нельзя удалять


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
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
    )
    inlines = [
        StatusHistoryInline,
    ]


@admin.register(TenderStatusHistory)
class TenderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "tender",
        "old_status",
        "new_status",
        "changed_by",
        "changed_at",
    )
    list_filter = (
        "new_status",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
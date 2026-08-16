from django.urls import path

from . import views

app_name = "tenders"

urlpatterns = [
    path("tenders/", views.TenderCreateView.as_view(), name="tender-create"),
    path("tenders/<int:tender_id>/", views.TenderDetailView.as_view(), name="tender-detail"),
    path("tenders/<int:tender_id>/status/", views.TenderStatusChangeView.as_view(), name="tender-status"),
    path("tenders/<int:tender_id>/history/", views.TenderStatusHistoryView.as_view(), name="tender-history"),
]
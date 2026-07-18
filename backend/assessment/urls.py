from django.urls import path

from .views import (
    AdminStatsView,
    QuestionListView,
    RatingListView,
    ResultPDFView,
    ResultView,
    SubmitView,
)

urlpatterns = [
    path("questions/", QuestionListView.as_view(), name="questions"),
    path("submit/", SubmitView.as_view(), name="submit"),
    path("result/<int:pk>/", ResultView.as_view(), name="result-detail"),
    path("result/<int:pk>/pdf/", ResultPDFView.as_view(), name="result-pdf"),
    path("ratings/", RatingListView.as_view(), name="ratings"),
    path("admin/stats/", AdminStatsView.as_view(), name="admin-stats"),
]

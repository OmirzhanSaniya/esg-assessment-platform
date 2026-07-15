from django.urls import path
from .views import AdminStatsView, QuestionListView, RatingListView, ResultDetailView, ResultPDFView, SubmitAssessmentView


urlpatterns = [
    path(
        "questions/",
        QuestionListView.as_view()
    ),
    path(
        "submit/",
        SubmitAssessmentView.as_view(),
        name="submit"
    ),
    path(
        "result/<int:pk>/",
        ResultDetailView.as_view(),
        name="result-detail",
    ),
    path(
        "result/<int:pk>/pdf/",
        ResultPDFView.as_view(),
        name="result-pdf",
    ),
    path("admin/stats/", AdminStatsView.as_view(), name="admin-stats"),
    path("ratings/", RatingListView.as_view(), name="ratings"),
]
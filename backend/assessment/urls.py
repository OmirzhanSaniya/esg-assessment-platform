from django.urls import path
from .views import QuestionListView, SubmitAssessmentView


urlpatterns = [
    path(
        "questions/",
        QuestionListView.as_view()
    ),
    path(
        "submit/",
        SubmitAssessmentView.as_view(),
        name="submit"
    )
]
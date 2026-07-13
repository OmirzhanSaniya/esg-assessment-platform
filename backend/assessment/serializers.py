from rest_framework import serializers
from .models import Question, Result


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            "id",
            "internal_code",
            "text",
            "block",
            "question_type",
            "weight",
            "order",
        )



class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = (
            "id",
            "score_e",
            "score_s",
            "score_g",
            "score_total",
            "level",
            "created_at",
        )



class SubmitAssessmentSerializer(serializers.Serializer):
    answers = serializers.DictField()
    controversy_answers = serializers.DictField(required=False, default=dict)
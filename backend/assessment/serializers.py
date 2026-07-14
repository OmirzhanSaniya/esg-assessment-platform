from rest_framework import serializers
from .models import Question, Result, Answer
from scoring.esg_config import calculate_esg_score, generate_roadmap_from_answers

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

class AnswerSerializer(serializers.ModelSerializer):
    question = serializers.CharField(source="question.internal_code")
    text = serializers.CharField(source="question.text")

    class Meta:
        model = Answer
        fields = (
            "question",
            "text",
            "value",
        )

class ResultDetailSerializer(serializers.ModelSerializer):

    answers = AnswerSerializer(many=True)
    roadmap = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = [
            "id",
            "score_e",
            "score_s",
            "score_g",
            "score_total",
            "level",
            "created_at",
            "answers",
            "roadmap",
        ]


    def get_roadmap(self, obj):

        answers = {}

        for answer in obj.answers.all():
            answers[answer.question.internal_code] = answer.value


        score = calculate_esg_score(
            answers=answers,
            controversy_answers={},
            sector_id=obj.company.industry,
            sub_industry_id=obj.company.sub_industry,
        )


        return generate_roadmap_from_answers(
            score,
            {}
        )

class SubmitAssessmentSerializer(serializers.Serializer):
    answers = serializers.DictField()
    controversy_answers = serializers.DictField(required=False, default=dict)


class AdminStatsSerializer(serializers.Serializer):
    users = serializers.IntegerField()
    companies = serializers.IntegerField()
    assessments = serializers.IntegerField()
    average_score = serializers.FloatField()


class RatingSerializer(ResultSerializer):
    company_id = serializers.IntegerField(source="company.id")
    company = serializers.CharField(source="company.name")
    industry = serializers.CharField(source="company.industry")
    updated_at = serializers.DateTimeField(source="created_at")

    class Meta(ResultSerializer.Meta):
        fields = (
            "company_id",
            "company",
            "industry",
            "score_total",
            "level",
            "updated_at",
        )
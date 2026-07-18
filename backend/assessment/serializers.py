from rest_framework import serializers

from scoring.esg_config import CONTROVERSY_FLAGS, QUESTIONS, get_sector_name

from .models import Answer, Question, Result


# Значения здесь остаются lazy gettext-объектами. str(...) вызывается уже во время
# HTTP-запроса, после того как LocaleMiddleware активировал ru/kk/en.
QUESTION_TEXT_BY_CODE = {
    item["id"]: item["text"]
    for item in [*QUESTIONS, *CONTROVERSY_FLAGS]
}


class QuestionSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()

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
            "is_controversy",
            "severity",
        )
        read_only_fields = fields

    def get_text(self, obj):
        # Текст из БД используется как fallback для неизвестного internal_code.
        return str(QUESTION_TEXT_BY_CODE.get(obj.internal_code, obj.text))


class AnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(min_value=1)
    value = serializers.IntegerField()


class SubmitAssessmentSerializer(serializers.Serializer):
    answers = AnswerInputSerializer(many=True, allow_empty=False)

    def validate_answers(self, answers):
        question_ids = [item["question_id"] for item in answers]

        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError(
                "На один вопрос нельзя отправить несколько ответов."
            )

        return answers


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
        read_only_fields = fields


class AnswerSerializer(serializers.ModelSerializer):
    question = serializers.CharField(source="question.internal_code")
    text = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ("question", "text", "value")
        read_only_fields = fields

    def get_text(self, obj):
        return str(
            QUESTION_TEXT_BY_CODE.get(
                obj.question.internal_code,
                obj.question.text,
            )
        )


class AdminStatsSerializer(serializers.Serializer):
    users = serializers.IntegerField()
    companies = serializers.IntegerField()
    assessments = serializers.IntegerField()
    average_score = serializers.FloatField()


class RatingSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(source="company.id")
    company = serializers.CharField(source="company.name")
    industry = serializers.CharField(source="company.industry")
    industry_name = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(source="created_at")

    class Meta:
        model = Result
        fields = (
            "company_id",
            "company",
            "industry",
            "industry_name",
            "score_e",
            "score_s",
            "score_g",
            "score_total",
            "level",
            "updated_at",
        )
        read_only_fields = fields

    def get_industry_name(self, obj):
        return get_sector_name(obj.company.industry)

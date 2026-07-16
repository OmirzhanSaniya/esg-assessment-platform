from rest_framework import serializers

from .models import Answer, Question, Recommendation, Result


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
            "is_controversy",
            "severity",
        )
        read_only_fields = fields


class AnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(min_value=1)
    value = serializers.IntegerField()

    def validate(self, attrs):
        question_id = attrs["question_id"]
        value = attrs["value"]

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "question_id": (
                        f"Вопрос с id={question_id} не существует."
                    )
                }
            )

        if question.is_controversy:
            if value not in (0, 1):
                raise serializers.ValidationError(
                    {
                        "value": (
                            "Для controversy-вопроса значение "
                            "должно быть 0 или 1."
                        )
                    }
                )

        elif question.question_type == Question.QuestionType.YES_NO:
            if value not in (0, 1):
                raise serializers.ValidationError(
                    {
                        "value": (
                            "Для вопроса yes_no значение "
                            "должно быть 0 или 1."
                        )
                    }
                )

        elif question.question_type == Question.QuestionType.PERCENTAGE:
            if not 0 <= value <= 100:
                raise serializers.ValidationError(
                    {
                        "value": (
                            "Для процентного вопроса значение "
                            "должно быть от 0 до 100."
                        )
                    }
                )

        elif question.question_type in (
            Question.QuestionType.SCALE,
            Question.QuestionType.SINGLE_CHOICE,
        ):
            if not 0 <= value <= 3:
                raise serializers.ValidationError(
                    {
                        "value": (
                            "Для шкалы значение должно быть "
                            "от 0 до 3."
                        )
                    }
                )

        attrs["question"] = question

        return attrs


class SubmitAssessmentSerializer(serializers.Serializer):
    answers = AnswerInputSerializer(
        many=True,
        allow_empty=False,
    )

    def validate_answers(self, answers):
        question_ids = [
            answer["question_id"]
            for answer in answers
        ]

        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError(
                "На один вопрос нельзя отправить несколько ответов."
            )

        return answers


class AnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(
        read_only=True,
    )

    internal_code = serializers.CharField(
        source="question.internal_code",
        read_only=True,
    )

    question_text = serializers.CharField(
        source="question.text",
        read_only=True,
    )

    class Meta:
        model = Answer
        fields = (
            "id",
            "question_id",
            "internal_code",
            "question_text",
            "value",
        )
        read_only_fields = fields


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = (
            "id",
            "block",
            "level",
            "text_ru",
            "text_kz",
            "text_en",
        )
        read_only_fields = fields


class ResultSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(
        source="company.name",
        read_only=True,
    )

    answers = AnswerSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Result
        fields = (
            "id",
            "company_name",
            "score_e",
            "score_s",
            "score_g",
            "score_total",
            "level",
            "created_at",
            "answers",
        )
        read_only_fields = fields
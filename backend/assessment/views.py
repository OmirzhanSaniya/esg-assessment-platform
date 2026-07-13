from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Result, Answer, Question
from accounts.models import Company

from .serializers import QuestionSerializer
from .serializers import SubmitAssessmentSerializer

from scoring.esg_config import calculate_esg_score

class QuestionListView(APIView):

    def get(self, request):

        questions = Question.objects.all()

        serializer = QuestionSerializer(
            questions,
            many=True
        )

        grouped = {
            "E": [],
            "S": [],
            "G": []
        }

        for question in serializer.data:
            grouped[question["block"]].append(question)

        return Response(grouped)
    

class SubmitAssessmentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = SubmitAssessmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answers = serializer.validated_data["answers"]
        controversy_answers = serializer.validated_data.get(
            "controversy_answers",
            {}
        )

        company = request.user.company


        result_data = calculate_esg_score(
            answers=answers,
            controversy_answers=controversy_answers,
            sector_id=company.industry,
            sub_industry_id=company.sub_industry
        )


        result = Result.objects.create(
            company=company,
            score_e=result_data["pillar_scores"]["E"],
            score_s=result_data["pillar_scores"]["S"],
            score_g=result_data["pillar_scores"]["G"],
            score_total=result_data["esg_final"],
            level=result_data["tier"],
        )


        for question_code, value in answers.items():

            try:
                question = Question.objects.get(
                    internal_code=question_code
                )

                Answer.objects.create(
                    result=result,
                    question=question,
                    value=value
                )

            except Question.DoesNotExist:
                pass


        return Response(
            {
                "message": "Assessment submitted successfully.",
                "result_id": result.id
            }
        )
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import RetrieveAPIView, ListAPIView

from .models import Result, Answer, Question
from accounts.models import User, Company
from .serializers import QuestionSerializer, ResultDetailSerializer, SubmitAssessmentSerializer, AdminStatsSerializer, RatingSerializer

from scoring.esg_config import calculate_esg_score, generate_roadmap_from_answers

from django.db.models import Avg

from io import BytesIO

from django.http import FileResponse
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FONT_PATH = BASE_DIR / "fonts" / "DejaVuSans.ttf"

pdfmetrics.registerFont(
    TTFont("DejaVu", str(FONT_PATH))
)

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
    

class ResultDetailView(RetrieveAPIView):

    serializer_class = ResultDetailSerializer
    queryset = Result.objects.select_related(
        "company"
    ).prefetch_related(
        "answers__question"
    )


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
    

class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        average = Result.objects.aggregate(avg=Avg("score_total"))["avg"] or 0

        data = {
            "users": User.objects.count(),
            "companies": Company.objects.count(),
            "assessments": Result.objects.count(),
            "average_score": round(average, 2),
        }
        serializer = AdminStatsSerializer(data)
        return Response(serializer.data)
    

class RatingListView(ListAPIView):
    serializer_class = RatingSerializer

    def get_queryset(self):
        queryset = (
            Result.objects
            .select_related("company")
            .order_by("company_id", "-created_at")
            .distinct("company_id")
        )

        industry = self.request.query_params.get("industry")
        if industry:
            queryset = queryset.filter(company__industry=industry)

        return queryset



class ResultPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            result = Result.objects.select_related(
                "company"
            ).prefetch_related(
                "answers__question"
            ).get(
                id=pk,
                company=request.user.company,
            )

        except Result.DoesNotExist:
            return Response({"detail": "Result not found."}, status=404)


        serializer = ResultDetailSerializer(result)
        data = serializer.data

        roadmap = data["roadmap"]


        buffer = BytesIO()

        doc = SimpleDocTemplate(buffer)

        style = ParagraphStyle(
            "BodyText",
            fontName="DejaVu",
            fontSize=12,
        )

        story = [
            Paragraph("ESG Assessment Report", style),
            Paragraph(f"Company: {result.company.name}", style),
            Paragraph(f"Environmental: {result.score_e:.1f}", style),
            Paragraph(f"Social: {result.score_s:.1f}", style),
            Paragraph(f"Governance: {result.score_g:.1f}", style),
            Paragraph(f"Total score: {result.score_total:.1f}", style),
            Paragraph(f"Level: {result.level}", style),

            Paragraph(
                roadmap["summary"]["conclusion"],
                style
            ),
        ]

        doc.build(story)

        buffer.seek(0)

        return FileResponse(
            buffer,
            as_attachment=True,
            filename=f"assessment_{pk}.pdf",
        )
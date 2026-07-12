from rest_framework import serializers
from accounts.models import User, Company


class RegisterSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(max_length=255)
    industry = serializers.CharField(max_length=30)
    sub_industry = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        allow_null=True
    )

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "company_name",
            "industry",
            "sub_industry",
        )

    def create(self, validated_data):
        company_name = validated_data.pop("company_name")
        industry = validated_data.pop("industry")
        sub_industry = validated_data.pop("sub_industry", None)

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            role="company",
            **validated_data
        )

        Company.objects.create(
            user=user,
            name=company_name,
            industry=industry,
            sub_industry=sub_industry,
        )

        return user
    
    
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            "name",
            "industry",
            "sub_industry",
        )


class ProfileSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "role",
            "created_at",
            "company",
        )

    def get_company(self, obj):
        try:
            company = obj.company
            return CompanySerializer(company).data
        except Company.DoesNotExist:
            return None
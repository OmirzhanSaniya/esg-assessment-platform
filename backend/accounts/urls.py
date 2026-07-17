from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import LogoutView, RegisterView, CompanyProfileView, CompanyHistoryView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path(
        "auth/login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),

    path(
        "auth/logout/",
        LogoutView.as_view(),
        name="logout"
    ),

    path(
        "auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),

    path(
        "company/profile/",
        CompanyProfileView.as_view(),
        name="profile",
    ),

    path(
        "company/history/",
        CompanyHistoryView.as_view(),
        name="company-history"
    ),
]
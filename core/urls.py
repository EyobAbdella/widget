from django.urls import path
from .views import GoogleRedirectAPI, GoogleAPI

urlpatterns = [
    path("google-oauth2/callback/", GoogleAPI.as_view()),
    path(
        "google-oauth2/redirect/",
        GoogleRedirectAPI.as_view(),
        name="google-oauth2-redirect",
    ),
]

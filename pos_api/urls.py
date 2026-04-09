# pos_api/urls.py
from django.urls import path
from .views import FetchNextCommand, SubmitResult

urlpatterns = [
    path("fetch/", FetchNextCommand.as_view()),
    path("result/<int:command_id>/", SubmitResult.as_view()),
]
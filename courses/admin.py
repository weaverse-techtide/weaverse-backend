from django.conf import settings
from django.contrib import admin

from .models import (
    Assignment,
    Course,
    Lecture,
    MultipleChoiceQuestion,
    MultipleChoiceQuestionChoice,
    Topic,
)

if settings.DEBUG:
    admin.register(Course)
    admin.register(Lecture)
    admin.register(Topic)
    admin.register(Assignment)
    admin.register(MultipleChoiceQuestion)
    admin.register(MultipleChoiceQuestionChoice)

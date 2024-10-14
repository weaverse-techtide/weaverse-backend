from django.conf import settings
from django.contrib import admin

from .models import (
    Assignment,
    Course,
    Curriculum,
    Lecture,
    MultipleChoiceQuestion,
    MultipleChoiceQuestionChoice,
    Topic,
)

if settings.DEBUG:
    admin.site.register(Course)
    admin.site.register(Lecture)
    admin.site.register(Topic)
    admin.site.register(Assignment)
    admin.site.register(MultipleChoiceQuestion)
    admin.site.register(MultipleChoiceQuestionChoice)
    admin.site.register(Curriculum)

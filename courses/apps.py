from django.apps import AppConfig


class CoursesConfig(AppConfig):
    """
    Course 앱의 설정 클래스입니다.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "courses"

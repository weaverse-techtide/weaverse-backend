# Generated by Django 5.1.1 on 2024-10-10 02:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_rename_course_level_course_skill_level_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='courses', to=settings.AUTH_USER_MODEL, verbose_name='작성자'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='curriculum',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='curriculums', to=settings.AUTH_USER_MODEL, verbose_name='작성자'),
            preserve_default=False,
        ),
    ]

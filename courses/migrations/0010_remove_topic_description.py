# Generated by Django 5.1.1 on 2024-10-13 08:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_course_author_curriculum_author'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topic',
            name='description',
        ),
    ]

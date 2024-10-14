# Generated by Django 5.1.1 on 2024-10-10 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_alter_course_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='course_level',
            new_name='skill_level',
        ),
        migrations.AddField(
            model_name='curriculum',
            name='category',
            field=models.CharField(choices=[('JavaScript', 'JavaScript'), ('Python', 'Python'), ('Django', 'Django'), ('React', 'React'), ('Vue', 'Vue'), ('Node', 'Node'), ('AWS', 'AWS'), ('Docker', 'Docker'), ('DB', 'DB')], default='JavaScript', max_length=255, verbose_name='카테고리'),
        ),
        migrations.AddField(
            model_name='curriculum',
            name='skill_level',
            field=models.CharField(choices=[('beginner', '초급'), ('intermediate', '중급'), ('advanced', '고급')], default='beginner', max_length=255, verbose_name='난이도'),
        ),
    ]

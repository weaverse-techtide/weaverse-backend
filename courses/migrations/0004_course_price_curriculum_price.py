# Generated by Django 5.1.1 on 2024-10-01 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_remove_lecture_description_course_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='price',
            field=models.PositiveIntegerField(default=1000000, verbose_name='가격'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='curriculum',
            name='price',
            field=models.PositiveIntegerField(default=1000000, verbose_name='가격'),
            preserve_default=False,
        ),
    ]

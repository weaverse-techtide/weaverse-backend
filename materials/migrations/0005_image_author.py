# Generated by Django 5.1.1 on 2024-10-13 11:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0004_remove_image_file_remove_image_image_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='images', to=settings.AUTH_USER_MODEL, verbose_name='이미지를 등록한 사용자'),
            preserve_default=False,
        ),
    ]

# Generated by Django 5.1.1 on 2024-10-03 06:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jwtauth", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="blacklistedtoken",
            name="token_type",
            field=models.CharField(
                choices=[("access", "Access"), ("refresh", "Refresh")],
                default="refresh",
                max_length=10,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="blacklistedtoken",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="blacklisted_tokens",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="blacklistedtoken",
            name="token",
            field=models.CharField(max_length=500, unique=True),
        ),
        migrations.AddIndex(
            model_name="blacklistedtoken",
            index=models.Index(fields=["token"], name="jwtauth_bla_token_f4b383_idx"),
        ),
        migrations.AddIndex(
            model_name="blacklistedtoken",
            index=models.Index(
                fields=["user", "token_type"], name="jwtauth_bla_user_id_971c12_idx"
            ),
        ),
    ]

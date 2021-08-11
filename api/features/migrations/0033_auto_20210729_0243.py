# Generated by Django 2.2.24 on 2021-07-29 02:43

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ("features", "0032_update_feature_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="featurestate",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="historicalfeaturestate",
            name="updated_at",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(2021, 7, 29, 2, 43, 40, 186073, tzinfo=utc),
                editable=False,
            ),
            preserve_default=False,
        ),
    ]
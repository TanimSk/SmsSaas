# Generated by Django 4.2.6 on 2025-03-03 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forwarder", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="inappropiate_content",
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 4.1.7 on 2025-01-04 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("custom_auth", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="labsactive",
            name="lab_id",
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),
    ]
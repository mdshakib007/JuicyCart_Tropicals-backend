# Generated by Django 5.1 on 2025-02-09 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listing', '0003_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='rating',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

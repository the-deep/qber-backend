# Generated by Django 4.2.1 on 2023-09-06 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0005_alter_questionleafgroup_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
    ]

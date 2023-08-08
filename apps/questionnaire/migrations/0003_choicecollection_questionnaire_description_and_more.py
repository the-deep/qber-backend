# Generated by Django 4.2.1 on 2023-08-07 06:23

from django.contrib.postgres.operations import CreateExtension
from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import utils.common


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('questionnaire', '0002_initial'),
    ]

    operations = [
        CreateExtension("postgis"),
        migrations.CreateModel(
            name='ChoiceCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('label', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name='QuestionGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('label', models.CharField(max_length=255)),
                ('relevant', models.CharField(max_length=255)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='questionnaire.questiongroup')),
                ('questionnaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaire.questionnaire')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Integer (i.e., whole number) input.'), (2, 'Decimal input.'), (3, 'Free text response.'), (4, 'Multiple choice question; only one answer can be selected.'), (5, 'Multiple choice question; multiple answers can be selected.'), (6, 'Rank question; order a list.')])),
                ('name', models.CharField(max_length=255, validators=[utils.common.validate_xlsform_name])),
                ('label', models.TextField()),
                ('hint', models.TextField(blank=True)),
                ('choice_collection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='questionnaire.choicecollection')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='questionnaire.questiongroup')),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
                ('questionnaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaire.questionnaire')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='choicecollection',
            name='questionnaire',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaire.questionnaire'),
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('label', models.CharField(max_length=255)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326)),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaire.choicecollection')),
            ],
        ),
    ]

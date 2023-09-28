# Generated by Django 4.2.5 on 2023-09-28 05:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('qbank', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionbank',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='questionbank',
            name='modified_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='qbquestion',
            name='choice_collection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='qbank.qbchoicecollection'),
        ),
        migrations.AddField(
            model_name='qbquestion',
            name='leaf_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='qbank.qbleafgroup'),
        ),
        migrations.AddField(
            model_name='qbquestion',
            name='qbank',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qbank.questionbank'),
        ),
        migrations.AddField(
            model_name='qbleafgroup',
            name='qbank',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qbank.questionbank'),
        ),
        migrations.AddField(
            model_name='qbchoicecollection',
            name='qbank',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qbank.questionbank'),
        ),
        migrations.AddField(
            model_name='qbchoice',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qbank.qbchoicecollection'),
        ),
        migrations.AlterUniqueTogether(
            name='qbleafgroup',
            unique_together={('qbank', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='qbchoicecollection',
            unique_together={('qbank', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='qbchoice',
            unique_together={('collection', 'name')},
        ),
    ]

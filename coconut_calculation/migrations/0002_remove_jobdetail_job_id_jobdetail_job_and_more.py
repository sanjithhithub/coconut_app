# Generated by Django 4.2.16 on 2025-03-07 11:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coconut_calculation', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobdetail',
            name='job_id',
        ),
        migrations.AddField(
            model_name='jobdetail',
            name='job',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='coconut_calculation.job'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='password_reset_requested_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

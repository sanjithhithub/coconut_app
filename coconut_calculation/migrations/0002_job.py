# Generated by Django 5.1.4 on 2025-01-14 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coconut_calculation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
    ]

# Generated by Django 5.1.7 on 2025-03-24 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release_form', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='releasedstock',
            name='production_code',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='releasedstock',
            name='warehouse_id',
            field=models.CharField(blank=True, max_length=100, primary_key=True, serialize=False),
        ),
    ]

# Generated by Django 5.1.7 on 2025-03-24 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FromsStock',
            fields=[
                ('warehouse_id', models.CharField(blank=True, max_length=100, primary_key=True, serialize=False)),
                ('production_code', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('product', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=50)),
                ('item_code', models.CharField(max_length=100)),
                ('quantity', models.IntegerField()),
                ('pallet_position', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=50)),
            ],
        ),
    ]

# Generated by Django 4.1.13 on 2024-07-18 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genphen', '0011_promoterdistance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variantgrade',
            name='grade',
            field=models.IntegerField(),
        ),
    ]

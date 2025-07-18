# Generated by Django 5.2.3 on 2025-07-15 18:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('garden', '0013_community_additional_info_community_bank_details_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='choice',
            field=models.CharField(choices=[('for', 'За'), ('against', 'Против'), ('abstained', 'Воздержался')], max_length=10),
        ),
        migrations.AlterField(
            model_name='vote',
            name='voting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='garden.voting'),
        ),
    ]

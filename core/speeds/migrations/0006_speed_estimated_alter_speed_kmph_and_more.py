# Generated by Django 4.2 on 2023-04-14 21:51

import core.speeds.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('speeds', '0005_speed_speed_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='speed',
            name='estimated',
            field=models.BooleanField(default=False, verbose_name='estimated'),
        ),
        migrations.AlterField(
            model_name='speed',
            name='kmph',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(1080000000), core.speeds.validators.CustomMinValueValidator(0)], verbose_name='speed in km/h'),
        ),
        migrations.AlterField(
            model_name='speed',
            name='speed_type',
            field=models.TextField(choices=[('average', 'Average'), ('top', 'Top'), ('constant', 'Constant'), ('relative', 'Relative')], verbose_name='speed type'),
        ),
        migrations.AlterField(
            model_name='speedreport',
            name='report',
            field=models.TextField(blank=True, choices=[('spam', 'Spam'), ('incorrcect data', 'Incorrect Data'), ('non english', 'Non English'), ('inappropriate language', 'Inappropriate Language'), ('other', 'Other')], null=True, verbose_name='report'),
        ),
    ]

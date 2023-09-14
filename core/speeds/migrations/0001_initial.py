# Generated by Django 4.2.5 on 2023-09-14 18:38

import core.speeds.validators
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Speed',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, verbose_name='name')),
                ('description', models.CharField(blank=True, max_length=128, null=True, verbose_name='description')),
                ('speed_type', models.CharField(choices=[('average', 'Average'), ('top', 'Top'), ('constant', 'Constant'), ('relative', 'Relative')], verbose_name='speed type')),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), blank=True, size=4)),
                ('kmph', models.FloatField(validators=[django.core.validators.MaxValueValidator(1080000000), core.speeds.validators.CustomMinValueValidator(0)], verbose_name='speed in km/h')),
                ('estimated', models.BooleanField(default=False, verbose_name='estimated')),
                ('is_public', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('downvotes', models.PositiveIntegerField(default=0, verbose_name='downvotes')),
                ('upvotes', models.PositiveIntegerField(default=1, verbose_name='upvotes')),
                ('score', models.IntegerField(default=1, verbose_name='score')),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='SpeedBookmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, max_length=32, null=True, verbose_name='category')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SpeedFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField(choices=[(-1, 'Downvote'), (0, 'Default State'), (1, 'Upvote')], default=0, verbose_name='vote')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SpeedReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_reason', models.CharField(blank=True, choices=[('spam', 'Spam'), ('incorrcect data', 'Incorrect Data'), ('non english', 'Non English'), ('inappropriate language', 'Inappropriate Language'), ('other', 'Other')], null=True, verbose_name='report reason')),
                ('detail', models.CharField(blank=True, max_length=256, null=True, verbose_name='detail')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('speed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report', to='speeds.speed')),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
    ]

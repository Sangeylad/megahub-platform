# Generated by Django 4.2.23 on 2025-07-26 20:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mailing_contacts_core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('brands_core', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListSegment',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('segment_type', models.CharField(choices=[('static', 'Static'), ('dynamic', 'Dynamic'), ('behavioral', 'Behavioral'), ('demographic', 'Demographic')], default='dynamic', max_length=30)),
                ('conditions', models.JSONField(default=dict)),
                ('logical_operator', models.CharField(default='AND', max_length=10)),
                ('subscriber_count', models.IntegerField(default=0)),
                ('last_evaluated_at', models.DateTimeField(blank=True, null=True)),
                ('auto_update', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brands_core.brand')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('subscribers', models.ManyToManyField(blank=True, to='mailing_contacts_core.emailsubscriber')),
            ],
            options={
                'unique_together': {('name', 'brand')},
            },
        ),
        migrations.CreateModel(
            name='SegmentCondition',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('field_name', models.CharField(max_length=100)),
                ('operator', models.CharField(choices=[('equals', 'Equals'), ('not_equals', 'Not Equals'), ('contains', 'Contains'), ('not_contains', 'Not Contains'), ('starts_with', 'Starts With'), ('ends_with', 'Ends With'), ('greater_than', 'Greater Than'), ('less_than', 'Less Than'), ('greater_equal', 'Greater or Equal'), ('less_equal', 'Less or Equal'), ('in', 'In'), ('not_in', 'Not In')], max_length=20)),
                ('value', models.CharField(max_length=255)),
                ('logical_operator', models.CharField(default='AND', max_length=10)),
                ('order', models.IntegerField(default=0)),
                ('segment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='segment_conditions', to='mailing_lists_segments.listsegment')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]

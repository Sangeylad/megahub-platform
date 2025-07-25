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
            name='ListMembership',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('subscription_source', models.CharField(choices=[('manual', 'Manual'), ('import', 'Import'), ('api', 'API'), ('form', 'Form'), ('integration', 'Integration'), ('automation', 'Automation')], default='manual', max_length=50)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MailingList',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('list_type', models.CharField(choices=[('static', 'Static'), ('dynamic', 'Dynamic'), ('smart', 'Smart')], default='static', max_length=30)),
                ('subscriber_count', models.IntegerField(default=0)),
                ('is_public', models.BooleanField(default=False)),
                ('tags', models.JSONField(default=list)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brands_core.brand')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('subscribers', models.ManyToManyField(blank=True, through='mailing_lists_core.ListMembership', to='mailing_contacts_core.emailsubscriber')),
            ],
        ),
        migrations.AddField(
            model_name='listmembership',
            name='mailing_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mailing_lists_core.mailinglist'),
        ),
        migrations.AddField(
            model_name='listmembership',
            name='subscriber',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mailing_contacts_core.emailsubscriber'),
        ),
        migrations.AddIndex(
            model_name='mailinglist',
            index=models.Index(fields=['list_type', 'brand'], name='mailing_lis_list_ty_b0ad4e_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='mailinglist',
            unique_together={('name', 'brand')},
        ),
        migrations.AlterUniqueTogether(
            name='listmembership',
            unique_together={('mailing_list', 'subscriber')},
        ),
    ]

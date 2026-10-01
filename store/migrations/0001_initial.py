

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('brand', models.CharField(blank=True, max_length=150)),
                ('category', models.CharField(blank=True, max_length=300)),
                ('description', models.TextField(blank=True)),
                ('tags', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('image_url', models.URLField(blank=True, max_length=600)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('view', 'View'), ('like', 'Like')], default='view', max_length=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='store.product')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]

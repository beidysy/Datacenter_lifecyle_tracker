# Generated by Django 5.1.2 on 2024-10-24 06:56

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0005_merge_20241024_0256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newinventory',
            name='product_id',
            field=models.CharField(default=uuid.uuid4, max_length=100, unique=True),
        ),
    ]

"""
-- AMW Django ERP - Migration --
Add unique constraint to slug fields and remove old code fields.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("security", "0002_add_slug_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="department",
            name="slug",
            field=models.SlugField(blank=True, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="policy",
            name="slug",
            field=models.SlugField(blank=True, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="role",
            name="slug",
            field=models.SlugField(blank=True, max_length=50, unique=True),
        ),
        migrations.RemoveField(
            model_name="department",
            name="code",
        ),
        migrations.RemoveField(
            model_name="policy",
            name="code",
        ),
        migrations.RemoveField(
            model_name="role",
            name="code",
        ),
    ]

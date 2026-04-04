"""
-- AMW Django ERP - Migration --
Add unique constraint to slug fields and remove old code field.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("purchasing", "0002_add_slug_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="suppliercategory",
            name="slug",
            field=models.SlugField(blank=True, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="supplier",
            name="slug",
            field=models.SlugField(blank=True, max_length=50, unique=True),
        ),
        migrations.RemoveField(
            model_name="suppliercategory",
            name="code",
        ),
    ]

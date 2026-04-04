"""
-- AMW Django ERP - Migration --
Add unique constraint to slug fields and remove old code field from Category.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0003_add_slug_fields"),
    ]

    operations = [
        # Add unique constraint to slug fields
        migrations.AlterField(
            model_name="category",
            name="slug",
            field=models.SlugField(blank=True, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="slug",
            field=models.SlugField(blank=True, max_length=50, unique=True),
        ),
        # Remove old code field from Category
        migrations.RemoveField(
            model_name="category",
            name="code",
        ),
    ]

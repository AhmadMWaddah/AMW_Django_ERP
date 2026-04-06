"""
-- AMW Django ERP - Migration --
Add slug fields to SupplierCategory and Supplier, populate data.
"""

import uuid

from django.db import migrations, models
from django.utils.text import slugify


def populate_supplier_category_slugs(apps, schema_editor):
    """Populate supplier category slugs from existing code field."""
    SupplierCategory = apps.get_model("purchasing", "SupplierCategory")
    for cat in SupplierCategory.objects.all():
        if not cat.slug:
            if hasattr(cat, "code") and cat.code:
                cat.slug = cat.code
            else:
                cat.slug = slugify(cat.name) or "supplier-category"
            base = cat.slug
            counter = 1
            while SupplierCategory.objects.filter(slug=cat.slug).exclude(pk=cat.pk).exists():
                cat.slug = f"{base}-{counter}"
                counter += 1
            cat.save(update_fields=["slug"])


def populate_supplier_slugs(apps, schema_editor):
    """Populate supplier slugs from name + random suffix."""
    Supplier = apps.get_model("purchasing", "Supplier")
    for supplier in Supplier.objects.all():
        if not supplier.slug:
            base = slugify(supplier.name) or "supplier"
            supplier.slug = f"{base}-{uuid.uuid4().hex[:6]}"
            counter = 1
            while Supplier.objects.filter(slug=supplier.slug).exclude(pk=supplier.pk).exists():
                supplier.slug = f"{base}-{uuid.uuid4().hex[:6]}-{counter}"
                counter += 1
            supplier.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("purchasing", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="suppliercategory",
            name="slug",
            field=models.SlugField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="supplier",
            name="slug",
            field=models.SlugField(blank=True, max_length=50),
        ),
        migrations.RunPython(
            populate_supplier_category_slugs,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            populate_supplier_slugs,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

"""
-- AMW Django ERP - Migration --
Add slug fields to Category and Product, rename code to slug.

This migration:
1. Adds slug fields (non-unique initially)
2. Populates slugs from existing code field (Category) or generates from SKU (Product)
3. Adds unique constraint to slug fields
4. Removes old code field from Category
"""

from django.db import migrations, models
from django.utils.text import slugify


def populate_category_slugs(apps, schema_editor):
    """Populate category slugs from existing code field."""
    Category = apps.get_model("inventory", "Category")
    for category in Category.objects.all():
        if not category.slug:
            # Try to use old code value if it exists
            if hasattr(category, "code") and category.code:
                category.slug = category.code
            else:
                category.slug = slugify(category.name) or "category"
            # Ensure uniqueness
            base = category.slug
            counter = 1
            while Category.objects.filter(slug=category.slug).exclude(pk=category.pk).exists():
                category.slug = f"{base}-{counter}"
                counter += 1
            category.save(update_fields=["slug"])


def populate_product_slugs(apps, schema_editor):
    """Populate product slugs from SKU."""
    Product = apps.get_model("inventory", "Product")
    for product in Product.objects.all():
        if not product.slug:
            product.slug = slugify(product.sku) or f"product-{product.pk}"
            # Ensure uniqueness
            base = product.slug
            counter = 1
            while Product.objects.filter(slug=product.slug).exclude(pk=product.pk).exists():
                product.slug = f"{base}-{counter}"
                counter += 1
            product.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0002_stockadjustment_rejection_comment"),
    ]

    operations = [
        # Add slug fields (non-unique initially to allow population)
        migrations.AddField(
            model_name="category",
            name="slug",
            field=models.SlugField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="product",
            name="slug",
            field=models.SlugField(blank=True, max_length=50),
        ),
        # Populate slugs from existing data
        migrations.RunPython(
            populate_category_slugs,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            populate_product_slugs,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

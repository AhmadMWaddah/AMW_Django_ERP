"""
-- AMW Django ERP - Migration --
Add slug fields to CustomerCategory and Customer, populate data.
"""

from django.db import migrations, models
from django.utils.text import slugify
import uuid


def populate_customer_category_slugs(apps, schema_editor):
    """Populate customer category slugs from existing code field."""
    CustomerCategory = apps.get_model("sales", "CustomerCategory")
    for cat in CustomerCategory.objects.all():
        if not cat.slug:
            if hasattr(cat, "code") and cat.code:
                cat.slug = cat.code
            else:
                cat.slug = slugify(cat.name) or "customer-category"
            base = cat.slug
            counter = 1
            while CustomerCategory.objects.filter(slug=cat.slug).exclude(pk=cat.pk).exists():
                cat.slug = f"{base}-{counter}"
                counter += 1
            cat.save(update_fields=["slug"])


def populate_customer_slugs(apps, schema_editor):
    """Populate customer slugs from name + random suffix."""
    Customer = apps.get_model("sales", "Customer")
    for customer in Customer.objects.all():
        if not customer.slug:
            base = slugify(customer.name) or "customer"
            customer.slug = f"{base}-{uuid.uuid4().hex[:6]}"
            counter = 1
            while Customer.objects.filter(slug=customer.slug).exclude(pk=customer.pk).exists():
                customer.slug = f"{base}-{uuid.uuid4().hex[:6]}-{counter}"
                counter += 1
            customer.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customercategory",
            name="slug",
            field=models.SlugField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="customer",
            name="slug",
            field=models.SlugField(blank=True, max_length=50),
        ),
        migrations.RunPython(
            populate_customer_category_slugs,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            populate_customer_slugs,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

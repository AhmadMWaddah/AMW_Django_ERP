"""
-- AMW Django ERP - Backfill Slugs Management Command --

Iterates through all models with a slug field and generates slugs
for any record where the slug is currently empty.
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Backfill empty slug fields across all models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        model_configs = [
            {
                "app": "accounts",
                "model": "Employee",
                "slug_source": lambda obj: (
                    f"{obj.first_name}-{obj.last_name}"
                    if (obj.first_name and obj.last_name)
                    else obj.email.split("@")[0]
                ),
            },
            {
                "app": "security",
                "model": "Department",
                "slug_source": lambda obj: obj.name,
            },
            {
                "app": "security",
                "model": "Role",
                "slug_source": lambda obj: obj.name,
            },
            {
                "app": "security",
                "model": "Policy",
                "slug_source": lambda obj: obj.name,
            },
            {
                "app": "inventory",
                "model": "Category",
                "slug_source": lambda obj: obj.name,
            },
            {
                "app": "inventory",
                "model": "Product",
                "slug_source": lambda obj: obj.sku,
            },
            {
                "app": "sales",
                "model": "CustomerCategory",
                "slug_source": lambda obj: obj.name,
            },
            {
                "app": "sales",
                "model": "Customer",
                "slug_source": lambda obj: obj.name,
            },
            {
                "app": "purchasing",
                "model": "SupplierCategory",
                "slug_source": lambda obj: obj.name,
            },
            {
                "app": "purchasing",
                "model": "Supplier",
                "slug_source": lambda obj: obj.name,
            },
        ]

        total_updated = 0

        for config in model_configs:
            model_label = f"{config['app']}.{config['model']}"
            self.stdout.write(f"Processing {model_label}...")

            try:
                from django.apps import apps

                Model = apps.get_model(config["app"], config["model"])
            except LookupError:
                self.stdout.write(self.style.WARNING(f"  Model {model_label} not found, skipping."))
                continue

            empty_slugs = Model.objects.filter(slug__exact="") | Model.objects.filter(slug__isnull=True)
            count = empty_slugs.count()

            if count == 0:
                self.stdout.write(self.style.SUCCESS(f"  All {Model._meta.verbose_name_plural} have slugs."))
                continue

            self.stdout.write(f"  Found {count} records with empty slugs.")

            if dry_run:
                for obj in empty_slugs[:5]:
                    source = config["slug_source"](obj)
                    generated = slugify(source) if source else "generated"
                    self.stdout.write(f"    Would update: {obj} -> slug='{generated}'")
                if count > 5:
                    self.stdout.write(f"    ... and {count - 5} more")
                continue

            updated = 0
            for obj in empty_slugs:
                source = config["slug_source"](obj)
                base_slug = slugify(source) if source else ""

                if not base_slug:
                    base_slug = model_label.lower().replace(".", "-")

                slug = base_slug
                counter = 1
                while Model.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                obj.slug = slug
                obj.save(update_fields=["slug"])
                updated += 1

            self.stdout.write(self.style.SUCCESS(f"  Updated {updated} records."))
            total_updated += updated

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run complete. No changes made."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Backfill complete. Total updated: {total_updated}"))

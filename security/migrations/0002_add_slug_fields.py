"""
-- AMW Django ERP - Migration --
Add slug fields to Department, Policy, and Role models.
"""

from django.db import migrations, models
from django.utils.text import slugify


def populate_department_slugs(apps, schema_editor):
    Department = apps.get_model("security", "Department")
    for dept in Department.objects.all():
        if not dept.slug:
            if hasattr(dept, "code") and dept.code:
                dept.slug = dept.code
            else:
                dept.slug = slugify(dept.name) or "department"
            base = dept.slug
            counter = 1
            while Department.objects.filter(slug=dept.slug).exclude(pk=dept.pk).exists():
                dept.slug = f"{base}-{counter}"
                counter += 1
            dept.save(update_fields=["slug"])


def populate_policy_slugs(apps, schema_editor):
    Policy = apps.get_model("security", "Policy")
    for policy in Policy.objects.all():
        if not policy.slug:
            if hasattr(policy, "code") and policy.code:
                policy.slug = policy.code
            else:
                policy.slug = slugify(policy.name) or "policy"
            base = policy.slug
            counter = 1
            while Policy.objects.filter(slug=policy.slug).exclude(pk=policy.pk).exists():
                policy.slug = f"{base}-{counter}"
                counter += 1
            policy.save(update_fields=["slug"])


def populate_role_slugs(apps, schema_editor):
    Role = apps.get_model("security", "Role")
    for role in Role.objects.all():
        if not role.slug:
            if hasattr(role, "code") and role.code:
                role.slug = role.code
            else:
                role.slug = slugify(role.name) or "role"
            base = role.slug
            counter = 1
            while Role.objects.filter(slug=role.slug).exclude(pk=role.pk).exists():
                role.slug = f"{base}-{counter}"
                counter += 1
            role.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("security", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="department",
            name="slug",
            field=models.SlugField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="policy",
            name="slug",
            field=models.SlugField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="role",
            name="slug",
            field=models.SlugField(blank=True, max_length=50),
        ),
        migrations.RunPython(
            populate_department_slugs,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            populate_policy_slugs,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            populate_role_slugs,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

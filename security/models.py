"""
-- AMW Django ERP - Security/IAM Models --

Constitution Section 6.3: IAM Strategy
- Employee -> Department -> Role -> Policies
- Policy checks must be reusable from Python code

Models:
- Department: Organizational units (hierarchical)
- Role: Job functions within departments
- Policy: Permission rules (allow/deny actions)
"""

from django.db import models
from django.utils.text import slugify


class Department(models.Model):
    """
    Department model for organizational hierarchy.
    
    Supports parent-child relationships for department structures.
    Example: IT -> Backend, IT -> Frontend, HR -> Recruitment
    """
    
    name = models.CharField(max_length=100, unique=True)
    code = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text='Parent department (for hierarchical structure)'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_all_children(self):
        """Get all descendant departments recursively."""
        children = list(self.children.all())
        for child in self.children.all():
            children.extend(child.get_all_children())
        return children


class Policy(models.Model):
    """
    Policy model for defining permissions.
    
    Policies are atomic permission rules that can be attached to roles.
    Example: 'inventory.stock_adjust', 'sales.order.create'
    """
    
    EFFECT_CHOICES = [
        ('allow', 'Allow'),
        ('deny', 'Deny'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    code = models.SlugField(unique=True, blank=True)
    description = models.TextField(
        blank=True,
        help_text='What this policy permits or denies'
    )
    effect = models.CharField(
        max_length=10,
        choices=EFFECT_CHOICES,
        default='allow',
        help_text='Allow or Deny this action'
    )
    resource = models.CharField(
        max_length=100,
        help_text='Resource pattern (e.g., inventory.*, sales.order.*)'
    )
    action = models.CharField(
        max_length=100,
        help_text='Action pattern (e.g., create, read, update, delete)'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_policies'
        verbose_name = 'Policy'
        verbose_name_plural = 'Policies'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.effect})"
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name)
        super().save(*args, **kwargs)
    
    def matches(self, resource, action):
        """
        Check if this policy matches a given resource and action.
        Supports wildcard patterns (*).
        """
        import fnmatch
        
        resource_match = fnmatch.fnmatch(resource, self.resource)
        action_match = fnmatch.fnmatch(action, self.action)
        
        return resource_match and action_match


class Role(models.Model):
    """
    Role model for grouping policies.
    
    Roles are assigned to employees and grant them the policies attached to the role.
    Each role belongs to a department.
    """
    
    name = models.CharField(max_length=100)
    code = models.SlugField(unique=True, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='roles',
        help_text='Department this role belongs to'
    )
    policies = models.ManyToManyField(
        Policy,
        related_name='roles',
        help_text='Policies granted by this role'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        unique_together = ['department', 'name']
        ordering = ['department__name', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.department.name})"
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_all_policies(self):
        """Get all policies for this role."""
        return self.policies.filter(is_active=True)

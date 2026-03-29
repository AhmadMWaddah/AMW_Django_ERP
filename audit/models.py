"""
-- AMW Django ERP - Audit Models --

Constitution Section 6.7: Audit Rule
- Business-critical state changes must be logged
- Audit records must capture: actor, action, target, timestamp, before/after data
"""

import json
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """
    Centralized audit log for all business-critical operations.
    
    Captures:
    - Actor: Who performed the action
    - Action: What operation was performed
    - Target: What object/resource was affected
    - Timestamp: When it happened
    - Before/After: State changes (for updates)
    """
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('read', 'Read'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('adjust', 'Adjust'),
        ('transfer', 'Transfer'),
        ('other', 'Other'),
    ]
    
    # -- Actor Information --
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text='Employee who performed the action'
    )
    actor_email = models.EmailField(
        blank=True,
        help_text='Email backup (in case user is deleted)'
    )
    actor_name = models.CharField(
        max_length=200,
        blank=True,
        help_text='Name backup (in case user is deleted)'
    )
    
    # -- Action Information --
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        help_text='Type of action performed'
    )
    action_code = models.CharField(
        max_length=100,
        help_text='Machine-readable action code (e.g., inventory.stock.adjust)'
    )
    action_description = models.TextField(
        blank=True,
        help_text='Human-readable description of the action'
    )
    
    # -- Target Information --
    content_type = models.CharField(
        max_length=100,
        help_text='Type of object affected (e.g., inventory.Product)'
    )
    object_id = models.CharField(
        max_length=100,
        help_text='ID of the object affected'
    )
    object_repr = models.CharField(
        max_length=300,
        help_text='String representation of the object'
    )
    
    # -- State Changes --
    before_data = models.JSONField(
        null=True,
        blank=True,
        help_text='State before the change (for updates/deletes)'
    )
    after_data = models.JSONField(
        null=True,
        blank=True,
        help_text='State after the change (for creates/updates)'
    )
    
    # -- Metadata --
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text='When the action occurred'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the request'
    )
    user_agent = models.TextField(
        blank=True,
        help_text='User agent string from request'
    )
    extra_data = models.JSONField(
        null=True,
        blank=True,
        help_text='Additional context-specific data'
    )
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['actor', '-timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action_code} by {self.actor_name} at {self.timestamp}"
    
    def save(self, *args, **kwargs):
        # Auto-populate backup fields from actor
        if self.actor and not self.actor_email:
            self.actor_email = self.actor.email
        if self.actor and not self.actor_name:
            self.actor_name = str(self.actor)
        super().save(*args, **kwargs)
    
    @classmethod
    def log_action(cls, actor, action_code, action, content_type, object_id, 
                   object_repr, before_data=None, after_data=None, 
                   ip_address=None, user_agent=None, extra_data=None):
        """
        Convenience method to create an audit log entry.
        
        Usage:
            AuditLog.log_action(
                actor=request.user,
                action_code='inventory.stock.adjust',
                action='adjust',
                content_type='inventory.Product',
                object_id=product.id,
                object_repr=str(product),
                before_data={'quantity': old_qty},
                after_data={'quantity': new_qty},
                ip_address=request.META.get('REMOTE_ADDR'),
            )
        """
        return cls.objects.create(
            actor=actor,
            action_code=action_code,
            action=action,
            content_type=content_type,
            object_id=object_id,
            object_repr=object_repr,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=extra_data,
        )

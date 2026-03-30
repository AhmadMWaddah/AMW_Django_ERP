"""
-- AMW Django ERP - Audit Logging Utilities --

Constitution Section 6.7: Business-critical state changes must be logged.

Usage:
    from audit.logic.logging import audit_operation

    @audit_operation(action_code='inventory.stock.adjust', action='adjust')
    def adjust_stock(employee, product, quantity):
        # Operation logic
        pass
"""

import functools

from audit.models import AuditLog


def audit_operation(action_code, action="other", get_target=None, get_before_state=None, get_after_state=None):
    """
    Decorator to automatically log operations to audit log.

    Usage:
        @audit_operation(
            action_code='inventory.stock.adjust',
            action='adjust',
            get_target=lambda result: result,  # Get target from function result
            get_before_state=lambda product: {'quantity': product.quantity},  # Capture before
            get_after_state=lambda product: {'quantity': product.quantity}  # Capture after
        )
        def adjust_stock(employee, product, quantity):
            # Operation logic
            return product  # Return the modified target

    Args:
        action_code: Machine-readable action code
        action: Action type (create, update, delete, etc.)
        get_target: Function to extract target object from RESULT (not args)
        get_before_state: Optional function to capture state BEFORE operation (receives args)
        get_after_state: Optional function to capture state AFTER operation (receives result)

    Returns:
        Decorated function with audit logging
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract employee/actor from args
            actor = None
            for arg in args:
                if hasattr(arg, "is_authenticated"):
                    actor = arg
                    break

            # Capture BEFORE state if provided
            before_data = None
            if get_before_state:
                try:
                    before_data = get_before_state(*args, **kwargs)
                except Exception as e:
                    before_data = {"error": f"Failed to capture before state: {str(e)}"}

            # Execute operation
            result = func(*args, **kwargs)

            # Log to audit
            if actor:
                # Extract target from RESULT (not args)
                target = None
                if get_target:
                    try:
                        target = get_target(result)
                    except Exception:
                        target = None

                # Capture AFTER state if provided
                after_data = None
                if get_after_state and target:
                    try:
                        after_data = get_after_state(target)
                    except Exception as e:
                        after_data = {"error": f"Failed to capture after state: {str(e)}"}

                # Create audit log
                AuditLog.log_action(
                    actor=actor,
                    action_code=action_code,
                    action=action,
                    content_type=target.__class__.__name__ if target else "Unknown",
                    object_id=str(getattr(target, "id", "unknown")) if target and hasattr(target, "id") else "unknown",
                    object_repr=str(target) if target else "Unknown",
                    before_data=before_data,
                    after_data=after_data if after_data else serialize_for_audit(target),
                )

            return result

        return wrapper

    return decorator


def serialize_for_audit(obj):
    """
    Serialize an object for audit logging.

    Args:
        obj: Object to serialize (Model instance, dict, or primitive)

    Returns:
        dict or None: Serialized data suitable for JSON storage
    """
    from datetime import date, datetime
    from decimal import Decimal

    if obj is None:
        return None

    # Django Model
    if hasattr(obj, "__class__") and hasattr(obj, "__dict__"):
        from django.db import models

        if isinstance(obj, models.Model):
            data = {
                "id": obj.id,
                "__class__": obj.__class__.__name__,
            }
            # Add all field values
            for field in obj._meta.fields:
                value = getattr(obj, field.name, None)
                # Handle datetime/date values (convert to ISO format string)
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif isinstance(value, date):
                    value = value.isoformat()
                # Handle Decimal values (convert to string)
                elif isinstance(value, Decimal):
                    value = str(value)
                data[field.name] = value
            return data

    # Dictionary - recursively serialize values
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            if isinstance(v, datetime):
                result[k] = v.isoformat()
            elif isinstance(v, date):
                result[k] = v.isoformat()
            elif isinstance(v, Decimal):
                result[k] = str(v)
            elif isinstance(v, (str, int, float, bool, type(None))):
                result[k] = v
            else:
                result[k] = str(v)
        return result

    # Primitive - handle datetime/date/decimal
    if isinstance(obj, datetime):
        return {"value": obj.isoformat()}
    elif isinstance(obj, date):
        return {"value": obj.isoformat()}
    elif isinstance(obj, Decimal):
        return {"value": str(obj)}

    # Default: convert to string
    return {"value": str(obj)}


def log_audit(actor, action_code, action, target, before=None, after=None, **extra):
    """
    Convenience function to log an audit entry.

    Usage:
        log_audit(
            actor=request.user,
            action_code='sales.order.confirm',
            action='approve',
            target=order,
            before_data={'status': 'draft'},
            after_data={'status': 'confirmed'}
        )

    Args:
        actor: Employee who performed the action
        action_code: Machine-readable action code
        action: Action type
        target: Target object
        before: State before (dict or object)
        after: State after (dict or object)
        **extra: Additional data to store

    Returns:
        AuditLog instance
    """
    return AuditLog.log_action(
        actor=actor,
        action_code=action_code,
        action=action,
        content_type=target.__class__.__name__ if target else "Unknown",
        object_id=getattr(target, "id", None),
        object_repr=str(target) if target else "Unknown",
        before_data=serialize_for_audit(before),
        after_data=serialize_for_audit(after),
        extra_data=extra if extra else None,
    )

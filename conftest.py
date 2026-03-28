"""
-- AMW Django ERP - pytest Configuration --

This file provides pytest fixtures and configuration for the test suite.
"""

import pytest
from django.conf import settings


@pytest.fixture
def test_user(django_user_model):
    """
    Create a test user for authentication tests.
    Note: This will be updated when Employee model is implemented in Phase 2.
    """
    return django_user_model.objects.create_user(username="testuser", password="testpass123", email="test@example.com")


@pytest.fixture
def test_settings():
    """
    Provide test-specific settings overrides.
    """
    original_settings = {}

    def _override_settings(**kwargs):
        for key, value in kwargs.items():
            original_settings[key] = getattr(settings, key, None)
            setattr(settings, key, value)
        return settings

    yield _override_settings

    # Restore original settings
    for key, value in original_settings.items():
        if value is None:
            delattr(settings, key)
        else:
            setattr(settings, key, value)

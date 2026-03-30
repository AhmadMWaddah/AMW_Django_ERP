# This package contains environment-specific settings modules.
#
# Structure:
#   - base.py:   Common settings shared across all environments
#   - dev.py:    Development-specific settings (debug, dev tools)
#   - prod.py:   Production-specific settings (security, performance)
#
# Usage:
#   export DJANGO_SETTINGS_MODULE=config.settings.dev
#   python manage.py runserver

"""Empty placeholder loader so {% load url_active %} succeeds.

We previously used a custom template tag for active-link styling but moved that
logic inline. The empty file is kept so existing templates don't break and so
the namespace is reserved for future helpers.
"""

from __future__ import annotations

from django import template

register = template.Library()

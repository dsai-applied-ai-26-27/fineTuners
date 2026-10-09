"""Template helpers. Loaded in a template with `{% load ui %}`.

A custom tag or filter is an ordinary function registered on a `Library`. They must return
safe HTML themselves: `format_html` escapes every argument it interpolates, which is why it
is used here instead of building strings by hand.
"""

import re

from django import template
from django.templatetags.static import static
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def icon(name, extra=""):
    """{% icon "search" %} -> an <svg> that points into the icon sprite."""
    return format_html(
        '<svg class="icon {}" aria-hidden="true"><use href="{}#{}"></use></svg>',
        extra,
        static("icons.svg"),
        name,
    )


@register.filter
def highlight(text, query):
    """Wrap each occurrence of `query` in <mark>. Escapes first, then adds the one tag."""
    escaped = conditional_escape(text)
    if not query:
        return escaped
    pattern = re.compile(re.escape(conditional_escape(query)), re.IGNORECASE)
    return mark_safe(pattern.sub(lambda match: f"<mark>{match.group(0)}</mark>", escaped))  # noqa: S308


@register.filter
def trim_zero(value):
    """10.0 -> 10, 2.5 -> 2.5. For points."""
    if value is None:
        return ""
    return f"{value:g}"


@register.filter
def letter(index):
    """0 -> A, 1 -> B. For labelling choices."""
    return chr(ord("A") + int(index))


@register.inclusion_tag("components/topic_chips.html")
def topic_chips(course, topics):
    """Renders a template with its own small context: the pattern for reusable fragments
    that need a little logic."""
    return {"course": course, "topics": topics}

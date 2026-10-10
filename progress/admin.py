"""Progress in the admin: for looking, not for editing.

These rows are written only by `progress.sync`. A grade changed by hand here would be
overwritten, or would overwrite the person's own, depending on its timestamp; neither is
what anyone wants. To remove someone's progress, delete their user: it cascades.
"""

from django.contrib import admin

from catalog.admin import ReadOnlyAdmin

from . import models


@admin.register(models.Record)
class RecordAdmin(ReadOnlyAdmin):
    list_display = ["user", "course", "key", "state", "streak", "count", "version"]
    list_filter = ["state", "course"]
    search_fields = ["key", "user__email", "user__username"]
    list_select_related = ["user"]


@admin.register(models.Attempt)
class AttemptAdmin(ReadOnlyAdmin):
    list_display = ["user", "course", "paper", "score", "max_score", "seconds"]
    list_filter = ["course"]
    search_fields = ["paper", "user__email", "user__username"]
    list_select_related = ["user"]


@admin.register(models.Day)
class DayAdmin(ReadOnlyAdmin):
    list_display = ["user", "day", "cards", "minutes"]
    date_hierarchy = "day"
    list_select_related = ["user"]


@admin.register(models.Ledger)
class LedgerAdmin(ReadOnlyAdmin):
    list_display = ["user", "version", "updated_at"]
    list_select_related = ["user"]

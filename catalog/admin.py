"""Admin as a content inspector.

The database is rebuilt from the files under courses/ by `manage.py sync_content`, so editing
a row here would be undone by the next sync. Every model is therefore registered read-only:
you can browse, filter and search what the importer produced, but not change it.
"""

from django.contrib import admin

from . import models

admin.site.site_header = "dsai.pages content"
admin.site.site_title = "dsai.pages"
admin.site.index_title = (
    "Read-only. Edit the files under courses/, then run: manage.py sync_content"
)


class ReadOnlyAdmin(admin.ModelAdmin):
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.Course)
class CourseAdmin(ReadOnlyAdmin):
    list_display = ["code", "title", "year", "status", "hue", "synced_at"]
    list_filter = ["status", "year"]
    search_fields = ["title", "code", "slug"]


@admin.register(models.Topic)
class TopicAdmin(ReadOnlyAdmin):
    list_display = ["title", "key", "course", "order"]
    list_filter = ["course"]
    search_fields = ["title", "key"]


@admin.register(models.Document)
class DocumentAdmin(ReadOnlyAdmin):
    list_display = ["title", "kind", "number", "course", "status", "date", "reading_minutes"]
    list_filter = ["course", "kind", "status"]
    search_fields = ["title", "slug", "search_text"]


class CardInline(admin.TabularInline):
    model = models.Card
    fields = ["key", "kind", "high_yield", "topic"]
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(models.Deck)
class DeckAdmin(ReadOnlyAdmin):
    list_display = ["title", "slug", "course", "topic", "lecture"]
    list_filter = ["course"]
    search_fields = ["title", "slug"]
    inlines = [CardInline]


@admin.register(models.Card)
class CardAdmin(ReadOnlyAdmin):
    list_display = ["key", "kind", "deck", "course", "topic", "high_yield"]
    list_filter = ["course", "kind", "high_yield"]
    search_fields = ["key", "search_text"]


@admin.register(models.Assessment)
class AssessmentAdmin(ReadOnlyAdmin):
    list_display = ["title", "kind", "course", "date"]
    list_filter = ["course", "kind"]
    search_fields = ["title", "slug"]


@admin.register(models.QuestionSet)
class QuestionSetAdmin(ReadOnlyAdmin):
    list_display = ["title", "kind", "course", "assessment", "duration_min", "total_points"]
    list_filter = ["course", "kind"]
    search_fields = ["title", "slug"]


@admin.register(models.Question)
class QuestionAdmin(ReadOnlyAdmin):
    list_display = ["key", "number", "kind", "question_set", "course", "points", "topic"]
    list_filter = ["course", "kind"]
    search_fields = ["key", "title", "search_text"]


@admin.register(models.FormulaSection)
class FormulaSectionAdmin(ReadOnlyAdmin):
    list_display = ["title", "course", "topic"]
    list_filter = ["course"]


@admin.register(models.Formula)
class FormulaAdmin(ReadOnlyAdmin):
    list_display = ["name", "key", "section", "course"]
    list_filter = ["course"]
    search_fields = ["name", "key", "search_text"]


@admin.register(models.Term)
class TermAdmin(ReadOnlyAdmin):
    list_display = ["term", "key", "course", "topic"]
    list_filter = ["course"]
    search_fields = ["term", "key", "search_text"]


@admin.register(models.Hook)
class HookAdmin(ReadOnlyAdmin):
    list_display = ["target", "kind", "key", "course", "topic", "card"]
    list_filter = ["course", "kind"]
    search_fields = ["target", "key", "search_text"]


class LocusInline(admin.TabularInline):
    model = models.Locus
    fields = ["order", "key", "place"]
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(models.Palace)
class PalaceAdmin(ReadOnlyAdmin):
    list_display = ["title", "slug", "course", "topic"]
    list_filter = ["course"]
    inlines = [LocusInline]

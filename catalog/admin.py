"""Admin as a content inspector.

The database is rebuilt from the files under courses/ by `manage.py sync_content`, so editing
a row here would be undone by the next sync. Every model is therefore registered read-only:
you can browse, filter and search what the importer produced, but not change it.

One thing about a course is decided here and not in its files: whether students see it,
and whether it asks for an educator. Those are actions on the Courses list. They do not
touch the course row; they write the owner's switch for it (desk.CourseSetting), which
survives every sync.
"""

from django.contrib import admin, messages
from django.db.models import Count, OuterRef, Subquery

from desk.models import CourseSetting, Educator

from . import models

admin.site.site_header = "DSAI Vault admin"
admin.site.site_title = "DSAI Vault"
admin.site.index_title = (
    "People are under Users; what they send is under Requests and educators. "
    "Course content is read-only here: edit the files under courses/, then run "
    "manage.py sync_content"
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
    list_display = ["code", "title", "semester", "year", "status", "visibility", "writer"]
    list_filter = ["status", "semester", "year", "enabled"]
    search_fields = ["title", "code", "slug"]
    actions = ["open_course", "close_course", "has_writer", "needs_writer", "follow_file"]

    def get_queryset(self, request):
        # The switch and the educators of each course, fetched with the list itself. A
        # course is tied to them by its series (text), not by a foreign key, so the join
        # is written out as subqueries: "the setting whose series is this row's series".
        setting = CourseSetting.objects.filter(series=OuterRef("series"))
        educators = Educator.objects.filter(series=OuterRef("series")).order_by()
        return (
            super()
            .get_queryset(request)
            .annotate(
                switch_enabled=Subquery(setting.values("enabled")[:1]),
                switch_educator=Subquery(setting.values("has_educator")[:1]),
                n_educators=Subquery(
                    educators.values("series").annotate(n=Count("pk")).values("n")
                ),
                an_educator=Subquery(educators.values("user__email")[:1]),
            )
        )

    @admin.display(description="Students see it", ordering="enabled")
    def visibility(self, course):
        if course.switch_enabled is None:
            return "Yes" if course.enabled else "No (course file)"
        return "Yes (set here)" if course.switch_enabled else "No (set here)"

    @admin.display(description="Written by")
    def writer(self, course):
        if course.switch_educator is False:
            return "Asks for an educator (set here)"
        names = course.an_educator or ""
        if (course.n_educators or 0) > 1:
            names += f" and {course.n_educators - 1} more"
        if names:
            return names
        if course.switch_educator:
            return "Someone (set here)"
        return "Someone (course file)" if course.has_educator else "Nobody: asks for an educator"

    # -- the switches -----------------------------------------------------------------------
    # An action receives the ticked rows as a queryset. A switch belongs to a series, so
    # ticking one year of a course switches every year of it.

    def _switch(self, request, queryset, **values):
        series = sorted(set(queryset.values_list("series", flat=True)))
        for name in series:
            # update_or_create: change the row if the series has one, else make it.
            CourseSetting.objects.update_or_create(series=name, defaults=values)
        return len(series)

    def _say(self, request, count, what):
        self.message_user(
            request, f"{count} course{'' if count == 1 else 's'} {what}.", messages.SUCCESS
        )

    @admin.action(description="Open to students")
    def open_course(self, request, queryset):
        self._say(request, self._switch(request, queryset, enabled=True), "opened to students")

    @admin.action(description="Close: hide from students")
    def close_course(self, request, queryset):
        self._say(request, self._switch(request, queryset, enabled=False), "hidden from students")

    @admin.action(description="Someone writes it: stop asking for an educator")
    def has_writer(self, request, queryset):
        count = self._switch(request, queryset, has_educator=True)
        self._say(request, count, "no longer asking for an educator")

    @admin.action(description="Ask for an educator on its page")
    def needs_writer(self, request, queryset):
        count = self._switch(request, queryset, has_educator=False)
        self._say(request, count, "now asking for an educator")

    @admin.action(description="Clear my switches: follow the course file again")
    def follow_file(self, request, queryset):
        series = set(queryset.values_list("series", flat=True))
        CourseSetting.objects.filter(series__in=series).delete()
        self._say(request, len(series), "following the course file again")


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

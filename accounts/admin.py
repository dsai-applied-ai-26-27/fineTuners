"""People in the admin: who has an account, what they have studied, and the few things an
administrator may do to them.

Django registers its own admin for the user model. It is replaced here by a narrower one:

- Nobody is added by hand. An account comes into being when someone signs in with Google.
- There is no password to set. The form shows the name, the address and three switches.
- The list and the page of one person show their study progress, read from `progress`.
- Progress is cleared the way a device clears it (`progress.sync.forget`), so the person's
  browsers drop their copies too instead of sending them back.
"""

from datetime import UTC, datetime

from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count, Max, OuterRef, Q, Subquery, Sum
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from progress.models import Attempt, Day, Ledger, Record
from progress.sync import forget

from .models import Enrollment

User = get_user_model()

admin.site.unregister(User)
# Groups hand out permissions to sets of staff. The site has one kind of administrator,
# so the page would only ever be empty.
admin.site.unregister(Group)


def moment(milliseconds):
    """A device's clock reading (milliseconds since 1970) as a date and time, or None."""
    return datetime.fromtimestamp(milliseconds / 1000, UTC) if milliseconds else None


@admin.register(User)
class PersonAdmin(UserAdmin):
    list_display = [
        "email",
        "full_name",
        "date_joined",
        "last_login",
        "graded",
        "last_studied",
        "is_active",
        "is_staff",
    ]
    list_filter = ["is_active", "is_staff"]
    search_fields = ["email", "first_name", "last_name", "username"]
    ordering = ["-date_joined"]
    actions = ["forget_progress"]

    fieldsets = [
        (None, {"fields": ["email", "first_name", "last_name"]}),
        (
            "Access",
            {
                "fields": ["is_active", "is_staff", "is_superuser"],
                "description": "Switching Active off locks the person out without deleting "
                "anything. Staff and Superuser together open this admin.",
            },
        ),
        ("Account", {"fields": ["signs_in_with", "date_joined", "last_login"]}),
        ("Study progress", {"fields": ["courses", "progress"]}),
    ]
    readonly_fields = ["signs_in_with", "date_joined", "last_login", "courses", "progress"]

    # -- what may be done -----------------------------------------------------------------

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        # Your own account is deleted from Settings, where it also signs you out. Here it
        # would be one misplaced tick in a list away.
        if obj is not None and obj == request.user:
            return False
        return super().has_delete_permission(request, obj)

    def get_deleted_objects(self, objs, request):
        # Before deleting, the admin lists everything that goes along by cascade and checks
        # that the administrator may delete each kind. Progress rows are read-only in their
        # own admin pages (progress/admin.py), which would veto deleting anyone who has ever
        # studied. They belong to the person, so here they are allowed to go with them.
        deleted, counts, perms_needed, protected = super().get_deleted_objects(objs, request)
        owned = {model._meta.verbose_name for model in (Record, Attempt, Day, Ledger)}
        return deleted, counts, perms_needed - owned, protected

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj is not None and obj == request.user:
            # Nobody can lock themselves out of the admin by unticking their own box.
            fields += ["is_active", "is_staff", "is_superuser"]
        return fields

    # -- the list ---------------------------------------------------------------------------

    def get_queryset(self, request):
        # Progress rows have no reverse link from the user (related_name="+"), so the counts
        # come from correlated subqueries: for each user row, "the records of *that* user".
        # .values("user") turns the inner query into one group, which Count and Max sum up.
        records = Record.objects.filter(user=OuterRef("pk")).order_by().values("user")
        return (
            super()
            .get_queryset(request)
            .annotate(
                n_graded=Subquery(records.annotate(n=Count("pk")).values("n")),
                last_graded=Subquery(records.annotate(latest=Max("graded_at")).values("latest")),
            )
        )

    @admin.display(description="Name", ordering="first_name")
    def full_name(self, user):
        return user.get_full_name() or "-"

    @admin.display(description="Items graded", ordering="n_graded")
    def graded(self, user):
        return user.n_graded or 0

    @admin.display(description="Last studied", ordering="last_graded")
    def last_studied(self, user):
        return moment(user.last_graded) or "-"

    # -- the page of one person -------------------------------------------------------------

    @admin.display(description="Signs in with")
    def signs_in_with(self, user):
        providers = sorted({account.provider.title() for account in user.socialaccount_set.all()})
        return ", ".join(providers) or "No linked account (a local or development user)"

    @admin.display(description="On their dashboard")
    def courses(self, user):
        return ", ".join(sorted(Enrollment.objects.series_of(user))) or "No course chosen yet."

    @admin.display(description="By course")
    def progress(self, user):
        state = Record.State
        courses = (
            Record.objects.filter(user=user)
            .values("course")
            .annotate(
                solid=Count("pk", filter=Q(state=state.SOLID)),
                shaky=Count("pk", filter=Q(state=state.SHAKY)),
                missed=Count("pk", filter=Q(state=state.MISSED)),
                latest=Max("graded_at"),
            )
            .order_by("course")
        )
        attempts = Attempt.objects.filter(user=user).count()
        days = Day.objects.filter(user=user).aggregate(
            n=Count("pk"), cards=Sum("cards"), minutes=Sum("minutes")
        )
        if not courses and not attempts and not days["n"]:
            return "Nothing stored yet."

        # format_html escapes every value it is given. Course names here were sent by a
        # browser, so they are never pasted into HTML any other way.
        rows = format_html_join(
            "",
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>",
            (
                (
                    row["course"],
                    row["solid"],
                    row["shaky"],
                    row["missed"],
                    f"{moment(row['latest']):%Y-%m-%d %H:%M} UTC",
                )
                for row in courses
            ),
        )
        records_url = reverse("admin:progress_record_changelist")
        return format_html(
            "<table><thead><tr><th>Course</th><th>Solid</th><th>Shaky</th><th>Missed</th>"
            "<th>Last graded</th></tr></thead><tbody>{}</tbody></table>"
            "<p>{} mock exam sitting{}. Active on {} day{}: {} cards, {} minutes of timer.</p>"
            '<p><a href="{}?user__id__exact={}">Every graded item of this person</a></p>',
            rows,
            attempts,
            "" if attempts == 1 else "s",
            days["n"],
            "" if days["n"] == 1 else "s",
            days["cards"] or 0,
            days["minutes"] or 0,
            records_url,
            user.pk,
        )

    # -- actions ----------------------------------------------------------------------------

    @admin.action(description="Clear the study progress of the selected people")
    def forget_progress(self, request, queryset):
        # An action is called twice. First from the list: show a page that asks. Then from
        # that page, which posts the same selection back with `confirmed` added.
        if "confirmed" not in request.POST:
            return TemplateResponse(
                request,
                "admin/accounts/forget_progress.html",
                {
                    **self.admin_site.each_context(request),
                    "title": "Clear study progress?",
                    "people": queryset,
                    "opts": self.model._meta,
                    "action": "forget_progress",
                },
            )
        for user in queryset:
            forget(user)
        count = queryset.count()
        self.message_user(
            request,
            f"Cleared the progress of {count} {'person' if count == 1 else 'people'}. "
            "Their devices drop their own copies the next time they open the site.",
            messages.SUCCESS,
        )
        return None

"""The pages of the desk: Ask or report, and everything about educators."""

from datetime import timedelta
from functools import wraps

from django.conf import settings
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from catalog import editions
from catalog.mine import catalogue
from catalog.models import Course
from catalog.nav import course_data, has_content
from catalog.welcome import educator_state
from ingest import handin, live

from . import handins, kit, notices
from .forms import EducatorApplicationForm, RequestForm
from .models import Educator, EducatorApplication, HandIn, Request
from .notify import notify
from .switches import switches

# The most one person may send in a day. Far above honest use; it keeps one account from
# filling the owner's list (and phone).
DAILY_REQUESTS = 10
# And the most hand-ins. Each one is checked in full and kept.
DAILY_HANDINS = 20


def signed_in(view):
    """These pages write rows that belong to a person. On the open site, where nobody is
    signed in, they lead back to the start."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("catalog:home")
        return view(request, *args, **kwargs)

    return wrapper


def _titles(request):
    """series -> course, for every course a visitor can see."""
    return {course.series: course for course in catalogue(request)}


def _admin_url(request, obj):
    name = f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change"
    return request.build_absolute_uri(reverse(name, args=[obj.pk]))


@signed_in
def ask(request):
    """Ask for content, report a fault, or suggest something. One form for all three."""
    courses = catalogue(request)
    by_series = _titles(request)
    today = Request.objects.filter(
        user=request.user, created_at__gte=timezone.now() - timedelta(days=1)
    ).count()

    if request.method == "POST":
        form = RequestForm(request.POST, courses=courses)
        if today >= DAILY_REQUESTS:
            form.add_error(None, "You have sent a lot today. Come back tomorrow.")
        elif form.is_valid():
            # commit=False: build the row without saving, to add what the form does not
            # carry (who is asking), then save.
            sent = form.save(commit=False)
            sent.user = request.user
            sent.save()
            course = by_series.get(sent.series)
            title = {
                Request.Kind.CONTENT: "New request: content",
                Request.Kind.BUG: "New report: something is wrong",
                Request.Kind.IDEA: "New idea for the site",
            }[sent.kind] + (f" ({course.title})" if course else "")
            url = _admin_url(request, sent)
            # Under the bell: the owner, and for a course whoever writes it. They are
            # told what kind of thing arrived, not by whom.
            notices.tell(
                notices.owners(), title, url=reverse("admin:desk_request_change", args=[sent.pk])
            )
            if course and sent.kind != Request.Kind.IDEA:
                notices.tell(
                    notices.educators_of(sent.series, but=request.user),
                    f"Asked about {course.title}: {sent.get_kind_display().lower()}",
                    url=f"{reverse('desk:educators')}#course-{course.slug}",
                )
            # After the row is safely stored, and never before: see desk/notify.py.
            transaction.on_commit(
                lambda: notify(
                    title,
                    "Sent with Ask or report. Open the admin to read it.",
                    level="warning" if sent.kind == Request.Kind.BUG else "info",
                    url=url,
                    dedupe_key=f"dsai-request-{sent.pk}",
                )
            )
            return redirect(f"{reverse('desk:ask')}?sent=1")
    else:
        slug = request.GET.get("course", "")
        about = next((c for c in courses if c.slug == slug or c.series == slug), None)
        kind = request.GET.get("kind", "")
        form = RequestForm(
            courses=courses,
            initial={
                "kind": kind if kind in Request.Kind.values else Request.Kind.CONTENT,
                "series": about.series if about else "",
                "page": request.GET.get("from", "")[:300],
            },
        )

    mine = list(Request.objects.filter(user=request.user)[:10])
    for item in mine:
        item.course = by_series.get(item.series)
    return render(
        request,
        "desk/ask.html",
        {"form": form, "mine": mine, "sent": "sent" in request.GET, "active": "ask"},
    )


def _seeking(request):
    """Open courses nobody is writing yet: what one can apply for. By semester, then in
    the order of the dashboard."""
    gate = switches(request)
    courses = [course for course in catalogue(request) if not gate.has_educator(course)]
    return sorted(courses, key=lambda c: (c.semester or 99, c.order, c.title))


@signed_in
def apply(request):
    """Offer to write a course. Sending it again for the same course updates the offer."""
    courses = _seeking(request)
    by_series = {course.series: course for course in courses}
    wanted = request.POST.get("series") or request.GET.get("course", "")
    wanted = next((c.series for c in courses if wanted in (c.series, c.slug)), "")
    existing = EducatorApplication.objects.filter(user=request.user, series=wanted).first()
    taken = bool(request.GET.get("course")) and not wanted and request.method == "GET"

    if request.method == "POST":
        form = EducatorApplicationForm(request.POST, instance=existing, courses=courses)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.user = request.user
            if offer.status != EducatorApplication.Status.ACCEPTED:
                offer.status, offer.decided_at = EducatorApplication.Status.PENDING, None
            offer.save()
            course = by_series[offer.series]
            url = _admin_url(request, offer)
            notices.tell(
                notices.owners(),
                f"Educator application: {course.title}",
                url=reverse("admin:desk_educatorapplication_change", args=[offer.pk]),
            )
            transaction.on_commit(
                lambda: notify(
                    f"Educator application: {course.title}",
                    "Someone offers to write this course. Open the admin to read it.",
                    level="success",
                    url=url,
                    dedupe_key=f"dsai-educator-{offer.pk}",
                )
            )
            return redirect(f"{reverse('desk:educators')}?applied=1")
    else:
        initial = {"series": wanted, "name": request.user.get_full_name()}
        form = EducatorApplicationForm(instance=existing, courses=courses, initial=initial)

    return render(
        request,
        "desk/apply.html",
        {"form": form, "existing": existing, "taken": taken, "active": "educators"},
    )


def _written_by(series):
    """The current year of each of these courses, open to students or not."""
    return editions.latest(list(Course.objects.filter(series__in=series)))


def _may_write(user, series):
    return user.is_staff or Educator.objects.filter(user=user, series=series).exists()


def _educators_page(request, *, refused=None):
    """The educators' page: what the role is, the courses you write (how to add to them,
    the form that takes a hand-in, what was added so far, what was asked), your
    applications, and the courses still looking for someone.

    `refused` is (series, Refused) when a hand-in has just been turned down: the page is
    shown again with the reason beside that course.
    """
    by_series = _titles(request)
    writing = []
    series = list(Educator.objects.filter(user=request.user).values_list("series", flat=True))
    asked = Request.objects.filter(series__in=series, status=Request.Status.NEW).exclude(
        kind=Request.Kind.IDEA
    )
    # defer(): the zip of each hand-in stays in the database; a list needs its summary.
    steps = HandIn.objects.filter(series__in=series).defer("archive").select_related("user")
    handed = request.GET.get("handed", "")
    # Their courses are read directly, not from the catalogue: an educator may be
    # writing a course that students cannot see yet.
    for course in _written_by(series):
        name = course.series
        course.counts = course_data(course)["counts"]
        course.ready = has_content(course)
        course.asked = [item for item in asked if item.series == name]
        course.timeline = [step for step in steps if step.series == name][:30]
        # The newest step, if it is on the site and theirs, can be taken back by them.
        newest = next((s for s in course.timeline if s.status == HandIn.Status.LIVE), None)
        course.undo = newest if newest and newest.user_id == request.user.pk else None
        course.handed = next((s for s in course.timeline if str(s.pk) == handed), None)
        course.refused = refused[1] if refused and refused[0] == name else None
        writing.append(course)

    offers = list(EducatorApplication.objects.filter(user=request.user))
    for offer in offers:
        offer.course = by_series.get(offer.series)
    state = educator_state(request.user)
    return render(
        request,
        "desk/educators.html",
        {
            "writing": writing,
            "offers": [offer for offer in offers if offer.course],
            "seeking": [c for c in _seeking(request) if c.series not in series],
            "kit": settings.EDUCATOR_KIT_URL,
            "kit_version": kit.VERSIONS[0] if kit.VERSIONS else None,
            # Versions of the kit this person has not been told about yet.
            "kit_news": kit.news_for(state["kit_seen"]) if series else [],
            "applied": "applied" in request.GET,
            "taken_back": "taken_back" in request.GET,
            "welcome": {"educator": bool(series), "educator_tour": state["offer"]},
            "active": "educators",
        },
    )


@signed_in
def educators(request):
    return _educators_page(request)


@signed_in
def guide(request):
    """Writing a course, start to finish: the same steps as the kit's README, on the site,
    with the address of the kit. Anyone signed in may read it: it is also what someone
    thinking of applying wants to know."""
    return render(
        request,
        "desk/guide.html",
        {
            "kit": settings.EDUCATOR_KIT_URL,
            "kit_version": kit.VERSIONS[0] if kit.VERSIONS else None,
            "welcome": {"educator": educator_state(request.user)["educator"]},
            "active": "educators",
        },
    )


@signed_in
@require_POST
def files(request, series):
    """The files of a course as one zip (course.yaml and content/), for the person who
    writes it: what they unpack into their copy of the educator kit.

    It is what the site shows at this moment, hand-ins included, so it is never more than
    they can already see, and raw material is not part of it: there is none on the
    server. A POST, because it also records which version this person now has.
    """
    current = _written_by([series]) if _may_write(request.user, series) else []
    folder = live.folder(current[0].slug) if current else None
    if folder is None:
        raise Http404
    handins.remember(request.user, series, handin.content_version(folder))
    response = HttpResponse(handin.pack(folder), content_type="application/zip")
    # "attachment" makes the browser save the file instead of trying to show it.
    response["Content-Disposition"] = f'attachment; filename="{folder.name}.zip"'
    return response


@signed_in
@require_POST
def hand_in(request, series):
    """Take in the zip an educator uploads for their course (desk/handins.py). Accepted,
    it is on the site before the next page loads; refused, the page says exactly why."""
    current = _written_by([series]) if _may_write(request.user, series) else []
    if not current:
        raise Http404
    course = current[0]
    upload = request.FILES.get("zip")
    try:
        if upload is None:
            raise handins.Refused("bad", ["No file arrived. Choose the zip that pack.py made."])
        today = HandIn.objects.filter(
            user=request.user, created_at__gte=timezone.now() - timedelta(days=1)
        ).count()
        if today >= DAILY_HANDINS:
            raise handins.Refused("busy", ["That is a lot of hand-ins for one day. Try tomorrow."])
        # The box on the form: "what this removes or rewrites is meant".
        confirmed = request.POST.get("removals") == "yes"
        record = handins.take(request.user, course, upload, confirmed=confirmed)
    except handins.Refused as refusal:
        return _educators_page(request, refused=(series, refusal))

    url = _admin_url(request, record)
    transaction.on_commit(
        lambda: notify(
            f"Hand-in on the site: {course.title}",
            f"{record.summary}. It is live. Open the admin to see it or to take it back.",
            # One that removed something is worth a look sooner.
            level="warning" if record.removes else "success",
            url=url,
            dedupe_key=f"dsai-handin-{record.pk}",
        )
    )
    return redirect(f"{reverse('desk:educators')}?handed={record.pk}#course-{course.slug}")


@signed_in
@require_POST
def take_back(request, pk):
    """An educator takes back their own hand-in, if it is the newest one on the site
    for its course: the course returns to the version before it. (The owner can take
    off any hand-in, in the admin.)"""
    record = get_object_or_404(HandIn, pk=pk, status=HandIn.Status.LIVE)
    newest = HandIn.objects.filter(slug=record.slug, status=HandIn.Status.LIVE).first()
    if record.user_id != request.user.pk or newest.pk != record.pk:
        raise Http404
    handins.withdraw(record, by=request.user)
    notices.tell(
        notices.owners(),
        f"A hand-in for `{record.slug}` was taken back by its educator",
        url=reverse("admin:desk_handin_change", args=[record.pk]),
    )
    return redirect(f"{reverse('desk:educators')}?taken_back=1#course-{record.slug}")


@signed_in
def handin_zip(request, pk):
    """One step of a course's history as a zip: the whole course as it stood after it.

    For the course's educators it is the backup: an earlier version to look at, or to
    unpack and hand in again. For the owner it is what `manage.py import_course` takes;
    theirs carries a note saying which version of their own files it was built on.
    """
    record = get_object_or_404(HandIn, pk=pk)
    if not _may_write(request.user, record.series):
        raise Http404
    data = bytes(record.archive)
    if request.user.is_staff:
        slug, files = handin.unzip(data, handins.MAX_UNPACKED)
        note = {"handin": record.pk, "version": record.version, "base": handins.root_base(record)}
        data = handin.pack_files(slug, files, note)
    response = HttpResponse(data, content_type="application/zip")
    name = f"{record.slug}-version-{record.pk}.zip"
    response["Content-Disposition"] = f'attachment; filename="{name}"'
    return response


@signed_in
@require_POST
def resolve(request, pk):
    """An educator marks a request about their course as done, with a line of answer."""
    item = get_object_or_404(Request, pk=pk)
    if not (item.series and _may_write(request.user, item.series)):
        raise Http404
    item.status = Request.Status.DONE
    item.answer = request.POST.get("answer", "").strip()[:1000]
    item.save(update_fields=["status", "answer"])
    answered(item)
    return redirect("desk:educators")


def answered(item):
    """Tell the person who sent a request that it now has an answer or a new state."""
    notices.tell(
        [item.user],
        f"Your request is {item.get_status_display().lower()}",
        item.answer or f"{item.get_kind_display()}: {item.message[:120]}",
        url=reverse("desk:ask"),
    )


@signed_in
def notifications(request):
    """Everything under the bell, for reading at length."""
    rows = list(request.user.notifications.all()[:100])
    return render(request, "desk/notifications.html", {"rows": rows, "active": "notifications"})


@signed_in
@require_POST
def notifications_read(request):
    """Posted when the bell is opened (static/js/components/bell.js): what was shown
    counts as read, on every device."""
    notices.mark_read(request.user)
    return HttpResponse(status=204)

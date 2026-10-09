"""The pipeline, start to finish, for one course or all of them.

    discover -> load + validate -> index (cross-checks) -> render -> maths check -> write

Everything up to `write` only reads files and collects problems in a Report. The database is
touched in the last step, and only if the report has no errors — so a half-valid course never
replaces a working one.
"""

from pathlib import Path

from django.conf import settings
from django.utils import timezone

from catalog.models import Course

from . import mathcheck, store
from .assets import Assets
from .build import Builder
from .discover import content_hash, discover, find_courses
from .load import load_bundle
from .markdown import Renderer
from .refs import Resolver
from .report import Report


def sync_course(course_dir, *, check_only=False, force=False):
    course_dir = Path(course_dir)
    slug = course_dir.name
    report = Report(course=slug)
    digest = content_hash(course_dir)
    if not check_only and not force:
        # A file can be saved again without changing (an edit undone, a restored copy). The
        # bytes still match, so there is nothing to import, but record that they were
        # compared: the "files changed" notice on the site goes by this time.
        unchanged = Course.objects.filter(slug=slug, content_hash=digest)
        if unchanged.update(synced_at=timezone.now()):
            report.status = "unchanged"
            return report

    files = discover(course_dir, report)
    bundle = load_bundle(files, report)
    if bundle is None:
        report.status = "failed"
        return report

    builder = Builder(bundle, report)
    resolver = Resolver(builder.index())
    assets = Assets(slug)
    renderer = Renderer(report=report, resolver=resolver, assets=assets, content_root=files.content)
    try:
        plan = builder.plan(renderer, resolver)
    except Exception:
        # A broken cross-reference already reported can leave gaps that trip the second
        # pass. Those errors are what the author needs; a crash with a clean report is a bug.
        if report.ok:
            raise
        report.status = "failed"
        return report

    note = mathcheck.check(renderer.math, report)
    if note:
        report.notes.append(note)
    report.counts = plan.counts()

    if not report.ok:
        report.status = "failed"
    elif check_only:
        report.status = "checked"
    else:
        assets.commit()
        store.write(plan, digest)
        report.status = "synced"
    return report


def sync_all(*, only=None, check_only=False, force=False):
    """Sync every course under settings.CONTENT_ROOTS (or just the slugs in `only`)."""
    courses = find_courses(settings.CONTENT_ROOTS)
    reports = []
    for slug in only or []:
        if slug not in courses:
            report = Report(course=slug, status="failed")
            roots = ", ".join(str(root) for root in settings.CONTENT_ROOTS)
            report.error(
                "course.yaml",
                f"no course folder `{slug}` with a course.yaml was found",
                hint=f"looked in: {roots}. Create one with: manage.py startcourse {slug}",
            )
            reports.append(report)
    for slug, path in courses.items():
        if only and slug not in only:
            continue
        reports.append(sync_course(path, check_only=check_only, force=force))

    if not only and not check_only:
        for course in Course.objects.exclude(slug__in=courses):
            report = Report(course=course.slug, status="removed")
            report.notes.append("its folder no longer exists, so it was removed from the database")
            course.delete()
            reports.append(report)
    return reports

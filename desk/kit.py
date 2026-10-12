"""The versions of the educator kit, and telling educators about a new one.

The kit is a public repository that educators clone and keep current with `git pull`. It
is generated from this application (`manage.py export_authoring`), and so is its list of
versions: `VERSIONS` below is written into the kit as VERSION and CHANGELOG.md.

To release a version: add it **at the top** with the next number, export the kit, commit
and push it there. Then announce it in the admin (Kit announcements): educators see a
notice on their page and get an e-mail telling them to pull. Announcing is a step of its
own on purpose. The site learns the number when the code is deployed, which can be before
the kit's repository has it, and "pull" must not be said too early.
"""

from dataclasses import dataclass
from datetime import date

from django.db.models import Max


@dataclass(frozen=True)
class Version:
    number: int
    date: date
    title: str
    changes: tuple[str, ...]


VERSIONS = (
    Version(
        number=2,
        date=date(2026, 10, 12),
        title="Material from an earlier year, and a README that starts from zero",
        changes=(
            "Important: material from an earlier year of a course goes in a folder named "
            "after that year, source/2025-26/. Your assistant then writes it up as that "
            "year's, and never passes its dates, exam format or coursework off as the "
            "current ones.",
            "The README now starts from zero: installing git and uv, where to type the "
            "commands, and what to do when one of them complains.",
        ),
    ),
    Version(
        number=1,
        date=date(2026, 10, 12),
        title="The first kit",
        changes=(
            "Instructions for an AI assistant (AGENTS.md) and the /update-cms skill.",
            "The authoring guide, every field of every file, and an example course.",
            "tools/unpack.py, tools/check.py and tools/pack.py.",
        ),
    ),
)

LATEST = VERSIONS[0].number if VERSIONS else 0


def announced():
    """The newest version educators have been told about; 0 if none was announced."""
    from .models import KitAnnouncement

    return KitAnnouncement.objects.aggregate(newest=Max("number"))["newest"] or 0


def news_for(seen):
    """The announced versions above `seen`, newest first: what a notice shows."""
    upto = announced()
    return [version for version in VERSIONS if seen < version.number <= upto]


def changelog():
    """The list as Markdown, for the kit's CHANGELOG.md."""
    lines = ["# Versions of the educator kit", ""]
    lines += ["Newest first. Get the latest with `git pull`.", ""]
    for version in VERSIONS:
        lines += [f"## {version.number}: {version.title} ({version.date:%d %B %Y})", ""]
        lines += [f"- {change}" for change in version.changes]
        lines.append("")
    return "\n".join(lines)


def tell_educators(number):
    """E-mail every educator that version `number` of the kit is out. Returns how many
    messages were queued. The notice on their page comes from the announcement itself."""
    from django.conf import settings

    from . import mail
    from .models import Educator

    version = next(version for version in VERSIONS if version.number == number)
    people = {role.user for role in Educator.objects.select_related("user")}
    changes = "\n".join(f"- {change}" for change in version.changes)
    body = (
        f"Version {number} of the educator kit is out: {version.title}.\n\n"
        f"{changes}\n\n"
        "To get it, open the kit's folder on your computer and run:\n\n"
        "    git pull\n\n"
        "Your course is not touched by it.\n\n"
        f"The kit: {settings.EDUCATOR_KIT_URL}\n"
        f"The guide: {settings.SITE_URL}/educators/guide/"
    )
    return mail.send(people, f"Educator kit version {number}: run git pull", body)

"""What changed on the site, told to the people who use it.

Each `Update` is one release worth telling: a headline and a few points, each of which may
link to the page it is about. Someone who has not seen an update yet is shown it in the
"What's new" dialog the next time they open their dashboard, and all of them stay readable
at /whats-new/.

To announce something, add an Update **at the top** with the next number. Numbers only go
up and are never reused or changed: accounts.Profile remembers the last one each person saw.

The tour is not versioned. It is rewritten in place and always describes the site as it
is, so someone taking it today has, by definition, seen everything up to the latest update.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Point:
    title: str
    text: str
    link: str = ""  # the name of a URL without arguments, e.g. "desk:ask"
    label: str = ""  # what the link says


@dataclass(frozen=True)
class Update:
    number: int
    date: date
    title: str
    points: tuple[Point, ...]
    # The step of the tour that shows it (counted from 0), if one does: the dialog then
    # offers to open the tour there.
    tour_step: int | None = None


UPDATES = (
    Update(
        number=1,
        date=date(2026, 10, 12),
        title="Ask for content, report a mistake, write a course",
        points=(
            Point(
                "Ask or report",
                "Missing a lecture, found a mistake, or have an idea for the site? Send it "
                "from the menu. The answer comes back on the same page.",
                "desk:ask",
                "Ask or report",
            ),
            Point(
                "Every course of the programme",
                "All semesters are listed now, also the courses nobody has written up yet. "
                "Pick the ones you take; an empty course says so and lets you ask for it.",
                "catalog:choose",
                "Choose courses",
            ),
            Point(
                "Become an educator",
                "The courses are written by students. If you know one well, you can apply "
                "to write it for everyone else.",
                "desk:educators",
                "How it works",
            ),
        ),
        tour_step=5,
    ),
)

LATEST = UPDATES[0].number if UPDATES else 0


def since(number):
    """The updates numbered above `number`, newest first."""
    return [update for update in UPDATES if update.number > number]

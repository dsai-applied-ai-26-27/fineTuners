"""Two questions about a course that the owner's desk decides.

    is_open(course)       may students see it?
    has_educator(course)  is someone writing it?

Each starts from the course's own file (`enabled`, `has_educator` in course.yaml), and for
each the owner's switch in the admin (desk.CourseSetting), once used, wins. An accepted
educator (desk.Educator) also counts as "someone is writing it".

One `Switches` object answers for every course and reads each table at most once, so a
page that lists thirty courses still asks the database twice.
"""

from .models import CourseSetting, Educator


class Switches:
    def __init__(self):
        self._settings = None
        self._taught = None

    def _setting(self, course):
        if self._settings is None:
            self._settings = {row.series: row for row in CourseSetting.objects.all()}
        return self._settings.get(course.series)

    def is_open(self, course):
        setting = self._setting(course)
        if setting is not None and setting.enabled is not None:
            return setting.enabled
        return course.enabled

    def has_educator(self, course):
        setting = self._setting(course)
        if setting is not None and setting.has_educator is not None:
            return setting.has_educator
        if course.has_educator:
            return True
        if self._taught is None:
            self._taught = set(Educator.objects.values_list("series", flat=True))
        return course.series in self._taught


def switches(request):
    """The switches for this request: made once, shared by the view and the templates."""
    if not hasattr(request, "_switches"):
        request._switches = Switches()
    return request._switches

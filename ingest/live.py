"""Which folder holds the files the site shows for a course.

Almost always that is the owner's folder under the courses directory. The exception is a
course that an educator has added to since the owner last published: the site then shows
the course as handed in, from a folder of its own, until the owner's files contain those
additions. That decision belongs to whoever keeps the hand-ins (desk/handins.py), which
registers itself here; this module only knows that such a thing may exist.

    folders()            slug -> folder, for every course there is
    folder("rl")         the folder of one course, or None
    folders(settle=True) the same, and let the providers tidy up what has been overtaken
"""

from django.conf import settings

from .discover import find_courses

_providers = []


def provide(provider):
    """Register `provider(base, settle=..., notes=...) -> folders`. It is given the owner's
    folders by slug and returns the folders to use instead."""
    if provider not in _providers:
        _providers.append(provider)


def folders(*, settle=False, notes=None):
    """The folder to read each course from. `notes` (a dict) collects one line per course
    worth telling whoever is syncing."""
    found = find_courses(settings.CONTENT_ROOTS)
    for provider in _providers:
        found = provider(found, settle=settle, notes=notes if notes is not None else {})
    return found


def folder(slug):
    return folders().get(slug)

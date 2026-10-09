from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404

from ingest.discover import find_course


def source_file(request, course, path):
    """Serve an original file from courses/<course>/source/ so a note can link to its PDF.

    Off unless SERVE_SOURCE_FILES is set (on in DEBUG): these files are usually not yours
    to publish. The resolved path must stay inside source/, which stops `../` tricks."""
    if not settings.SERVE_SOURCE_FILES:
        raise Http404("Source files are not served on this site.")
    folder = find_course(course, settings.CONTENT_ROOTS)
    if folder is None:
        raise Http404("No such course.")
    root = (Path(folder) / "source").resolve()
    target = (root / path).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise Http404("No such file.")
    # FileResponse streams the file in chunks and sets the content type from its name.
    return FileResponse(target.open("rb"), filename=target.name)

"""How static files are stored once `collectstatic` has gathered them (production only).

Django's manifest storage copies every file under a second name that contains a hash of its
contents (`app.js` -> `app.2bee543c4f7e.js`) and makes `{% static %}` print that name. A
changed file therefore gets a new address, so browsers and Cloudflare may keep each one
forever and a deploy never serves a stale script. WhiteNoise's subclass also stores a
compressed copy of each file.
"""

from whitenoise.storage import CompressedManifestStaticFilesStorage


class StaticStorage(CompressedManifestStaticFilesStorage):
    # The site's JavaScript is native ES modules that import each other by relative path.
    # With this on, those paths are rewritten to the hashed names as well; without it only
    # the entry point would be safe to cache forever.
    support_js_module_import_aggregation = True

"""Fetch the third-party front-end assets into static/.

The site has no JavaScript build step. Libraries, fonts and icons are downloaded once from
the npm registry at pinned versions, verified against the registry's sha512 integrity hash,
and committed. Re-run after changing a version or the icon list:

    uv run python tools/vendor_assets.py

Standard library only, so it also runs before the project's dependencies are installed.
"""

import base64
import hashlib
import io
import re
import sys
import tarfile
import urllib.request
from pathlib import Path

STATIC = Path(__file__).resolve().parent.parent / "static"

# name -> (version, integrity as published by the registry)
PACKAGES = {
    "alpinejs": (
        "3.17.4",
        "sha512-N2gsr+58XVUt7OAPKnUGiKPDtkd+xbSGTae8C8IJxeRdkkhBJPIautkJ+qcwb7lcjJ/QK3/CPVIbN20JPvtK7A==",
    ),
    "katex": (
        "0.19.0",
        "sha512-v6Tznz3zJ7u3niRCoDTsumM2+HA2XXcCu+WAacCeHD2z3p9A9Ks987o5FzfTGBN0e8A0vjEgIDvLbICrXpdw/Q==",
    ),
    "@fontsource-variable/google-sans-flex": (
        "5.3.1",
        "sha512-ItkWlFvW61+BmwOMJQfPY81KpvvslqbiTyfYKceOx+0kEFBzTcPbbMVcL9BKrmqhhqnq36kNs7YRbxonovOmNg==",
    ),
    "@fontsource-variable/literata": (
        "5.3.0",
        "sha512-1Jw7xvOcoGyB83lxB2nG4bfNbqtX2/TTbdh9sHAOmU064SvmSdulDtA5RBu5JYWf64fdaKX7xU+z3GO1T2bCHA==",
    ),
    "@fontsource-variable/jetbrains-mono": (
        "5.3.0",
        "sha512-F32xpS2NsGYoQi2ADSkKTgpJj7ozajsGgDJ8woTnqjmIB+dxDIqImjl4pXZVEExu8UFZ2ndhmX18EBS/hdz3Lw==",
    ),
    "@material-symbols/svg-400": (
        "0.47.6",
        "sha512-lXYsZWNXXu6gTVTAS/aRtOuKrjYhbyl1Y/t1JELXku3GZe0DLPfQ8O8UcbHGs1H22s32kGJVilkTKO2OkGzPXA==",
    ),
}

# Files copied verbatim: package -> {path in tarball: path under static/}
COPY = {
    "alpinejs": {"package/dist/module.esm.min.js": "vendor/alpine/alpine.esm.min.js"},
    "katex": {"package/dist/katex.min.js": "vendor/katex/katex.min.js"},
}

# Font packages: package -> stylesheets inside it whose @font-face rules we keep.
FONT_CSS = {
    "@fontsource-variable/google-sans-flex": ["package/rond.css"],  # weight + roundness axes
    "@fontsource-variable/literata": ["package/opsz.css", "package/opsz-italic.css"],
    "@fontsource-variable/jetbrains-mono": ["package/wght.css"],
}
FONT_SUBSETS = ("latin", "latin-ext")  # latin-ext covers č ć đ š ž

# Material Symbols (Rounded, weight 400). Name on the left is what templates use.
ICONS = {
    "home": "home",
    "menu": "menu",
    "close": "close",
    "search": "search",
    "settings": "settings",
    "course": "school",
    "lecture": "menu_book",
    "lab": "science",
    "homework": "assignment",
    "guide": "explore",
    "cards": "style",
    "problems": "quiz",
    "exam": "fact_check",
    "formulas": "functions",
    "glossary": "dictionary",
    "sheet": "description",
    "memory": "psychology",
    "palace": "castle",
    "hook": "lightbulb",
    "topic": "label",
    "timer": "timer",
    "play": "play_arrow",
    "pause": "pause",
    "reset": "replay",
    "visible": "visibility",
    "hidden": "visibility_off",
    "dark": "dark_mode",
    "light": "light_mode",
    "auto": "brightness_auto",
    "check": "check",
    "done": "check_circle",
    "todo": "radio_button_unchecked",
    "prev": "chevron_left",
    "next": "chevron_right",
    "expand": "keyboard_arrow_down",
    "forward": "arrow_forward",
    "back": "arrow_back",
    "shuffle": "shuffle",
    "keyboard": "keyboard",
    "download": "download",
    "upload": "upload",
    "delete": "delete",
    "print": "print",
    "link": "link",
    "external": "open_in_new",
    "key": "star",
    "warning": "warning",
    "info": "info",
    "paper": "edit_note",
    "due": "bolt",
    "flag": "flag",
    "bell": "notifications",
    "schedule": "schedule",
    "streak": "local_fire_department",
    "trend": "trending_up",
    "filter": "filter_list",
    "more": "more_horiz",
    "help": "help",
    "source": "attach_file",
    "route": "route",
    "place": "location_on",
    "history": "history",
    "calendar": "calendar_month",
    "sync": "sync",
    "error": "error",
    "tune": "tune",
    "sound": "volume_up",
    "mute": "volume_off",
    "cover": "flip",
    "target": "target",
    "skip": "skip_next",
    "steps": "format_list_numbered",
    "cloze": "border_color",
    "definition": "bookmark",
    "theorem": "verified",
    "proof": "rule",
    "example": "experiment",
    "pitfall": "report",
    "tip": "emoji_objects",
    "empty": "inbox",
}


def fetch(name):
    version, integrity = PACKAGES[name]
    base = name.split("/")[-1]
    url = f"https://registry.npmjs.org/{name}/-/{base}-{version}.tgz"
    print(f"  {name}@{version}")
    with urllib.request.urlopen(url, timeout=120) as response:
        data = response.read()
    algorithm, _, expected = integrity.partition("-")
    actual = base64.b64encode(hashlib.new(algorithm, data).digest()).decode()
    if actual != expected:
        sys.exit(f"integrity mismatch for {name}@{version}: refusing to unpack")
    return tarfile.open(fileobj=io.BytesIO(data), mode="r:gz")


def read(tar, member):
    extracted = tar.extractfile(member)
    if extracted is None:
        sys.exit(f"missing in tarball: {member}")
    return extracted.read()


def write(relative, data):
    target = STATIC / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def vendor_copies():
    for name, files in COPY.items():
        with fetch(name) as tar:
            for member, destination in files.items():
                write(destination, read(tar, member))
            if name == "katex":
                vendor_katex_css(tar)


def vendor_katex_css(tar):
    for member in tar.getmembers():
        if member.name.startswith("package/dist/fonts/") and member.name.endswith(".woff2"):
            write(f"vendor/katex/fonts/{Path(member.name).name}", read(tar, member.name))
    css = read(tar, "package/dist/katex.min.css").decode("utf-8")
    # Only the woff2 files are shipped, so drop the woff/ttf fallbacks that would 404.
    css = re.sub(r',url\(fonts/[^)]+\.(?:woff|ttf)\) format\("(?:woff|truetype)"\)', "", css)
    write("vendor/katex/katex.min.css", css.encode("utf-8"))


def vendor_fonts():
    rules = []
    for name, stylesheets in FONT_CSS.items():
        with fetch(name) as tar:
            for stylesheet in stylesheets:
                css = read(tar, stylesheet).decode("utf-8")
                for block in re.findall(r"@font-face\s*\{[^}]*\}", css):
                    match = re.search(r"url\(\./files/([^)]+)\)", block)
                    if not match:
                        continue
                    filename = match.group(1)
                    if not any(f"-{subset}-" in filename for subset in FONT_SUBSETS):
                        continue
                    write(f"fonts/{filename}", read(tar, f"package/files/{filename}"))
                    rules.append(block.replace("./files/", "./"))
    header = "/* Generated by tools/vendor_assets.py. Do not edit. */\n"
    write("fonts/fonts.css", (header + "\n".join(rules) + "\n").encode("utf-8"))


def vendor_icons():
    wanted = {f"package/rounded/{symbol}.svg": alias for alias, symbol in ICONS.items()}
    symbols = {}
    with fetch("@material-symbols/svg-400") as tar:
        for member in tar:
            alias = wanted.get(member.name)
            if alias is None:
                continue
            svg = read(tar, member).decode("utf-8")
            view_box = re.search(r'viewBox="([^"]+)"', svg).group(1)
            inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
            symbols[alias] = f'<symbol id="{alias}" viewBox="{view_box}">{inner}</symbol>'
    missing = sorted(set(ICONS) - set(symbols))
    if missing:
        sys.exit(f"icons not found in Material Symbols: {', '.join(missing)}")
    body = "\n".join(symbols[alias] for alias in sorted(symbols))
    sprite = f'<svg xmlns="http://www.w3.org/2000/svg">\n{body}\n</svg>\n'
    write("icons.svg", sprite.encode("utf-8"))
    print(f"  {len(symbols)} icons -> static/icons.svg")


def write_versions():
    lines = ["Third-party assets in static/, fetched by tools/vendor_assets.py", ""]
    lines += [f"{name} {version}" for name, (version, _) in PACKAGES.items()]
    write("vendor/VERSIONS.txt", ("\n".join(lines) + "\n").encode("utf-8"))


if __name__ == "__main__":
    print("libraries")
    vendor_copies()
    print("fonts")
    vendor_fonts()
    print("icons")
    vendor_icons()
    write_versions()
    print("done")

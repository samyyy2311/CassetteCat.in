#!/usr/bin/env python3
"""Copies the developer guides from each app's repository into docs/developers, so the docs site shows the same
pages as GitHub. The repositories stay the source; run this after their docs change."""
import posixpath
import re
from pathlib import Path
from urllib.request import Request, urlopen

RAW = "https://raw.githubusercontent.com/samyyy2311/{}/main/{}"
BLOB = "https://github.com/samyyy2311/{}/blob/main/{}"
ROOT = Path(__file__).resolve().parents[1] / "docs" / "developers"

# (folder on the site, repository, [(page, path in the repository, Lucide icon for the sidebar)])
GUIDES = [
    ("android", "CassetteCat", [
        ("building", "docs/dev/building.md", "hammer"),
        ("architecture", "docs/dev/architecture.md", "blocks"),
        ("how-to", "docs/dev/how-to.md", "list-checks"),
        ("theme", "docs/dev/theme.md", "palette"),
        ("desktop-remote-protocol", "docs/dev/desktop-remote-protocol.md", "network"),
        ("releasing", "docs/dev/releasing.md", "package"),
    ]),
    ("desktop", "CassetteCat-Desktop", [
        ("building", "docs/dev/building.md", "hammer"),
        ("architecture", "ARCHITECTURE.md", "blocks"),
        ("design", "DESIGN.md", "palette"),
        ("releasing", "docs/dev/releasing.md", "package"),
    ]),
]


def fetch(repo, path):
    request = Request(RAW.format(repo, path), headers={"User-Agent": "CassetteCat-site-build"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def convert(text, folder, repo, source, icon, pages):
    title = re.match(r"#\s+(.+)\n", text).group(1).strip()
    body = text[text.index("\n") + 1:].lstrip("\n")
    on_site = {path: f"/developers/{folder}/{page}" for page, path, _ in pages}

    def link(match):
        label, target = match.group(1), match.group(2)
        if re.match(r"^[a-z]+:|^#", target):
            return match.group(0)
        path, _, anchor = target.partition("#")
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), path))
        url = on_site.get(resolved) or BLOB.format(repo, resolved)
        return f"[{label}]({url}{'#' + anchor if anchor else ''})"

    body = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, body)
    edit = BLOB.format(repo, source)
    return f'---\ntitle: "{title}"\nicon: "{icon}"\n---\n\n<Note>Copied from [{source}]({edit}) in the {repo} repository.</Note>\n\n{body}'


def main():
    for folder, repo, pages in GUIDES:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
        for page, path, icon in pages:
            (ROOT / folder / f"{page}.mdx").write_text(convert(fetch(repo, path), folder, repo, path, icon, pages), encoding="utf-8")


if __name__ == "__main__":
    main()

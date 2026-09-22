#!/usr/bin/env python3
import html, json, re
from pathlib import Path
from urllib.request import Request, urlopen

API = "https://api.github.com/repos/samyyy2311/CassetteCat/releases?per_page=100"
PAGE = Path(__file__).resolve().parents[1] / "changelog.html"

def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return re.sub(r"\[([^]]+)]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', text)

def parse(body):
    sections, category = [], None
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        heading = re.match(r"^#{1,3}\s+(.+)$", line)
        if heading:
            category = heading.group(1)
            continue
        item = re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)(.+)$", line)
        if not sections or sections[-1][0] != category:
            sections.append((category, []))
        sections[-1][1].append(item.group(1) if item else line)
    return sections or [(None, ["See the release on GitHub for details."])]

def main():
    request = Request(API, headers={"Accept": "application/vnd.github+json", "User-Agent": "CassetteCat-site-build"})
    with urlopen(request, timeout=30) as response:
        releases = [r for r in json.load(response) if not r["draft"] and not r["prerelease"]]
    if not releases:
        raise RuntimeError("No public releases found")
    toc, content = [], []
    for number, release in enumerate(releases, 1):
        tag = release["tag_name"].removeprefix("v")
        anchor = f"v{tag.replace('.', '-')}"
        toc.append(f'          <li><a href="#{anchor}"><span class="toc-num">{number:02d}</span>v{html.escape(tag)}</a></li>')
        title = re.sub(rf"^v?{re.escape(tag)}\s*[-–—:]?\s*", "", release.get("name") or "").strip()
        lines = [f'        <section id="{anchor}">', f'          <h2><span class="sec-num">{number:02d}.</span>v{html.escape(tag)}{(" - " + inline(title)) if title else ""}</h2>']
        for category, items in parse(release.get("body") or ""):
            if category:
                lines.append(f"          <p><strong>{inline(category)}</strong></p>")
            lines += ["          <ul>", *(f"            <li>{inline(item)}</li>" for item in items), "          </ul>"]
        lines.append("        </section>")
        content.append("\n".join(lines))
    content_html = "\n\n".join(content)
    page = PAGE.read_text(encoding="utf-8")
    page = re.sub(r"(<span><b>Latest</b>\s*)v[^<]*(</span>)", rf"\g<1>v{html.escape(releases[0]['tag_name'].removeprefix('v'))}\2", page)
    page = re.sub(r'(<span><b>Source</b>\s*).*?(</span>)', r'\1<a href="https://github.com/samyyy2311/CassetteCat/releases" target="_blank" rel="noopener">GitHub Releases</a>\2', page)
    page = re.sub(r'(<aside class="doc-toc">\s*<h4>Versions</h4>\s*<ol>).*?(</ol>\s*</aside>)', rf"\1\n{'\n'.join(toc)}\n        \2", page, flags=re.DOTALL)
    page = re.sub(r'(<div class="doc-body">\s*<p class="doc-lede">).*?(</p>\s*)<section id=.*?</section>(\s*</div>\s*</div>\s*</main>)', rf'\1Release notes are generated from <a href="https://github.com/samyyy2311/CassetteCat/releases" target="_blank" rel="noopener">public GitHub Releases</a> when this site deploys.\2\n{content_html}\n\n      \3', page, flags=re.DOTALL)
    PAGE.write_text(page, encoding="utf-8")

if __name__ == "__main__":
    main()

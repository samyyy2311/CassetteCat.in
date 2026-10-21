#!/usr/bin/env python3
import html, json, re
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

API = "https://api.github.com/repos/samyyy2311/{}/releases?per_page=100"
PLATFORMS = [("android", "Android", "CassetteCat"), ("desktop", "Desktop", "CassetteCat-Desktop")]
ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "changelog.html"
INDEX = ROOT / "index.html"
SITEMAP = ROOT / "sitemap.xml"

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
        heading = re.match(r"^#{1,3}\s+(.+)$", line) or re.match(r"^\*\*([^*]+)\*\*$", line)
        if heading:
            # The changelog's own version heading repeats the release: "[1.9.1]", "[1.0.0] - 2026-10-15", or
            # "[1.6.5] - A title", of which only the title is kept.
            text = re.sub(r"^\[?v?\d+(\.\d+)+\]?\s*(-\s*(\d{4}-\d{2}-\d{2})?)?\s*", "", heading.group(1))
            if text:
                category = text
            continue
        item = re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)(.+)$", line)
        if not sections or sections[-1][0] != category:
            sections.append((category, []))
        sections[-1][1].append(item.group(1) if item else line)
    return sections or [(None, ["See the release on GitHub for details."])]

def strip_tags(text):
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()

def sync_structured_data(path, version=None):
    page = path.read_text(encoding="utf-8")
    match = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', page, re.S)
    data = json.loads(match.group(2))
    faqs = re.findall(r"<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>", page, re.S)
    for node in data["@graph"]:
        if version and node["@type"] in ("SoftwareApplication", "MobileApplication"):
            node["softwareVersion"] = version
        if node["@type"] == "FAQPage":
            node["mainEntity"] = [
                {"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
                for q, a in faqs
            ]
    block = json.dumps(data, indent=2, ensure_ascii=False).replace("\n", "\n  ")
    page = page[:match.start(2)] + "\n  " + block + "\n  " + page[match.end(2):]
    path.write_text(page, encoding="utf-8")

def sync_sitemap():
    sitemap = SITEMAP.read_text(encoding="utf-8")
    SITEMAP.write_text(re.sub(r"<lastmod>[^<]*</lastmod>", f"<lastmod>{date.today().isoformat()}</lastmod>", sitemap), encoding="utf-8")

def fetch_releases(repo):
    request = Request(API.format(repo), headers={"Accept": "application/vnd.github+json", "User-Agent": "CassetteCat-site-build"})
    with urlopen(request, timeout=30) as response:
        releases = [r for r in json.load(response) if not r["draft"] and not r["prerelease"]]
    if not releases:
        raise RuntimeError(f"No public releases found for {repo}")
    return releases

def render(platform, label, releases):
    series, content = [], [f'        <div class="release-panel" id="{platform}" data-platform="{platform}" role="tabpanel" aria-label="{label}">']
    for index, release in enumerate(releases):
        tag = release["tag_name"].removeprefix("v")
        anchor = f"{platform}-v{tag.replace('.', '-')}"
        name = ".".join(tag.split(".")[:2])
        if not series or series[-1][0] != name:
            series.append((name, []))
        series[-1][1].append(f'<a href="#{anchor}">v{html.escape(tag)}</a>')
        name = re.sub(r"^CassetteCat\s+", "", release.get("name") or "")
        title = re.sub(rf"^v?{re.escape(tag)}\s*[-\u2013\u2014:]?\s*", "", name).strip()
        heading = f'v{html.escape(tag)}{(" - " + inline(title)) if title else ""}'
        lines = [f'        <section id="{anchor}">', f'          <details{" open" if index == 0 else ""}>',
                 f"          <summary><h3>{heading}</h3></summary>"]
        for category, items in parse(release.get("body") or ""):
            if category:
                lines.append(f"          <p><strong>{inline(category)}</strong></p>")
            lines += ["          <ul>", *(f"            <li>{inline(item)}</li>" for item in items), "          </ul>"]
        lines += ["          </details>", "        </section>"]
        content.append("\n".join(lines))
    content[-1] += "\n        </div>"
    # The versions list groups each series, such as 1.7.0 to 1.7.7, with only the newest open.
    toc = []
    for index, (name, links) in enumerate(series):
        if len(links) == 1:
            toc.append(f'          <li data-platform="{platform}">{links[0]}</li>')
            continue
        items = "".join(f"<li>{link}</li>" for link in links)
        toc.append(f'          <li data-platform="{platform}"><details{" open" if index == 0 else ""}>'
                   f"<summary>v{name}</summary><ol>{items}</ol></details></li>")
    return toc, content

def main():
    toc, content, latest = [], [], {}
    for platform, label, repo in PLATFORMS:
        releases = fetch_releases(repo)
        latest[platform] = releases[0]["tag_name"].removeprefix("v")
        platform_toc, platform_content = render(platform, label, releases)
        toc += platform_toc
        content += platform_content
    page = PAGE.read_text(encoding="utf-8")
    for platform, label, _ in PLATFORMS:
        page = re.sub(rf"(<span><b>{label}</b>\s*)v[^<]*(</span>)", rf"\g<1>v{html.escape(latest[platform])}\2", page)
    page = re.sub(r"(<!-- releases:toc -->).*?(<!-- /releases:toc -->)", rf"\1\n{'\n'.join(toc)}\n          \2", page, flags=re.DOTALL)
    page = re.sub(r"(<!-- releases:notes -->).*?(<!-- /releases:notes -->)", rf"\1\n{'\n\n'.join(content)}\n        \2", page, flags=re.DOTALL)
    PAGE.write_text(page, encoding="utf-8")
    sync_structured_data(INDEX)
    for platform, _, _ in PLATFORMS:
        sync_structured_data(ROOT / f"{platform}.html", latest[platform])
    sync_sitemap()

if __name__ == "__main__":
    main()

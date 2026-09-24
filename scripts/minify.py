#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def minify_css(content):
    content = re.sub(r"/\*[\s\S]*?\*/", "", content)
    content = re.sub(r"\s+", " ", content)
    content = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", content)
    return content.replace(";}", "}").strip()


def minify_js(content):
    content = re.sub(r"/\*[\s\S]*?\*/", "", content)
    content = re.sub(r"^\s*//.*$", "", content, flags=re.MULTILINE)
    content = re.sub(r"(?<!:)//.*$", "", content, flags=re.MULTILINE)
    content = re.sub(r"[ \t]+", " ", content)
    return "\n".join(line.strip() for line in content.splitlines() if line.strip())


def minify_inline_script(block):
    open_tag = re.match(r"<script[^>]*>", block, flags=re.IGNORECASE).group(0)
    inner = block[len(open_tag):-len("</script>")]
    if "application/ld+json" in open_tag.lower():
        inner = json.dumps(json.loads(inner), separators=(",", ":"), ensure_ascii=False)
    else:
        inner = minify_js(inner)
    return open_tag + inner + "</script>"


def minify_html(content):
    kept = []

    def keep(match):
        kept.append(match.group(0))
        return f"\0{len(kept) - 1}\0"

    content = re.sub(r"<(script|pre|textarea)[\s\S]*?</\1>", keep, content, flags=re.IGNORECASE)
    content = re.sub(r"<!--[\s\S]*?-->", "", content)
    content = re.sub(r">\s+<", "><", content)
    content = re.sub(r"\s+", " ", content)

    for i, block in enumerate(kept):
        if block.lower().startswith("<script") and "src=" not in block.lower():
            block = minify_inline_script(block)
        content = content.replace(f"\0{i}\0", block)
    return content.strip()


def main():
    jobs = [(path, minify_html) for path in ROOT.glob("*.html")]
    jobs += [(path, minify_css) for path in (ROOT / "assets").glob("*.css")]
    jobs += [(path, minify_js) for path in (ROOT / "assets").glob("*.js") if not path.name.endswith(".min.js")]

    for path, minify in jobs:
        before = path.read_text(encoding="utf-8")
        after = minify(before)
        path.write_text(after, encoding="utf-8")
        print(f"{path.name}: {len(before)} -> {len(after)} bytes")


if __name__ == "__main__":
    main()

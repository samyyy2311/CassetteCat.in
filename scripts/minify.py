#!/usr/bin/env python3
"""
Production asset minifier for CassetteCat.
Strips comments, collapses whitespace, and compresses HTML, CSS, and JS
into single continuous lines for production deployment.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def minify_css(content: str) -> str:
    # Strip comments
    content = re.sub(r"/\*[\s\S]*?\*/", "", content)
    # Normalize whitespace
    content = re.sub(r"\s+", " ", content)
    # Remove space around delimiters
    content = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", content)
    # Remove trailing semicolons
    content = re.sub(r";}", "}", content)
    return content.strip()

def minify_js(content: str) -> str:
    # Strip multi-line comments
    content = re.sub(r"/\*[\s\S]*?\*/", "", content)
    # Strip single-line comments that are not part of URLs
    content = re.sub(r"^\s*//.*$", "", content, flags=re.MULTILINE)
    content = re.sub(r"(?<!:)//.*$", "", content, flags=re.MULTILINE)
    # Normalize whitespace
    content = re.sub(r"[ \t]+", " ", content)
    # Collapse multiple newlines
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    return "\n".join(lines)

def minify_html(content: str) -> str:
    # Preserve pre/code/textarea/script blocks if any
    protected_blocks = []
    def save_block(match):
        protected_blocks.append(match.group(0))
        return f"___PROTECTED_BLOCK_{len(protected_blocks) - 1}___"

    # Protect script and pre tags from aggressive whitespace collapse
    content = re.sub(r"<(script|pre|textarea)[\s\S]*?</\1>", save_block, content, flags=re.IGNORECASE)

    # Strip HTML comments
    content = re.sub(r"<!--[\s\S]*?-->", "", content)

    # Collapse whitespace between tags
    content = re.sub(r">\s+<", "><", content)

    # Collapse intra-tag whitespace and normal text whitespace
    content = re.sub(r"\s+", " ", content)

    # Restore protected blocks
    for idx, block in enumerate(protected_blocks):
        if block.lower().startswith("<script") and "src=" not in block.lower():
            tag_open = re.match(r"^<script[^>]*>", block, flags=re.IGNORECASE).group(0)
            tag_close = "</script>"
            inner = block[len(tag_open):-len(tag_close)]
            if "application/ld+json" in tag_open.lower():
                try:
                    import json
                    inner = json.dumps(json.loads(inner), separators=(',', ':'))
                except Exception:
                    pass
            else:
                inner = minify_js(inner)
            block = tag_open + inner + tag_close
        content = content.replace(f"___PROTECTED_BLOCK_{idx}___", block)

    return content.strip()

def main():
    html_files = list(ROOT.glob("*.html"))
    css_files = list((ROOT / "assets").glob("*.css"))
    js_files = [f for f in (ROOT / "assets").glob("*.js") if not f.name.endswith(".min.js")]

    processed = 0

    for f in html_files:
        original = f.read_text(encoding="utf-8")
        minified = minify_html(original)
        f.write_text(minified, encoding="utf-8")
        processed += 1
        print(f"Minified {f.name} ({len(original)} -> {len(minified)} bytes)")

    for f in css_files:
        original = f.read_text(encoding="utf-8")
        minified = minify_css(original)
        f.write_text(minified, encoding="utf-8")
        processed += 1
        print(f"Minified {f.name} ({len(original)} -> {len(minified)} bytes)")

    for f in js_files:
        original = f.read_text(encoding="utf-8")
        minified = minify_js(original)
        f.write_text(minified, encoding="utf-8")
        processed += 1
        print(f"Minified {f.name} ({len(original)} -> {len(minified)} bytes)")

    print(f"\nDone! Successfully minified {processed} production files.")

if __name__ == "__main__":
    main()

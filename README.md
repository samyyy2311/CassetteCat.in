# CassetteCat Website

<p align="center">
  <img src="assets/play_store_icon_512.png" width="112" alt="CassetteCat logo">
</p>

<p align="center">
  The home of <a href="https://cassettecat.caffeinelabs.in">CassetteCat</a>.
</p>

<p align="center">
  <a href="https://github.com/samyyy2311/CassetteCat">Android app</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/samyyy2311/CassetteCat-Desktop">Desktop app</a>
</p>

This repository contains the static website, deployed with GitHub Pages. Releases and Android downloads stay in the [CassetteCat Android repository](https://github.com/samyyy2311/CassetteCat).

## Local preview

Serve the folder with any static server:

```bash
python -m http.server
```

Then open http://localhost:8000. Clean URLs such as `/changelog` only work on GitHub Pages, so use `/changelog.html` locally.

## Deploy

Pushing to `main` runs the Pages workflow, which:

1. Rebuilds `changelog.html` from the public GitHub Releases, updates the app version and FAQ structured data in `index.html`, and refreshes the dates in `sitemap.xml` (`scripts/build_releases.py`).
2. Minifies the HTML, CSS and JS (`scripts/minify.py`).

Keep the FAQ in `index.html` as `<details><summary>Question</summary><p>Answer</p></details>` blocks so the build can mirror it into the structured data.

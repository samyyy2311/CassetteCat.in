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

## Local preview & Build

Open `index.html` with any static file server. The deployment workflow automatically compiles the changelog from public GitHub Releases and minifies all production assets before publishing to GitHub Pages.

To test minification locally:
```bash
python scripts/minify.py
```

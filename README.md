# CassetteCat website

The website for [CassetteCat](https://github.com/samyyy2311/CassetteCat), the music player for the music you own, at [cassettecat.caffeinelabs.in](https://cassettecat.caffeinelabs.in). It also serves the user guide and developer guides for both apps at [/docs](https://cassettecat.caffeinelabs.in/docs).

The site is plain HTML, CSS and JavaScript, with no framework and no build step beyond minifying.

## What's where

| Path | What it is |
| :--- | :--- |
| `index.html`, `android.html`, `desktop.html` | The home page and each app's page |
| `changelog.html` | Every release of both apps, built from GitHub Releases |
| `privacy.html`, `terms.html`, `404.html` | The privacy policy, terms and the not-found page |
| `assets/` | `style.css`, `main.js`, logos, screenshots and icons |
| `docs/` | The guides, published by [Mintlify](https://mintlify.com). `docs.json` sets their navigation |
| `worker.js` | The Cloudflare Worker: `/docs` goes to Mintlify, everything else to the site's files |
| `llms.txt`, `sitemap.xml`, `robots.txt`, `manifest.json` | For search engines, AI crawlers and installing the site |

`main.js` fills in the latest downloads, download counts and GitHub stars from the GitHub API when a page loads, so the download buttons don't need updating for each release.

## Run it locally

```bash
python -m http.server 8000
```

Then open [localhost:8000](http://localhost:8000). To preview the guides, run `npx mint dev` in `docs/`.

## After a release

```bash
python scripts/build_releases.py
```

It rebuilds `changelog.html` from both apps' GitHub releases, puts the latest versions in each page's structured data, and updates `sitemap.xml`. Commit the result.

## Updating the guides

- **User guide**: edit the `.mdx` files in `docs/android`, `docs/desktop` and `docs/`. Check them with `npx mint broken-links` in `docs/`.
- **Developer guides**: these live in the apps' repositories. After they change, copy them into `docs/developers` with:

  ```bash
  python scripts/sync_dev_docs.py
  ```

## Deploying

Cloudflare builds and deploys the site from `main` on every push. The build command is set in the Cloudflare dashboard and writes the site to `_site`, which `wrangler.jsonc` serves. `scripts/minify.py` minifies the HTML, CSS and JavaScript in place. Mintlify publishes `docs/` from `main` on its own. When `style.css` or `main.js` changes, raise the `?v=` date where the pages link them, so browsers fetch the new file.

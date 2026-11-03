# Statics

Standalone HTML pages, listed at <https://lomzem.github.io/statics/>.

Add, rename, or remove `.html` files anywhere outside hidden directories. On
every push to `main`, GitHub Actions builds and deploys the site. The root
`index.html` is generated only in the deployment output; do not maintain it by
hand. Nested `index.html` pages are included in the catalogue.

Links use each page's `<title>`, falling back to its relative filename when the
title is absent or blank. Links sort by relative path. Static files and assets
retain their paths; hidden directories (including `.github` tooling) are omitted.

Build locally with `uv` (it manages Python; no package dependencies are needed):

```sh
uv run --no-project --python 3.12 .github/scripts/build_site.py . _site
uv run --no-project --python 3.12 python -m http.server --directory _site
```

The builder replaces the output directory on every run, removing stale files.
`_site/` is ignored by Git. GitHub Pages must use **GitHub Actions** as its source.

Run the tests:

```sh
uv run --no-project --python 3.12 python -m unittest discover -s .github/tests -v
```

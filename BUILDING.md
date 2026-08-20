# Building and deploying the course website

The course website in `docs/` is **generated** from the session notebooks by `build.py`.
It is a plain static site — no server, no framework, nothing to run at view time — so it
deploys straight to GitHub Pages.

For the course itself, see [README.md](README.md).

## Building

```bash
pip install nbformat nbconvert Pillow
python build.py
```

This writes the complete site into `docs/`. To preview it locally:

```bash
python build.py --serve
```

Useful flags:

| Flag | What it does |
|---|---|
| `--notebooks PATH` | Read the session notebooks from somewhere else |
| `--skip-notebooks` | Rebuild only the home / part / credits pages (fast, for copy edits) |
| `--no-optimize` | Copy images verbatim instead of re-encoding them to WebP |

## How it works

`build.py` reads the notebooks from the `session 01/` … `session 19/` folders in this
repository, converts each to HTML with `nbconvert`, and wraps it in the site template.

Images referenced by the notebooks are copied into `docs/assets/img/` and their `<img>`
sources rewritten to relative paths, so the published site is entirely self-contained. They
are also downscaled to 1400px and re-encoded to WebP, which takes the site from roughly
97 MB to 22 MB.

The reading order — Home → Part 1 → its sessions → Part 2 → … → Credits — and every
previous/next link is derived from the `PARTS` list, so moving a session between parts only
requires editing that one list.

## Deploying to GitHub Pages

1. Commit the generated `docs/` directory (it is intentionally **not** gitignored).
2. In the repository: **Settings → Pages**.
3. Set **Source** to `Deploy from a branch`, branch `main`, folder **`/docs`**.
4. Save. The site appears at `https://<user>.github.io/<repo>/`.

`docs/.nojekyll` is generated automatically — it stops GitHub running Jekyll over the
output, which would otherwise ignore any file or directory beginning with an underscore.

## Editing the site content

All of the site copy lives in constants at the top of `build.py`:

| Constant | Controls |
|---|---|
| `PARTS` | Part names, which sessions belong to which part, blurbs, chips |
| `SESSIONS` | Session titles |
| `COMBINED` | Sessions tagged "Concept + Implementation" |
| `KAGGLE` | The "Open this session on Kaggle" link for each session |
| `PART_PAGES` | Each part page: its lede, the recap of the previous part, body copy |
| `HOME_AIM`, `PREREQS`, `LEARN_ITEMS` | The home page |
| `TOOLKIT`, `AUTHORS` | The credits page |

Visual design lives in `site/style.css`, which is copied to `docs/assets/style.css` on each
build. The palette, type scale and spacing are defined as CSS custom properties at the top
of that file.

## A note on rebuilds

WebP re-encoding is not byte-reproducible, so every full rebuild rewrites all 58 images even
when the notebooks have not changed. If that churn in git history becomes annoying, either
use `--skip-notebooks` for copy-only edits, or move the build into a GitHub Action and stop
committing `docs/` altogether.

# Sean Lu — macro trade ideas

A small, hand-built static site. Articles are Markdown files; `build.py` turns them into HTML. No framework, no platform, no third-party requests. Fonts and the math renderer are served from this repository.

```
site.yml                 ← name, tagline, URL, links, disclaimer
content/
  trades/                ← one .md file per trade idea
  postmortems/           ← one .md file per post-mortem
  images/                ← charts, screenshots, pictures
  about.md
charts/
  style.py               ← matplotlib style that matches the site
  example_call_spread.py ← example chart script
templates/               ← HTML layout (Jinja)
static/style.css         ← all styling; colours are at the top
build.py                 ← the whole build: ~380 lines
```

## One-time setup

1. Install Python 3.10+ and run `pip install -r requirements.txt`.
2. Edit `site.yml` with your name, tagline, URL and links.
3. Preview locally with `python build.py serve`, then open http://localhost:8000.

## Publish to GitHub Pages (free)

1. Create a GitHub repository named **`<your-username>.github.io`**. The site then lives at `https://<your-username>.github.io`.
2. Upload this folder to it (GitHub Desktop is easiest), or from a terminal:
   ```
   git init && git add . && git commit -m "Launch site"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-username>.github.io.git
   git push -u origin main
   ```
3. On GitHub, go to **Settings → Pages → Build and deployment → Source** and choose **GitHub Actions**.
4. Every push to `main` now rebuilds and publishes the site in about a minute. Progress shows in the **Actions** tab.

**Custom domain (optional, about $10–15 a year):** buy one (Cloudflare, Namecheap, Porkbun), enter it under **Settings → Pages → Custom domain**, add the DNS records GitHub shows you, and tick **Enforce HTTPS**. Then update `url` in `site.yml`.

**Get on Google:** add the site in [Google Search Console](https://search.google.com/search-console), verify it, and submit `https://<your-site>/sitemap.xml`.

## Writing

**New trade idea:**
```
python build.py new trade "Long USDJPY vol into BoJ"
```
This creates a dated file in `content/trades/` with the full template: ticket fields at the top, then sections for thesis, what's priced, the trade, risks and the review date. It starts as a draft. Remove `draft: true` when you're ready to publish.

**Closing a trade:** set `status: closed` and add `closed`, `exit` and `result` (for example `result: "+1.5R"`). The Trade Ideas page recalculates hit rate and total R automatically.

**New post-mortem:**
```
python build.py new postmortem "Review: USDJPY vol"
```
Set `trade:` to the trade's file name without `.md`. The two posts then link to each other.

**Delete a post:** delete its file. **Edit a post:** edit its file. Then commit and push.

## Formatting reference

| You want | Write |
|---|---|
| Heading | `## Thesis` |
| Bold / italic | `**bold**`, `*italic*` |
| Chart or picture with caption | `![Alt text](/images/file.svg "Caption under the image")` |
| Screenshot with a thin frame | `![Alt](/images/shot.png "Caption"){.bordered}` |
| Inline math | `\( K_1 + c \)` |
| Display math | `$$ \text{P\&L} = \max(F-K_1,0) - c $$` |
| Table | Standard Markdown pipes (see the example posts) |
| Footnote | `text[^1]` … `[^1]: The note.` |
| Quote | `> text` |

A single `$` is never treated as math, so `$100M notional` is safe.

## Charts

```
cd charts
python example_call_spread.py      # writes content/images/example-call-spread-payoff.svg
```
Copy that script for new charts. `style.apply()` gives every chart the site's look; `style.save(fig, "name")` writes an SVG into `content/images/`. Keep each chart's script so you can regenerate it with new data for the post-mortem.

## Changing the look

- **Colours:** the variables at the top of `static/style.css` (light and dark mode).
- **Reading width:** `--measure` in the same file.
- **Fonts:** `static/fonts/` plus the `@font-face` rules at the top of the CSS.
- **Layout:** `templates/`.

## Before launch

- [x] Example posts moved to `examples/`, where they're kept for reference but not published.
- [ ] Set `url` in `site.yml` to `https://<your-username>.github.io` (or your domain).
- [ ] Fill in `content/about.md`. The HTML comments mark what to replace.
- [ ] Optional: set your email or LinkedIn in `site.yml`.

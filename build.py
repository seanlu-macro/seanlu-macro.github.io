#!/usr/bin/env python3
"""
Static site builder.  content/*.md  ->  _site/*.html

  python build.py                      build the site into _site/
  python build.py serve                build, then preview at http://localhost:8000
  python build.py new trade "Title"    start a new trade idea from the template
  python build.py new postmortem "Title"

Everything the site does lives in this file, templates/ and static/style.css.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
OUT = ROOT / "_site"

SECTIONS = {
    "trades": {
        "title": "Trade Ideas",
        "intro": "Each idea is published before the outcome is known, with an "
                 "explicit entry, stop, target and the reason it could be wrong.",
    },
    "postmortems": {
        "title": "Post-Mortems",
        "intro": "Every closed idea gets a review, win or lose: was the thesis "
                 "right, was the trade right, and what would I do differently.",
    },
}

# Order and labels of the fields shown in the trade "ticket" box.
TICKET_FIELDS = [
    ("asset", "Asset class"),
    ("expression", "Expression"),
    ("entry", "Entry"),
    ("target", "Target"),
    ("stop", "Stop"),
    ("risk", "Risk"),
    ("horizon", "Horizon"),
    ("conviction", "Conviction"),
    ("closed", "Closed"),
    ("exit", "Exit"),
    ("result", "Result"),
]


# ─── Content model ────────────────────────────────────────────────

@dataclass
class Page:
    path: Path
    section: str              # "trades", "postmortems" or "" for standalone pages
    slug: str
    meta: dict
    body_md: str
    body_html: str = ""
    has_math: bool = False
    related: "Page | None" = field(default=None, repr=False)

    @property
    def title(self) -> str:
        return self.meta.get("title", self.slug)

    @property
    def date(self) -> dt.date | None:
        d = self.meta.get("date")
        if isinstance(d, dt.datetime):
            return d.date()
        if isinstance(d, str):
            return dt.date.fromisoformat(d)
        return d

    @property
    def url(self) -> str:
        return f"/{self.section}/{self.slug}/" if self.section else f"/{self.slug}/"

    @property
    def summary(self) -> str:
        return self.meta.get("summary", "")

    @property
    def status(self) -> str:
        return str(self.meta.get("status", "")).lower()

    @property
    def result_r(self) -> float | None:
        """Numeric result in R, parsed from e.g. '+1.6R' or '-1R'."""
        m = re.search(r"[+-−]?\d+(?:\.\d+)?", str(self.meta.get("result", "")))
        return float(m.group().replace("−", "-")) if m else None

    @property
    def ticket(self) -> list[tuple[str, str]]:
        return [(label, str(self.meta[k])) for k, label in TICKET_FIELDS
                if self.meta.get(k) not in (None, "")]


def read_page(path: Path, section: str) -> Page:
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        meta = yaml.safe_load(fm) or {}
    slug = meta.get("slug") or path.stem
    return Page(path=path, section=section, slug=slug, meta=meta, body_md=body.strip())


# ─── Markdown ─────────────────────────────────────────────────────

MD_EXTENSIONS = [
    "extra",            # tables, footnotes, fenced code, attr lists, md in html
    "sane_lists",
    "smarty",           # curly quotes, en/em dashes
    "toc",
    "pymdownx.arithmatex",   # math, rendered in the browser by KaTeX
    "pymdownx.tilde",        # ~~strikethrough~~
]
MD_CONFIG = {
    # Inline math is \( ... \) and block math is $$ ... $$.  Single $ is NOT math,
    # so "$100M notional" stays plain text.
    "pymdownx.arithmatex": {"generic": True, "inline_syntax": ["round"],
                            "block_syntax": ["dollar", "square", "begin"]},
    "toc": {"permalink": False},
}

# A paragraph holding only an image becomes a <figure>; its title becomes the caption.
#   ![Alt text](/images/chart.svg "Caption shown under the image")
FIGURE_RE = re.compile(r"<p>\s*(<img [^>]+?)\s*/?>\s*</p>")
TITLE_RE = re.compile(r'\s+title="([^"]*)"')
CLASS_RE = re.compile(r'\s+class="([^"]*)"')


def _figure(m: re.Match) -> str:
    img = m.group(1)
    cap = TITLE_RE.search(img)
    img = TITLE_RE.sub("", img)
    cls = CLASS_RE.search(img)
    fig_cls = f' class="{cls.group(1)}"' if cls else ""
    caption = f"<figcaption>{cap.group(1)}</figcaption>" if cap else ""
    return f'<figure{fig_cls}>{img} loading="lazy">{caption}</figure>'


def render_markdown(text: str) -> tuple[str, bool]:
    md = markdown.Markdown(extensions=MD_EXTENSIONS, extension_configs=MD_CONFIG)
    out = md.convert(text)
    out = FIGURE_RE.sub(_figure, out)
    # Wrap tables so wide ones scroll on phones instead of breaking the layout.
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace(
        "</table>", "</table></div>")
    return out, 'class="arithmatex"' in out


# ─── Build ────────────────────────────────────────────────────────

def load_content() -> tuple[dict[str, list[Page]], list[Page]]:
    sections: dict[str, list[Page]] = {}
    for name in SECTIONS:
        pages = [read_page(p, name) for p in sorted((CONTENT / name).glob("*.md"))]
        pages = [p for p in pages if not p.meta.get("draft")]
        pages.sort(key=lambda p: (p.date or dt.date.min), reverse=True)
        sections[name] = pages
    standalone = [read_page(p, "") for p in sorted(CONTENT.glob("*.md"))]
    standalone = [p for p in standalone if not p.meta.get("draft")]

    # Link each post-mortem to the trade it reviews (front matter: `trade: <slug>`).
    trades = {t.slug: t for t in sections["trades"]}
    for pm in sections["postmortems"]:
        t = trades.get(str(pm.meta.get("trade", "")))
        if t:
            pm.related, t.related = t, pm

    for page in [*standalone, *[p for ps in sections.values() for p in ps]]:
        page.body_html, page.has_math = render_markdown(page.body_md)
    return sections, standalone


def track_record(trades: list[Page]) -> dict:
    closed = [t for t in trades if t.status == "closed" and t.result_r is not None]
    wins = [t for t in closed if t.result_r > 0]
    total = sum(t.result_r for t in closed)
    return {
        "ideas": len(trades),
        "open": sum(1 for t in trades if t.status == "open"),
        "closed": len(closed),
        "hit_rate": f"{len(wins) / len(closed):.0%}" if closed else "—",
        "total_r": f"{total:+.1f}R" if closed else "—",
    }


def build() -> None:
    cfg = yaml.safe_load((ROOT / "site.yml").read_text(encoding="utf-8"))
    cfg["url"] = cfg["url"].rstrip("/")
    base = (cfg.get("base_path") or "").rstrip("/")

    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      autoescape=select_autoescape(["html"]))
    env.filters["fmtdate"] = lambda d: d.strftime("%-d %b %Y") if d else ""
    env.filters["isodate"] = lambda d: d.isoformat() if d else ""
    env.globals.update(site=cfg, sections=SECTIONS, year=dt.date.today().year)

    sections, standalone = load_content()

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "static", OUT / "static")
    if (CONTENT / "images").exists():
        shutil.copytree(CONTENT / "images", OUT / "images")

    urls: list[tuple[str, dt.date | None]] = []

    def write(url: str, template: str, **ctx) -> None:
        page_html = env.get_template(template).render(page_url=url, **ctx)
        if base:  # prefix root-relative links when hosted in a sub-folder
            page_html = re.sub(r'(href|src)="/(?!/)', rf'\1="{base}/', page_html)
        dest = OUT / url.strip("/") / "index.html" if url != "/" else OUT / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page_html, encoding="utf-8")

    write("/", "home.html", trades=sections["trades"],
          postmortems=sections["postmortems"])
    urls.append(("/", None))

    for name, pages in sections.items():
        write(f"/{name}/", "list.html", section=name, pages=pages,
              record=track_record(pages) if name == "trades" else None)
        urls.append((f"/{name}/", None))
        for p in pages:
            write(p.url, "post.html", page=p)
            urls.append((p.url, p.date))

    for p in standalone:
        write(p.url, "page.html", page=p)
        urls.append((p.url, p.date))

    # 404 page (GitHub Pages serves /404.html automatically)
    nf = env.get_template("404.html").render(page_url="/404.html")
    if base:
        nf = re.sub(r'(href|src)="/(?!/)', rf'\1="{base}/', nf)
    (OUT / "404.html").write_text(nf, encoding="utf-8")

    write_sitemap(cfg, base, urls)
    write_feed(cfg, base, sections)
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {cfg['url']}{base}/sitemap.xml\n")
    (OUT / ".nojekyll").write_text("")

    n = sum(len(v) for v in sections.values()) + len(standalone)
    print(f"Built {n} pages → {OUT.relative_to(ROOT)}/")


def write_sitemap(cfg: dict, base: str, urls) -> None:
    rows = []
    for url, date in urls:
        lastmod = f"<lastmod>{date.isoformat()}</lastmod>" if date else ""
        rows.append(f"  <url><loc>{cfg['url']}{base}{url}</loc>{lastmod}</url>")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")


def write_feed(cfg: dict, base: str, sections) -> None:
    items = sorted((p for ps in sections.values() for p in ps),
                   key=lambda p: p.date or dt.date.min, reverse=True)[:30]
    esc = html.escape
    entries = []
    for p in items:
        link = f"{cfg['url']}{base}{p.url}"
        pub = dt.datetime.combine(p.date, dt.time(12)).strftime(
            "%a, %d %b %Y %H:%M:%S +0000") if p.date else ""
        entries.append(
            f"<item><title>{esc(p.title)}</title><link>{link}</link>"
            f"<guid>{link}</guid><pubDate>{pub}</pubDate>"
            f"<description>{esc(p.summary)}</description></item>")
    (OUT / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
        f"<title>{esc(cfg['title'])}</title><link>{cfg['url']}{base}/</link>"
        f"<description>{esc(cfg['description'])}</description>"
        + "".join(entries) + "</channel></rss>\n", encoding="utf-8")


# ─── Helpers ──────────────────────────────────────────────────────

TEMPLATES = {
    "trade": """---
title: "{title}"
date: {date}
summary: "One sentence: the view and how you are expressing it."
status: open            # open | closed
asset: Rates            # Rates | FX | Equities | Commodities | Credit | Vol
expression: ""          # e.g. "Long SR3 Z6 97.00/97.50 call spread"
entry: ""
target: ""
stop: ""
risk: "1R = "           # what one unit of risk is, e.g. "1R = 10bp of a $100M book"
horizon: ""
conviction: Medium      # Low | Medium | High
# When the trade is closed, add:
# closed: YYYY-MM-DD
# exit: ""
# result: "+1.0R"
draft: true             # remove this line to publish
---

## Thesis

## What the market is pricing

## Why the market is wrong

## The trade

## Risks and what would prove me wrong

## Review date
""",
    "postmortem": """---
title: "{title}"
date: {date}
summary: "One sentence: what happened and the main lesson."
trade: ""               # file name of the trade idea, without .md
outcome: ""             # Win | Loss | Scratch
draft: true             # remove this line to publish
---

## Recap

## What happened

## Thesis right? Trade right?

## What I would do differently

## Lessons
""",
}


def new(kind: str, title: str) -> None:
    folder = {"trade": "trades", "postmortem": "postmortems"}[kind]
    today = dt.date.today().isoformat()
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    path = CONTENT / folder / f"{today}-{slug}.md"
    if path.exists():
        sys.exit(f"{path} already exists")
    path.write_text(TEMPLATES[kind].format(title=title.replace('"', "'"), date=today))
    print(f"Created {path.relative_to(ROOT)}  (draft — remove `draft: true` to publish)")


def serve(port: int = 8000) -> None:
    import functools
    import http.server
    build()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    print(f"Preview at http://localhost:{port}  (Ctrl+C to stop; rebuild to see edits)")
    http.server.ThreadingHTTPServer(("", port), handler).serve_forever()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        build()
    elif args[0] == "serve":
        serve()
    elif args[0] == "new" and len(args) == 3 and args[1] in ("trade", "postmortem"):
        new(args[1], args[2])
    else:
        sys.exit(__doc__)

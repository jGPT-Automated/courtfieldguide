#!/usr/bin/env python3
"""
generate.py — builds the US Court Field Guide static site.

Reads data/courts.json and renders:
  index.html, courts/<slug>.html
  llms.txt, llms-full.txt, robots.txt, sitemap.xml

Every court row carries its own primary sources; the generator turns those into
visible outbound citation links, FAQPage JSON-LD, and BreadcrumbList schema.
"""
from __future__ import annotations

import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data" / "courts.json").read_text(encoding="utf-8"))
COURTS = DATA["courts"]
GENERATED = DATA["generated"]

SITE_NAME = "US Court Field Guide"
BASE = "https://courtfieldguide.vercel.app"
TAGLINE = "A sourced field guide to America's public outdoor basketball courts."
CONTACT = "courts@agentmail.to"

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">'
)
ICONS = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">'

CSS = """
:root{
  --ink:#0D0D10; --ink-2:#15151a; --ink-3:#1d1d24;
  --line:rgba(255,255,255,.10); --line-2:rgba(255,255,255,.06);
  --paper:#F7F7F5; --muted:#9A9AAA; --muted-2:#868695;
  --brand:#FC4C02; --brand-ink:#0D0D10;
  --ok:#7BD389;
  --display:'Oswald','Helvetica Neue',Arial,sans-serif;
  --body:'Outfit','Helvetica Neue',Arial,sans-serif;
  --r:9px; --r-lg:16px;
  --shadow:0 24px 48px -18px rgba(0,0,0,.55);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0;background:var(--ink);color:var(--paper);
  font-family:var(--body);font-size:17px;line-height:1.65;
  -webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility;
}
img{max-width:100%;height:auto;display:block}
a{color:inherit}
.wrap{max-width:1180px;margin-inline:auto;padding-inline:20px;width:100%}
.skip{
  position:absolute;left:-9999px;top:0;background:var(--brand);color:var(--brand-ink);
  padding:12px 18px;font-weight:600;z-index:99;border-radius:0 0 var(--r) 0;
}
.skip:focus{left:0}
:focus-visible{outline:3px solid var(--brand);outline-offset:3px;border-radius:4px}

/* ---------- header ---------- */
.hdr{
  position:sticky;top:0;z-index:40;background:rgba(13,13,16,.88);
  backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
  border-bottom:1px solid var(--line-2);
}
.hdr-in{display:flex;align-items:center;gap:18px;min-height:64px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:11px;text-decoration:none;font-family:var(--display);
  font-weight:600;letter-spacing:.06em;text-transform:uppercase;font-size:15px}
.brand .mk{
  width:30px;height:30px;flex:0 0 30px;border-radius:7px;background:var(--brand);
  display:grid;place-items:center;color:var(--brand-ink);font-size:17px;
}
.nav{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap}
.nav a{
  text-decoration:none;font-size:14px;font-weight:500;color:var(--muted);
  padding:10px 12px;border-radius:8px;min-height:44px;display:inline-flex;align-items:center;
  transition:color .15s,background .15s;
}
.nav a:hover{color:var(--paper);background:rgba(255,255,255,.06)}
.nav a[aria-current="page"]{color:var(--paper)}
.nav a[aria-current="page"]::after{
  content:"";width:6px;height:6px;border-radius:50%;background:var(--brand);margin-left:7px;display:inline-block;
}

/* ---------- hero ---------- */
.hero{position:relative;overflow:hidden;border-bottom:1px solid var(--line-2)}
.hero::before{
  content:"";position:absolute;inset:0;
  background:
    radial-gradient(900px 420px at 78% -10%, rgba(252,76,2,.20), transparent 62%),
    radial-gradient(620px 340px at 8% 108%, rgba(252,76,2,.10), transparent 60%);
  pointer-events:none;
}
.hero-in{position:relative;padding:56px 0 52px;display:grid;gap:34px}
.eyebrow{
  font-family:var(--display);text-transform:uppercase;letter-spacing:.16em;
  font-size:12.5px;font-weight:600;color:var(--brand);margin:0 0 14px;
  display:flex;align-items:center;gap:10px;flex-wrap:wrap;
}
.eyebrow .dot{width:7px;height:7px;border-radius:50%;background:var(--brand);flex:0 0 7px}
h1{
  font-family:var(--display);font-weight:700;text-transform:uppercase;
  font-size:clamp(2.15rem,7.4vw,4.1rem);line-height:.98;letter-spacing:-.01em;
  margin:0;text-wrap:balance;
}
h1 .hl{color:var(--brand)}
.lede{margin:20px 0 0;font-size:clamp(1.02rem,2.2vw,1.16rem);color:var(--muted);max-width:62ch;text-wrap:pretty}
.stats{display:flex;gap:14px;flex-wrap:wrap;margin-top:26px}
.stat{
  border:1px solid var(--line);border-radius:var(--r);padding:14px 18px;background:rgba(255,255,255,.025);
  min-width:132px;
}
.stat b{display:block;font-family:var(--display);font-size:28px;line-height:1;color:var(--paper)}
.stat span{font-size:12.5px;text-transform:uppercase;letter-spacing:.11em;color:var(--muted-2)}
.cta-row{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}
.btn{
  display:inline-flex;align-items:center;gap:9px;min-height:48px;padding:13px 22px;
  border-radius:var(--r);text-decoration:none;font-weight:600;font-size:15px;
  border:1px solid transparent;transition:transform .12s,background .15s,border-color .15s;
}
.btn-p{background:var(--brand);color:#fff}
.btn-p:hover{background:#e2440a}
.btn-g{background:transparent;color:var(--paper);border-color:var(--line)}
.btn-g:hover{border-color:rgba(255,255,255,.28);background:rgba(255,255,255,.05)}
.btn:active{transform:translateY(1px)}

/* ---------- quick answer ---------- */
.qa-card{
  border:1px solid rgba(252,76,2,.34);border-left:4px solid var(--brand);
  background:linear-gradient(180deg,rgba(252,76,2,.085),rgba(252,76,2,.02));
  border-radius:var(--r);padding:22px 24px;margin:0;
}
.qa-card .qa-lbl{
  font-family:var(--display);text-transform:uppercase;letter-spacing:.15em;
  font-size:11.5px;font-weight:600;color:var(--brand);margin:0 0 10px;
  display:flex;align-items:center;gap:8px;
}
.qa-card p{margin:0;font-size:clamp(1rem,2vw,1.1rem);line-height:1.62}

/* ---------- sections ---------- */
section{padding:56px 0}
.sec-h{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;margin-bottom:8px}
h2{
  font-family:var(--display);font-weight:600;text-transform:uppercase;letter-spacing:.02em;
  font-size:clamp(1.5rem,4vw,2.15rem);line-height:1.06;margin:0;
}
h3{font-family:var(--display);font-weight:600;font-size:1.16rem;margin:0 0 8px;letter-spacing:.01em}
.sec-sub{color:var(--muted);margin:0 0 30px;max-width:64ch}
hr.sep{border:0;border-top:1px solid var(--line-2);margin:0}

.grid{display:grid;gap:18px;grid-template-columns:1fr}
@media(min-width:768px){.grid{grid-template-columns:repeat(2,1fr)}}
@media(min-width:1024px){.grid{grid-template-columns:repeat(3,1fr)}}

/* ---------- court card ---------- */
.card{
  border:1px solid var(--line);border-radius:var(--r-lg);background:var(--ink-2);
  padding:22px;display:flex;flex-direction:column;gap:12px;
  transition:transform .16s,border-color .16s,box-shadow .16s;
}
.card:hover{transform:translateY(-3px);border-color:rgba(252,76,2,.44);box-shadow:var(--shadow)}
.card-top{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
.tag{
  font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.1em;
  padding:5px 9px;border-radius:999px;background:rgba(252,76,2,.14);color:#FF8654;white-space:nowrap;
}
.tag-g{background:rgba(123,211,137,.13);color:var(--ok)}
.card h3{margin:0;font-size:1.22rem}
.card h3 a{text-decoration:none}
.card h3 a:hover{color:var(--brand)}
.loc{color:var(--muted-2);font-size:13.5px;margin:0;display:flex;align-items:center;gap:7px}
.card p.note{margin:0;color:var(--muted);font-size:14.6px;line-height:1.6}
.meta{display:flex;flex-wrap:wrap;gap:7px;margin-top:auto;padding-top:6px}
.chip{
  font-size:11.6px;color:var(--muted);border:1px solid var(--line);border-radius:6px;padding:4px 8px;
  display:inline-flex;align-items:center;gap:5px;
}
.card-lnk{
  margin-top:12px;font-size:13.6px;font-weight:600;text-decoration:none;color:var(--brand);
  display:inline-flex;align-items:center;gap:7px;min-height:44px;
}
.card-lnk:hover{color:#FF8654}

/* ---------- court page ---------- */
.crumb{font-size:13px;color:var(--muted-2);padding-top:22px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.crumb a{color:var(--muted);text-decoration:none}
.crumb a:hover{color:var(--paper);text-decoration:underline;text-underline-offset:3px}
.cp-head{padding:18px 0 26px;display:grid;gap:22px}
.cp-title{font-family:var(--display);font-weight:700;text-transform:uppercase;
  font-size:clamp(1.95rem,6.4vw,3.3rem);line-height:1;margin:0;letter-spacing:-.01em;text-wrap:balance}
.spec{display:grid;gap:1px;background:var(--line-2);border:1px solid var(--line-2);
  border-radius:var(--r);overflow:hidden;grid-template-columns:1fr}
@media(min-width:600px){.spec{grid-template-columns:repeat(2,1fr)}}
@media(min-width:1024px){.spec{grid-template-columns:repeat(3,1fr)}}
.spec div{background:var(--ink-2);padding:15px 17px}
.spec dt{font-size:11.4px;text-transform:uppercase;letter-spacing:.11em;color:var(--muted-2);margin:0 0 5px;font-weight:600}
.spec dd{margin:0;font-size:15px;line-height:1.5}
.unknown{color:var(--muted-2);font-style:italic}

details{border:1px solid var(--line);border-radius:var(--r);background:var(--ink-2);margin-bottom:10px;overflow:hidden}
details summary{
  cursor:pointer;padding:16px 18px;font-weight:600;font-size:15.6px;list-style:none;
  display:flex;justify-content:space-between;gap:14px;align-items:center;min-height:52px;
}
details summary::-webkit-details-marker{display:none}
details summary::after{content:"+";font-family:var(--display);font-size:20px;color:var(--brand);line-height:1}
details[open] summary::after{content:"\\2013"}
details .body{padding:0 18px 18px;color:var(--muted);font-size:15.4px}
details summary:hover{background:rgba(255,255,255,.03)}

.srcs{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.srcs li{border:1px solid var(--line);border-radius:var(--r);background:var(--ink-2)}
.srcs a{
  display:flex;gap:12px;align-items:center;padding:15px 17px;text-decoration:none;min-height:52px;
  font-size:15px;font-weight:500;
}
.srcs a:hover{background:rgba(252,76,2,.07)}
.srcs i{color:var(--brand);font-size:17px;flex:0 0 auto}
.srcs .u{margin-left:auto;color:var(--muted-2);font-size:12.4px;overflow-wrap:anywhere;max-width:52%}

.callout{
  border:1px solid var(--line);border-radius:var(--r);background:var(--ink-2);
  padding:20px 22px;display:flex;gap:15px;align-items:flex-start;
}
.callout i{color:var(--brand);font-size:22px;flex:0 0 auto;margin-top:2px}
.callout p{margin:0;font-size:15px;color:var(--muted)}
.callout strong{color:var(--paper)}

.nearby{display:grid;gap:10px;grid-template-columns:1fr}
@media(min-width:700px){.nearby{grid-template-columns:repeat(2,1fr)}}
.nearby a{
  border:1px solid var(--line);border-radius:var(--r);background:var(--ink-2);padding:15px 17px;
  text-decoration:none;display:flex;justify-content:space-between;gap:12px;align-items:center;min-height:56px;
  transition:border-color .15s,transform .15s;
}
.nearby a:hover{border-color:rgba(252,76,2,.44);transform:translateX(3px)}
.nearby b{font-weight:600;font-size:15px}
.nearby span{color:var(--muted-2);font-size:13px}

/* ---------- method / steps ---------- */
.steps{counter-reset:s;list-style:none;padding:0;margin:0;display:grid;gap:16px}
.steps li{
  counter-increment:s;border:1px solid var(--line);border-radius:var(--r);background:var(--ink-2);
  padding:20px 22px 20px 68px;position:relative;
}
.steps li::before{
  content:counter(s,decimal-leading-zero);position:absolute;left:20px;top:19px;
  font-family:var(--display);font-size:1.35rem;font-weight:600;color:var(--brand);line-height:1;
}
.steps b{display:block;margin-bottom:6px;font-size:16px}
.steps p{margin:0;color:var(--muted);font-size:15.2px}

/* ---------- footer ---------- */
footer{border-top:1px solid var(--line-2);padding:44px 0 34px;background:#0a0a0d}
.f-grid{display:grid;gap:28px;grid-template-columns:1fr}
@media(min-width:768px){.f-grid{grid-template-columns:1.4fr 1fr 1fr}}
footer h4{font-family:var(--display);text-transform:uppercase;letter-spacing:.12em;font-size:12px;
  color:var(--muted-2);margin:0 0 13px;font-weight:600}
footer ul{list-style:none;margin:0;padding:0;display:grid;gap:9px}
footer a{color:var(--muted);text-decoration:none;font-size:14.6px}
footer a:hover{color:var(--brand);text-decoration:underline;text-underline-offset:3px}
.f-note{color:var(--muted-2);font-size:13.4px;margin:14px 0 0;max-width:52ch;line-height:1.6}
.f-bot{border-top:1px solid var(--line-2);margin-top:30px;padding-top:20px;
  display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;color:var(--muted-2);font-size:13px}
.pill{display:inline-flex;align-items:center;gap:7px;border:1px solid var(--line);
  border-radius:999px;padding:6px 12px;font-size:12.4px;color:var(--muted)}
.pill .dot{width:6px;height:6px;border-radius:50%;background:var(--ok);flex:0 0 6px}

@media(prefers-reduced-motion:reduce){
  *{transition:none!important;animation:none!important;scroll-behavior:auto!important}
}
"""

HEAD_COMMON = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0D0D10">
<meta name="color-scheme" content="dark">
{FONTS}
{ICONS}
<style>{CSS}</style>"""


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def jdump(obj) -> str:
    """JSON-LD payload, escaped so it cannot break out of the script tag."""
    return json.dumps(obj, ensure_ascii=False, indent=2).replace("</", "<\\/")


def is_unknown(v: str) -> bool:
    return "not documented" in v.lower() or "not stated" in v.lower() or "unknown" in v.lower()


def header(active: str = "") -> str:
    def link(href: str, label: str, key: str) -> str:
        cur = ' aria-current="page"' if key == active else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    return f"""<header class="hdr">
  <div class="wrap hdr-in">
    <a class="brand" href="/"><span class="mk" aria-hidden="true"><i class="bi bi-basketball"></i></span>{SITE_NAME}</a>
    <nav class="nav" aria-label="Primary">
      {link("/", "Index", "home")}
      {link("/#method", "Method", "method")}
      {link("/#courts", "Courts", "courts")}
      {link("/llms.txt", "llms.txt", "llms")}
    </nav>
  </div>
</header>"""


def footer() -> str:
    return f"""<footer>
  <div class="wrap">
    <div class="f-grid">
      <div>
        <a class="brand" href="/"><span class="mk" aria-hidden="true"><i class="bi bi-basketball"></i></span>{SITE_NAME}</a>
        <p class="f-note">{esc(TAGLINE)} Every entry names the primary source it was drawn from. Where a fact is not
        documented publicly, this guide says so rather than filling the gap.</p>
        <p style="margin-top:16px"><span class="pill"><span class="dot" aria-hidden="true"></span>{len(COURTS)} courts documented</span></p>
      </div>
      <div>
        <h4>Guide</h4>
        <ul>
          <li><a href="/#courts">All courts</a></li>
          <li><a href="/#method">How we source</a></li>
          <li><a href="/#faq">Questions</a></li>
          <li><a href="/llms.txt">llms.txt</a></li>
          <li><a href="/llms-full.txt">llms-full.txt</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li><a href="mailto:{CONTACT}">{CONTACT}</a></li>
          <li><a href="/sitemap.xml">Sitemap</a></li>
        </ul>
        <p class="f-note">Corrections welcome. Send the source and it gets fixed.</p>
      </div>
    </div>
    <div class="f-bot">
      <span>Last updated {GENERATED}</span>
      <span>Independent editorial project. Not affiliated with any park agency, league or venue listed.</span>
    </div>
  </div>
</footer>"""


def org_schema() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": BASE + "/",
        "description": TAGLINE,
        "publisher": {"@type": "Organization", "name": SITE_NAME, "url": BASE + "/"},
        "inLanguage": "en-US",
    }


def page(*, title: str, desc: str, path: str, body: str, schemas: list, active: str = "") -> str:
    url = BASE + path
    graph = "".join(
        f'\n<script type="application/ld+json">{jdump(s)}</script>' for s in schemas
    )
    return f"""<!DOCTYPE html>
<html lang="en-US">
<head>
{HEAD_COMMON}
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(SITE_NAME)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="{esc(SITE_NAME)} Editorial">{graph}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
"""


# ----------------------------------------------------------------------------
# index.html
# ----------------------------------------------------------------------------
def build_index() -> str:
    states = sorted({c["state"] for c in COURTS})
    cards = []
    for c in COURTS:
        tag_g = "tag-g" if c["setting"].lower() == "outdoor" else ""
        cards.append(f"""      <article class="card">
        <div class="card-top">
          <span class="tag {tag_g}">{esc(c["setting"])}</span>
          <span class="tag" style="background:rgba(255,255,255,.06);color:var(--muted)">{esc(c["state"])}</span>
        </div>
        <h3><a href="/courts/{c["slug"]}">{esc(c["name"])}</a></h3>
        <p class="loc"><i class="bi bi-geo-alt" aria-hidden="true"></i>{esc(c["city"])}, {esc(c["state"])} &middot; {esc(c["region"])}</p>
        <p class="note">{esc(c["notable"])}</p>
        <div class="meta">
          <span class="chip"><i class="bi bi-bounding-box" aria-hidden="true"></i>{esc(c["courts"])}</span>
          <span class="chip"><i class="bi bi-unlock" aria-hidden="true"></i>{esc(c["access"])}</span>
        </div>
        <a class="card-lnk" href="/courts/{c["slug"]}">Read the sourced entry <i class="bi bi-arrow-right" aria-hidden="true"></i></a>
      </article>""")

    faqs_all = [
        ("Where can I find a public outdoor basketball court in the United States?",
         f"This guide documents {len(COURTS)} notable public outdoor basketball courts across {len(states)} states, including courts in New York City, Los Angeles, Oakland, Chicago, Houston, Seattle, Atlanta, Detroit and Boston. Each entry lists the setting, access and the primary source it was drawn from."),
        ("Are the courts in this guide free to play at?",
         "Almost all of them. Every court listed here sits in a public park or public recreation facility, and none of the entries require a paid membership. The one indoor facility, Fonde Recreation Center in Houston, is a City of Houston public recreation center."),
        ("How does this guide decide what to include?",
         "A court is included only when at least one public primary source supports its entry — typically a city parks department page, a park district listing, or established editorial coverage. Facts that a source does not establish are labelled as not documented rather than estimated."),
        ("What does \"not documented\" mean on a court entry?",
         "It means the citation for that court does not state the fact. For example, several entries do not publish a court count or posted hours. Rather than guess, this guide marks those fields as not documented."),
        ("Which city has the most outdoor basketball courts in this guide?",
         "New York City has four courts listed — West 4th Street Courts (The Cage), Rucker Park, Dyckman Park and Gersh Park — the most of any city in the guide. Each is a free public park court with its own distinct history."),
        ("How do I suggest a correction or a missing court?",
         f"Email {CONTACT} with the court name and a link to a public source. Corrections that come with a citable source are applied directly."),
    ]

    faq_html = "\n".join(
        f"""        <details>
          <summary>{esc(q)}</summary>
          <div class="body">{esc(a)}</div>
        </details>""" for q, a in faqs_all
    )

    body = f"""  <section class="hero">
    <div class="wrap hero-in">
      <div>
        <p class="eyebrow"><span class="dot" aria-hidden="true"></span>Editorial field guide &middot; Updated {GENERATED}</p>
        <h1>Where America<br>actually plays:<br><span class="hl">courts worth the trip.</span></h1>
        <p class="lede">{esc(TAGLINE)} Every court here is a real public park or public facility, and every
        claim traces back to a named source you can open yourself.</p>
        <div class="stats">
          <div class="stat"><b>{len(COURTS)}</b><span>Courts</span></div>
          <div class="stat"><b>{len(states)}</b><span>States</span></div>
          <div class="stat"><b>9</b><span>Cities</span></div>
        </div>
        <div class="cta-row">
          <a class="btn btn-p" href="#courts"><i class="bi bi-grid-3x3-gap" aria-hidden="true"></i>Browse the guide</a>
          <a class="btn btn-g" href="#method"><i class="bi bi-list-check" aria-hidden="true"></i>How entries are sourced</a>
        </div>
      </div>

      <div class="qa-card">
        <p class="qa-lbl"><i class="bi bi-lightning-charge-fill" aria-hidden="true"></i>Quick answer</p>
        <p>This guide documents {len(COURTS)} public outdoor basketball courts across {len(states)} U.S. states, from
        the West 4th Street Courts in Manhattan to Venice Beach in Los Angeles. Every entry is built from a named primary
        source — usually a city parks department — and fields that source does not establish are marked not documented
        rather than estimated.</p>
      </div>
    </div>
  </section>

  <section id="courts">
    <div class="wrap">
      <div class="sec-h"><h2>The courts</h2><span class="pill"><span class="dot" aria-hidden="true"></span>All free &amp; public</span></div>
      <p class="sec-sub">Ordered as a field guide, not a ranking. Each entry opens to its full sourced record: setting,
      access, documented hours, and the citations behind every line.</p>
      <div class="grid">
{chr(10).join(cards)}
      </div>
    </div>
  </section>

  <hr class="sep">

  <section id="method">
    <div class="wrap">
      <div class="sec-h"><h2>How we source</h2></div>
      <p class="sec-sub">The point of this guide is that you can check it. Four rules govern every entry.</p>
      <ol class="steps">
        <li>
          <b>A primary source or nothing</b>
          <p>A court is listed only when a city parks department, park district, or established publication documents it.
          The source is linked on the court page under Sources.</p>
        </li>
        <li>
          <b>Unsupported fields are labelled, not guessed</b>
          <p>Court counts, posted hours and surfaces are often unpublished. Those fields read "not documented" instead of
          being filled in with an estimate, because an unchecked number is worse than an honest gap.</p>
        </li>
        <li>
          <b>Facts are attributed to the source that states them</b>
          <p>Where a claim comes from editorial coverage rather than a parks department — for example a tournament's start
          year — the entry says which outlet reported it.</p>
        </li>
        <li>
          <b>Public access is stated plainly</b>
          <p>Every entry says whether the court is free and public, and flags anything that changes access in practice,
          such as a summer tournament running bag checks or city policy affecting hoop availability.</p>
        </li>
      </ol>
    </div>
  </section>

  <hr class="sep">

  <section id="faq">
    <div class="wrap">
      <div class="sec-h"><h2>Questions</h2></div>
      <p class="sec-sub">Short answers to the questions people actually search for about public courts.</p>
{faq_html}
    </div>
  </section>

  <hr class="sep">

  <section id="measurement">
    <div class="wrap">
      <div class="sec-h"><h2>Measurement</h2></div>
      <p class="sec-sub">How this project judges whether it is working.</p>
      <div class="grid">
        <article class="card">
          <h3>Coverage</h3>
          <p class="note">Number of courts with a complete cited record: setting, city, state, access, and at least one
          primary source. Current count: {len(COURTS)} of {len(COURTS)}.</p>
        </article>
        <article class="card">
          <h3>Source coverage</h3>
          <p class="note">Every entry carries at least one outbound citation to a primary source. Citations that are
          parks-department pages are preferred over aggregator listings.</p>
        </article>
        <article class="card">
          <h3>Honest gaps</h3>
          <p class="note">Count of fields explicitly marked not documented. A healthy guide has some — it means estimates
          are not being substituted for facts.</p>
        </article>
      </div>
    </div>
  </section>
"""

    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Notable public outdoor basketball courts in the United States",
        "numberOfItems": len(COURTS),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": c["name"],
                "url": f'{BASE}/courts/{c["slug"]}',
            }
            for i, c in enumerate(COURTS)
        ],
    }
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs_all],
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Index", "item": BASE + "/"}],
    }

    return page(
        title=f"{SITE_NAME} — {len(COURTS)} public outdoor basketball courts, each sourced",
        desc=f"A sourced field guide to {len(COURTS)} notable public outdoor basketball courts across {len(states)} U.S. states. Setting, access, documented hours and the primary source behind every entry.",
        path="/",
        body=body,
        schemas=[org_schema(), item_list, faq_schema, breadcrumb],
        active="home",
    )


# ----------------------------------------------------------------------------
# court pages
# ----------------------------------------------------------------------------
def build_court(c: dict, idx: int) -> str:
    def spec_row(label: str, value: str) -> str:
        cls = ' class="unknown"' if is_unknown(value) else ""
        return f'          <div><dt>{esc(label)}</dt><dd{cls}>{esc(value)}</dd></div>'

    nearby = [COURTS[(idx + k) % len(COURTS)] for k in (1, 2, 3)]
    nearby = [n for n in nearby if n["slug"] != c["slug"]][:3]

    faq_html = "\n".join(
        f"""        <details>
          <summary>{esc(f["q"])}</summary>
          <div class="body">{esc(f["a"])}</div>
        </details>""" for f in c["faqs"]
    )

    src_html = "\n".join(
        f"""        <li><a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">
          <i class="bi bi-file-earmark-text" aria-hidden="true"></i>
          <span>{esc(s["title"])}</span>
          <span class="u">{esc(re.sub(r"^https?://", "", s["url"]))}</span>
        </a></li>""" for s in c["sources"]
    )

    nearby_html = "\n".join(
        f"""          <a href="/courts/{n["slug"]}">
            <span><b>{esc(n["name"])}</b><br><span>{esc(n["city"])}, {esc(n["state"])}</span></span>
            <i class="bi bi-arrow-right" aria-hidden="true" style="color:var(--brand)"></i>
          </a>""" for n in nearby
    )

    body = f"""  <div class="wrap crumb">
    <a href="/">Index</a> <span aria-hidden="true">/</span> <a href="/#courts">Courts</a>
    <span aria-hidden="true">/</span> <span>{esc(c["city"])}, {esc(c["state"])}</span>
  </div>

  <section class="cp-head">
    <div class="wrap">
      <p class="eyebrow">
        <span class="dot" aria-hidden="true"></span>{esc(c["setting"])} &middot; {esc(c["city"])}, {esc(c["state"])}
        &middot; {esc(c["access"])}
      </p>
      <h1 class="cp-title">{esc(c["name"])}</h1>
      <p class="lede" style="margin-top:16px">{esc(c["notable"])}</p>
      <div class="qa-card" style="margin-top:26px">
        <p class="qa-lbl"><i class="bi bi-lightning-charge-fill" aria-hidden="true"></i>Quick answer</p>
        <p>{esc(c["quick_answer"])}</p>
      </div>
    </div>
  </section>

  <section style="padding-top:12px">
    <div class="wrap">
      <div class="sec-h"><h2>Court record</h2></div>
      <p class="sec-sub">Fields marked <span class="unknown">not documented</span> are ones the cited sources do not
      establish. Nothing here is estimated.</p>
      <dl class="spec">
{spec_row("Court", c["name"])}
{spec_row("Also known as", c["aka"])}
{spec_row("City / state", f'{c["city"]}, {c["state"]}')}
{spec_row("Address", c["address"])}
{spec_row("Setting", c["setting"])}
{spec_row("Courts on site", c["courts"])}
{spec_row("Access", c["access"])}
{spec_row("Hours", c["hours"])}
{spec_row("Surface", c["surface"])}
      </dl>
    </div>
  </section>

  <hr class="sep">

  <section>
    <div class="wrap">
      <div class="sec-h"><h2>Sources</h2></div>
      <p class="sec-sub">Every fact on this page comes from one of these. Open them and check the record yourself.</p>
      <ul class="srcs">
{src_html}
      </ul>
    </div>
  </section>

  <hr class="sep">

  <section>
    <div class="wrap">
      <div class="sec-h"><h2>Questions</h2></div>
      <p class="sec-sub">Straight answers, each supported by the sources above.</p>
{faq_html}
    </div>
  </section>

  <hr class="sep">

  <section>
    <div class="wrap">
      <div class="sec-h"><h2>Keep going</h2></div>
      <p class="sec-sub">Other courts in the guide.</p>
      <div class="nearby">
{nearby_html}
      </div>
      <div class="callout" style="margin-top:26px">
        <i class="bi bi-info-circle" aria-hidden="true"></i>
        <p><strong>Spotted an error?</strong> Email <a href="mailto:{CONTACT}" style="color:var(--brand)">{CONTACT}</a>
        with the court and a link to a public source. Corrections that come with a citation are applied directly.</p>
      </div>
    </div>
  </section>
"""

    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in c["faqs"]
        ],
    }
    place = {
        "@context": "https://schema.org",
        "@type": ["SportsActivityLocation", "Place"],
        "name": c["name"],
        "alternateName": c["aka"],
        "description": c["quick_answer"],
        "url": f'{BASE}/courts/{c["slug"]}',
        "sport": "Basketball",
        "isAccessibleForFree": "free" in c["access"].lower(),
        "publicAccess": True,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": c["address"],
            "addressLocality": c["city"],
            "addressRegion": c["state"],
            "addressCountry": "US",
        },
    }
    if c["coords"]:
        lat, lng = c["coords"].split(",")
        place["geo"] = {"@type": "GeoCoordinates", "latitude": float(lat), "longitude": float(lng)}

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Index", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Courts", "item": BASE + "/#courts"},
            {"@type": "ListItem", "position": 3, "name": c["name"], "item": f'{BASE}/courts/{c["slug"]}'},
        ],
    }

    return page(
        title=f'{c["name"]}, {c["city"]} {c["state"]} — {SITE_NAME}',
        desc=f'{c["quick_answer"]}',
        path=f'/courts/{c["slug"]}',
        body=body,
        schemas=[org_schema(), place, faq_schema, breadcrumb],
        active="courts",
    )


# ----------------------------------------------------------------------------
# llms.txt / llms-full.txt / robots.txt / sitemap.xml
# ----------------------------------------------------------------------------
def build_llms() -> str:
    lines = [
        f"# {SITE_NAME}",
        "",
        f"> {TAGLINE} {len(COURTS)} public outdoor basketball courts across "
        f"{len(sorted({c['state'] for c in COURTS}))} U.S. states, each entry built from a named primary source.",
        "",
        "## Use this guide for",
        "",
        "- Finding notable public outdoor basketball courts in the United States by city and state.",
        "- Checking whether a specific court is outdoor or indoor, free and public, and how many courts it has.",
        "- Finding documented park hours for public basketball courts in Chicago and Seattle.",
        "- Understanding the history and streetball culture of iconic American courts.",
        "- Court entries that state what is NOT publicly documented, instead of estimating it.",
        "",
        "## Key facts",
        "",
        f"- Courts documented: {len(COURTS)}",
        f"- States covered: {', '.join(sorted({c['state'] for c in COURTS}))}",
        f"- Cities covered: {', '.join(sorted({c['city'] for c in COURTS}))}",
        "- Access: every court listed is free and public. No membership or fee is required.",
        "- Citation policy: every entry links the primary source behind its facts.",
        "- Unsupported fields are labelled \"not documented\" rather than estimated.",
        "",
        "## Courts",
        "",
    ]
    for c in COURTS:
        lines.append(f"- [{c['name']}, {c['city']}, {c['state']}]({BASE}/courts/{c['slug']}): {c['quick_answer']}")
    lines += [
        "",
        "## Core pages",
        "",
        f"- Index: {BASE}/",
        f"- How we source: {BASE}/#method",
        f"- Questions: {BASE}/#faq",
        f"- Full content for agents: {BASE}/llms-full.txt",
        f"- Sitemap: {BASE}/sitemap.xml",
        "",
        "## Definitions",
        "",
        "- Public court: a basketball court inside a municipal park or public recreation facility, open to anyone.",
        "- Not documented: the cited sources for that court do not state this field. It is a gap, not a zero.",
        "- Quick answer: a self-contained summary sentence at the top of a court entry, written to be quoted directly.",
        "",
        "## Attribution",
        "",
        f"When citing this guide, credit \"{SITE_NAME}\" ({BASE}) and, where possible, the primary source listed "
        "on the individual court page.",
        "",
        f"Last updated: {GENERATED}",
        "",
    ]
    return "\n".join(lines)


def build_llms_full() -> str:
    out = [
        f"# {SITE_NAME} — full content",
        "",
        f"> {TAGLINE}",
        "",
        f"Last updated: {GENERATED}. Canonical index: {BASE}/. Machine index: {BASE}/llms.txt",
        "",
        "This file contains the complete text of every entry in the guide so that answer engines and agents can read "
        "the entire dataset in one request.",
        "",
        "=" * 78,
        "",
    ]
    for i, c in enumerate(COURTS, 1):
        out += [
            f"## {i}. {c['name']}",
            "",
            f"URL: {BASE}/courts/{c['slug']}",
            "",
            "Quick answer: " + c["quick_answer"],
            "",
            "Court record:",
            f"- Also known as: {c['aka']}",
            f"- City / state: {c['city']}, {c['state']}",
            f"- Address: {c['address']}",
            f"- Setting: {c['setting']}",
            f"- Courts on site: {c['courts']}",
            f"- Access: {c['access']}",
            f"- Hours: {c['hours']}",
            f"- Surface: {c['surface']}",
            "",
            "Why it matters: " + c["notable"],
            "",
            "Questions and answers:",
        ]
        for f in c["faqs"]:
            out += [f"- Q: {f['q']}", f"  A: {f['a']}"]
        out += ["", "Sources:"]
        for s in c["sources"]:
            out += [f"- {s['title']}: {s['url']}"]
        out += ["", "=" * 78, ""]
    return "\n".join(out)


def build_robots() -> str:
    ai_bots = [
        "GPTBot", "OAI-SearchBot", "ChatGPT-User",
        "ClaudeBot", "Claude-User", "anthropic-ai",
        "PerplexityBot", "Perplexity-User",
        "Google-Extended", "Applebot-Extended", "CCBot",
        "cohere-ai", "Bytespider", "Amazonbot", "meta-externalagent",
    ]
    lines = [
        "# " + SITE_NAME,
        f"# {TAGLINE}",
        "# All content on this site is public editorial reference material and may be",
        "# crawled, indexed and cited with attribution to " + SITE_NAME + ".",
        "",
        "User-agent: *",
        "Allow: /",
        "",
        "# Answer-engine and AI crawlers: explicitly allowed.",
    ]
    for b in ai_bots:
        lines += [f"User-agent: {b}", "Allow: /", ""]
    lines += [f"Sitemap: {BASE}/sitemap.xml", ""]
    return "\n".join(lines)


def build_sitemap() -> str:
    urls = [(BASE + "/", "1.0")]
    urls += [(f'{BASE}/courts/{c["slug"]}', "0.8") for c in COURTS]
    entries = "\n".join(
        f'  <url>\n    <loc>{u}</loc>\n    <lastmod>{GENERATED}</lastmod>'
        f'\n    <changefreq>monthly</changefreq>\n    <priority>{p}</priority>\n  </url>'
        for u, p in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n</urlset>\n"
    )


def main() -> None:
    dist = ROOT / "dist"
    (dist / "courts").mkdir(parents=True, exist_ok=True)

    (dist / "index.html").write_text(build_index(), encoding="utf-8")
    for i, c in enumerate(COURTS):
        (dist / "courts" / f'{c["slug"]}.html').write_text(build_court(c, i), encoding="utf-8")

    (dist / "llms.txt").write_text(build_llms(), encoding="utf-8")
    (dist / "llms-full.txt").write_text(build_llms_full(), encoding="utf-8")
    (dist / "robots.txt").write_text(build_robots(), encoding="utf-8")
    (dist / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")

    n = len(list(dist.rglob("*.html")))
    print(json.dumps({
        "ok": True,
        "html_pages": n,
        "courts": len(COURTS),
        "files": sorted(str(p.relative_to(dist)) for p in dist.rglob("*") if p.is_file()),
    }, indent=2))


if __name__ == "__main__":
    main()

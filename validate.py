#!/usr/bin/env python3
"""Validate the built site: JSON-LD parses, required machine files exist, no secrets."""
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

DIST = pathlib.Path(__file__).resolve().parent / "dist"
problems, notes = [], []

# 1. every JSON-LD block must parse
html_files = sorted(DIST.rglob("*.html"))
for p in html_files:
    src = p.read_text(encoding="utf-8")
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, re.S)
    if not blocks:
        problems.append(f"{p.relative_to(DIST)}: no JSON-LD")
    for i, b in enumerate(blocks):
        try:
            json.loads(b)
        except Exception as e:
            problems.append(f"{p.relative_to(DIST)}: JSON-LD block {i} invalid: {e}")
    for need in ('<meta name="description"', 'rel="canonical"', '<title>', 'class="qa-card"'):
        if need not in src:
            problems.append(f"{p.relative_to(DIST)}: missing {need}")
notes.append(f"HTML pages checked: {len(html_files)}")

# 2. machine files
for f in ("llms.txt", "llms-full.txt", "robots.txt", "sitemap.xml"):
    if not (DIST / f).is_file():
        problems.append(f"missing {f}")

robots = (DIST / "robots.txt").read_text()
for bot in ("GPTBot", "OAI-SearchBot", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot"):
    if f"User-agent: {bot}" not in robots:
        problems.append(f"robots.txt does not allowlist {bot}")

try:
    root = ET.fromstring((DIST / "sitemap.xml").read_text())
    locs = [e.text for e in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    notes.append(f"sitemap URLs: {len(locs)}")
    if len(locs) != len(html_files):
        problems.append(f"sitemap has {len(locs)} urls but {len(html_files)} html pages")
except Exception as e:
    problems.append(f"sitemap.xml invalid: {e}")

llms = (DIST / "llms.txt").read_text()
if llms.count("](/courts/") + llms.count("courtfieldguide.vercel.app/courts/") < 12:
    problems.append("llms.txt does not link all 12 courts")
notes.append(f"llms.txt chars: {len(llms)}  llms-full.txt chars: {len((DIST/'llms-full.txt').read_text())}")

# 3. no secrets / no placeholder junk
SECRET_PAT = re.compile(r"(fc-[0-9a-f]{16,}|sk-[A-Za-z0-9]{16,}|Bearer\s+[A-Za-z0-9_\-]{16,}|"
                        r"am_us_inbox_[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|team_pQChcm)")
lorem = re.compile(r"(lorem ipsum|jane doe|acme|placeholder|TODO|FIXME)", re.I)
for p in sorted(DIST.rglob("*")):
    if p.is_file():
        t = p.read_text(encoding="utf-8", errors="replace")
        if SECRET_PAT.search(t):
            problems.append(f"SECRET-like string in {p.relative_to(DIST)}")
        if lorem.search(t) and p.suffix in (".html", ".txt"):
            problems.append(f"placeholder text in {p.relative_to(DIST)}: {lorem.search(t).group(0)}")

# 4. no remote images (hotlink fragility)
for p in html_files:
    t = p.read_text(encoding="utf-8")
    for m in re.findall(r'<img[^>]+src="([^"]+)"', t):
        problems.append(f"{p.relative_to(DIST)}: remote/hotlinked image {m}")

# 5. banned fonts / pure black / h-screen
for p in html_files:
    t = p.read_text(encoding="utf-8")
    for bad in ("font-family:'Inter'", "family=Inter", "#000000"):
        if bad in t:
            problems.append(f"{p.relative_to(DIST)}: banned token {bad}")
    if "100vh" in t:
        problems.append(f"{p.relative_to(DIST)}: uses 100vh instead of dvh")

print(json.dumps({"ok": not problems, "notes": notes, "problems": problems}, indent=2))
sys.exit(1 if problems else 0)

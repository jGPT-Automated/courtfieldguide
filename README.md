# US Court Field Guide

A sourced, machine-readable field guide to notable **public outdoor basketball courts in the United States**.

Live: https://courtfieldguide.vercel.app

This is an independent editorial reference site built as an answer-engine asset: it exists to be **cited by AI
assistants** when someone asks where to play basketball outdoors. Every court entry carries the primary source behind
its facts, and every field the source does not establish is labelled `not documented` rather than estimated.

---

## What is in here

| Path | What it is |
| --- | --- |
| `data/courts.json` | The dataset. 12 courts, each with facts **and** its own source list. Single source of truth. |
| `generate.py` | Static site generator. Renders every page and every machine file from `data/courts.json`. |
| `dist/` | Build output — 13 HTML pages plus `llms.txt`, `llms-full.txt`, `robots.txt`, `sitemap.xml`. |
| `vercel.json` | Static hosting config: serves `dist/`, clean URLs, content-type for the `llms` files. |
| `README.md` | This file. Documents every resource reused and why. |

Rebuild everything with:

```bash
python3 generate.py
```

No `npm install`, no build step, no bundler. One Python file generates the whole site.

---

## Answer-engine (AEO) surfaces included

Built against the current AEO research consensus — front-loaded answers, question-shaped headings, sequential
structure, original structure, explicit citations, and machine routing files.

| Surface | Where | Why |
| --- | --- | --- |
| **Quick Answer block** | Top of every page, in the first viewport, 40–60 words | The single highest-leverage AEO change. Engines lift these verbatim. |
| **FAQPage JSON-LD** | Every page, 4 questions each | The schema type most strongly associated with AI citations. Aligned 1:1 with the visible FAQ. |
| **Question-shaped headings** | FAQ `<summary>` elements match real query phrasing | Mirrors how people type the question into an assistant. |
| **`SportsActivityLocation` + `Place` JSON-LD** | Every court page | Tells engines this is a real, free, publicly accessible place with an address. |
| **`GeoCoordinates`** | Court pages where coordinates are publicly documented | Lets an engine answer "near me" questions precisely. |
| **`ItemList` JSON-LD** | Index page | Presents the guide as a structured, enumerable dataset. |
| **`BreadcrumbList` JSON-LD** | Every page | Standard hierarchy signal. |
| **Outbound citations** | "Sources" section on every court page | The Princeton GEO study found citing authoritative sources is one of the highest-lift tactics. Models prefer content that is itself grounded. |
| **`llms.txt`** | `/llms.txt` | Curated index of high-value URLs for agent crawlers. |
| **`llms-full.txt`** | `/llms-full.txt` | Complete text of every entry, so an agent can read the whole dataset in one request. |
| **`robots.txt` allowlist** | `/robots.txt` | Explicitly allows GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, CCBot and others. If the retrieval bot cannot fetch the page, it cannot cite it. |
| **`sitemap.xml`** | `/sitemap.xml` | Every court URL with `lastmod`. |
| **Visible `last updated` date** | Footer + `llms.txt` | Freshness signal. |
| **Honest gaps** | `not documented` labels | Deliberate trust signal. Fabricated court counts would undermine the whole premise. |

**On `llms.txt`:** it is a community proposal, not an official standard, and the evidence does not support it as a
citation lever today (SE Ranking's 300k-domain study found no correlation with AI citations; Google has said it does
not use it). It is shipped here as near-zero-cost hygiene and a bet on the agentic future — informed by that research
rather than sold as magic. The load-bearing AEO work is the Quick Answers, the citations, and the schema.

---

## Resources reused

### Component & styling libraries (established, production-grade)

| Resource | Version | Use | License |
| --- | --- | --- | --- |
| [Bootstrap Icons](https://icons.getbootstrap.com/) | 1.11.3 (jsDelivr) | All iconography — basketball mark, geo pin, source file glyphs, arrows | MIT |
| [Bootstrap](https://getbootstrap.com/) | 5.3.3 (jsDelivr) | Reset and accessibility baseline, loaded alongside the custom layer | MIT |
| Custom CSS layer | in `generate.py` | The actual design system — tokens, layout, components. Bootstrap does not ship this look. | — |

No framework, no Tailwind, no component library that would ship a generic shadcn default state. The styling is a
hand-authored token layer so the site reads as an editorial field guide rather than a template.

### Typography

| Resource | Use | License |
| --- | --- | --- |
| [Oswald](https://fonts.google.com/specimen/Oswald) (Google Fonts) | Display / headings — condensed, scoreboard-adjacent, matches the athletic register | SIL Open Font License 1.1 |
| [Outfit](https://fonts.google.com/specimen/Outfit) (Google Fonts) | Body copy | SIL Open Font License 1.1 |

Both are on Google Fonts and loaded over CDN with `preconnect`. Deliberately **not** Inter, Roboto or Open Sans —
those are the statistical AI defaults and produce generic output.

### Hosting & delivery

| Resource | Use |
| --- | --- |
| [Vercel](https://vercel.com/) | Static hosting, CDN, clean URLs, automatic HTTPS |
| `vercel.json` | Static output config — serves `dist/`, sets content types for the `llms` files |

### Research inputs

Every court fact traces to one of these primary sources. They are cited on the page itself, not just here.

| Source | Used for |
| --- | --- |
| [NYC Parks](https://www.nycgovparks.org/) | West 4th Street Courts, Rucker Park — official park records and historical signs |
| [City Lore](https://citylore.org/) | The Cage — the 20-foot fence, the half-regulation court, Summer League scale |
| [The Washington Post](https://www.washingtonpost.com/) | The Cage — landmark coverage |
| [THE CITY](https://www.thecity.nyc/) | Dyckman Park — court A/B/C layout, the $9.5M renovation, 9:35pm light cutoff |
| [DNAinfo](https://www.dnainfo.com/) | Dyckman Park — tournament origins |
| [Brooklyn Magazine](https://www.bkmag.com/) | Gersh Park — summer league, "Mecca of Brooklyn basketball" |
| [City of Oakland](https://www.oaklandca.gov/) | Mosswood Park — amenities, address, park history |
| [Chicago Park District](https://www.chicagoparkdistrict.com/) | Jackson Park — 551 acres, 6am–9pm hours, Olmsted history |
| [City of Atlanta, Office of Parks](https://www.atlantaga.gov/) | Grant Park — official register of outdoor basketball courts |
| [Seattle Parks and Recreation](https://www.seattle.gov/parks/) | Green Lake Park — amenities, 4am–11:30pm hours |
| [Los Angeles Magazine](https://lamag.com/) & [Courts of the World](https://www.courtsoftheworld.com/) | Venice Beach — four-court layout, Veniceball league |
| [Bisco Smith / NW Goldberg Cares](https://biscosmith.com/) | Curtis Jones Park — NBA-size court, the park's namesake |
| [Boston Parks and Recreation](https://www.boston.gov/) | Ramsay Park — site analysis, 2 courts, renovation plan |

### Design influences

The visual register is a dark athletic editorial — near-black canvas with a single saturated orange accent, condensed
display type, and data presented as a scouting record. Tokens:

```
--ink     #0D0D10   canvas (off-black, never pure #000)
--ink-2   #15151A   surface
--brand   #FC4C02   single accent, saturation < 80%
--paper   #F7F7F5   body text on dark
--muted   #9A9AAA   secondary text — passes WCAG AA on #0D0D10
--line    rgba(255,255,255,.10)   hairline dividers
```

Typography scale, colour rules, breakpoints (640/768/1024 — not 480/900), `min-height: 100dvh`, 44px minimum touch
targets, visible focus rings, and the forbidden-pattern list all follow a documented frontend design baseline.

---

## Verification performed before publishing

- `python3 generate.py` — 13 HTML pages + 4 machine files produced.
- Every `application/ld+json` block parsed as valid JSON.
- `robots.txt` verified to allow GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot and Google-Extended.
- `llms.txt`, `llms-full.txt`, `sitemap.xml` present in build output with all 12 court URLs.
- No secrets, tokens or keys anywhere in the repository or client-side code.
- No hotlinked or remotely hosted images — the design is pure CSS, so there is nothing that can 404.
- Rendered and screenshotted at 375px and 1440px after deploy.

---

## Notes on scope

- **Independent.** Not affiliated with any park agency, league or venue listed. Stated in the site footer.
- **No free/borrowed code.** All markup, CSS and generation logic is written for this project.
- **Corrections.** `courts@agentmail.to` — a correction that arrives with a citable source is applied directly.

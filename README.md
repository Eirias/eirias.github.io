# Sebastian Volling — Portfolio

A static, single-page developer portfolio in a terminal / code-editor aesthetic.
No build step, no frameworks — just `index.html`, `styles.css`, `main.js`.

## Features

- **Bilingual EN/DE** — toggle in the top bar (`⌘ EN/DE`), persisted in `localStorage`,
  defaults to EN on first visit.
- **Light + Dark theme** — toggle in the top bar, persisted, respects
  `prefers-color-scheme` on first visit.
- **Sections:** summary · experience · projects (own products + client work) · skills · contact.
- Sticky sidebar nav with scroll-spy, fully responsive (sidebar collapses on mobile).
- Content sourced from CV + itropical-live-solutions.com. App Store / Google Play /
  website links are live.

## Preview locally

```bash
cd "Portfolio Kopie"
python3 -m http.server 8000
# open http://localhost:8000
```

(Opening `index.html` directly via `file://` also works, but a server is cleaner.)

## Editing content

All text and project data lives in `index.html`. Translatable strings use paired
attributes — edit both:

```html
<span data-en="English text" data-de="Deutscher Text">English text</span>
```

`main.js` swaps `innerHTML` based on the selected language, so keep these as leaf
elements (no nested markup inside a `data-en` element).

## Deploy

Static files — host anywhere:

- **GitHub Pages:** push the three files to a repo, enable Pages on the branch root.
- **Subdomain of your site:** drop the files in a folder served by your host
  (e.g. `volling.itropical-live-solutions.com`).
- **Netlify / Cloudflare Pages / Vercel:** drag-and-drop the folder, no config needed.

The Google Fonts links (JetBrains Mono + Inter) are the only external dependency;
the page degrades gracefully to system fonts offline.

## To consider next

- Add a downloadable résumé link (PDF) in the sidebar / contact section.
- Add real app screenshots to the project cards for more visual punch.
- Set a custom favicon / Open Graph image (currently an inline SVG monogram).

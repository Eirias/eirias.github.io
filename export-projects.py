#!/usr/bin/env python3
"""One PDF and PNG per project (own products + selected client work), plus a
descriptions.md with the name/description text for upload forms.

  python3 export-projects.py [outdir]
"""
import html, json, pathlib, sys
from playwright.sync_api import sync_playwright

root = pathlib.Path(__file__).parent
out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "~/Desktop/9am-portfolio").expanduser()
out.mkdir(parents=True, exist_ok=True)

EXTRACT = """() => {
  const groups = [...document.querySelectorAll('#projects .cards')].slice(0, 2);
  const labels = ['Own product', 'Client work'];
  const out = [];
  groups.forEach((g, gi) => {
    g.querySelectorAll('.card').forEach(c => {
      out.push({
        group: labels[gi],
        title: c.querySelector('.card__title').textContent.trim(),
        year: (c.querySelector('.card__year')?.textContent || '').trim(),
        desc: c.querySelector('.card__desc')?.getAttribute('data-en')
              || c.querySelector('.card__desc')?.textContent.trim() || '',
        icon: c.querySelector('.card__icon')?.getAttribute('src') || '',
        mono: c.querySelector('.card__icon--mono') ? true : false,
        initials: c.querySelector('.card__icon')?.textContent.trim() || '',
        chips: [...c.querySelectorAll('.chip')].map(e => e.textContent.trim()),
        shots: [...c.querySelectorAll('.shots__thumb')].map(b => b.dataset.full),
        links: [...c.querySelectorAll('.card__links a')].map(a => ({
          label: a.textContent.replace('↗', '').trim(), href: a.href })),
        avail: (c.querySelector('.card__avail')?.textContent || '').trim(),
      });
    });
  });
  return out;
}"""

PAGE = """<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  @page {{ size: A4; margin: 16mm 14mm; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: Inter, -apple-system, sans-serif; color: #16161a; }}
  @media screen {{ body {{ padding: 44px 40px; }} }}
  .head {{ display: flex; align-items: center; gap: 14px; }}
  .icon {{ width: 56px; height: 56px; border-radius: 13px; object-fit: cover; }}
  h1 {{ font-size: 26px; margin: 0; letter-spacing: -.4px; }}
  .meta {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #6b7280; margin-top: 3px; }}
  .kicker {{ font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #16a34a;
             text-transform: uppercase; letter-spacing: .12em; margin-bottom: 16px; }}
  .desc {{ font-size: 14.5px; line-height: 1.65; margin: 18px 0 0; max-width: 62ch; }}
  h2 {{ font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #6b7280;
        text-transform: uppercase; letter-spacing: .12em; margin: 26px 0 10px; font-weight: 500; }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 7px; }}
  .chip {{ font-family: 'JetBrains Mono', monospace; font-size: 11.5px; padding: 5px 10px;
           border: 1px solid #e3e3e0; border-radius: 7px; background: #fafaf9; }}
  .shots {{ display: flex; flex-wrap: wrap; gap: 10px; }}
  .shots img {{ height: 250px; border-radius: 9px; border: 1px solid #e3e3e0; }}
  .links {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; }}
  .links a {{ color: #16a34a; text-decoration: none; margin-right: 16px; }}
  .foot {{ margin-top: 30px; padding-top: 12px; border-top: 1px solid #e8e8e5;
           font-family: 'JetBrains Mono', monospace; font-size: 10.5px; color: #9ca3af; }}
</style></head><body>
  <p class="kicker">{group}</p>
  <div class="head">{icon}<div><h1>{title}</h1><div class="meta">{year}</div></div></div>
  <p class="desc">{desc}</p>
  {tech}{shots}{links}
  <div class="foot">Sebastian Volling &middot; Senior iOS Engineer &amp; Tech Lead &middot; eirias.github.io</div>
</body></html>"""


def section(title, body):
    return f"<h2>{title}</h2>{body}" if body else ""


def build(p, base):
    icon = (f'<img class="icon" src="{base}/{p["icon"]}" alt="">' if p["icon"]
            else f'<div class="icon" style="background:#dcfce7;display:flex;align-items:center;'
                 f'justify-content:center;font-weight:700">{html.escape(p["initials"])}</div>')
    tech = section("Tech", '<div class="chips">'
                   + "".join(f'<span class="chip">{html.escape(c)}</span>' for c in p["chips"])
                   + "</div>") if p["chips"] else ""
    shots = section("Screens", '<div class="shots">'
                    + "".join(f'<img src="{base}/{s}" alt="">' for s in p["shots"])
                    + "</div>") if p["shots"] else ""
    links = ""
    if p["links"] or p["avail"]:
        inner = " ".join(f'<a href="{l["href"]}">{html.escape(l["label"])} &#8599;</a>'
                         for l in p["links"])
        if p["avail"]:
            inner += f'<span style="color:#6b7280">{html.escape(p["avail"])}</span>'
        links = section("Links", f'<div class="links">{inner}</div>')
    return PAGE.format(group=p["group"], icon=icon, title=html.escape(p["title"]),
                       year=html.escape(p["year"]), desc=html.escape(p["desc"]),
                       tech=tech, shots=shots, links=links)


def slug(s):
    keep = [ch.lower() if ch.isalnum() else "-" for ch in s]
    return "-".join("".join(keep).split("-")).strip("-")


with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page()
    base = root.resolve().as_uri()
    pg.goto(f"{base}/index.html", wait_until="networkidle")
    projects = pg.evaluate(EXTRACT)

    index = ["# 9am.works portfolio uploads", ""]
    for i, p in enumerate(projects, 1):
        name = f"{i:02d}-{slug(p['title'])}"
        tmp = out / f"{name}.html"
        tmp.write_text(build(p, base))
        pg.goto(tmp.as_uri(), wait_until="networkidle")
        pg.wait_for_function(
            "Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)",
            timeout=30000)
        pg.emulate_media(media="print")
        pg.pdf(path=str(out / f"{name}.pdf"), format="A4", print_background=True,
               prefer_css_page_size=True)
        pg.emulate_media(media="screen")
        pg.set_viewport_size({"width": 794, "height": 400})
        pg.screenshot(path=str(out / f"{name}.png"), full_page=True, scale="device")
        tmp.unlink()
        index += [f"## {p['title']}", f"file: {name}.pdf", f"group: {p['group']}",
                  f"year: {p['year']}", "", p["desc"], ""]
    b.close()

(out / "descriptions.md").write_text("\n".join(index))
print(f"{len(projects)} PDFs -> {out}")

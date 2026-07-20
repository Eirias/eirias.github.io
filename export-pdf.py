#!/usr/bin/env python3
"""Render index.html to a print-ready PDF: python3 export-pdf.py [out.pdf]"""
import pathlib, sys
from playwright.sync_api import sync_playwright

src = (pathlib.Path(__file__).parent / "index.html").resolve().as_uri()
out = sys.argv[1] if len(sys.argv) > 1 else "Sebastian-Volling-Portfolio.pdf"

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 1600})
    pg.goto(src, wait_until="networkidle")
    # force lazy images to load, then wait until every one is decoded
    pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
    pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    pg.wait_for_function(
        "Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)",
        timeout=30000)
    pg.emulate_media(media="print")
    pg.pdf(path=out, format="A4", print_background=True,
           margin={"top": "12mm", "bottom": "14mm", "left": "12mm", "right": "12mm"},
           display_header_footer=True, header_template="<span></span>",
           footer_template='<div style="width:100%;font:9px -apple-system,sans-serif;'
                           'color:#888;padding:0 12mm;display:flex;justify-content:space-between">'
                           '<span>Sebastian Volling &middot; Senior iOS Engineer</span>'
                           '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')
    b.close()
print("wrote", out)

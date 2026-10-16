"""Generates the PWA icons and the share image (og-image.png) with Chromium.

Usage:    python scripts/make_assets.py [site folder, site/ by default]
Requires: pip install playwright && playwright install chromium

If you change the site's name or headline, edit NAME, HEADLINE and SUBTITLE and run it again.
Then run scripts/build_site.py so the service worker picks up the new image.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SITE = (Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "site").resolve()
ICONS = SITE / "icons"

NAME = "AI/ML Questions"
HEADLINE = "How much do you know about AI and machine learning?"
SUBTITLE = "Every option explains why it is right or wrong.<br>Free, no sign-up."
LEGEND = ("Easy", "Medium", "Hard")

GRAPHITE = "#2B303B"
DOTS = ("#3BC27A", "#F2C232", "#F06666")


def icon_svg(maskable):
    if maskable:
        # Full-bleed background; the dots stay inside the central safe zone.
        bg = f'<rect width="512" height="512" fill="{GRAPHITE}"/>'
        r, dx = 38, 96
    else:
        bg = f'<rect width="512" height="512" rx="112" fill="{GRAPHITE}"/>'
        r, dx = 46, 116
    dots = "".join(
        f'<circle cx="{256 + (i - 1) * dx}" cy="256" r="{r}" fill="{c}"/>' for i, c in enumerate(DOTS)
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">{bg}{dots}</svg>'


OG_CSS = """
  html, body { margin: 0; }
  body { width: 1200px; height: 627px; background: #F5F6F8; color: #151922; font-family: 'IBM Plex Sans', sans-serif; }
  .card { position: relative; box-sizing: border-box; width: 100%; height: 100%; padding: 64px 88px;
          display: flex; flex-direction: column; justify-content: space-between; }
  .brand { display: flex; align-items: center; gap: 16px; font: 500 28px/1 'IBM Plex Mono', monospace; letter-spacing: 0.02em; }
  .mark { display: flex; gap: 7px; }
  .dot { display: inline-block; width: 22px; height: 22px; border-radius: 50%; }
  .easy { background: #1E9A55; } .medium { background: #E2A400; } .hard { background: #D33F3F; }
  h1 { margin: 0; max-width: 820px; font: 400 70px/1.08 'STIX Two Text', serif; letter-spacing: -0.01em; }
  p { margin: 24px 0 0; max-width: 700px; font-size: 29px; line-height: 1.35; color: #5A6170; }
  .legend { display: flex; gap: 36px; font-size: 26px; color: #151922; }
  .legend span { display: inline-flex; align-items: center; gap: 12px; }
  .legend .dot { width: 18px; height: 18px; }
  .sheet { position: absolute; right: 96px; top: 50%; transform: translateY(-50%); display: grid; gap: 18px; }
  .bubble { box-sizing: border-box; width: 76px; height: 76px; border-radius: 50%; border: 3px solid #B7BECA;
            display: grid; place-items: center; font: 500 30px/1 'IBM Plex Mono', monospace; color: #5A6170; }
  .bubble.filled { background: GRAPHITE; border-color: GRAPHITE; color: #FFFFFF; }
""".replace("GRAPHITE", GRAPHITE)

OG_HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<base href="{SITE.as_uri()}/">
<link rel="stylesheet" href="fonts.css">
<style>{OG_CSS}</style></head><body>
<div class="card">
  <div class="brand"><span class="mark"><span class="dot easy"></span><span class="dot medium"></span><span class="dot hard"></span></span>{NAME}</div>
  <div>
    <h1>{HEADLINE}</h1>
    <p>{SUBTITLE}</p>
  </div>
  <div class="legend">
    <span><i class="dot easy"></i>{LEGEND[0]}</span><span><i class="dot medium"></i>{LEGEND[1]}</span><span><i class="dot hard"></i>{LEGEND[2]}</span>
  </div>
  <div class="sheet" aria-hidden="true">
    <span class="bubble">A</span><span class="bubble">B</span><span class="bubble filled">C</span><span class="bubble">D</span>
  </div>
</div>
</body></html>"""


def main():
    ICONS.mkdir(exist_ok=True)
    (ICONS / "icon.svg").write_text(icon_svg(False) + "\n", encoding="utf-8")
    og_path = SITE.parent / ".og-template.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for name, size, maskable in (
            ("icon-192.png", 192, False),
            ("icon-512.png", 512, False),
            ("icon-maskable-512.png", 512, True),
            ("apple-touch-icon.png", 180, True),
        ):
            page.set_viewport_size({"width": size, "height": size})
            svg = icon_svg(maskable).replace("<svg ", f'<svg width="{size}" height="{size}" ', 1)
            page.set_content(f'<html><body style="margin:0;background:transparent">{svg}</body></html>')
            page.screenshot(path=str(ICONS / name), omit_background=not maskable)
        page.set_viewport_size({"width": 1200, "height": 627})
        try:
            og_path.write_text(OG_HTML, encoding="utf-8")
            page.goto(og_path.as_uri())
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(300)
            loaded = page.evaluate("[...document.fonts].filter(f => f.status === 'loaded').map(f => f.family)")
            page.screenshot(path=str(SITE / "og-image.png"))
        finally:
            og_path.unlink(missing_ok=True)
        browser.close()
    print("fonts in the og image:", sorted(set(loaded)))
    for f in sorted(ICONS.iterdir()):
        print(f"icons/{f.name}", f.stat().st_size, "B")
    print("og-image.png", (SITE / "og-image.png").stat().st_size, "B")


if __name__ == "__main__":
    main()

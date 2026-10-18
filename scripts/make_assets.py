"""Generates the PWA icons, the share image (og-image.png), the screenshots in the READMEs and the
repository's social preview for GitHub, with Chromium.

Usage:    python scripts/make_assets.py [site folder, site/ by default]
Requires: pip install playwright pillow && playwright install chromium

If you change the site's name or headline, edit NAME, HEADLINE and SUBTITLE and run it again.
Then run scripts/build_site.py so the service worker picks up the new image.

The screenshots show SCREENSHOT_QUESTION answered in study mode, in English and Spanish, in light
and dark, and go to docs/images/. They are taken from the site as it is in the site folder, so
build its data first, and run this again when that question changes.
"""
import functools
import json
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SITE = (Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "site").resolve()
ICONS = SITE / "icons"
IMAGES = ROOT / "docs" / "images"
# The site's fonts with font-display: block. The site uses optional, which can leave the fallback
# font in place for a whole page load when a font arrives late; an image must wait for its fonts.
FONTS_CSS = (SITE / "fonts.css").read_text(encoding="utf-8").replace("font-display: optional", "font-display: block")

# The question in the READMEs, answered with a wrong option so that both marks show.
SCREENSHOT_QUESTION = "llm-0008"
SCREENSHOT_CHOICE = "b"
SCREENSHOT_WIDTH = 760

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
<style>{FONTS_CSS}</style>
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


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def screenshot_quiz():
    """A saved study quiz of 10 questions, stopped at the 5th: SCREENSHOT_QUESTION, already answered."""
    index = json.loads((SITE / "data" / "index.json").read_text(encoding="utf-8"))
    questions = {
        q["id"]: q for path in index["files"] for q in json.loads((SITE / path).read_text(encoding="utf-8"))
    }
    if SCREENSHOT_QUESTION not in questions:
        return None
    others = sorted(set(questions) - {SCREENSHOT_QUESTION})[:9]
    items = []
    for n, qid in enumerate(others[:4] + [SCREENSHOT_QUESTION] + others[4:]):
        q = questions[qid]
        choice = SCREENSHOT_CHOICE if qid == SCREENSHOT_QUESTION else q["answer"][0] if n < 4 else None
        items.append({"id": qid, "order": [o["id"] for o in q["options"]], "choice": choice, "first": False, "sent": True})
    return {"v": 2, "mode": "study", "index": 4, "sid": "0" * 16, "items": items}


def make_screenshots(browser):
    """Takes the screenshots from a local copy of the site. The quiz is saved already answered and
    is only resumed, so no answer is sent anywhere."""
    quiz = screenshot_quiz()
    if quiz is None:
        print(f"Skipped the screenshots: {SCREENSHOT_QUESTION} is not in site/data (run scripts/build_site.py).")
        return []
    IMAGES.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(SITE)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}/"
    saved = json.dumps(json.dumps(quiz))
    paths = []
    try:
        for lang in ("en", "es"):
            for scheme in ("light", "dark"):
                context = browser.new_context(
                    viewport={"width": SCREENSHOT_WIDTH, "height": 900},
                    device_scale_factor=2,
                    color_scheme=scheme,
                    service_workers="block",
                )
                # Without this, Cloudflare Web Analytics would count each screenshot as a visit.
                context.route(
                    "**/*",
                    lambda route: route.abort() if "cloudflareinsights" in route.request.url else route.continue_(),
                )
                context.route("**/fonts.css", lambda route: route.fulfill(body=FONTS_CSS, content_type="text/css"))
                context.add_init_script(f"localStorage.setItem('aiml:quiz', {saved});")
                page = context.new_page()
                page.goto(f"{base}#{lang}")
                page.wait_for_selector("#resume-go", state="visible")
                page.click("#resume-go")
                page.wait_for_selector(".feedback")
                page.evaluate("document.fonts.ready")
                foot = page.locator(".q-foot").bounding_box()
                path = IMAGES / f"question-{lang}-{scheme}.png"
                page.screenshot(
                    path=str(path),
                    full_page=True,
                    clip={"x": 0, "y": 0, "width": SCREENSHOT_WIDTH, "height": foot["y"] + foot["height"] + 32},
                )
                context.close()
                # 256 colors are enough for the interface and make the file about three times smaller.
                image = Image.open(path).convert("RGB")
                image.quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(path, optimize=True)
                paths.append(path)
    finally:
        server.shutdown()
    return paths


MARK_SVG = {
    "wrong": '<svg viewBox="0 0 16 16"><path d="M4 4l8 8M12 4l-8 8" stroke="#0F1116" stroke-width="2.4" stroke-linecap="round"/></svg>',
    "right": '<svg viewBox="0 0 16 16"><path d="M3.2 8.6l3.1 3.1 6.5-7" fill="none" stroke="#0F1116" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}

# The image GitHub shows when the repository is shared. It is uploaded by hand in the repository's
# Settings → General → Social preview; GitHub recommends 1280 × 640. It uses the site's dark colors
# and a shortened SCREENSHOT_QUESTION, so update the texts here if that question changes.
SOCIAL_CSS = """
  html, body { margin: 0; }
  body { width: 1280px; height: 640px; background: #0F1116; color: #E7E9EE; font-family: 'IBM Plex Sans', sans-serif; }
  .frame { box-sizing: border-box; display: grid; grid-template-columns: 1fr 600px; gap: 64px; align-items: center;
           width: 100%; height: 100%; padding: 56px 72px; }
  .left { display: flex; flex-direction: column; justify-content: space-between; height: 100%; }
  .brand { display: flex; align-items: center; gap: 14px; font: 500 26px/1 'IBM Plex Mono', monospace; letter-spacing: 0.02em; }
  .mark { display: flex; gap: 6px; }
  .dot { display: inline-block; flex: none; border-radius: 50%; }
  .mark .dot { width: 18px; height: 18px; }
  .easy { background: #3BC27A; } .medium { background: #F2C232; } .hard { background: #F06666; }
  h1 { margin: 0; font: 400 72px/1.04 'STIX Two Text', serif; letter-spacing: -0.01em; }
  .sub { margin: 24px 0 0; font-size: 26px; line-height: 1.4; color: #9AA2B1; }
  .langs { font: 400 21px/1 'IBM Plex Mono', monospace; letter-spacing: 0.02em; color: #9AA2B1; }
  .question { display: grid; gap: 18px; }
  .meta { display: flex; align-items: center; gap: 12px; font-size: 19px; color: #9AA2B1; }
  .level { display: inline-flex; align-items: center; gap: 8px; font-weight: 600; color: #E7E9EE; }
  .level .dot { width: 13px; height: 13px; }
  .stem { margin: 0; font: 400 28px/1.34 'STIX Two Text', serif; }
  .options { display: grid; gap: 10px; margin: 0; padding: 0; list-style: none; }
  .option { display: grid; grid-template-columns: 36px 1fr; align-items: center; gap: 16px; padding: 9px 16px;
            border: 1.5px solid #2A2F3A; border-radius: 10px; background: #171A21; font: 400 25px/1.3 'STIX Two Text', serif; }
  .bubble { box-sizing: border-box; display: grid; place-items: center; width: 36px; height: 36px; border: 2px solid #424A59;
            border-radius: 50%; color: #9AA2B1; font: 500 17px/1 'IBM Plex Mono', monospace; }
  .bubble svg { width: 18px; height: 18px; }
  .wrong { border-color: #F06666; background: #2D1518; } .wrong .bubble { border-color: #F06666; background: #F06666; }
  .right { border-color: #3BC27A; background: #11281B; } .right .bubble { border-color: #3BC27A; background: #3BC27A; }
  .why { margin: 6px 0 2px; padding-left: 70px; font-size: 20px; line-height: 1.4; color: #9AA2B1; }
"""


def social_html(total):
    count = f"{total} free questions" if total else "Free questions"
    dots = '<span class="mark"><i class="dot easy"></i><i class="dot medium"></i><i class="dot hard"></i></span>'
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<base href="{SITE.as_uri()}/">
<style>{FONTS_CSS}</style>
<style>{SOCIAL_CSS}</style></head><body>
<div class="frame">
  <div class="left">
    <div class="brand">{dots}{NAME}</div>
    <div>
      <h1>Every option<br>explains why.</h1>
      <p class="sub">{count} on AI and<br>machine learning.</p>
    </div>
    <div class="langs">English · Español · Open source</div>
  </div>
  <div class="question">
    <div class="meta"><span class="level"><i class="dot medium"></i>Medium</span>Transformers &amp; LLMs · Decoding</div>
    <p class="stem">With logits 2 and 0, token A has probability 0.88 at temperature 1. And at temperature 0.5?</p>
    <ol class="options">
      <li><div class="option"><span class="bubble">A</span>0.50</div></li>
      <li><div class="option wrong"><span class="bubble">{MARK_SVG["wrong"]}</span>0.73</div>
        <p class="why">That is temperature 2. A lower one does the opposite.</p></li>
      <li><div class="option"><span class="bubble">C</span>0.88</div></li>
      <li><div class="option right"><span class="bubble">{MARK_SVG["right"]}</span>0.98</div>
        <p class="why">The logits become 4 and 0: e⁴/(e⁴+1) ≈ 0.98.</p></li>
    </ol>
  </div>
</div>
</body></html>"""


def make_social_preview(page):
    index = SITE / "data" / "index.json"
    total = json.loads(index.read_text(encoding="utf-8"))["total"] if index.exists() else None
    template = SITE.parent / ".social-template.html"
    path = IMAGES / "social-preview.png"
    IMAGES.mkdir(parents=True, exist_ok=True)
    page.set_viewport_size({"width": 1280, "height": 640})
    try:
        template.write_text(social_html(total), encoding="utf-8")
        page.goto(template.as_uri())
        page.evaluate("document.fonts.ready")
        page.screenshot(path=str(path))
    finally:
        template.unlink(missing_ok=True)
    return path


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
        social = make_social_preview(page)
        screenshots = make_screenshots(browser)
        browser.close()
    print("fonts in the og image:", sorted(set(loaded)))
    for f in sorted(ICONS.iterdir()):
        print(f"icons/{f.name}", f.stat().st_size, "B")
    print("og-image.png", (SITE / "og-image.png").stat().st_size, "B")
    for path in [social, *screenshots]:
        print(path.relative_to(ROOT).as_posix(), path.stat().st_size, "B")


if __name__ == "__main__":
    main()

"""Render brochure.html -> out/<file>.pdf (+ PNG previews). Names/SRNs come from setup/team.json."""
import json
import pathlib
import sys
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
team = json.loads((ROOT / "setup" / "team.json").read_text())["members"]

html = (HERE / "brochure.html").read_text(encoding="utf-8")
for m in team:
    k = m["key"]
    init = "".join(w[0] for w in m["name"].split()[:2]).upper()
    html = (html.replace("{{%s_NAME}}" % k, m["name"]).replace("{{%s_SRN}}" % k, m["srn"])
                .replace("{{%s_INIT}}" % k, init))
out = ROOT / "out"
out.mkdir(exist_ok=True)
rendered = out / "brochure.render.html"
rendered.write_text(html, encoding="utf-8")

srn3 = "-".join(m["srn3"] for m in team)
pdf = out / f"EBS24CS-P02 {srn3} Chairside.pdf"

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page()
    pg.goto(rendered.as_uri(), wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    pg.pdf(path=str(pdf), format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    if "--preview" in sys.argv:
        pg.set_viewport_size({"width": 794, "height": 1123})
        pages = pg.query_selector_all("section.page")
        for i, el in enumerate(pages, 1):
            el.screenshot(path=str(out / f"brochure_p{i}.png"))
    b.close()
print(pdf)

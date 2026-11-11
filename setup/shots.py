"""Capture report screenshots from the live ERPNext site (light theme) -> out/shots/NN_slug.png
Doc names are resolved from the data, so this works after any rebuild."""
import json
import pathlib
import sys
import time
from urllib.parse import quote, urlencode
from playwright.sync_api import sync_playwright
from api import admin, TEAM, ENV, BASE
from seed import COMPANY, SHOWCASE_O2C, SHOWCASE_P2P, CREDIT_DEMO

OUT = pathlib.Path(__file__).parent.parent / "out" / "shots"
OUT.mkdir(parents=True, exist_ok=True)
a = admin()


def first(dt, filters, field="name", order="creation asc"):
    r = a.find(dt, filters, [field], limit=1, order_by=order)
    return r[0][field] if r else None


def doc(dt, name):
    return f"/app/{dt.lower().replace(' ', '-')}/{quote(name)}"


def qr(report, **f):
    return f"/app/query-report/{quote(report)}?{urlencode(f)}"


# --- resolve showcase documents ---------------------------------------------------
g = SHOWCASE_O2C["customer"]
qtn = first("Quotation", {"party_name": g, "transaction_date": SHOWCASE_O2C["quotation_date"]})
so = first("Sales Order", {"customer": g, "transaction_date": SHOWCASE_O2C["so_date"]})
pick = first("Pick List Item", {"sales_order": so}, "parent")
dn = first("Delivery Note Item", {"against_sales_order": so}, "parent")
si = first("Sales Invoice Item", {"sales_order": so}, "parent") or first("Sales Invoice Item", {"delivery_note": dn}, "parent")
pe_in = first("Payment Entry Reference", {"reference_name": si}, "parent")
code = SHOWCASE_P2P["item"]
mr = first("Material Request Item", {"item_code": code, "docstatus": 1}, "parent", "creation desc")
rfq = first("Request for Quotation Item", {"material_request": mr}, "parent")
po = first("Purchase Order", {"transaction_date": SHOWCASE_P2P["date"], "supplier": SHOWCASE_P2P["winner"]})
qi = first("Quality Inspection", {"item_code": code, "docstatus": 1}, "name", "creation desc")
pr = first("Purchase Receipt Item", {"purchase_order": po}, "parent")
pi = first("Purchase Invoice Item", {"purchase_receipt": pr}, "parent")
pe_out = first("Payment Entry Reference", {"reference_name": pi}, "parent")
credit_so = first("Sales Order", {"customer": CREDIT_DEMO["customer"]})
F = dict(company=COMPANY, from_date="2026-08-01", to_date="2026-11-30")

SHOTS = [
    # slug, url, wait-selector-or-None, scroll_y
    ("01_home", "/app/home", None, 0),
    ("02_company", doc("Company", COMPANY), None, 0),
    ("03_customers", "/app/customer?customer_group=%5B%22is%22%2C%22set%22%5D", None, 0),
    ("04_customer_form", doc("Customer", g), None, 0),
    ("05_suppliers", "/app/supplier", None, 0),
    ("06_items", "/app/item", None, 0),
    ("07_item_form", doc("Item", code), None, 0),
    ("08_item_inventory", doc("Item", code), None, 900),
    ("09_warehouses", "/app/warehouse/view/tree", None, 0),
    ("10_employees", "/app/employee", None, 0),
    ("11_item_prices", "/app/item-price?price_list=Chain%20Tier%20Selling", None, 0),
    ("12_batches", "/app/batch", None, 0),
    ("13_sales_orders", "/app/sales-order", None, 0),
    ("14_purchase_orders", "/app/purchase-order", None, 0),
    ("20_o2c_quotation", doc("Quotation", qtn), None, 0),
    ("21_o2c_sales_order", doc("Sales Order", so), None, 0),
    ("22_o2c_pick_list", doc("Pick List", pick), None, 0),
    ("23_o2c_delivery_note", doc("Delivery Note", dn), None, 0),
    ("24_o2c_sales_invoice", doc("Sales Invoice", si), None, 0),
    ("25_o2c_payment_entry", doc("Payment Entry", pe_in), None, 0),
    ("27_o2c_fefo_batches", qr("Serial and Batch Summary", company=COMPANY, from_date="2026-07-31", to_date="2026-11-05",
                               item_code=code), None, 0),
    ("28_o2c_batch_balance_lig2", qr("Batch-Wise Balance History", company=COMPANY, from_date="2026-07-31",
                                     to_date="2026-11-05", item_code=code), None, 0),
    ("26_o2c_credit_block", doc("Sales Order", credit_so), None, 0),
    ("30_p2p_material_request", doc("Material Request", mr), None, 0),
    ("31_p2p_rfq", doc("Request for Quotation", rfq), None, 0),
    ("32_p2p_quotation_compare", qr("Supplier Quotation Comparison", company=COMPANY, from_date=SHOWCASE_P2P["date"],
                                     to_date=SHOWCASE_P2P["date"], group_by="Group by Supplier"), None, 0),
    ("33_p2p_purchase_order", doc("Purchase Order", po), None, 0),
    ("34_p2p_quality_inspection", doc("Quality Inspection", qi), None, 0),
    ("35_p2p_purchase_receipt", doc("Purchase Receipt", pr), None, 0),
    ("36_p2p_purchase_invoice", doc("Purchase Invoice", pi), None, 0),
    ("37_p2p_payment_entry", doc("Payment Entry", pe_out), None, 0),
    ("40_rep_customer_register", "/app/customer/view/report/Clinic%20Customer%20Register", None, 0),
    ("41_rep_sales_analytics", qr("Sales Analytics", tree_type="Customer Group", doc_type="Sales Invoice",
                                  value_quantity="Value", range="Monthly", **F), None, 0),
    ("42_rep_accounts_receivable", qr("Accounts Receivable", company=COMPANY, report_date="2026-11-04",
                                      ageing_based_on="Due Date", range1=30, range2=60, range3=90, range4=120), None, 0),
    ("43_rep_batch_balance", qr("Batch-Wise Balance History", **F), None, 0),
    ("44_rep_purchase_analytics", qr("Purchase Analytics", tree_type="Supplier", doc_type="Purchase Invoice",
                                     value_quantity="Value", range="Monthly", **F), None, 0),
    ("45_rep_gross_profit", qr("Gross Profit", group_by="Item Group", **F), None, 0),
    ("46_rep_item_register", "/app/item/view/report/Item%20Register", None, 0),
    ("50_dashboard", "/app/dashboard-view/Cusp%20Command%20Centre", None, 0),
    ("51_dashboard_lower", "/app/dashboard-view/Cusp%20Command%20Centre", None, 820),
]

only = set(sys.argv[1:])
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    ctx = b.new_context(viewport={"width": 1440, "height": 1000}, device_scale_factor=1.5, color_scheme="light")
    pg = ctx.new_page()
    pg.goto(f"{BASE}/login")
    pg.fill("#login_email", TEAM["M1"]["email"])
    pg.fill("#login_password", ENV["MEMBER_PW"])
    pg.click(".btn-login")
    pg.wait_for_url("**/app**", timeout=30000)
    manifest = {}
    if not only or "00_install_terminal" in only:
        import html as _h
        txt = (OUT.parent / "install_terminal.txt").read_text(encoding="utf-8", errors="replace")
        body = "".join(f"<div class='{'cmd' if l.startswith('$ ') else 'out'}'>{_h.escape(l) or '&nbsp;'}</div>" for l in txt.splitlines())
        t = ctx.new_page()
        t.set_content("<html><body style='margin:0;background:#fff'><div style='font:13px/1.55 Consolas,monospace;"
                      "background:#FAFAF7;border:1px solid #d8d4c8;border-radius:8px;margin:18px;width:900px'>"
                      "<div style='background:#ECE9E1;padding:7px 12px;border-radius:8px 8px 0 0;font:12px Segoe UI;color:#555'>"
                      "carbo@ubuntu (WSL2): ~/frappe-bench</div><div style='padding:12px 16px'>" + body +
                      "</div></div><style>.cmd{color:#0F4C4A;font-weight:bold}.out{color:#333}</style></body></html>")
        t.locator("body > div").screenshot(path=str(OUT / "00_install_terminal.png"))
        t.close()
        print("00_install_terminal")
    for slug, url, sel, scroll in SHOTS:
        if only and slug not in only:
            continue
        pg.goto(BASE + url)
        try:
            pg.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        time.sleep(2.5)
        pg.evaluate("document.querySelectorAll('.alert, .desk-alert, .toast-container').forEach(e=>e.remove())")
        if scroll:
            pg.evaluate(f"window.scrollTo(0,{scroll})")
            time.sleep(0.8)
        path = OUT / f"{slug}.png"
        pg.screenshot(path=str(path))
        manifest[slug] = url
        print(slug, url)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
    b.close()

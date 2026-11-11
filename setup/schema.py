"""Build ER diagrams (Graphviz DOT -> PNG) of the ERPNext tables used in each cycle,
from live DocType metadata. Frappe has no DB foreign keys, so relations come from Link fields."""
import pathlib
import subprocess
from api import admin

OUT = pathlib.Path(__file__).parent.parent / "out" / "schema"
OUT.mkdir(parents=True, exist_ok=True)

KEY = {  # extra business columns to show (besides PK/FKs)
    "Customer": ["customer_name"], "Supplier": ["supplier_name"], "Item": ["item_name", "has_batch_no", "has_expiry_date"],
    "Warehouse": ["warehouse_name"], "Employee": ["employee_name", "employee_number"], "Price List": ["selling", "buying"],
    "Item Price": ["price_list_rate"], "Batch": ["expiry_date"], "Sales Person": ["sales_person_name"],
    "Customer Group": [], "Territory": [], "Supplier Group": [], "Item Group": [],
    "Quotation": ["transaction_date", "grand_total", "status"],
    "Sales Order": ["transaction_date", "po_no", "grand_total", "status"],
    "Sales Order Item": ["qty", "rate", "amount"],
    "Pick List": ["purpose", "status"], "Pick List Item": ["qty", "picked_qty"],
    "Delivery Note": ["posting_date", "grand_total", "status"], "Delivery Note Item": ["qty", "rate"],
    "Sales Invoice": ["posting_date", "due_date", "grand_total", "outstanding_amount", "status"],
    "Sales Invoice Item": ["qty", "rate", "amount"],
    "Payment Entry": ["payment_type", "posting_date", "paid_amount", "mode_of_payment"],
    "Payment Entry Reference": ["reference_doctype", "allocated_amount"],
    "Material Request": ["transaction_date", "material_request_type", "status"], "Material Request Item": ["qty"],
    "Request for Quotation": ["transaction_date", "status"], "Supplier Quotation": ["transaction_date", "grand_total"],
    "Purchase Order": ["transaction_date", "grand_total", "status"], "Purchase Order Item": ["qty", "rate", "amount"],
    "Purchase Receipt": ["posting_date", "status"], "Purchase Receipt Item": ["qty", "received_qty", "rate"],
    "Quality Inspection": ["inspection_type", "status"],
    "Purchase Invoice": ["posting_date", "bill_no", "grand_total", "outstanding_amount"], "Purchase Invoice Item": ["qty", "rate"],
}

O2C = ["Customer", "Customer Group", "Territory", "Sales Person", "Item", "Item Group", "Warehouse", "Price List",
       "Item Price", "Batch", "Quotation", "Sales Order", "Sales Order Item", "Pick List", "Pick List Item",
       "Delivery Note", "Delivery Note Item", "Sales Invoice", "Sales Invoice Item", "Payment Entry", "Payment Entry Reference"]
P2P = ["Supplier", "Supplier Group", "Employee", "Item", "Item Group", "Warehouse", "Price List", "Item Price", "Batch",
       "Material Request", "Material Request Item", "Request for Quotation", "Supplier Quotation", "Purchase Order",
       "Purchase Order Item", "Purchase Receipt", "Purchase Receipt Item", "Quality Inspection", "Purchase Invoice",
       "Purchase Invoice Item", "Payment Entry", "Payment Entry Reference"]
MASTERS = {"Customer", "Customer Group", "Territory", "Sales Person", "Item", "Item Group", "Warehouse", "Price List",
           "Item Price", "Batch", "Supplier", "Supplier Group", "Employee"}
# Dynamic links / custom fields that matter for the story
EXTRA = {"Payment Entry Reference": [("reference_name", "Sales Invoice"), ("reference_name", "Purchase Invoice")],
         "Purchase Order": [("buyer", "Employee")]}
ARROW = "→"
SKIP_FIELDS = {"target_warehouse", "set_target_warehouse", "fg_item", "territory_manager", "parent_warehouse",
               "from_warehouse", "rejected_warehouse", "set_from_warehouse", "set_reserve_warehouse"}
SKIP_PAIRS = {("Item", "customer"), ("Item Price", "customer"), ("Item Price", "batch_no"), ("Supplier Quotation Item", "item_group")}


def meta(a, dt):
    d = a.get("DocType", dt)
    fields = d["fields"]
    if dt == "Purchase Order":
        fields = fields + [{"fieldname": "buyer", "fieldtype": "Link", "options": "Employee"}]
    return d, fields


def note(kind, tgt):
    if kind == "FK":
        t = "FK (dynamic)" if tgt == "dynamic" else f"FK {ARROW} {tgt}"
    else:
        t = kind
    return f'<font point-size="8" color="#5D6762">{t}</font>' if t else " "


def build(name, doctypes, title):
    a = admin()
    inc = set(doctypes)
    nodes, edges = [], []
    for dt in doctypes:
        d, fields = meta(a, dt)
        rows = [("name", "PK", "")]
        if d.get("istable"):
            parent = next((p for p in doctypes if p != dt and dt.startswith(p) and p not in MASTERS), None)
            if dt == "Payment Entry Reference":
                parent = "Payment Entry"
            if parent:
                rows.append(("parent", "FK", parent))
                edges.append((dt, parent, "parent"))
        for f in fields:
            if (f["fieldname"] in SKIP_FIELDS or (dt, f["fieldname"]) in SKIP_PAIRS
                    or (d.get("istable") and f["fieldname"] == "item_group")):
                continue
            if f.get("fieldtype") == "Link" and f.get("options") in inc and f["options"] != dt:
                if not any(r[0] == f["fieldname"] for r in rows):
                    rows.append((f["fieldname"], "FK", f["options"]))
                edges.append((dt, f["options"], f["fieldname"]))
        for fn, tgt in EXTRA.get(dt, []):
            if tgt in inc:
                if not any(r[0] == fn for r in rows):
                    rows.append((fn, "FK", "dynamic"))
                edges.append((dt, tgt, fn))
        for k in KEY.get(dt, []):
            if not any(r[0] == k for r in rows):
                rows.append((k, "", ""))
        fill = "#EAF2EF" if dt in MASTERS else ("#FFFFFF" if d.get("istable") else "#FBEDE6")
        head = "#0F4C4A" if dt in MASTERS else "#B5482A"
        cells = "".join(
            f'<tr><td align="left"><font point-size="9">{("<b>" + fn + "</b>") if kind == "PK" else fn}</font></td>'
            f'<td align="left">{note(kind, tgt)}</td></tr>'
            for fn, kind, tgt in rows[:14])
        label = (f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="3" bgcolor="{fill}" color="#C9BFAE">'
                 f'<tr><td colspan="2" bgcolor="{head}"><font color="white" point-size="10"><b>tab{dt}</b></font></td></tr>{cells}</table>>')
        nodes.append(f'"{dt}" [shape=plain label={label}];')
    seen, elines = set(), []
    for s, t, f in edges:
        if (s, t, f) in seen:
            continue
        seen.add((s, t, f))
        elines.append(f'"{s}" -> "{t}" [arrowhead=tee arrowtail=crow dir=both color="#7D8A85"];')
    dot = ("digraph G {\n graph [rankdir=LR splines=true nodesep=0.35 ranksep=0.9 bgcolor=white fontname=\"DejaVu Sans\" "
           f'label="{title}" labelloc=t fontsize=16 pad=0.3];\n node [fontname="DejaVu Sans"];\n edge [fontname="DejaVu Sans"];\n'
           + "\n".join(nodes) + "\n" + "\n".join(elines) + "\n}\n")
    p = OUT / f"{name}.dot"
    p.write_text(dot, encoding="utf-8")
    wsl = "/mnt/c" + str(OUT).replace("C:", "").replace("\\", "/")
    subprocess.run(["wsl", "-d", "Ubuntu", "--", "dot", "-Tpng", "-Gdpi=150", f"{wsl}/{name}.dot", "-o", f"{wsl}/{name}.png"], check=True)
    print(OUT / f"{name}.png")


if __name__ == "__main__":
    build("schema_o2c", O2C, "Cusp Dental Supplies on ERPNext: Order-to-Cash tables (MariaDB; Link fields shown as FK)")
    build("schema_p2p", P2P, "Cusp Dental Supplies on ERPNext: Procure-to-Pay tables (MariaDB; Link fields shown as FK)")

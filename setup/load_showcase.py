"""Stage 3: the two documented showcase cycles + demo states.
O2C: Quotation -> Sales Order -> Pick List (FEFO) -> Delivery Note -> Sales Invoice -> Payment Entry
P2P: auto Material Request (reorder job) -> RFQ -> 2 Supplier Quotations -> Purchase Order
     -> Purchase Receipt + Quality Inspection -> Purchase Invoice -> Payment Entry
Run after load_txn.py. The reorder job is triggered via bench (scheduler job, normally runs nightly)."""
import subprocess
from api import ApiError
from load_txn import priced, S, emp, plus, dated, fix_terms, ins_sub, taxes, batch, short, sales_doc, so_create, pay, PEENYA, P_TAX, A, C
from seed import *
from api import TEAM, ENV


def o2c():
    x = SHOWCASE_O2C
    so = so_create("SO11", x["so_date"], x["customer"], x["items"], qdate=x["quotation_date"])
    a = S("ADMIN")
    if a.value("Sales Order", so, "per_delivered") >= 100:
        print("o2c: already delivered", so)
        return so
    w = S("M4")
    pl = a.value("Pick List Item", {"sales_order": so, "docstatus": ["<", 2]}, "parent")
    if not pl:
        doc = w.call("erpnext.selling.doctype.sales_order.sales_order.create_pick_list", source_name=so)
        doc.update({"company": C, "purpose": "Delivery"})
        pl = w.insert(doc)["name"]  # ERPNext assigns batches on save, earliest expiry first
    if a.value("Pick List", pl, "docstatus") == 0:
        pick = w.get("Pick List", pl)
        for loc in pick["locations"]:
            loc["picked_qty"] = loc["qty"]
        w.save(pick)
        w.submit("Pick List", pl)
    print("o2c: pick list", pl, [(l["item_code"], l.get("batch_no"), l["qty"]) for l in a.get("Pick List", pl)["locations"]])
    dn = w.call("erpnext.stock.doctype.pick_list.pick_list.create_delivery_note", source_name=pl)
    if isinstance(dn, str):
        dn = w.get("Delivery Note", dn)
    if dn.get("docstatus") == 0 and dn.get("name") and w.exists("Delivery Note", dn["name"]):
        dn = w.get("Delivery Note", dn["name"])
        dated(dn, x["pick_date"], "12:00:00")
        dn.update({"lr_no": "CDS-VAN-1103", "transporter_name": "Own van (Ravi Kumar)"})
        w.save(dn)
        w.submit("Delivery Note", dn["name"])
        dn_name = dn["name"]
    else:
        dated(dn, x["pick_date"], "12:00:00")
        dn.update({"lr_no": "CDS-VAN-1103", "transporter_name": "Own van (Ravi Kumar)"})
        dn_name = ins_sub(w, dn)
    m = S("M2")
    si = m.call("erpnext.stock.doctype.delivery_note.delivery_note.make_sales_invoice", source_name=dn_name)
    dated(si, x["invoice_date"], "16:00:00")
    fix_terms(si, x["invoice_date"])
    si_name = ins_sub(m, si)
    pay("Sales Invoice", si_name, x["payment_date"])
    print("o2c: done", so, pl, dn_name, si_name)


def credit_demo():
    x = CREDIT_DEMO
    so = so_create("SO12", x["date"], x["customer"], x["items"])
    print("credit demo:", so, S("ADMIN").value("Sales Order", so, "status"))


def open_quotation():
    x = OPEN_QUOTATION
    a = S("ADMIN")
    if a.value("Quotation", {"party_name": x["customer"]}, "name"):
        return
    seller = TERRITORIES[[c[1] for c in CUSTOMERS if c[0] == x["customer"]][0]]
    m = S(seller)
    ins_sub(m, sales_doc("Quotation", x["customer"], x["date"], x["items"], seller))
    print("open quotation: done")


def bench(cmd):
    full = f"cd {ENV['BENCH_DIR']} && export PATH=$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin && bench --site {ENV['SITE']} {cmd}"
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-u", "carbo", "--", "bash", "-c", full], capture_output=True, text=True)
    print(r.stdout[-400:], r.stderr[-400:])


def p2p():
    x = SHOWCASE_P2P
    a = S("ADMIN")
    code = x["item"]
    mr = a.value("Material Request Item", {"item_code": code, "docstatus": 1}, "parent")
    if not mr:
        a.single("Stock Settings", {"auto_indent": 1})  # off during data load so the nightly job can't fire early
        bench("execute erpnext.stock.reorder_item.reorder_item")
        mr = a.value("Material Request Item", {"item_code": code, "docstatus": 1}, "parent")
    if not mr:
        raise ApiError("reorder job did not create a Material Request for " + code)
    print("p2p: auto material request", mr)
    b = S("M3")
    rfq = a.value("Request for Quotation Item", {"material_request": mr, "docstatus": 1}, "parent")
    if not rfq:
        doc = b.call("erpnext.stock.doctype.material_request.material_request.make_request_for_quotation", source_name=mr)
        doc.update({"transaction_date": x["date"], "company": C,
                    "message_for_supplier": "Please quote your best price and earliest dispatch for the item below. "
                                            "Minimum 24 months remaining shelf life on delivery.",
                    "suppliers": [{"supplier": s, "send_email": 0} for s in x["suppliers"]]})
        for it in doc["items"]:
            it["schedule_date"] = plus(x["date"], 3)
            it["warehouse"] = PEENYA
        rfq = ins_sub(b, doc)
    sq_names = {}
    for sup, rate in x["suppliers"].items():
        hit = a.value("Supplier Quotation", {"supplier": sup, "docstatus": 1, "transaction_date": x["date"]}, "name")
        if hit:
            sq_names[sup] = hit
            continue
        sq = b.call("erpnext.buying.doctype.request_for_quotation.request_for_quotation.make_supplier_quotation_from_rfq",
                    source_name=rfq, for_supplier=sup)
        sq.update({"transaction_date": x["date"], "valid_till": plus(x["date"], 15),
                   "taxes_and_charges": P_TAX, "taxes": taxes("purchase")})
        for it in sq["items"]:
            it.update({k: v for k, v in priced(it["item_code"], it["qty"], "buy").items() if k not in ("qty",)})
            it["rate"] = it["price_list_rate"] = rate
        sq_names[sup] = ins_sub(b, sq)
    print("p2p: rfq", rfq, "quotations", sq_names)
    win = x["winner"]
    po = a.value("Purchase Order Item", {"supplier_quotation": sq_names[win], "docstatus": 1}, "parent")
    if not po:
        doc = b.call("erpnext.buying.doctype.supplier_quotation.supplier_quotation.make_purchase_order", source_name=sq_names[win])
        doc.update({"transaction_date": x["date"], "schedule_date": plus(x["date"], 3), "buyer": emp("M3"),
                    "order_confirmation_no": f"OC/SEPT/2611/PO12", "order_confirmation_date": x["date"],
                    "set_warehouse": PEENYA})
        for it in doc["items"]:
            it["schedule_date"] = plus(x["date"], 3)
            it["warehouse"] = PEENYA
        po = ins_sub(b, doc)
    print("p2p: purchase order", po)

    # receipt with quality inspection
    if not a.value("Item", code, "inspection_required_before_purchase"):
        a.set_value("Item", code, "inspection_required_before_purchase", 1)
    for p in ("Cartridge seal and label intact", "Storage temperature below 25 C on arrival",
              "Remaining shelf life at least 24 months"):
        a.ensure({"doctype": "Quality Inspection Parameter", "parameter": p}, "parameter")
    w = S("M4")
    pr = a.value("Purchase Receipt Item", {"purchase_order": po, "docstatus": ["<", 2]}, "parent")
    bid = batch(code, f"CDS-{TEAM['M4']['srn3']}-{short(code)}-1126", x["expiry"], "2026-09-01")
    if not pr:
        doc = w.call("erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_receipt", source_name=po)
        dated(doc, x["date"], "15:30:00")
        doc["supplier_delivery_note"] = "DC-SEPT-1104"
        for it in doc["items"]:
            it.update({"batch_no": bid, "use_serial_batch_fields": 1})
        pr = w.insert(doc)["name"]
    if a.value("Purchase Receipt", pr, "docstatus") == 0:
        qi = a.value("Quality Inspection", {"reference_name": pr, "docstatus": 1}, "name")
        if not qi:
            qi = ins_sub(w, {"doctype": "Quality Inspection", "inspection_type": "Incoming", "reference_type": "Purchase Receipt",
                             "reference_name": pr, "item_code": code, "batch_no": bid, "sample_size": 2,
                             "report_date": x["date"], "inspected_by": TEAM["M4"]["email"], "manual_inspection": 1,
                             "status": "Accepted", "remarks": "2 of 50 boxes opened and checked. All parameters accepted.",
                             "readings": [{"specification": p, "status": "Accepted", "manual_inspection": 1, "numeric": 0}
                                          for p in ("Cartridge seal and label intact",
                                                    "Storage temperature below 25 C on arrival",
                                                    "Remaining shelf life at least 24 months")]})
        doc = w.get("Purchase Receipt", pr)
        for it in doc["items"]:
            it["quality_inspection"] = qi
        w.save(doc)
        w.submit("Purchase Receipt", pr)
    print("p2p: receipt", pr)
    m = S("M2")
    pi = a.value("Purchase Invoice Item", {"purchase_receipt": pr, "docstatus": 1}, "parent")
    if not pi:
        doc = m.call("erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice", source_name=pr)
        dated(doc, x["date"], "17:30:00")
        doc.update({"bill_no": "SEPT/INV/2611/0412", "bill_date": x["date"]})
        fix_terms(doc, x["date"])
        pi = ins_sub(m, doc)
    pay("Purchase Invoice", pi, x["date"])
    print("p2p: done", mr, rfq, po, pr, pi)


if __name__ == "__main__":
    o2c()
    credit_demo()
    open_quotation()
    p2p()

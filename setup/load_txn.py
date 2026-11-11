"""Stage 2: opening balances + all transactions, replayed in date order, each step
performed by the team member who owns it. Idempotent per document (keyed on
customer PO ref / supplier order-confirmation ref and document statuses)."""
import datetime as dt
import json
from api import admin, member, TEAM, ApiError
from seed import *

C, A = COMPANY, ABBR
PEENYA = f"Peenya Central - {A}"
S_TAX = f"Karnataka GST (CGST + SGST) - {A}"
P_TAX = f"Karnataka GST Input (CGST + SGST) - {A}"
CHAIN = {n for n, t, g, *_ in CUSTOMERS if g == "Clinic Chain"}
TERR = {n: t for n, t, *_ in CUSTOMERS}
ITEM = {i[0]: i for i in ITEMS}

_sessions = {}


def S(key):
    if key not in _sessions:
        _sessions[key] = admin() if key == "ADMIN" else member(key)
    return _sessions[key]


def emp(key):
    return S("ADMIN").value("Employee", {"employee_number": TEAM[key]["srn"]}, "name")


def plus(d, days):
    return (dt.date.fromisoformat(d) + dt.timedelta(days=days)).isoformat()


def short(code):
    return code.split("-", 1)[1]


def taxes(kind):
    a = S("ADMIN")
    if kind == "sales":
        return a.call("erpnext.controllers.accounts_controller.get_taxes_and_charges",
                      master_doctype="Sales Taxes and Charges Template", master_name=S_TAX)
    return a.call("erpnext.controllers.accounts_controller.get_taxes_and_charges",
                  master_doctype="Purchase Taxes and Charges Template", master_name=P_TAX)


def ins_sub(api, doc):
    d = api.insert(doc)
    api.submit(d["doctype"], d["name"])
    return d["name"]


def batch(code, batch_id, expiry, mfg):
    a = S("ADMIN")
    if not a.exists("Batch", batch_id):
        doc = {"doctype": "Batch", "batch_id": batch_id, "item": code, "manufacturing_date": mfg}
        if expiry:
            doc["expiry_date"] = expiry
        a.insert(doc)
    return batch_id


def dated(doc, d, t="11:00:00"):
    doc.update({"posting_date": d, "posting_time": t, "set_posting_time": 1})
    return doc


def fix_terms(doc, d):
    doc["payment_schedule"] = []
    doc["due_date"] = None
    doc["payment_terms_template"] = "Net 30"
    return doc



def priced(code, qty, kind, chain=False):
    """Explicit rate + GST map per line (API inserts don't run the UI's price fetch)."""
    i = ITEM[code]
    rate = i[6] if kind == "buy" else (i[8] if chain else i[7])
    half = i[9] / 2
    accts = (f"Input CGST - {A}", f"Input SGST - {A}") if kind == "buy" else (f"Output CGST - {A}", f"Output SGST - {A}")
    return {"item_code": code, "qty": qty, "rate": rate, "price_list_rate": rate, "uom": i[3], "conversion_factor": 1,
            "item_tax_template": f"GST {i[9]}% - {A}", "item_tax_rate": json.dumps({ac: half for ac in accts}),
            "warehouse": PEENYA}

# ---------------------------------------------------------------- opening
def opening():
    a = S("ADMIN")
    co = a.get("Company", C)
    bank = f"Canara Bank Current A/c - {A}"
    if co.get("default_bank_account") != bank:
        a.set_value("Company", C, "default_bank_account", bank)
    if not a.find("Journal Entry", {"voucher_type": "Opening Entry", "docstatus": 1}):
        equity = a.find("Account", {"company": C, "root_type": "Equity", "is_group": 0}, ["name"])
        cap = next((e["name"] for e in equity if "Capital" in e["name"]), equity[0]["name"])
        ins_sub(a, {"doctype": "Journal Entry", "voucher_type": "Opening Entry", "company": C,
                    "posting_date": "2026-07-31", "is_opening": "Yes",
                    "user_remark": "Promoters' capital brought in, opening bank balance",
                    "accounts": [{"account": bank, "debit_in_account_currency": 2500000},
                                 {"account": cap, "credit_in_account_currency": 2500000}]})
    if a.find("Stock Reconciliation", {"purpose": "Opening Stock", "docstatus": 1}):
        return
    rows = []
    for code, suf, qty, exp, who in OPENING:
        row = {"item_code": code, "warehouse": PEENYA, "qty": qty, "valuation_rate": ITEM[code][6]}
        if suf:
            bid = batch(code, f"CDS-{TEAM[who]['srn3']}-{short(code)}-0726{suf}", exp, "2026-07-01")
            row.update({"batch_no": bid, "use_serial_batch_fields": 1})
        rows.append(row)
    w = S("M4")
    ins_sub(w, dated({"doctype": "Stock Reconciliation", "company": C, "purpose": "Opening Stock",
                      "expense_account": f"Temporary Opening - {A}", "items": rows}, "2026-07-31", "09:00:00"))
    print("opening: done")


# ---------------------------------------------------------------- purchase steps
def po_create(p):
    pid, d, sup, buyer, items, *_ = p
    b = S(buyer)
    ref = f"OC/{sup.split()[0][:4].upper()}/{d[2:4]}{d[5:7]}/{pid}"
    hit = b.value("Purchase Order", {"order_confirmation_no": ref, "docstatus": 1}, "name")
    if hit:
        return hit
    doc = {"doctype": "Purchase Order", "supplier": sup, "company": C, "transaction_date": d,
           "schedule_date": plus(d, 3), "order_confirmation_no": ref, "order_confirmation_date": d,
           "buyer": emp(buyer), "set_warehouse": PEENYA, "buying_price_list": "Standard Buying",
           "taxes_and_charges": P_TAX, "taxes": taxes("purchase"),
           "items": [{**priced(c, q, "buy"), "schedule_date": plus(d, 3)} for c, q in items]}
    return ins_sub(b, doc)


def po_receive(p, po):
    pid, d, sup, buyer, items, rdate, recv, partial, expiry, paid = p
    a = S("ADMIN")
    if a.value("Purchase Order", po, "per_received") > 0:
        return a.find("Purchase Receipt Item", {"purchase_order": po, "docstatus": 1}, ["parent"])[0]["parent"]
    r = S(recv)
    pr = r.call("erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_receipt", source_name=po)
    dated(pr, rdate, "15:00:00")
    pr["supplier_delivery_note"] = f"DC-{pid}-{rdate[5:7]}{rdate[8:]}"
    for row in pr["items"]:
        code = row["item_code"]
        if partial and code in partial:
            row["qty"] = row["received_qty"] = partial[code]
        if ITEM[code][4]:
            bid = batch(code, f"CDS-{TEAM[recv]['srn3']}-{short(code)}-{rdate[5:7]}{rdate[2:4]}",
                        expiry.get(code), plus(rdate, -60))
            row.update({"batch_no": bid, "use_serial_batch_fields": 1})
    return ins_sub(r, pr)


def pr_bill(p, pr):
    pid, d, sup, buyer, items, rdate, *_ = p
    a = S("ADMIN")
    hit = a.find("Purchase Invoice Item", {"purchase_receipt": pr, "docstatus": 1}, ["parent"])
    if hit:
        return hit[0]["parent"]
    m = S("M2")
    pi = m.call("erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice", source_name=pr)
    dated(pi, rdate, "17:00:00")
    pi.update({"bill_no": f"{sup.split()[0][:4].upper()}/INV/{rdate[2:4]}{rdate[5:7]}/{pid[2:]:0>3}",
               "bill_date": rdate})
    fix_terms(pi, rdate)
    return ins_sub(m, pi)


def pay(dt_, inv, d, fraction=1.0, mode="NEFT"):
    a = S("ADMIN")
    if a.find("Payment Entry Reference", {"reference_name": inv, "docstatus": 1}, ["parent"]):
        return
    m = S("M2")
    pe = m.call("erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry", dt=dt_, dn=inv)
    pe.update({"posting_date": d, "mode_of_payment": mode, "reference_no": f"UTR{d.replace('-', '')}{inv[-4:]}",
               "reference_date": d})
    if fraction < 1:
        amt = round(pe["paid_amount"] * fraction, 2)
        pe["paid_amount"] = pe["received_amount"] = amt
        pe["references"][0]["allocated_amount"] = amt
        pe["base_paid_amount"] = pe["base_received_amount"] = amt
    ins_sub(m, pe)


# ---------------------------------------------------------------- sales steps
def price_list(cust):
    return "Chain Tier Selling" if cust in CHAIN else "Standard Selling"


def sales_doc(dtype, cust, d, items, seller):
    doc = {"doctype": dtype, "company": C, "transaction_date": d, "selling_price_list": price_list(cust),
           "set_warehouse": PEENYA, "taxes_and_charges": S_TAX, "taxes": taxes("sales"),
           "items": [{**priced(c, q, "sell", cust in CHAIN), "delivery_date": plus(d, 1)} for c, q in items]}
    if dtype == "Quotation":
        vt = plus(d, 15)
        doc.update({"quotation_to": "Customer", "party_name": cust, "order_type": "Sales",
                    "valid_till": vt if vt >= dt.date.today().isoformat() else None})
    else:
        doc.update({"customer": cust, "delivery_date": plus(d, 1),
                    "sales_team": [{"sales_person": TEAM[seller]["name"], "allocated_percentage": 100}]})
    return doc


def so_create(sid, d, cust, items, qdate=None, submit_as=None):
    seller = TERRITORIES[TERR[cust]]
    m = S(seller)
    ref = f"PO/{''.join(w[0] for w in cust.split() if w[0].isalpha()).upper()}/{d[2:4]}{d[5:7]}/{sid[2:]:0>2}"
    hit = m.value("Sales Order", {"po_no": ref, "docstatus": ["<", 2]}, "name")
    if hit:
        return hit
    if qdate:
        q = ins_sub(m, sales_doc("Quotation", cust, qdate, items, seller))
        so = m.call("erpnext.selling.doctype.quotation.quotation.make_sales_order", source_name=q)
        so.update({"transaction_date": d, "delivery_date": plus(d, 1), "set_warehouse": PEENYA,
                   "sales_team": [{"sales_person": TEAM[seller]["name"], "allocated_percentage": 100}]})
        for row in so["items"]:
            row["delivery_date"] = plus(d, 1)
            row["warehouse"] = PEENYA
    else:
        so = sales_doc("Sales Order", cust, d, items, seller)
    so.update({"po_no": ref, "po_date": d})
    name = m.insert(so)["name"]
    try:
        (submit_as or m).submit("Sales Order", name)
    except ApiError as e:
        if submit_as is None and "credit limit" in str(e).lower():
            print(f"  {sid}: credit limit blocked submit by {seller} -> Accounts Manager approves")
            S("M2").submit("Sales Order", name)
        else:
            raise
    return name


def deliver(so, d):
    a = S("ADMIN")
    if a.value("Sales Order", so, "per_delivered") >= 100:
        return a.find("Delivery Note Item", {"against_sales_order": so, "docstatus": 1}, ["parent"])[0]["parent"]
    w = S("M4")
    dn = w.call("erpnext.selling.doctype.sales_order.sales_order.make_delivery_note", source_name=so)
    dated(dn, d, "10:30:00")
    dn["lr_no"] = f"CDS-VAN-{d[5:7]}{d[8:]}"
    dn["transporter_name"] = "Own van (Ravi Kumar)"
    fefo(dn["items"], d)
    return ins_sub(w, dn)


def fefo(rows, d):
    """Split batch-item rows across batches, earliest expiry first."""
    a = S("ADMIN")
    out = []
    for row in rows:
        code = row["item_code"]
        if not ITEM[code][4]:
            out.append(row)
            continue
        avail = a.call("erpnext.stock.doctype.batch.batch.get_batch_qty", item_code=code, warehouse=PEENYA) or []
        exp = {b["name"]: b.get("expiry_date") or "9999-12-31"
               for b in a.find("Batch", {"item": code}, ["name", "expiry_date"])}
        avail = sorted([b for b in avail if b["qty"] > 0], key=lambda b: exp.get(b["batch_no"], "9999"))
        need = row["qty"]
        for b in avail:
            if need <= 0:
                break
            take = min(need, b["qty"])
            r = dict(row)
            r.update({"qty": take, "stock_qty": take, "batch_no": b["batch_no"], "use_serial_batch_fields": 1})
            r.pop("name", None)
            out.append(r)
            need -= take
        if need > 0:
            raise ApiError(f"not enough stock for {code} on {d}: short {need}")
    rows[:] = out


def bill(dn, d):
    a = S("ADMIN")
    hit = a.find("Sales Invoice Item", {"delivery_note": dn, "docstatus": 1}, ["parent"])
    if hit:
        return hit[0]["parent"]
    m = S("M2")
    si = m.call("erpnext.stock.doctype.delivery_note.delivery_note.make_sales_invoice", source_name=dn)
    dated(si, d, "16:00:00")
    fix_terms(si, d)
    return ins_sub(m, si)


# ---------------------------------------------------------------- replay
def replay():
    ev = []
    for p in PURCHASES:
        ev.append((p[1], 0, "po", p))
        ev.append((p[5], 1, "receive", p))
        if p[9]:
            ev.append((p[9], 3, "pay_po", p))
    for s in SALES:
        ev.append((s[1], 2, "so", s))
        ev.append((s[4], 2, "deliver", s))
        if s[6]:
            ev.append((s[6][0], 3, "pay_so", s))
    ev.sort(key=lambda e: (e[0], e[1]))
    po_of, pr_of, pi_of, so_of, si_of = {}, {}, {}, {}, {}
    for d, _, kind, x in ev:
        if kind == "po":
            po_of[x[0]] = po_create(x)
        elif kind == "receive":
            pr_of[x[0]] = po_receive(x, po_of[x[0]])
            pi_of[x[0]] = pr_bill(x, pr_of[x[0]])
        elif kind == "pay_po":
            pay("Purchase Invoice", pi_of[x[0]], d)
        elif kind == "so":
            so_of[x[0]] = so_create(x[0], x[1], x[2], x[3], qdate=x[7])
        elif kind == "deliver":
            dn = deliver(so_of[x[0]], x[4])
            si_of[x[0]] = bill(dn, x[5])
        elif kind == "pay_so":
            pay("Sales Invoice", si_of[x[0]], d, x[6][1], "UPI" if x[6][1] < 1 else "NEFT")
        print(f"{d} {kind:8s} {x[0]} ok")


if __name__ == "__main__":
    opening()
    replay()

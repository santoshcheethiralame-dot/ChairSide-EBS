"""Assemble the Part A project report (HTML -> PDF) from live data + out/shots + out/schema.
Each screenshot gets its own page with a caption and a short description (brief items 10-11)."""
import html
import json
import pathlib
from playwright.sync_api import sync_playwright
from api import admin, TEAM
from seed import COMPANY, ABBR, SHOWCASE_O2C, SHOWCASE_P2P, CREDIT_DEMO, ITEMS, CUSTOMERS, SUPPLIERS

ROOT = pathlib.Path(__file__).parent.parent
OUT = ROOT / "out"
SHOTS = OUT / "shots"
a = admin()


def first(dt, filters, field="name", order="creation asc"):
    r = a.find(dt, filters, [field], limit=1, order_by=order)
    return r[0][field] if r else "-"


def count(dt, filters=None):
    return a.call("frappe.client.get_count", doctype=dt, filters=filters or {})


def inr(x):
    x = round(float(x or 0))
    s = str(x)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    return "₹" + s


m = TEAM
names = {k: f"{v['name']} ({v['srn']})" for k, v in m.items()}
g = SHOWCASE_O2C["customer"]
so = first("Sales Order", {"customer": g, "transaction_date": SHOWCASE_O2C["so_date"]})
qtn = first("Quotation", {"party_name": g, "transaction_date": SHOWCASE_O2C["quotation_date"]})
pick = first("Pick List Item", {"sales_order": so}, "parent")
dn = first("Delivery Note Item", {"against_sales_order": so}, "parent")
si = first("Sales Invoice Item", {"delivery_note": dn}, "parent")
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
so_doc = a.get("Sales Order", so)
si_doc = a.get("Sales Invoice", si)
po_doc = a.get("Purchase Order", po)
pick_doc = a.get("Pick List", pick)
pick_batches = sorted({l.get("batch_no") for l in pick_doc["locations"] if l.get("batch_no")})
revenue = sum(r["grand_total"] for r in a.find("Sales Invoice", {"docstatus": 1}, ["grand_total"]))
purchases = sum(r["grand_total"] for r in a.find("Purchase Invoice", {"docstatus": 1}, ["grand_total"]))
overdue = sum(r["outstanding_amount"] for r in a.find("Sales Invoice", {"docstatus": 1, "status": "Overdue"}, ["outstanding_amount"]))
gp = a.call("frappe.desk.query_report.run", report_name="Gross Profit",
            filters={"company": COMPANY, "from_date": "2026-08-01", "to_date": "2026-11-30", "group_by": "Item Group"})
tot = next(r for r in gp["result"] if isinstance(r, dict) and r.get("item_group") == "Total")
gprof, margin = tot["gross_profit"], f"{tot['gross_profit_%']:.1f}%"

counts = {
    "Customer": count("Customer"), "Supplier": count("Supplier"), "Item": count("Item"),
    "Warehouse": count("Warehouse", {"is_group": 0, "company": COMPANY}), "Employee": count("Employee"),
    "Price List": count("Price List"), "Item Price": count("Item Price"), "Batch": count("Batch"),
    "Sales Order": count("Sales Order", {"docstatus": 1}), "Purchase Order": count("Purchase Order", {"docstatus": 1}),
    "Quotation": count("Quotation", {"docstatus": 1}), "Delivery Note": count("Delivery Note", {"docstatus": 1}),
    "Sales Invoice": count("Sales Invoice", {"docstatus": 1}), "Purchase Receipt": count("Purchase Receipt", {"docstatus": 1}),
    "Purchase Invoice": count("Purchase Invoice", {"docstatus": 1}), "Payment Entry": count("Payment Entry", {"docstatus": 1}),
}

# ------------------------------------------------------------------ image pages
IMAGES = [
    ("00_install_terminal", "Installation: bench, Frappe and ERPNext running in WSL Ubuntu",
     "ERPNext v15 was installed with the Frappe Bench tool on Ubuntu 24.04 (WSL2) with MariaDB 10.11, Redis, Node 20 and "
     "Python 3.12. The output confirms the installed app versions and the site <b>cusp.localhost</b>, served at http://localhost:8000."),
    ("01_home", "ERPNext desk after login",
     f"The ERPNext home workspace, logged in as {names['M1']}. Each team member has their own user account, so every "
     "document in this report shows the member who created it."),
    ("02_company", "Company master: Cusp Dental Supplies Pvt. Ltd.",
     f"The company was created with the setup wizard: country India, currency INR, fiscal year April 2026 to March 2027, "
     f"abbreviation <b>{ABBR}</b> and the standard Indian chart of accounts. Default warehouse, bank account and tax "
     "templates are attached to it."),
    ("03_customers", "Master 1: Customers (12 Bengaluru dental clinics)",
     "All 12 customers are fictional clinics across five Bengaluru territories, grouped by clinic type "
     "(single-chair, multi-chair, implant centre, orthodontic, paediatric, clinic chain). Each has a credit limit, "
     "Net 30 payment terms, a contact doctor and a billing address."),
    ("04_customer_form", f"Customer form: {g}",
     "A clinic chain customer. Its customer group carries the <b>Chain Tier Selling</b> price list, so chain orders "
     "are priced about 8% below standard automatically. The sales team row links the clinic to the sales person "
     "who covers its territory."),
    ("05_suppliers", "Master 2: Suppliers (8)",
     "Seven dental manufacturers and one local wholesaler (Chickpet Surgicals, fictional), in two supplier groups. "
     "Each supplier has Net 30 terms, a contact and a Bengaluru supply-branch address."),
    ("06_items", "Master 3: Items (24 dental products in 8 item groups)",
     "Anaesthetics, restoratives, endodontics, implants, orthodontics, prosthetics, infection control and equipment. "
     "Item codes are meaningful (e.g. ANS-LIG2, IMP-3510), and each item has a GST item tax template (5% or 18%)."),
    ("07_item_form", f"Item form: {code}, lignocaine 2% cartridges",
     "Lignocaine is batch-tracked with expiry dates, because anaesthetic stock expires. The item also requires a "
     "quality inspection before purchase, which is used in the procure-to-pay cycle."),
    ("08_item_inventory", f"Item {code}: reorder level and batch settings",
     "The reorder level (25 boxes) and reorder quantity (50 boxes) for Peenya Central drive ERPNext's automatic "
     "Material Request in cycle 2."),
    ("09_warehouses", "Master 4: Warehouses",
     "Peenya Central (main store), Jayanagar Counter (walk-in sales), Quarantine &amp; Expired, and the default "
     "Stores, Work In Progress, Finished Goods and Goods In Transit warehouses created by the setup wizard."),
    ("10_employees", "Master 5: Employees (team members with SRNs)",
     "The four team members are employees, with their SRN as the employee number and a real role: Sales Manager, "
     "Accounts &amp; MIS Lead, Purchase Manager, and Warehouse &amp; Quality Lead. Two fictional staff complete the team."),
    ("11_item_prices", "Master 6: Price lists and item prices",
     f"Three price lists (Standard Buying, Standard Selling, Chain Tier Selling) with {counts['Item Price']} item "
     "prices. The same item has a different price by customer tier."),
    ("12_batches", "Supporting master: Batches with expiry dates",
     "Every batch ID embeds the SRN of the team member who counted or received the stock "
     "(CDS-&lt;SRN&gt;-&lt;item&gt;-&lt;MMYY&gt;), so SRNs appear in every stock transaction."),
    ("13_sales_orders", f"Transaction table 1: Sales Orders ({counts['Sales Order']})",
     "Twelve sales orders from August to November 2026, each by the sales person of the clinic's territory. "
     "Statuses show the full spread: completed, to bill, to deliver, and one order still awaiting delivery."),
    ("14_purchase_orders", f"Transaction table 2: Purchase Orders ({counts['Purchase Order']})",
     "Twelve purchase orders to the eight suppliers, each with a Buyer (employee) set through a custom field added "
     "with Customize Form. One order (Osstem, October) was only partly received, so it remains open."),
    ("20_o2c_quotation", f"Cycle 1, stage 1: Quotation {qtn}",
     f"{names['M3']}, who covers Bengaluru North, quotes {g} at the Chain Tier price list with Karnataka GST "
     "(CGST + SGST) applied per item."),
    ("21_o2c_sales_order", f"Cycle 1, stage 2: Sales Order {so}",
     f"The quotation is converted to a sales order (customer PO ref {so_doc.get('po_no')}). ERPNext checks the "
     f"customer's credit limit on submit. Grand total {inr(so_doc['grand_total'])}."),
    ("22_o2c_pick_list", f"Cycle 1, stage 3: Pick List {pick}",
     f"{names['M4']} creates the pick list. ERPNext chooses batches by <b>earliest expiry first</b> "
     f"(Stock Settings: Pick Serial / Batch Based On = Expiry). Batches picked: {', '.join(pick_batches) or '-'}."),
    ("28_o2c_batch_balance_lig2", "Cycle 1, evidence: batches consumed earliest-expiry-first",
     "Batch-Wise Balance History for lignocaine, 31 Jul to 5 Nov 2026. The opening batch expiring January 2027 "
     "(CDS-127-LIG2-0726A) was used up first, then the June 2028 batch. The September 2028 batch received in October "
     "is untouched, and the new batch from cycle 2 (June 2029) sits on top. FEFO picking, done by ERPNext."),
    ("23_o2c_delivery_note", f"Cycle 1, stage 4: Delivery Note {dn}",
     "Goods leave Peenya Central with the picked batch numbers recorded, which reduces stock and posts the cost "
     "of goods sold. The company van and driver are recorded as the transporter."),
    ("24_o2c_sales_invoice", f"Cycle 1, stage 5: Sales Invoice {si}",
     f"{names['M2']} raises the GST invoice from the delivery note. Due date follows Net 30 terms. "
     f"Invoice total {inr(si_doc['grand_total'])}."),
    ("25_o2c_payment_entry", f"Cycle 1, stage 6: Payment Entry {pe_in}",
     "The clinic pays by NEFT into the Canara Bank current account. The payment is allocated against the invoice, "
     "whose status becomes Paid, closing the order-to-cash cycle."),
    ("26_o2c_credit_block", f"Cycle 1, control: credit limit on Sales Order {credit_so}",
     f"Bluebell Dental Clinic has a ₹25,000 credit limit. When {names['M3']} submitted this order, ERPNext blocked it "
     f"for crossing the limit. {names['M2']} (Accounts Manager, the configured Credit Controller) approved and submitted it."),
    ("30_p2p_material_request", f"Cycle 2, stage 1: Material Request {mr} (raised automatically)",
     "Lignocaine stock fell below its reorder level of 25 boxes. ERPNext's reorder job (Stock Settings: raise "
     "Material Request when stock reaches re-order level) created this purchase request for the reorder quantity "
     "of 50 boxes. No one typed it."),
    ("31_p2p_rfq", f"Cycle 2, stage 2: Request for Quotation {rfq}",
     f"{names['M3']} sends the requirement to two suppliers, Septodont and Chickpet Surgicals, asking for a "
     "minimum 24 months of shelf life."),
    ("32_p2p_quotation_compare", "Cycle 2, stage 3: Supplier Quotation Comparison",
     "Both suppliers' quotations side by side. Septodont quoted ₹1,450 per box against Chickpet's ₹1,520, so "
     "Septodont wins the order."),
    ("33_p2p_purchase_order", f"Cycle 2, stage 4: Purchase Order {po}",
     f"Created from the winning supplier quotation, with {names['M3']} as Buyer. Grand total {inr(po_doc['grand_total'])} "
     "including input GST."),
    ("34_p2p_quality_inspection", f"Cycle 2, stage 5a: Quality Inspection {qi}",
     f"{names['M4']} inspects a sample of 2 boxes against three parameters (seal and label, storage temperature, "
     "remaining shelf life). Status Accepted. The receipt cannot be submitted without it."),
    ("35_p2p_purchase_receipt", f"Cycle 2, stage 5b: Purchase Receipt {pr}",
     "The 50 boxes arrive with a new batch whose ID carries the receiver's SRN and an expiry of June 2029. "
     "Stock increases at Peenya Central."),
    ("36_p2p_purchase_invoice", f"Cycle 2, stage 6: Purchase Invoice {pi}",
     "Created from the purchase receipt, so it is linked to both the receipt and the purchase order. Buying "
     "Settings require a PO and a receipt before any purchase invoice."),
    ("37_p2p_payment_entry", f"Cycle 2, stage 7: Payment Entry {pe_out}",
     f"{names['M2']} pays Septodont by NEFT, which closes the procure-to-pay cycle."),
    ("40_rep_customer_register", "Report 1 (master data): Clinic Customer Register",
     "A Report Builder report on the Customer master showing group, territory, payment terms, credit limit and "
     "sales person for every clinic. Built entirely in the UI."),
    ("41_rep_sales_analytics", "Report 2: Sales Analytics by clinic type, monthly",
     "Invoiced value per customer group per month, August to November 2026. The column chart is ERPNext's own."),
    ("42_rep_accounts_receivable", "Report 3: Accounts Receivable with ageing",
     f"Outstanding clinic invoices as on 4 Nov 2026 in 0-30 / 31-60 / 61-90 / 90+ day buckets. Overdue total: {inr(overdue)}."),
    ("43_rep_batch_balance", "Report 4: Batch-wise Balance History",
     "Opening, in, out and closing quantity for every batch. This is how the distributor finds stock that is close to expiry."),
    ("44_rep_purchase_analytics", "Report 5: Purchase Analytics by supplier, monthly",
     f"Purchase value per supplier per month. Total purchases August to November: {inr(purchases)}."),
    ("45_rep_gross_profit", "Report 6: Gross Profit by item group",
     f"Selling amount, buying amount and gross profit per item group. Overall gross profit {inr(gprof)}, a margin of {margin}."),
    ("46_rep_item_register", "Report 7 (master data): Item Register",
     "A Report Builder report on the Item master showing group, unit, batch and expiry tracking, and reorder "
     "level and quantity for all 24 items."),
    ("50_dashboard", "Executive dashboard: Cusp Command Centre (KPIs)",
     f"Five Number Cards: Revenue, invoice totals incl. GST ({inr(revenue)}), Overdue Receivables, Near-expiry Stock, Gross Profit and Active "
     "Clinic Customers. Below them, the Monthly Sales column chart and the Monthly Purchases line chart."),
    ("51_dashboard_lower", "Executive dashboard: charts",
     "Sales by Territory (bar), Sales by Clinic Type (donut) and Purchases by Supplier (bar). Every card and chart "
     "was configured from the Dashboard, Number Card and Dashboard Chart screens, without code."),
    ("schema_o2c", "Relational schema 1: Order-to-Cash tables",
     "ERPNext stores each DocType in a MariaDB table named tab&lt;DocType&gt;. Frappe does not create database "
     "foreign keys, so the relations shown are its Link fields, read from the live DocType metadata and drawn with "
     "Graphviz. Teal = master tables, coral = transaction tables, white = child (line-item) tables."),
    ("schema_p2p", "Relational schema 2: Procure-to-Pay tables",
     "The buying side: material request, RFQ, supplier quotation, purchase order, receipt, quality inspection, "
     "invoice and payment, with their line-item child tables and links to the masters."),
]


def img_page(slug, cap, desc, n):
    src = (OUT / "schema" / f"{slug}.png") if slug.startswith("schema") else (SHOTS / f"{slug}.png")
    if not src.exists():
        return f'<section class="pg img"><h3>Figure {n}. {cap}</h3><p class="miss">[missing image {slug}]</p></section>'
    return (f'<section class="pg img"><div class="fig"><img src="{src.as_uri()}"></div>'
            f'<h3>Figure {n}. {cap}</h3><p>{desc}</p></section>')


def table(rows, head):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>"


team_rows = [(k, v["name"], v["srn"], v["designation"]) for k, v in m.items()]
master_rows = [
    ("Customer", counts["Customer"], "Fictional Bengaluru dental clinics, 6 groups, 5 territories, credit limits"),
    ("Supplier", counts["Supplier"], "Dental manufacturers + 1 wholesaler, Net 30"),
    ("Item", counts["Item"], "24 dental products in 8 item groups, batch + expiry where real"),
    ("Warehouse", counts["Warehouse"], "Peenya Central, Jayanagar Counter, Quarantine & Expired + defaults"),
    ("Employee", counts["Employee"], "4 team members (SRN = employee number) + 2 staff"),
    ("Price List / Item Price", f"{counts['Price List']} / {counts['Item Price']}", "Standard Buying, Standard Selling, Chain Tier Selling"),
    ("Batch (supporting)", counts["Batch"], "Batch IDs embed the SRN of the member who counted/received the stock"),
]
txn_rows = [(k, v) for k, v in counts.items() if k in ("Quotation", "Sales Order", "Delivery Note", "Sales Invoice",
                                                         "Purchase Order", "Purchase Receipt", "Purchase Invoice", "Payment Entry")]

SOURCES = [
    ("Frappe Technologies, Contact (HQ address)", "https://frappe.io/contact"),
    ("Frappe Technologies, About / team", "https://frappe.io/about"),
    ("ERPNext product page (modules, 30,000+ companies, 200+ partners)", "https://frappe.io/erpnext"),
    ("ERPNext, Wikipedia (original author, v1.0 June 2010, GPL-3.0, tech stack)", "https://en.wikipedia.org/wiki/ERPNext"),
    ("Inc42: Rainmatter invests Rs 10 Cr in ERPNext (founded 2008 by Rushabh Mehta)", "https://inc42.com/buzz/zerodha-backed-rainmatter-invests-inr-10-cr-in-erpnext/"),
    ("Zerodha Z-Connect: announcing the investment in ERPNext (Nov 2020)", "https://zerodha.com/z-connect/rainmatter/announcing-the-investment-in-erpnext"),
    ("Frappe forum: ERPNext v16 release dates", "https://discuss.frappe.io/t/erpnext-hrms-frappe-framework-v16-release-dates/156349"),
    ("ERPNext customer stories (Frappe blog)", "https://frappe.io/blog/customer-success-stories"),
    ("Customer story: Teabox", "https://erpnext.com/customer-stories/teabox"),
    ("Customer story: Precihole Machines", "https://frappe.io/stories/Precihole Machines"),
    ("ERPNext docs: auto creation of Material Request", "https://docs.frappe.io/erpnext/user/manual/en/stock/articles/auto-creation-of-material-request"),
    ("ERPNext docs: Serial and Batch Bundle (pick by FIFO / LIFO / Expiry)", "https://docs.frappe.io/erpnext/serial-and-batch-bundle"),
    ("ERPNext docs: India Compliance app (GST)", "https://docs.frappe.io/erpnext/india-compliance-app"),
    ("Business Standard: GST on medical devices cut to 5% (Sept 2025)", "https://www.business-standard.com/industry/news/gst-cut-patient-benefits-cos-margin-pressure-125090401185_1.html"),
    ("Busy: GST rates on dental services and products", "https://busy.in/gst-rates/dental-services"),
    ("Frappe Bench (installation tool)", "https://github.com/frappe/bench"),
]

CSS = """
@page{size:A4;margin:16mm 16mm 18mm}
body{font-family:'Segoe UI',Arial,sans-serif;color:#1d2321;font-size:10.5pt;line-height:1.5}
h1{font-size:24pt;color:#0F4C4A;margin:0 0 4mm}h2{font-size:15pt;color:#0F4C4A;border-bottom:.5mm solid #0F4C4A;padding-bottom:1.5mm;margin:0 0 4mm}
h3{font-size:11.5pt;color:#0F4C4A;margin:4mm 0 1.5mm}
.pg{page-break-after:always}.pg:last-child{page-break-after:auto}
.cover{text-align:center;padding-top:40mm}.cover .code{font-size:12pt;letter-spacing:.1em;color:#5d6762}
.cover h1{font-size:30pt;margin-top:10mm}.cover .sub{font-size:14pt;color:#B5482A;margin-bottom:18mm}
table{border-collapse:collapse;width:100%;margin:2mm 0 5mm;font-size:9.5pt}th,td{border:.3mm solid #c9bfae;padding:1.6mm 2.4mm;text-align:left;vertical-align:top}
th{background:#EAF2EF;color:#0F4C4A}
.img .fig{border:.3mm solid #c9bfae;padding:1mm;margin-bottom:3mm}.img img{width:100%;display:block}
.img p{font-size:10pt}.miss{color:#b00}
ul{margin:1mm 0 3mm 5mm}li{margin:.8mm 0}.small{font-size:8.6pt;color:#5d6762}
a{color:#0F4C4A;word-break:break-all}
"""

parts = []
parts.append(f"""<section class="pg cover"><div class="code">UE24CS343AB8 · Enterprise Business Systems · Aug–Dec 2026</div>
<h1>Cusp Dental Supplies Pvt. Ltd.</h1><div class="sub">End-to-end ERP implementation on ERPNext v15 (Part A)</div>
{table(team_rows, ['', 'Name', 'SRN', 'Role in the company'])}
<p class="small">Industry domain: Healthcare (dental and medical supply distribution) · ERP: ERPNext v15 (open source, GPL-3.0) ·
Instance: local install, site cusp.localhost</p></section>""")

parts.append(f"""<section class="pg"><h2>1. Business scenario</h2>
<p><b>Cusp Dental Supplies Pvt. Ltd.</b> is a fictional Bengaluru distributor of dental consumables, implants,
orthodontic supplies and small equipment. Its head office and central warehouse are in Peenya Industrial Area, and
it runs a walk-in counter in Jayanagar. It supplies dental clinics across the city with same-day delivery.</p>
<p>Three problems shape the ERP setup:</p>
<ul><li><b>Stock expires.</b> Anaesthetic cartridges, composites and impression material carry expiry dates, so
every unit is batch-tracked and picked earliest-expiry-first.</li>
<li><b>Clinics order just in time.</b> An implant centre orders fixtures the day before surgery, so reorder levels
raise purchase requests automatically.</li>
<li><b>Clinics pay late.</b> Credit limits, Net 30 terms and receivables ageing keep cash under control.</li></ul>
<h3>Business process cycles implemented</h3>
{table([("Order-to-Cash", "Quotation → Sales Order → Pick List → Delivery Note → Sales Invoice → Payment Entry", "6"),
        ("Procure-to-Pay", "Material Request (automatic) → Request for Quotation → Supplier Quotations → Purchase Order → Quality Inspection + Purchase Receipt → Purchase Invoice → Payment Entry", "7")],
       ["Cycle", "Stages", "Stages shown"])}
<h3>Team and where our names and SRNs appear</h3>
{table([(names[k], v['designation'], 'User account, Employee (SRN as employee number), Sales Person, document owner, batch IDs') for k, v in m.items()],
       ['Member', 'Role', 'Appears in'])}
<p class="small">Master data: user accounts, employee records, sales persons. Transaction data: every document records
its creator; sales orders carry the sales person; purchase orders carry the Buyer; every batch ID contains the SRN of
the member who counted or received the stock.</p></section>""")

parts.append(f"""<section class="pg"><h2>2. The EBS product: ERPNext</h2>
<p><b>ERPNext</b> is an open-source ERP built on the Frappe Framework (Python, JavaScript, MariaDB) and released under
GPL-3.0. It covers accounting, procurement, sales, CRM, stock, manufacturing, projects, assets, point of sale,
quality, support and HR/payroll (through the Frappe HR app), with a no-code builder for forms, reports, workflows
and dashboards.</p>
{table([
    ("Company", "Frappe Technologies Pvt. Ltd."),
    ("Headquarters", "C/205, Neelkanth Business Park, Vidyavihar West, Mumbai, Maharashtra 400086, India"),
    ("Company locations", "Head office in Mumbai; sales phone lines for the United States and the United Kingdom; delivered worldwide through 200+ partners"),
    ("Founder / original author", "Rushabh Mehta"),
    ("Origin", "Company founded 2008; ERPNext v1.0 first published as open source in June 2010"),
    ("Versions", "v4 (2014) introduced the Frappe app architecture; v13, v14, v15 (installed here: 15.124.5 on Frappe 15.126.0); v16 stable from January 2026"),
    ("Licence and stack", "GPL-3.0; Python, JavaScript, Vue.js; MariaDB/PostgreSQL; Redis; Node.js"),
    ("Adoption", "30,000+ companies (vendor figure)"),
    ("Clients (public case studies)", "Teabox, Precihole Machines, Sree Mahalakshmi Agencies, Touchmagix Media"),
    ("Funding", "Rs 10 crore from Zerodha's Rainmatter (announced November 2020)"),
], ['Attribute', 'Detail'])}
<h3>Features used in this project</h3>
<ul><li>Selling: quotations, sales orders, pick lists, delivery notes, sales invoices, credit-limit control, sales teams</li>
<li>Buying: material requests, automatic reorder, RFQs, supplier quotations and comparison, purchase orders</li>
<li>Stock: batches with expiry, FEFO picking, quality inspection, stock reconciliation, multiple warehouses</li>
<li>Accounts: GST tax templates, payment terms, payment entries, receivables ageing, gross profit</li>
<li>No-code tools: Customize Form (custom Buyer field), Report Builder, Number Cards, Dashboard Charts, Dashboards</li></ul>
<p class="small">All facts are taken from the sources listed in Section 5.</p></section>""")

parts.append(f"""<section class="pg"><h2>3. Installation and setup</h2>
{table([("1", "Enable WSL2 Ubuntu 24.04 on Windows 11"),
        ("2", "Install MariaDB 10.11, Redis, Node 20 + yarn, wkhtmltopdf and Python build tools (apt)"),
        ("3", "Configure MariaDB for utf8mb4, set the root password"),
        ("4", "Install Frappe Bench (pipx) and run bench init --frappe-branch version-15"),
        ("5", "bench get-app --branch version-15 erpnext"),
        ("6", "bench new-site cusp.localhost, then bench --site cusp.localhost install-app erpnext"),
        ("7", "bench start, open http://localhost:8000 and complete the setup wizard (India, INR, FY Apr–Mar)"),
        ("8", "Configure: Stock Settings (FEFO, auto reorder), Buying Settings (PO and receipt required), Accounts Settings (credit controller), GST templates, Net 30 terms")],
       ['Step', 'Action'])}
<h3>Data loaded</h3>
{table(master_rows, ['Master entity', 'Records', 'Notes'])}
{table(txn_rows, ['Transaction document', 'Submitted'])}
<p class="small">Opening stock was entered with a Stock Reconciliation dated 31 Jul 2026 and opening capital with an
opening journal entry. All transactions are dated August to November 2026, entered in date order.</p></section>""")

parts.append("""<section class="pg"><h2>4. Figures</h2><p>The following pages show one screenshot per page, in this order:
installation and setup (Figures 1–2), master data (3–12), transaction tables (13–14), the order-to-cash cycle (15–21),
the procure-to-pay cycle (22–29), reports (30–36), the executive dashboard (37–38) and the relational schema (39–40).</p>
</section>""")

for n, (slug, cap, desc) in enumerate(IMAGES, 1):
    parts.append(img_page(slug, cap, desc, n))

src_rows = "".join(f"<li>{html.escape(t)}: <a href='{u}'>{u}</a></li>" for t, u in SOURCES)
parts.append(f"""<section class="pg"><h2>5. Sources</h2><ul>{src_rows}</ul>
<p class="small">Company, clinic and contact names in the data are fictional. Supplier names are real dental
manufacturers used for realism; all prices, quantities and documents are invented for this project.</p></section>""")

doc = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(parts)}</body></html>"
out_html = OUT / "report.render.html"
out_html.write_text(doc, encoding="utf-8")
srn3 = "-".join(v["srn3"] for v in m.values())
pdf = OUT / f"EBS24CS-P01 {srn3} ERPNext.pdf"
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page()
    pg.goto(out_html.as_uri(), wait_until="networkidle")
    pg.pdf(path=str(pdf), format="A4", print_background=True,
           display_header_footer=True, header_template="<span></span>",
           footer_template="<div style='font-size:8px;width:100%;text-align:center;color:#777'>Cusp Dental Supplies on ERPNext · page <span class='pageNumber'></span> of <span class='totalPages'></span></div>",
           margin={"top": "16mm", "bottom": "18mm", "left": "16mm", "right": "16mm"})
    b.close()
print(pdf)

# EBS Team Project — Idea Statement

**Course:** UE24CS343AB8 EBS, Aug–Dec 2026 · **Marks:** 20 (Part A 10 + Part B 10)
**Due:** Mon 16 Nov 2026 · **Presentations:** 16–19 Nov 2026 · **Team:** 4 max

> One story, two deliverables. Part A runs a real dental-supply business on an
> open-source ERP *as it works today*. Part B sells the *AI-native future* of that
> same industry. The brief says the parts are unrelated: they are graded
> separately, but nothing stops them sharing a world. That makes the presentation
> one arc instead of two disconnected demos.

---

## 0. The one-paragraph pitch

Bengaluru has thousands of dental clinics. Most run on WhatsApp, Excel and a
paper register. Behind them sits a supply chain of distributors that keeps
anaesthetic cartridges, composites, implants and gloves on the shelf, and much of
that stock expires. **Part A** is **Cusp Dental Supplies Pvt. Ltd.**, a fictional
Bengaluru distributor, running its order-to-cash and procure-to-pay cycles end to
end in **ERPNext**. It uses batch and expiry tracking, automatic reorder requests,
GST invoicing and an executive dashboard. **Part B** is **Chairside**, a
fictional AI-native ERP for dental clinics and their suppliers. Its agents handle
patient recall, restocking, lab orders and invoice checks under a trust layer
with two parts. A human mistake-correction becomes a permanent blocking rule (the
*Precedent Ledger*), and written clinic policy compiles into rules the software
actually enforces (the *Policy Compiler*). Cusp Dental appears in the Part B
brochure as a pilot customer.

Domain knowledge comes from the RECALL project (patient recovery for Bangalore
dental clinics). That includes treatment price *ladders* (a crown is
₹4k / ₹7k / ₹10k / ₹12k / ₹14k depending on material, never one number). **No real
clinic names are used anywhere.** All customers below were checked against RECALL's
64 real clinic profiles to avoid collisions.

---

# PART A — Cusp Dental Supplies on ERPNext

## A1. Product choice: ERPNext (Frappe), latest stable (v15/v16)

| Need from brief | ERPNext answer (no code) |
|---|---|
| Install open source EBS | Frappe Bench on WSL Ubuntu (already on this laptop). Fallback: `frappe_docker`; last resort: Odoo Community Windows installer |
| 6+ masters, transactions | Full Selling, Buying, Stock, Accounts modules |
| Realistic workflow stages | Quotation → Sales Order → Pick List → Delivery Note → Sales Invoice → Payment Entry, and the buying mirror |
| 3 reports | Built-in Sales Analytics, Accounts Receivable, Stock Balance, Batch-wise Balance, Gross Profit; Report Builder for custom ones |
| Executive dashboard, 4 KPIs, 2+ charts | **Dashboard** + **Number Card** + **Dashboard Chart** DocTypes, configured from the UI |
| Demo / modify live | Every document is editable/amendable in the browser |

**Why not Odoo:** Studio and editable spreadsheet dashboards are Enterprise-only.
Community Odoo makes requirement (7) harder.

**Known gotcha:** Frappe stores links as *Link fields*, **not** database foreign
keys. A DBeaver auto-ER diagram of MariaDB will show tables with **no
relationships**. Plan: draw the relational schema in **dbdiagram.io** (DBML),
using the Link fields of the ~14 DocTypes we touch. Still "using a tool", and it
comes out cleaner. The DBeaver table list goes in as a supporting screenshot.

## A2. The business

- **Industry domain (req 1):** **Healthcare**, specifically medical/dental supply
  distribution. Say this word in the report title page and the viva opener.
- **Legal name:** Cusp Dental Supplies Pvt. Ltd. (abbr. `CDS`)
- **Tagline (letterhead):** "On the shelf before the chair needs it."
- **HQ & central warehouse:** Peenya Industrial Area, Bengaluru 560058
- **Retail counter:** Jayanagar 4th Block (walk-in orders for small clinics)
- **Founded (fictional):** 2019 · **Currency:** INR · **Fiscal year:** Apr–Mar
- **What it does:** distributes dental consumables, implants, orthodontic
  supplies and small equipment to ~60 clinics across Bengaluru, with same-day
  delivery inside the city.
- **Its real pain (the story we tell in the viva):** anaesthetic and composite
  stock *expires*. Implant sizes are *many* and clinics order the day before
  surgery. Clinics pay *late*. So the ERP has to show batch and expiry tracking
  (FEFO picking), reorder levels, and receivables ageing.

## A3. Master data (6 required → we do 8)

### 1. Customers (12) — Customer Group + Territory set on each

| Customer | Area (Territory) | Group | Contact (fictional) |
|---|---|---|---|
| Banyan Tree Dental Studio | Indiranagar (East) | Multi-chair clinic | Dr. Meera Raghavan |
| Molarwise Family Dentistry | HSR Layout (South-East) | Single-chair clinic | Dr. Arjun Shetty |
| Pearl Arch Dental Care | Malleshwaram (North) | Multi-chair clinic | Dr. Kavya Iyengar |
| Root & Crown Dental | Whitefield (East) | Implant centre | Dr. Farhan Qureshi |
| Aligna Orthodontic Centre | Koramangala (South-East) | Orthodontic practice | Dr. Sneha Pai |
| Twin Canines Kids Dental | Jayanagar (South) | Paediatric clinic | Dr. Rohan Hegde |
| Gulmohar Dental & Implant Centre | Hebbal (North) | Clinic chain | Dr. Nandini Gowda |
| Basavanagudi Smile Works | Basavanagudi (South) | Single-chair clinic | Dr. Prakruthi Rao |
| Bluebell Dental Clinic | Yelahanka (North) | Single-chair clinic | Dr. Vivek Menon |
| Cubbon Dental Associates | MG Road (Central) | Multi-chair clinic | Dr. Ayesha Khan |
| Sankey Smiles Dental | Sadashivanagar (Central) | Multi-chair clinic | Dr. Tejas Kulkarni |
| Kanakapura Road Dental Hub | Kanakapura Rd (South) | Clinic chain | Dr. Lakshmi Narayan |

Each customer gets a billing address and a **credit limit**. Demo hook: an order
that exceeds the limit is blocked live.

**GSTIN trap:** GSTINs end in a checksum character. If we install the India
Compliance app, a made-up GSTIN will fail validation. Either mark the fictional
clinics as *Unregistered* (realistic: many small clinics are) or skip the app
and use plain tax templates (see A6 GST note).

### 2. Suppliers (8) — real manufacturers / Indian distributors

Dentsply Sirona India · Ivoclar Vivadent India · GC India Dental · Septodont
Healthcare India · Prime Dental Products · Waldent · Osstem Implant India ·
a local consumables wholesaler (fictional, e.g. *Chickpet Surgicals*)

Real supplier names count as "proper entity names". Note the source URL for each
on the sources page of the report.

### 3. Items (24) in 8 Item Groups — batch + expiry tracked where real

| Item Group | Example items (stock UOM) | Batch/expiry? |
|---|---|---|
| Anaesthetics | Lignocaine 2% + adrenaline 1:80,000, 2.2 ml cartridge (box of 50); Articaine 4% cartridge (box of 50) | Yes |
| Restoratives | Nano-hybrid composite, shade A2, 4 g syringe; Glass ionomer cement, Type II kit | Yes |
| Endodontics | NiTi rotary file set 25 mm (pack of 6); Gutta-percha points 2% (box of 120); Sodium hypochlorite 3%, 500 ml | Some |
| Implants | Implant fixture 3.5 × 10 mm; Implant fixture 4.0 × 11.5 mm; Healing abutment 4 mm | Yes (lot) |
| Orthodontics | MBT 0.022 bracket kit; NiTi archwire 0.014 upper (pack of 10) | No |
| Prosthetics | Zirconia milling block 98 mm; Alginate impression material, 450 g | Some |
| Infection control | Nitrile gloves, M (box of 100); Autoclave pouches 90 × 230 mm (200); Surface disinfectant 1 L | Gloves yes |
| Equipment | LED curing light; Ultrasonic scaler handpiece | No (serial optional) |

Each item gets a **reorder level + reorder qty** on the Peenya warehouse. That
powers the automatic Material Request in cycle 2.

### 4. Warehouses (4)
`Peenya Central - CDS` · `Jayanagar Counter - CDS` · `Goods In Transit - CDS` ·
`Quarantine & Expired - CDS`

### 5. Employees (4 + 2) — **team members go here**
Each team member is an Employee with their **SRN as the Employee number** and a
real role: Sales Manager (O2C owner), Purchase Manager (P2P owner), Warehouse &
Quality Lead, Accounts & MIS Lead. Two fictional staff (delivery executive,
counter clerk) complete the org chart.

### 6. Price Lists (3)
`Standard Selling` · `Chain Tier Selling` (≈8% lower, for Clinic chain group) ·
`Standard Buying`. This is the RECALL "ladder" idea in distributor form: the same
item has different prices by customer tier. **Populate an Item Price row for
all 24 items in all 3 lists (72 rows)**, otherwise orders fill in ₹0 and the
data no longer looks "sufficient". Set `Chain Tier Selling` as the default
price list on the *Clinic chain* Customer Group so it applies automatically.

### 7. Sales Persons + Territories
Territories: Bengaluru North / South / South-East / East / Central. Sales
persons = the team, so the sales-by-rep chart shows *our names*.

### 8. Customer Groups + Item Groups (as above)

## A4. Where the SRNs and names go (requirement 6 — visible in every screenshot)

The brief says "**all** your SRNs and Names" in "master **and** transaction
data". Every member must show up in both, and every transaction screenshot
should show at least one of us.

**In master data:**
- Employee records: name + SRN as Employee number (all 4)
- Sales Person records = all 4 members
- **One ERPNext User per member**, full name = "Name (SRN)", e.g. "Santosh C (PES1UG24CS127)"

**In transaction data:**
- **Each member logs in as themselves and creates their share of documents.** ERPNext
  stamps *Created By* / owner and the timeline ("Santosh C (PES1UG24CS127) created
  this") on every document. This is the strongest no-code embed.
- Sales Team (Sales Person) on every Sales Order = one of us
- Purchase Orders have no built-in buyer field. Add one with **Customize Form** →
  a Link field "Buyer" to Employee (configuration, not programming), set on every PO.
- **Batch IDs** = `CDS-<SRN last 3>-<item code>-<MMYY>`, e.g. `CDS-127-LIG2-1126`.
  **Rotate the SRN across batches** so all four SRNs appear. Batches show in every
  delivery note, receipt and stock report.
- Letter Head on all print formats: "Prepared by: <names + SRNs>". This covers
  printed output only, so it is a supplement, not the main embed.

## A5. Transactions (≥10 each in 2 tables → we do 12 + 12)

Spread posting dates **Aug–Nov 2026** so the monthly sales column chart has four
real columns.

**Entry order matters (ERPNext checks stock chronologically):**
1. **Opening stock first:** a Stock Reconciliation dated **31 Jul 2026** with
   batches and expiry dates for every stocked item. Without it, the first Delivery
   Note fails with "insufficient stock". Make some opening batches expire in
   Dec 2026–Feb 2027 so the near-expiry KPI has something to show.
2. Then enter documents in date order. Tick **"Edit Posting Date and Time"** on
   Delivery Notes, Receipts and Invoices to backdate them.
3. Never deliver on a date before the stock arrived. Backdated entries are reposted,
   and negative stock blocks them.
4. **Write the full 24-row seed sheet** (customer/supplier, items, qty, dates,
   which member enters it) **before** typing anything into ERPNext. This document
   only sketches examples.

**Table 1 — Sales Orders (12):** e.g. Root & Crown orders 6 × 3.5 × 10 fixtures +
6 healing abutments before a Thursday surgery list. Aligna orders bracket kits +
archwires monthly. Twin Canines orders GIC + gloves. One order deliberately
**exceeds a credit limit** (blocked, then approved by Accounts, as a demo beat).

**Table 2 — Purchase Orders (12):** e.g. Septodont cartridges (batch + expiry
captured at receipt), Osstem implants (lot numbers), Waldent equipment. One PO
is **auto-generated from a reorder-level Material Request**. One has a
**partial receipt** (back-order realism).

Every downstream document (Delivery Notes, Sales Invoices, Purchase Receipts,
Purchase Invoices, Payment Entries) follows from these, so the data is linked,
not 24 isolated rows.

## A6. The two business process cycles (≥4 stages each, screenshot every stage)

### Cycle 1 — Order-to-Cash ("Clinic order to cash in bank")
1. **Quotation** to Gulmohar Dental (Chain Tier price list applied)
2. **Sales Order** created from quotation (credit-limit check fires)
3. **Pick List**: ERPNext picks the batch that **expires first** (FEFO).
   Requires Stock Settings → *Pick Serial / Batch Based On* = **Expiry**. Test this
   on day 2 with two batches that have different expiry dates. If Pick List ignores
   it, show FEFO on the Delivery Note's batch selector instead.
4. **Delivery Note**: batch IDs with our SRN visible, stock leaves Peenya
5. **Sales Invoice** with GST lines
6. **Payment Entry** (NEFT/UPI). Invoice status flips to *Paid*. Receivables ageing updates.

### Cycle 2 — Procure-to-Pay ("Reorder to paid supplier")
1. **Material Request**, auto-raised when anaesthetic cartridges fall below reorder level
2. **Request for Quotation → Supplier Quotation** (2 suppliers compared)
3. **Purchase Order** to the winner
4. **Purchase Receipt**: batch number + expiry date captured, optional **Quality Inspection**
5. **Purchase Invoice** created *from* the receipt, so it is linked to both PO and
   receipt. Turn on Buying Settings → *Purchase Order Required* + *Purchase
   Receipt Required* so the chain can't be skipped. **Do not call this "3-way
   match"**: ERPNext links the documents but does not enforce price/qty matching.
6. **Payment Entry** to supplier

**Auto Material Request caveat:** the reorder check is a **daily scheduler job**
(around midnight), and the scheduler is **off by default** (`bench
enable-scheduler`, a setup command, not programming). It will **not** fire live
during the viva. Plan: drop cartridge stock below its reorder level one evening,
then screenshot the auto-created MR the next morning. In the viva, show that
auto MR and explain the trigger. If asked to demo live, raise an MR by hand.

Both cycles have 6 stages against the brief's 4, so we're safe if one screenshot is weak.
Bonus mini-flow if time allows: **expired-stock write-off** (Stock Entry to the
Quarantine warehouse).

**GST note:** India rationalised GST slabs in Sept 2025. Set each Item Tax
Template from the *current* rate for that HSN code, verified on cbic-gst.gov.in
(cite the URL). Do not copy rates from old blog posts.
**GST setup choice:** ERPNext's India GST features live in the separate *India
Compliance* app. Laziest safe path: **skip the app** and create two plain Sales
Taxes templates by hand (Intra-state CGST + SGST, Inter-state IGST) plus Item Tax
Templates per rate. All customers are in Karnataka, so intra-state is the default.
Install India Compliance only if someone wants GSTR reports, and then mind the
GSTIN trap in A3.

## A7. Reports (≥3 → we do 5) and the executive dashboard

The brief says the reports + dashboard must "showcase the **master data**,
transactions data and four KPIs". The reports below cover all three, and report 0
is the master-data one.

**Reports:**
0. **Clinic Customer Register** (Report Builder on Customer): name, group,
   territory, credit limit, default price list, sales person. **This is the
   master-data report.** Add an Item Register (code, group, batch/expiry flag,
   reorder level) as a second master report if pages allow.
1. Sales Analytics — monthly, by Customer Group and by Territory
2. Accounts Receivable — ageing buckets 0–30 / 31–60 / 61–90 / 90+
3. Batch-wise Balance History — stock with expiry dates (the distributor's nightmare report)
4. Purchase Analytics — spend by supplier per month
5. Gross Profit — by item group

**Executive Dashboard "Cusp Command Centre":**

Number Cards are simple aggregates (count/sum/avg) over one DocType, or a value
pulled from a report. Relative-date filters ("last 30 days") are awkward without
code. So each KPI below is defined to work with **static** filters, with a
fallback:

| KPI | How to build it (no code) | Fallback |
|---|---|---|
| **Revenue (₹), Aug–Nov** | Number Card: Sum of `grand_total` on submitted Sales Invoices | — |
| **Overdue Receivables (₹)** | Number Card: Sum of `outstanding_amount` on Sales Invoice where status = *Overdue* (ERPNext sets this itself) | Unpaid instead of Overdue |
| **Near-expiry Batches** | Number Card: Count (or Sum of `batch_qty`) on Batch where `expiry_date` ≤ 28 Feb 2027 | Batch-wise Balance History screenshot |
| **Gross Margin %** | Report-type Number Card from Gross Profit report | Gross Profit report on the dashboard page + % quoted in the caption |
| *(master)* **Active Clinic Customers** | Number Card: Count of Customer | — |

Test each card on **day 5**. Swap to the fallback the same day if a card won't
behave.

**Charts (≥2 → 4):** Monthly Sales (**column**, as the brief suggests; Dashboard
Chart on Sales Invoice, Sum, monthly time series) · Sales by Territory (bar,
group-by) · Top 5 Items by Revenue (bar) · Purchases vs Sales by month (line).

## A8. Report document (use faculty template)

- Min 10 images. We target **~22**: 12 cycle stages + 3 masters + 5 reports +
  dashboard + schema
- Each image on a **new page**, light theme (ERPNext default light, no dark mode),
  with caption + 2–3 line description
- **Dark-background traps:** install screenshots of a WSL terminal are black by
  default. Switch Windows Terminal to a light scheme (e.g. "One Half Light")
  before capturing them. dbdiagram.io has a dark mode, so export the schema in light.
- **Schema (req 9) scope:** masters (`tabCustomer`, `tabSupplier`, `tabItem`,
  `tabWarehouse`, `tabEmployee`, `tabPrice List`, `tabItem Price`, `tabBatch`) +
  transactions **and their child tables** (`tabSales Order` + `tabSales Order Item`,
  `tabPurchase Order` + `tabPurchase Order Item`, Delivery Note, Sales Invoice,
  Purchase Receipt, Purchase Invoice, Payment Entry). Draw links from the Link
  fields. Show only key columns (PK, FKs, 3–4 business fields).
- Sections: Business scenario → Product description (req 8) → Install steps →
  Masters → Transactions → Cycle 1 → Cycle 2 → Reports → Dashboard → Schema →
  Sources (URLs)
- **Product description research (req 8), every field the brief lists:**
  company (Frappe Technologies), **company locations** + **HQ**, **product
  versions** (version timeline + the one we installed), **features** (module
  list: Accounting, Selling, Buying, Stock, Manufacturing, Projects, HR via
  Frappe HR, CRM, etc.), **origin date**, **founders**, **clients** (named public
  case studies), plus licence (GPL-3.0) and the tech stack (Frappe framework,
  Python/JS, MariaDB). **Pull every fact from frappe.io / erpnext.com / GitHub
  and cite the URL. No facts from memory.**
- File (exact brief format, short 3-digit SRNs, ERP name):
  `EBS24CS-P01 127-xxx-xxx-xxx ERPNext.pdf`

## A9. Viva readiness (req 12)

Pairs: **M1 + M2 own O2C**, **M3 + M4 own P2P**. Everyone rehearses their cycle
end to end twice, live. Drill list: create and submit a new Sales Order for a
named clinic, cancel and amend an invoice, change a customer credit limit, add a
batch at receipt, rerun the AR report, explain one table in the schema.

**The viva runs on a live instance, so plan the machine:**
- ERPNext lives in WSL on one laptop. Before each viva slot: `bench start`, log
  in, open the dashboard, and keep the laptop on mains power.
- Take a `bench backup --with-files` after data entry is done (≈ 14 Nov), and
  again after any change. Copy it to a second member's laptop. Ideally have a
  second working install restored from that backup.
- Keep a short "demo script" card per member: which document, which record to modify.

---

# PART B — "Chairside" sales brochure

## B1. Identity

- **Company:** Chairside Labs Pvt. Ltd. (fictional AI-native EBS vendor), Koramangala, Bengaluru
- **Product:** **Chairside**, the AI-native operating system for dental clinics and the supply chain behind them (ERP + CRM + SCM)
- **Tagline:** **"The agents run the back office. You stay in the chair."**
  Alternates: "Every action explained. No mistake made twice." / "Autonomy you can audit."
- **Logo idea:** a dental-chair silhouette drawn as a single line that closes
  into a "C", with a small spark/node at the headrest. Flat SVG, works in one colour.
- **Palette:** enamel ivory background, deep teal (trust), coral accent (agent
  actions), graphite text. Light, print-friendly.
- **Type:** a characterful serif for headlines + a clean sans for body
  (decided at build time with the design skills).
- **Officers (req 6):** team names + SRNs as CEO, CTO, Chief Product Officer,
  Head of Trust & Safety.
- **Contact:** `hello@chairside.example`, `+91 80 0000 0000` (`.example` domain on
  purpose: fictional company, no real domain).

## B2. Modules (req 2) — mapped onto the brief's list

| Brief's module | Chairside module | What it covers |
|---|---|---|
| Sales | **Front Desk & CRM** | Patient records, appointments, treatment plans priced as ladders, recall outreach |
| Finance | **Billing & Ledger** | GST invoicing, UPI/card/EMI, insurance claim packs, receivables |
| Procurement | **Restock** | Supplier catalogue, POs, 3-way match, contract prices |
| Inventory / WH | **Store & Sterilisation** | Batch/expiry, FEFO, autoclave cycle logs, instrument kits |
| Production | **Lab Orders** | Crowns, bridges, aligners sent to dental labs: Rx, shade, due date, remakes |
| Quality | **Quality & Recall** | Lot traceability to patient, supplier recalls, incident log |
| HR | **Team & Chairs** | Rosters, chair utilisation, hygienist scheduling, payroll export |
| Analytics | **Pulse** | Owner dashboard: revenue per chair-hour, recall recovery, near-expiry stock |

**Services:** Implementation (2-week onboarding, Excel/legacy migration),
chairside staff training (in clinic, Kannada/English/Hindi), support (WhatsApp +
phone SLA), and *Agent Tuning*: a monthly review of the Precedent Ledger with the
customer.

## B3. The agents (req 3 — needs ≥3 modules; we show 5)

Every agent card in the brochure has the same four parts: **What it does · What
it can do alone · Where a human approves · What it will never do.**

1. **Recall Agent** (Front Desk & CRM)
   - Finds patients overdue for the next stage of treatment (root canal started but crown never fitted, aligner check missed) and drafts WhatsApp/voice outreach in the patient's language. Books into open chair slots.
   - *Alone:* reminders that use approved templates.
   - *Human:* the front desk approves any new message wording, and the dentist approves anything clinical.
   - *Never:* quotes a single price for a treatment that has a range. It always shows the ladder (RECALL's core lesson), and it never diagnoses.

2. **Restock Agent** (Restock + Store)
   - Reads *tomorrow's appointment book* (3 implant surgeries → 3 fixtures in the right sizes + abutments), checks stock FEFO, and drafts a PO to the cheapest supplier within contract.
   - *Alone:* POs under ₹5,000 to approved suppliers.
   - *Human:* the owner approves above the limit with one tap on their phone.
   - *Never:* orders from an unapproved supplier or above contract price.

3. **Ledger Sentinel** (Billing & Ledger)
   - Flags unusual invoices: a supplier bill priced above contract, a duplicate invoice number, a GST mismatch against the supplier's filing, a patient bill below the clinic's own price floor.
   - *Alone:* holds the payment and explains why.
   - *Human:* the accountant releases or rejects.
   - *Never:* moves money.

4. **Lab Liaison** (Lab Orders = Production)
   - Tracks every crown/aligner case at the lab, chases delays, and compares the delivered shade photo with the prescription before the patient visit.
   - *Human:* the dentist approves any remake request.

5. **Lot Tracer** (Quality & Recall)
   - When a supplier recalls a batch, lists every patient treated with that lot within minutes and drafts the clinic's response.
   - *Human:* the dentist decides patient contact.
   - *Never:* contacts patients about a recall without sign-off.

## B4. How it works (req 4) — one swimlane visual

**Procure-to-Pay, the Chairside way.** This deliberately mirrors Part A's cycle 2,
which makes for a strong presentation moment ("here is that cycle today, here
it is with agents").

| Step | AI lane (coral) | Human lane (teal) |
|---|---|---|
| 1 | Restock Agent reads tomorrow's surgeries + stock | |
| 2 | Drafts PO, picks supplier within contract | |
| 3 | | **Owner approves** (only if > ₹5,000) |
| 4 | Sends PO, tracks dispatch | |
| 5 | | **Assistant scans batch + expiry at delivery** |
| 6 | Ledger Sentinel 3-way matches PO ↔ receipt ↔ invoice | |
| 7 | | **Accountant releases payment** |
| 8 | Logs everything to the audit trail | |

## B5. Trust & security (req 5) — the section no other team will have

1. **Autonomy Dial, per agent, per clinic.** L0 Observe → L1 Suggest → L2 Draft →
   L3 Act with approval → L4 Act within limits. New clinics start at L1, and
   autonomy is *earned* with a track record.
2. **Precedent Ledger (from our `precedent` project).** When a human corrects an
   agent, the correction becomes a **blocking check**, not a note in a prompt.
   Brochure example: *"Sentinel once let a duplicate glove invoice through.
   Sunita rejected it. Since that day, a duplicate invoice number from any
   supplier is blocked before payment, at every clinic on Chairside."*
   Headline: **"No mistake made twice."**
3. **Policy Compiler (from our `injunct` project).** Upload the clinic's SOPs or
   price policy, and Chairside turns each sentence into an enforced rule where
   it can. A **coverage meter** shows what percentage of the policy is actually
   enforced, so owners see the gap instead of assuming coverage.
4. **Hard limits:** spend caps, supplier allow-lists, dual approval on payments,
   one-tap **pause all agents**.
5. **Every action explained:** reasoning, inputs and approver are logged and
   replayable for audit.
6. **Data:** built for India's DPDP Act 2023, data hosted in India, encryption in
   transit and at rest, role-based access, patient identifiers redacted before
   any model call, **patient data never trains shared models**.
7. **Clinical boundary:** agents never diagnose or prescribe. Clinical calls stay with the dentist.

## B6. Plans & pricing (req 6) — INR, per month, billed annually

| Plan | For | Price | Includes |
|---|---|---|---|
| **Solo** | 1–2 chairs | ₹2,499 / clinic | Front Desk, Billing, Store; Recall Agent up to L2 |
| **Practice** | 3–8 chairs | ₹6,999 / clinic | All modules, all 5 agents up to L3, Precedent Ledger |
| **Group** | Chains, 3+ branches | ₹1,199 / chair (min 20) | L4 autonomy, Policy Compiler, SSO, cross-branch stock |
| **Supplier Network** | Distributors (like Cusp Dental) | ₹14,999 / warehouse | Clinic order portal, Restock Agent integration, recall broadcast |

One-time: Implementation ₹25,000 (Solo/Practice), quoted for Group. Training
included. Premium support add-on available.

**Testimonial (fictional, clearly part of the story):** Cusp Dental Supplies, a
pilot distributor: *"Near-expiry write-offs fell after clinics started ordering
off tomorrow's surgery list."* No invented numbers; keep it qualitative.

## B7. Brochure layout (min 6 pages → we do 8, booklet style, A4 portrait)

1. **Cover**: logo, name, tagline, hero image (clinic chair in soft light)
2. **The problem / why now**: the clinic back office today (WhatsApp, Excel, expired stock, missed recalls). Any statistic must be cited or left out.
3. **The platform**: 8 module tiles + services strip
4. **Meet the agents**: 5 agent cards (does / alone / human approves / never)
5. **How it works**: the P2P swimlane, AI vs human lanes
6. **Trust & security**: Autonomy Dial graphic, Precedent Ledger story, Policy Compiler coverage meter, data promises
7. **Services + pilot customer**: implementation, training, support, Agent Tuning, Cusp testimonial
8. **Plans, contacts, officers, sources**: pricing table, contact block, team as officers with SRNs, image/info source URLs

**Images with blurbs (req 1 asks for "relevant and interesting images with
suitable blurbs"; one hero is not enough).** At least one image per page, and
each one gets a 1–2 line blurb:

| Page | Image | Blurb idea |
|---|---|---|
| 1 | Sunlit dental chair, empty operatory | "The chair is where care happens. Everything else, we run." |
| 2 | Cluttered front desk: WhatsApp, paper register, Excel | "Most clinics run on three apps and a notebook." |
| 3 | Product UI mock: owner dashboard on a tablet | "One screen for chairs, stock, cash and recalls." |
| 4 | Five agent "portrait" icons (consistent illustrated set) | One line per agent |
| 5 | The swimlane diagram (our own) | "Agents draft. People decide where it matters." |
| 6 | Autonomy Dial graphic + Policy coverage meter (our own) | "Autonomy is earned, never assumed." |
| 7 | Trainer with clinic staff at a chair | "Two weeks from Excel to Chairside." |
| 8 | Logo lock-up + team portraits (or initials) | Officer titles |

Our own diagrams and UI mocks avoid licensing issues. Stock photos must be
free-licence, with the URL on page 8.

**Build:** HTML/CSS print layout → Chrome "Save as PDF" (no Figma needed). Logo
as hand-built SVG.
**File (exact brief format):** `EBS24CS-P02 127-xxx-xxx-xxx Chairside.pdf`

**Presenting Part B (16–19 Nov):** the brief says "design, brand, **and
present**". Prepare 4–5 slides, or just walk through the PDF, as the leadership
team. Each officer pitches their own page (CEO → problem + platform, CTO →
agents + how it works, Head of Trust → security, CPO → pricing). Optionally open
with the 20-second `/brag` video.

**Presentation bonus:** a 20-second launch video of the brochure page via `/brag`.

---

# Plan, roles, risks

## Timeline (12 days)

| Date | Part A | Part B |
|---|---|---|
| Wed 4 Nov | Idea locked, team briefed | |
| Thu 5 | ERPNext installed on WSL, company + fiscal year + GST setup | Name/logo sketch |
| Fri 6 – Sat 7 | All 8 masters entered | Copy draft (all 8 pages) |
| Sun 8 – Mon 9 | 12 SOs + 12 POs and their full downstream chains | |
| Tue 10 | Reports + dashboard + schema in dbdiagram.io | Layout build |
| Wed 11 – Thu 12 | Screenshots (light theme), product research with URLs | Images, swimlane, pricing page |
| Fri 13 – Sat 14 | Report in faculty template | Polish, sources page, PDF export |
| Sun 15 | Full dry run: each member demos their cycle live | Final read |
| **Mon 16** | **Submit both PDFs** | |

## Roles (4)

| Member | Part A | Part B | Viva cycle |
|---|---|---|---|
| M1 | Sales masters + O2C transactions | Agents page | O2C |
| M2 | Customers/pricing + dashboard | Branding, logo, cover | O2C |
| M3 | Supplier/item masters + P2P transactions | Trust & security page | P2P |
| M4 | Reports, schema, report document | Pricing, layout, PDF | P2P |

## Risks → mitigations

| Risk | Mitigation |
|---|---|
| ERPNext install fights WSL | Day-1 timebox: bench by Thu night, else `frappe_docker`, else Odoo Community |
| Schema tool shows no relations | Known (Link fields, no FKs). Use dbdiagram.io from the start |
| Plagiarism flag | All text written fresh by us. Fictional names. No copied ERPNext docs; facts paraphrased and cited |
| Real clinic names leak in | Customer list above is collision-checked against RECALL's 64 real profiles. Never import from `recall/clinics` |
| GST rates wrong | Verify current HSN rates on cbic-gst.gov.in, cite URL |
| Dark screenshots | ERPNext light theme only, browser zoom 100% |
| Someone can't demo live | Every member runs their cycle end to end twice before 15 Nov |
| Linking A and B looks like we ignored "Part A and Part B are not related" | Each PDF stands alone. The only cross-link is the fictional testimonial on brochure p.7; drop it if faculty object |

---

# Compliance matrix (brief → where we satisfy it)

Verified line by line against `EBS-24CS_Team_Project_2026_Aug-Dec.pdf` on 4 Nov 2026.

## Admin

| Brief item | Status | Where |
|---|---|---|
| Team ≤ 4, **registered by 26/10/2026** | ⚠ **CONFIRM:** deadline already passed. Check we are registered | — |
| Part A and B in separate PDFs | ✅ | A8, B7 |
| File names: course code + short SRNs | ✅ (fill in teammates' SRNs) | A8, B7 |
| URLs for all sourced info, in both PDFs | ✅ | A8 sources section, brochure p.8 |
| Plagiarism-safe | ✅ fictional names, own text | Risks |
| Upload via faculty Google Drive form | ⏳ form not shared yet | — |
| Report template from faculty | ⏳ **not received yet**. Chase it; A8 depends on it | A8 |
| Due 16 Nov, presentations 16–19 Nov | ✅ | Timeline |

## Part A

| # | Requirement | Status | Where |
|---|---|---|---|
| — | Install open-source EBS on own computer | ✅ ERPNext on WSL; install screenshots | A1, A8 |
| — | No programming in the package | ✅ all config via UI; bench commands are setup only | A1 |
| 1 | Realistic scenario in a listed domain | ✅ Healthcare (dental supply distribution) | A2 |
| 2 | ≥ 6 master entities, sufficient data | ✅ 6 core (Customer, Supplier, Item, Warehouse, Employee, Price List) + 2; 72 Item Prices | A3 |
| 3 | ≥ 10 realistic transactions in each of 2 tables, proper names | ✅ 12 SO + 12 PO, real-style names. ⏳ full seed sheet still to write | A5 |
| 4 | Entire workflow of 2 cycles | ✅ O2C 6 stages, P2P 6 stages | A6 |
| 5 | Screenshots, ≥ 4 sequential stages per cycle, documented | ✅ 6 + 6 | A6, A8 |
| 6 | **All** SRNs + names in master **and** transaction data | ✅ Employees, Users, Sales Persons (master); owner stamps, Sales Team, PO Buyer field, rotated batch IDs (transactions) | A4 |
| 7 | ≥ 3 reports + exec dashboard: master data, transactions, 4 KPIs, ≥ 2 charts (e.g. monthly sales column) | ✅ 6 reports incl. master register; 4 KPIs + master card; 4 charts incl. monthly column. ⚠ Gross Margin card has a fallback | A7 |
| 8 | Product description: locations, HQ, versions, features, origin date, founders, clients | ✅ checklist, all cited | A8 |
| 9 | Relational schema via a tool | ✅ dbdiagram.io (ERPNext has no DB FKs, so auto-ER won't work) | A1, A8 |
| 10 | Report in template, ≥ 10 images, dashboard + reports | ✅ ~22 images | A8 |
| 11 | Each image on a new page, no dark backgrounds, caption + description | ✅ incl. terminal/dbdiagram light-mode traps | A8 |
| 12 | Live demo / modify / regenerate; each member explains a full cycle | ✅ pairs per cycle, drill list, backup instance | A9 |

## Part B

| # | Requirement | Status | Where |
|---|---|---|---|
| — | Startup vendor leadership team, AI-native EBS | ✅ Chairside Labs, team as officers | B1 |
| — | Agentic AI (reason, plan, execute) with guardrails | ✅ 5 agents, Autonomy Dial, Precedent Ledger | B3, B5 |
| 1 | Logo, name, tagline, images with blurbs | ✅ image + blurb per page | B1, B7 |
| 2 | Key modules + services (implementation, training, support) | ✅ 8 modules covering all brief examples; 4 services | B2 |
| 3 | AI in ≥ 3 modules + where a human approves | ✅ 5 modules, human gate on every card | B3 |
| 4 | One simple visual: process with AI vs people steps | ✅ P2P swimlane | B4 |
| 5 | Trust & security section | ✅ 7 controls | B5 |
| 6 | Pricing plans, contacts, student names as officers | ✅ 4 plans + services, `.example` contact, officers with SRNs | B6, B1 |
| — | Digital booklet PDF, ≥ 6 pages | ✅ 8 pages A4 | B7 |
| — | Present it | ✅ officer-per-page pitch | B7 |

**Open items before this is "done":** confirm team registration · get the
report template · teammates' names + SRNs · write the 24-row seed sheet ·
day-2 FEFO test · day-5 dashboard-card test.

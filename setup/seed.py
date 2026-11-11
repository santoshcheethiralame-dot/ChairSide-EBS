"""Seed data for Cusp Dental Supplies Pvt. Ltd. (fictional). Pure data, no logic.

Member keys (M1..M4) are resolved against team.json at load time.
Prices in INR. Dates are 2026 posting dates (fiscal year Apr 2026 - Mar 2027).
"""

COMPANY = "Cusp Dental Supplies Pvt. Ltd."
ABBR = "CDS"

ITEM_GROUPS = ["Anaesthetics", "Restoratives", "Endodontics", "Implants",
               "Orthodontics", "Prosthetics", "Infection Control", "Dental Equipment"]

CUSTOMER_GROUPS = ["Single-chair Clinic", "Multi-chair Clinic", "Implant Centre",
                   "Orthodontic Practice", "Paediatric Clinic", "Clinic Chain"]

SUPPLIER_GROUPS = ["Dental Manufacturers", "Dental Wholesalers"]

# territory -> member who covers it (also the Sales Person on its orders)
TERRITORIES = {
    "South": "M1",
    "South-East": "M1",
    "Central": "M2",
    "North": "M3",
    "East": "M4",
}

WAREHOUSES = ["Peenya Central", "Jayanagar Counter", "Quarantine & Expired"]

UOMS = ["Box", "Pack", "Kit", "Bottle", "Syringe", "Nos"]

# code, name, group, uom, batch, expiry, buy, sell, chain, gst, supplier, reorder(level, qty)
ITEMS = [
    ("ANS-LIG2", "Lignocaine 2% + Adrenaline 1:80,000 Cartridges (Box of 50)", "Anaesthetics", "Box", 1, 1, 1450, 1850, 1700, 5, "Septodont Healthcare India", (25, 50)),
    ("ANS-ART4", "Articaine 4% + Adrenaline 1:100,000 Cartridges (Box of 50)", "Anaesthetics", "Box", 1, 1, 2900, 3600, 3300, 5, "Septodont Healthcare India", (5, 10)),
    ("RST-CMPA2", "Nano-hybrid Composite, Shade A2, 4 g Syringe", "Restoratives", "Syringe", 1, 1, 1150, 1550, 1420, 5, "Ivoclar Vivadent India", (10, 20)),
    ("RST-CMPA3", "Nano-hybrid Composite, Shade A3, 4 g Syringe", "Restoratives", "Syringe", 1, 1, 1150, 1550, 1420, 5, "Ivoclar Vivadent India", (8, 15)),
    ("RST-GIC2", "Glass Ionomer Restorative Cement, Type II Kit", "Restoratives", "Kit", 1, 1, 1300, 1700, 1560, 5, "GC India Dental", (8, 15)),
    ("RST-BOND", "Universal Bonding Agent, 5 ml", "Restoratives", "Bottle", 1, 1, 2100, 2750, 2520, 5, "Dentsply Sirona India", (5, 10)),
    ("END-NITI25", "NiTi Rotary File Set, 25 mm (Pack of 6)", "Endodontics", "Pack", 0, 0, 1250, 1700, 1560, 5, "Dentsply Sirona India", (8, 10)),
    ("END-GP02", "Gutta-percha Points, 2% Taper (Box of 120)", "Endodontics", "Box", 1, 1, 380, 520, 480, 5, "Prime Dental Products", (15, 40)),
    ("END-NAOCL", "Sodium Hypochlorite 3% Irrigant, 500 ml", "Endodontics", "Bottle", 1, 1, 210, 320, 290, 5, "Prime Dental Products", (15, 30)),
    ("IMP-3510", "Dental Implant Fixture, 3.5 x 10 mm", "Implants", "Nos", 1, 1, 7800, 10500, 9800, 5, "Osstem Implant India", (6, 10)),
    ("IMP-4011", "Dental Implant Fixture, 4.0 x 11.5 mm", "Implants", "Nos", 1, 1, 8200, 11000, 10200, 5, "Osstem Implant India", (6, 10)),
    ("IMP-HA4", "Healing Abutment, 4 mm", "Implants", "Nos", 1, 1, 1400, 2000, 1850, 5, "Osstem Implant India", (10, 15)),
    ("ORT-MBT22", "MBT 0.022 Metal Bracket Kit (20 brackets)", "Orthodontics", "Kit", 0, 0, 950, 1350, 1240, 5, "Waldent Innovations", (8, 10)),
    ("ORT-NT14U", "NiTi Archwire 0.014, Upper (Pack of 10)", "Orthodontics", "Pack", 0, 0, 450, 650, 600, 5, "Waldent Innovations", (10, 20)),
    ("PRS-ZRB98", "Zirconia Milling Block, 98 x 14 mm", "Prosthetics", "Nos", 1, 0, 6500, 8400, 7900, 5, "Ivoclar Vivadent India", (4, 5)),
    ("PRS-ALG450", "Alginate Impression Material, 450 g", "Prosthetics", "Pack", 1, 1, 420, 580, 540, 5, "GC India Dental", (10, 20)),
    ("INF-GLVM", "Nitrile Examination Gloves, Medium (Box of 100)", "Infection Control", "Box", 1, 1, 290, 420, 380, 5, "Chickpet Surgicals", (30, 60)),
    ("INF-GLVS", "Nitrile Examination Gloves, Small (Box of 100)", "Infection Control", "Box", 1, 1, 290, 420, 380, 5, "Chickpet Surgicals", (20, 30)),
    ("INF-POUCH", "Self-sealing Autoclave Pouches, 90 x 230 mm (Box of 200)", "Infection Control", "Box", 0, 0, 480, 680, 620, 18, "Chickpet Surgicals", (20, 30)),
    ("INF-DISF", "Surface Disinfectant Spray, 1 L", "Infection Control", "Bottle", 1, 1, 520, 720, 660, 18, "Chickpet Surgicals", (10, 20)),
    ("INF-MASK", "3-ply Surgical Face Masks (Box of 50)", "Infection Control", "Box", 1, 1, 95, 160, 140, 5, "Chickpet Surgicals", (25, 40)),
    ("EQP-LEDCL", "LED Curing Light, Cordless", "Dental Equipment", "Nos", 0, 0, 6200, 8500, 7900, 5, "Waldent Innovations", (2, 4)),
    ("EQP-USCL", "Ultrasonic Scaler Handpiece, Detachable", "Dental Equipment", "Nos", 0, 0, 4800, 6600, 6100, 5, "Waldent Innovations", (2, 3)),
    ("EQP-APEX", "Electronic Apex Locator", "Dental Equipment", "Nos", 0, 0, 7400, 9800, 9200, 5, "Waldent Innovations", (1, 3)),
]

# name, group, contact first, contact last, city note
SUPPLIERS = [
    ("Septodont Healthcare India", "Dental Manufacturers", "Rakesh", "Iyer"),
    ("Dentsply Sirona India", "Dental Manufacturers", "Priya", "Sharma"),
    ("Ivoclar Vivadent India", "Dental Manufacturers", "Anil", "Desai"),
    ("GC India Dental", "Dental Manufacturers", "Kiran", "Reddy"),
    ("Prime Dental Products", "Dental Manufacturers", "Mahesh", "Patil"),
    ("Waldent Innovations", "Dental Manufacturers", "Neha", "Gupta"),
    ("Osstem Implant India", "Dental Manufacturers", "Sanjay", "Nair"),
    ("Chickpet Surgicals", "Dental Wholesalers", "Imran", "Pasha"),
]

# name, territory, group, doctor first, doctor last, address line, pincode, credit limit
CUSTOMERS = [
    ("Banyan Tree Dental Studio", "East", "Multi-chair Clinic", "Meera", "Raghavan", "12, 100 Feet Road, HAL 2nd Stage, Indiranagar", "560038", 150000),
    ("Molarwise Family Dentistry", "South-East", "Single-chair Clinic", "Arjun", "Shetty", "27th Main, Sector 2, HSR Layout", "560102", 60000),
    ("Pearl Arch Dental Care", "North", "Multi-chair Clinic", "Kavya", "Iyengar", "8th Cross, Margosa Road, Malleshwaram", "560003", 150000),
    ("Root & Crown Dental", "East", "Implant Centre", "Farhan", "Qureshi", "ITPL Main Road, Whitefield", "560066", 300000),
    ("Aligna Orthodontic Centre", "South-East", "Orthodontic Practice", "Sneha", "Pai", "80 Feet Road, 4th Block, Koramangala", "560034", 120000),
    ("Twin Canines Kids Dental", "South", "Paediatric Clinic", "Rohan", "Hegde", "11th Main, 4th Block, Jayanagar", "560011", 80000),
    ("Gulmohar Dental & Implant Centre", "North", "Clinic Chain", "Nandini", "Gowda", "Bellary Road, Hebbal", "560024", 400000),
    ("Basavanagudi Smile Works", "South", "Single-chair Clinic", "Prakruthi", "Rao", "Bull Temple Road, Basavanagudi", "560004", 60000),
    ("Bluebell Dental Clinic", "North", "Single-chair Clinic", "Vivek", "Menon", "4th Main, Yelahanka New Town", "560064", 25000),
    ("Cubbon Dental Associates", "Central", "Multi-chair Clinic", "Ayesha", "Khan", "Church Street, off MG Road", "560001", 150000),
    ("Sankey Smiles Dental", "Central", "Multi-chair Clinic", "Tejas", "Kulkarni", "Sankey Road, Sadashivanagar", "560080", 150000),
    ("Kanakapura Road Dental Hub", "South", "Clinic Chain", "Lakshmi", "Narayan", "Kanakapura Main Road, Konanakunte", "560062", 300000),
]

# Opening stock, 31 Jul 2026. (item, suffix, qty, expiry or None, counted_by member)
# Batch ID = CDS-<srn3 of counter>-<short>-0726<suffix>
OPENING = [
    ("ANS-LIG2", "A", 30, "2027-01-31", "M1"), ("ANS-LIG2", "B", 20, "2028-06-30", "M1"),
    ("ANS-ART4", "A", 10, "2028-03-31", "M1"),
    ("RST-CMPA2", "A", 15, "2027-02-28", "M1"), ("RST-CMPA2", "B", 10, "2028-01-31", "M1"),
    ("RST-CMPA3", "A", 15, "2027-12-31", "M1"),
    ("RST-GIC2", "A", 10, "2027-09-30", "M1"),
    ("RST-BOND", "A", 6, "2027-05-31", "M1"),
    ("END-NITI25", None, 15, None, "M2"),
    ("END-GP02", "A", 30, "2028-12-31", "M2"),
    ("END-NAOCL", "A", 25, "2027-02-15", "M2"),
    ("IMP-3510", "A", 10, "2031-06-30", "M3"),
    ("IMP-4011", "A", 8, "2031-06-30", "M3"),
    ("IMP-HA4", "A", 12, "2031-06-30", "M3"),
    ("ORT-MBT22", None, 12, None, "M3"),
    ("ORT-NT14U", None, 20, None, "M3"),
    ("PRS-ZRB98", "A", 5, None, "M2"),
    ("PRS-ALG450", "A", 15, "2027-01-15", "M2"),
    ("INF-GLVM", "A", 40, "2028-07-31", "M4"),
    ("INF-GLVS", "A", 20, "2028-07-31", "M4"),
    ("INF-POUCH", None, 25, None, "M4"),
    ("INF-DISF", "A", 15, "2027-12-31", "M4"),
    ("INF-MASK", "A", 30, "2026-12-31", "M4"),
    ("EQP-LEDCL", None, 3, None, "M4"),
    ("EQP-USCL", None, 2, None, "M4"),
    ("EQP-APEX", None, 1, None, "M4"),
]

# Purchase orders. id, date, supplier, buyer, items[(code, qty)], receipt date, receiver,
# received override {code: qty} for partial receipts, expiry per code, paid date or None
PURCHASES = [
    ("PO1", "2026-08-03", "Osstem Implant India", "M3", [("IMP-3510", 10), ("IMP-4011", 10), ("IMP-HA4", 15)],
     "2026-08-07", "M4", None, {"IMP-3510": "2031-07-31", "IMP-4011": "2031-07-31", "IMP-HA4": "2031-07-31"}, "2026-08-30"),
    ("PO2", "2026-08-10", "Chickpet Surgicals", "M3", [("INF-GLVM", 60), ("INF-GLVS", 30), ("INF-MASK", 40)],
     "2026-08-12", "M4", None, {"INF-GLVM": "2028-08-31", "INF-GLVS": "2028-08-31", "INF-MASK": "2027-07-31"}, "2026-09-10"),
    ("PO3", "2026-08-18", "Ivoclar Vivadent India", "M3", [("RST-CMPA2", 20), ("RST-CMPA3", 10), ("PRS-ZRB98", 5)],
     "2026-08-22", "M3", None, {"RST-CMPA2": "2028-08-31", "RST-CMPA3": "2028-08-31"}, "2026-09-20"),
    ("PO4", "2026-08-26", "Waldent Innovations", "M4", [("ORT-MBT22", 10), ("ORT-NT14U", 20), ("EQP-LEDCL", 4)],
     "2026-08-29", "M4", None, {}, "2026-09-25"),
    ("PO5", "2026-09-04", "GC India Dental", "M3", [("RST-GIC2", 15), ("PRS-ALG450", 20)],
     "2026-09-08", "M3", None, {"RST-GIC2": "2028-03-31", "PRS-ALG450": "2027-09-30"}, "2026-10-05"),
    ("PO6", "2026-09-15", "Dentsply Sirona India", "M3", [("END-NITI25", 10), ("RST-BOND", 10)],
     "2026-09-18", "M4", None, {"RST-BOND": "2028-09-30"}, "2026-10-15"),
    ("PO7", "2026-09-25", "Prime Dental Products", "M4", [("END-GP02", 40), ("END-NAOCL", 30)],
     "2026-09-28", "M4", None, {"END-GP02": "2029-09-30", "END-NAOCL": "2027-09-30"}, "2026-10-25"),
    ("PO8", "2026-10-05", "Septodont Healthcare India", "M3", [("ANS-LIG2", 20), ("ANS-ART4", 10)],
     "2026-10-08", "M3", None, {"ANS-LIG2": "2028-09-30", "ANS-ART4": "2028-09-30"}, "2026-11-02"),
    ("PO9", "2026-10-14", "Osstem Implant India", "M3", [("IMP-3510", 8), ("IMP-HA4", 10)],
     "2026-10-17", "M4", {"IMP-3510": 5}, {"IMP-3510": "2031-10-31", "IMP-HA4": "2031-10-31"}, None),
    ("PO10", "2026-10-22", "Waldent Innovations", "M4", [("EQP-APEX", 3), ("EQP-USCL", 3)],
     "2026-10-26", "M4", None, {}, None),
    ("PO11", "2026-10-29", "Chickpet Surgicals", "M3", [("INF-DISF", 20), ("INF-POUCH", 30), ("INF-GLVM", 40)],
     "2026-11-02", "M3", None, {"INF-DISF": "2028-10-31", "INF-GLVM": "2028-10-31"}, None),
    # PO12 is the showcase procure-to-pay cycle (auto Material Request -> RFQ -> ...), built separately.
]

# Sales orders. id, date, customer, items[(code, qty)], delivery date, invoice date,
# payment (date, fraction) or None, from_quotation date or None
SALES = [
    ("SO1", "2026-08-05", "Root & Crown Dental", [("IMP-3510", 6), ("IMP-HA4", 6), ("ANS-ART4", 2)], "2026-08-06", "2026-08-06", ("2026-08-28", 1.0), None),
    ("SO2", "2026-08-12", "Aligna Orthodontic Centre", [("ORT-MBT22", 8), ("ORT-NT14U", 10), ("INF-GLVM", 5)], "2026-08-13", "2026-08-13", ("2026-09-05", 1.0), None),
    ("SO3", "2026-08-20", "Pearl Arch Dental Care", [("RST-CMPA2", 6), ("RST-GIC2", 4), ("ANS-LIG2", 6), ("INF-MASK", 10)], "2026-08-21", "2026-08-21", ("2026-09-15", 1.0), None),
    ("SO4", "2026-09-03", "Gulmohar Dental & Implant Centre", [("IMP-4011", 5), ("IMP-HA4", 5), ("ANS-LIG2", 10), ("INF-GLVM", 20), ("EQP-LEDCL", 1)], "2026-09-04", "2026-09-04", ("2026-10-01", 1.0), "2026-09-01"),
    ("SO5", "2026-09-10", "Twin Canines Kids Dental", [("RST-GIC2", 6), ("ANS-LIG2", 4), ("INF-GLVS", 10), ("INF-POUCH", 6)], "2026-09-11", "2026-09-11", ("2026-10-05", 1.0), None),
    ("SO6", "2026-09-22", "Cubbon Dental Associates", [("END-NITI25", 6), ("END-GP02", 10), ("END-NAOCL", 8), ("RST-BOND", 3), ("ANS-LIG2", 6)], "2026-09-23", "2026-09-23", ("2026-10-20", 0.5), None),
    ("SO7", "2026-10-01", "Kanakapura Road Dental Hub", [("INF-GLVM", 30), ("INF-MASK", 20), ("INF-DISF", 10), ("ANS-LIG2", 10), ("RST-CMPA3", 8)], "2026-10-02", "2026-10-02", None, None),
    ("SO8", "2026-10-09", "Banyan Tree Dental Studio", [("PRS-ZRB98", 3), ("PRS-ALG450", 10), ("RST-CMPA2", 5), ("EQP-USCL", 1)], "2026-10-10", "2026-10-10", ("2026-10-30", 1.0), None),
    ("SO9", "2026-10-16", "Basavanagudi Smile Works", [("ANS-LIG2", 5), ("RST-CMPA2", 3), ("INF-GLVM", 6), ("END-NAOCL", 4)], "2026-10-17", "2026-10-17", None, None),
    ("SO10", "2026-10-24", "Sankey Smiles Dental", [("EQP-APEX", 1), ("END-NITI25", 4), ("END-GP02", 6), ("ANS-ART4", 4)], "2026-10-26", "2026-10-26", None, None),
    # SO11 = showcase order-to-cash (Gulmohar, from quotation, pick list), built separately.
    # SO12 = credit-limit demo (Bluebell), built separately.
]

SHOWCASE_O2C = {"customer": "Gulmohar Dental & Implant Centre", "quotation_date": "2026-10-30",
                "so_date": "2026-11-02", "pick_date": "2026-11-03", "invoice_date": "2026-11-03",
                "payment_date": "2026-11-04",
                "items": [("ANS-LIG2", 8), ("IMP-3510", 4), ("IMP-HA4", 4), ("INF-GLVM", 10)]}

CREDIT_DEMO = {"customer": "Bluebell Dental Clinic", "date": "2026-11-04",
               "items": [("EQP-LEDCL", 2), ("INF-GLVM", 10), ("ANS-LIG2", 2), ("RST-CMPA2", 2)]}

OPEN_QUOTATION = {"customer": "Molarwise Family Dentistry", "date": "2026-10-28",
                  "items": [("RST-CMPA2", 4), ("RST-GIC2", 2), ("INF-GLVM", 5), ("EQP-LEDCL", 1)]}

SHOWCASE_P2P = {"item": "ANS-LIG2", "suppliers": {"Septodont Healthcare India": 1450, "Chickpet Surgicals": 1520},
                "winner": "Septodont Healthcare India", "date": "2026-11-05", "expiry": "2029-06-30"}

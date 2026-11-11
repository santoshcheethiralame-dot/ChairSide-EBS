# ChairSide & Cusp Dental Supplies (EBS Team Project)

**Course:** UE24CS343AB8 Enterprise Business Solutions (EBS)  
**Deliverables:** Part A (ERP Implementation & Operations) + Part B (AI-Native Innovation)

---

## 📌 Project Overview

This project bridges traditional Enterprise Resource Planning with the AI-native future of healthcare supply chains:

1. **Part A — Cusp Dental Supplies Pvt. Ltd. (ERPNext v15)**
   - Production-grade deployment of ERPNext modeling a Bengaluru-based dental supply distributor.
   - Complete end-to-end operational cycles: **Order-to-Cash (O2C)** and **Procure-to-Pay (P2P)**.
   - Batch tracking, FEFO (First-Expired, First-Out), automated material reordering, credit limit enforcement, GST accounting, custom executive dashboard, and analytical reports.
   - Data populated via automated REST API orchestration reflecting individual team member ownership.

2. **Part B — ChairSide (AI-Native Dental Practice ERP)**
   - Conceptual AI-native system designed for dental clinics and suppliers.
   - Autonomous multi-agent coordination for patient recall, smart inventory replenishment, automated supplier quotation matching, and invoice auditing.
   - Built-in trust architecture featuring a **Precedent Ledger** (never repeat corrected mistakes) and **Policy Compiler** (convert clinic policies into deterministic execution rules).

---

## 📂 Project Structure

```
ebs-project/
├── backups/           # Database backup snapshot for instant restoration
├── brochure/          # Source HTML & build pipeline for Part B Chairside brochure
│   ├── brochure.html  # High-fidelity marketing & technical design document
│   └── build.py       # Playwright rendering script to produce Part B PDF
├── out/               # Generated deliverables and inspection artifacts
│   ├── EBS24CS-P01 127-XX2-XX3-XX4 ERPNext.pdf    # Part A Comprehensive Report
│   ├── EBS24CS-P02 127-XX2-XX3-XX4 Chairside.pdf  # Part B Product Brochure
│   ├── schema/        # Graphviz DOT files and rendered O2C / P2P ER diagrams
│   └── shots/         # High-resolution screenshots of ERPNext workflows & reports
├── setup/             # Automation suite for ERPNext configuration & data seeding
│   ├── 01_system.sh   # System dependencies (Node 20, MariaDB, Redis)
│   ├── 02_bench.sh    # Bench & ERPNext site initialization
│   ├── 03_start.sh    # ERPNext server startup script
│   ├── api.py         # Frappe REST API wrapper
│   ├── seed.py        # Master data, catalogs, pricing ladders, transaction fixtures
│   ├── load_masters.py
│   ├── load_txn.py
│   ├── load_showcase.py
│   ├── load_dashboard.py
│   ├── schema.py      # Live DocType metadata schema diagram generator
│   ├── shots.py       # Automated UI screenshot capture with Playwright
│   ├── report.py      # Part A report compiler
│   └── team.json      # Team configuration and role assignments
├── IDEA.md            # Detailed concept statement, workflow designs, and rubrics
└── README.md          # Project documentation
```

---

## 🚀 Quick Start & Rebuild

### 1. Start the ERPNext Server
From WSL Ubuntu:
```bash
wsl -d Ubuntu -u carbo -- bash /mnt/c/Users/carbo/projects/ebs-project/setup/03_start.sh
```
The ERPNext web interface is accessible at `http://localhost:8000`.

### 2. Regenerate Deliverable PDFs
Run from the Windows command line:
```bash
# Generate Part A ERPNext Report
python setup/report.py

# Generate Part B Chairside Brochure
python brochure/build.py
```
Outputs are written to the `out/` directory.

---

## 👥 Team
- **Santosh Cheethirala** (PES1UG24CS127) - *Sales Manager*
- Team members configured in `setup/team.json`.

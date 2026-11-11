# Cusp Dental Supplies on ERPNext: build and rebuild

Local course instance: ERPNext v15 in WSL Ubuntu 24.04, site `cusp.localhost`, served at
http://localhost:8000. Credentials are local test values in `local.env`.

## Logins

| Who | User | Password |
|---|---|---|
| Admin | `Administrator` | `ADMIN_PW` in local.env |
| Each member | email from `team.json` | `MEMBER_PW` in local.env |

## Start the server (every time, e.g. before the viva)

```bash
wsl -d Ubuntu -u carbo -- bash /mnt/c/Users/carbo/projects/ebs-project/setup/03_start.sh
```
Leave it running and open http://localhost:8000.

## Rebuild with real teammate names and SRNs

Names and SRNs appear in users, employees, sales persons, batch IDs and document owners,
so put them in **before** loading data:

1. Edit `team.json`: name, srn, srn3 (last 3 digits) for M2–M4.
2. Recreate the site: `wsl -d Ubuntu -u carbo -- bash .../setup/02_bench.sh --fresh`
3. Start the server (above), then from `setup/` in Windows:
   ```bash
   python load_masters.py && python load_txn.py && python load_showcase.py && python load_dashboard.py
   python schema.py && python shots.py && python report.py
   cd ../brochure && python build.py
   ```
4. Both PDFs land in `out/`.

## What each stage does

| Script | Stage |
|---|---|
| `01_system.sh` (root) | Node 20, MariaDB config, Redis |
| `02_bench.sh` | bench + Frappe/ERPNext v15 + site |
| `load_masters.py` | setup wizard, settings, taxes, 8 master entities, 72 item prices |
| `load_txn.py` | opening stock + 11 POs and 10 SOs replayed in date order, each by its owner |
| `load_showcase.py` | the two documented cycles (SO11 O2C, PO12 P2P), credit-limit demo, open quotation |
| `load_dashboard.py` | Report Builder reports, Number Cards, charts, "Cusp Command Centre" dashboard |
| `schema.py` | ER diagrams from live DocType metadata (Graphviz) |
| `shots.py` | report screenshots via headless Chrome |
| `report.py` | Part A report PDF |

Data was entered through ERPNext's REST API, acting as each member's own user, so every
document shows its real owner. Nothing in ERPNext was programmed or modified: all
configuration (custom field, reports, dashboard) is the same as doing it in the UI.
**Practise entering one Sales Order and one Purchase Order by hand before the viva.**

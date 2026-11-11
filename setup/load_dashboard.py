"""Stage 4: saved Report Builder reports (master data) + executive dashboard
(Number Cards + Dashboard Charts). Pure configuration, the same as doing it in the UI."""
import json
from api import admin
from seed import COMPANY

a = admin()


def report(name, ref, fields, order):
    if a.exists("Report", name):
        return
    a.insert({"doctype": "Report", "report_name": name, "ref_doctype": ref, "report_type": "Report Builder",
              "is_standard": "No", "module": "Selling" if ref == "Customer" else "Stock",
              "json": json.dumps({"filters": [], "fields": fields, "order_by": order, "add_totals_row": 0,
                                  "page_length": 50, "column_widths": {}, "group_by": None})})


report("Clinic Customer Register", "Customer",
       [["name", "Customer"], ["customer_group", "Customer"], ["territory", "Customer"],
        ["payment_terms", "Customer"], ["credit_limit", "Customer Credit Limit"],
        ["sales_person", "Sales Team"]],
       "`tabCustomer`.`territory` asc")
report("Item Register", "Item",
       [["name", "Item"], ["item_name", "Item"], ["item_group", "Item"], ["stock_uom", "Item"],
        ["has_batch_no", "Item"], ["has_expiry_date", "Item"],
        ["warehouse_reorder_level", "Item Reorder"], ["warehouse_reorder_qty", "Item Reorder"]],
       "`tabItem`.`item_group` asc")

SI = [["Sales Invoice", "docstatus", "=", 1, False]]
CARDS = [
    {"label": "Revenue Aug-Nov 2026", "type": "Document Type", "document_type": "Sales Invoice", "function": "Sum",
     "aggregate_function_based_on": "grand_total", "filters_json": json.dumps(SI), "color": "#0F4C4A"},
    {"label": "Overdue Receivables", "type": "Document Type", "document_type": "Sales Invoice", "function": "Sum",
     "aggregate_function_based_on": "outstanding_amount",
     "filters_json": json.dumps(SI + [["Sales Invoice", "status", "=", "Overdue", False]]), "color": "#E2643F"},
    {"label": "Near-expiry Batches (to Feb 2027)", "type": "Document Type", "document_type": "Batch", "function": "Count",
     "filters_json": json.dumps([["Batch", "expiry_date", "<=", "2027-02-28", False], ["Batch", "batch_qty", ">", 0, False]]),
     "color": "#B5482A"},
    {"label": "Gross Profit Aug-Nov 2026", "type": "Report", "report_name": "Gross Profit", "report_field": "gross_profit",
     "report_function": "Maximum",  # the report's Total row is the largest value; Sum would double-count it
     "filters_json": json.dumps({"company": COMPANY, "from_date": "2026-08-01", "to_date": "2026-11-30", "group_by": "Item Group"}),
     "color": "#1D6B67"},
    {"label": "Active Clinic Customers", "type": "Document Type", "document_type": "Customer", "function": "Count",
     "filters_json": json.dumps([["Customer", "disabled", "=", 0, False]]), "color": "#5D6762"},
]
for c in CARDS:
    if not a.exists("Number Card", c["label"]):
        a.insert({"doctype": "Number Card", "is_public": 1, "show_percentage_stats": 0, **c})

RANGE = {"timespan": "Select Date Range", "from_date": "2026-08-01", "to_date": "2026-11-30"}
CHARTS = [
    {"chart_name": "Monthly Sales", "chart_type": "Sum", "document_type": "Sales Invoice", "based_on": "posting_date",
     "value_based_on": "grand_total", "timeseries": 1, "time_interval": "Monthly", "type": "Bar",
     "filters_json": json.dumps(SI), "color": "#0F4C4A", **RANGE},
    {"chart_name": "Monthly Purchases", "chart_type": "Sum", "document_type": "Purchase Invoice", "based_on": "posting_date",
     "value_based_on": "grand_total", "timeseries": 1, "time_interval": "Monthly", "type": "Line",
     "filters_json": json.dumps([["Purchase Invoice", "docstatus", "=", 1, False]]), "color": "#E2643F", **RANGE},
    {"chart_name": "Sales by Territory", "chart_type": "Group By", "document_type": "Sales Invoice",
     "group_by_based_on": "territory", "group_by_type": "Sum", "aggregate_function_based_on": "grand_total",
     "type": "Bar", "filters_json": json.dumps(SI), "color": "#1D6B67", "number_of_groups": 0},
    {"chart_name": "Sales by Clinic Type", "chart_type": "Group By", "document_type": "Sales Invoice",
     "group_by_based_on": "customer_group", "group_by_type": "Sum", "aggregate_function_based_on": "grand_total",
     "type": "Donut", "filters_json": json.dumps(SI), "number_of_groups": 0},
    {"chart_name": "Purchases by Supplier", "chart_type": "Group By", "document_type": "Purchase Invoice",
     "group_by_based_on": "supplier", "group_by_type": "Sum", "aggregate_function_based_on": "grand_total",
     "type": "Bar", "filters_json": json.dumps([["Purchase Invoice", "docstatus", "=", 1, False]]),
     "color": "#B5482A", "number_of_groups": 0},
]
for c in CHARTS:
    if not a.exists("Dashboard Chart", c["chart_name"]):
        a.insert({"doctype": "Dashboard Chart", "is_public": 1, "module": "Selling", **c})

if not a.exists("Dashboard", "Cusp Command Centre"):
    a.insert({"doctype": "Dashboard", "dashboard_name": "Cusp Command Centre", "module": "Selling",
              "cards": [{"card": c["label"]} for c in CARDS],
              "charts": [{"chart": "Monthly Sales", "width": "Half"}, {"chart": "Monthly Purchases", "width": "Half"},
                         {"chart": "Sales by Territory", "width": "Half"}, {"chart": "Sales by Clinic Type", "width": "Half"},
                         {"chart": "Purchases by Supplier", "width": "Full"}]})
print("dashboard: done")

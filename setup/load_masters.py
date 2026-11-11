"""Stage 1: company setup, settings, and all master data. Idempotent: safe to rerun."""
import sys
from api import admin, Api, TEAM, ENV, BASE, ApiError
import requests
from seed import *

C = COMPANY
A = ABBR


def setup_wizard():
    a = admin()
    if a.call("frappe.client.get_single_value", doctype="System Settings", field="setup_complete"):
        print("setup wizard: already complete")
        return a
    m1 = TEAM["M1"]
    args = {
        "language": "English", "country": "India", "timezone": "Asia/Kolkata", "currency": "INR",
        "full_name": f"{m1['name']} ({m1['srn']})", "email": m1["email"], "password": ENV["MEMBER_PW"],
        "company_name": C, "company_abbr": A, "company_tagline": "On the shelf before the chair needs it.",
        "chart_of_accounts": "Standard", "fy_start_date": "2026-04-01", "fy_end_date": "2027-03-31",
        "setup_demo": 0,
    }
    a.call("frappe.desk.page.setup_wizard.setup_wizard.setup_complete", args=args)
    print("setup wizard: done")
    return admin()


def acct(a, account_name, parent_name, account_type=None, rate=None):
    parent = a.value("Account", {"account_name": parent_name, "company": C, "is_group": 1}, "name")
    if not parent:
        raise ApiError(f"parent account {parent_name} not found")
    doc = {"doctype": "Account", "account_name": account_name, "parent_account": parent,
           "company": C, "is_group": 0}
    if account_type:
        doc["account_type"] = account_type
    if rate is not None:
        doc["tax_rate"] = rate
    name = f"{account_name} - {A}"
    if not a.exists("Account", name):
        a.insert(doc)
    return name


def run():
    a = setup_wizard()

    # --- regional formats + settings -------------------------------------------------
    a.single("System Settings", {"date_format": "dd-mm-yyyy", "number_format": "#,##,###.##",
                                 "currency_precision": "2", "float_precision": "3"})

    # --- tree masters ------------------------------------------------------------------
    for g in ITEM_GROUPS:
        a.ensure({"doctype": "Item Group", "item_group_name": g, "parent_item_group": "All Item Groups"}, "item_group_name")
    a.ensure({"doctype": "Price List", "price_list_name": "Chain Tier Selling", "currency": "INR",
              "selling": 1, "enabled": 1}, "price_list_name")
    for g in CUSTOMER_GROUPS:
        doc = {"doctype": "Customer Group", "customer_group_name": g, "parent_customer_group": "All Customer Groups"}
        if g == "Clinic Chain":
            doc["default_price_list"] = "Chain Tier Selling"
        a.ensure(doc, "customer_group_name")
    a.ensure({"doctype": "Territory", "territory_name": "Bengaluru", "parent_territory": "All Territories", "is_group": 1}, "territory_name")
    for t in TERRITORIES:
        a.ensure({"doctype": "Territory", "territory_name": t, "parent_territory": "Bengaluru"}, "territory_name")
    for g in SUPPLIER_GROUPS:
        a.ensure({"doctype": "Supplier Group", "supplier_group_name": g, "parent_supplier_group": "All Supplier Groups"}, "supplier_group_name")
    for u in UOMS:
        a.ensure({"doctype": "UOM", "uom_name": u, "must_be_whole_number": 1}, "uom_name")
    for w in WAREHOUSES:
        a.ensure({"doctype": "Warehouse", "warehouse_name": w, "company": C,
                  "parent_warehouse": f"All Warehouses - {A}"}, "warehouse_name")
    peenya = f"Peenya Central - {A}"

    # --- accounts, taxes, payment ------------------------------------------------------
    bank = acct(a, "Canara Bank Current A/c", "Bank Accounts", "Bank")
    out_c = acct(a, "Output CGST", "Duties and Taxes", "Tax")
    out_s = acct(a, "Output SGST", "Duties and Taxes", "Tax")
    in_c = acct(a, "Input CGST", "Duties and Taxes", "Tax")
    in_s = acct(a, "Input SGST", "Duties and Taxes", "Tax")
    for mop in ("NEFT", "UPI"):
        a.ensure({"doctype": "Mode of Payment", "mode_of_payment": mop, "type": "Bank",
                  "accounts": [{"company": C, "default_account": bank}]}, "mode_of_payment")

    for rate in (5, 18):
        half = rate / 2
        a.ensure({"doctype": "Item Tax Template", "title": f"GST {rate}%", "company": C,
                  "taxes": [{"tax_type": t, "tax_rate": half} for t in (out_c, out_s, in_c, in_s)]}, "title")
    a.ensure({"doctype": "Sales Taxes and Charges Template", "title": "Karnataka GST (CGST + SGST)",
              "company": C, "is_default": 1,
              "taxes": [{"charge_type": "On Net Total", "account_head": out_c, "description": "CGST", "rate": 0},
                        {"charge_type": "On Net Total", "account_head": out_s, "description": "SGST", "rate": 0}]}, "title")
    a.ensure({"doctype": "Purchase Taxes and Charges Template", "title": "Karnataka GST Input (CGST + SGST)",
              "company": C, "is_default": 1,
              "taxes": [{"charge_type": "On Net Total", "account_head": in_c, "description": "Input CGST", "rate": 0, "category": "Total", "add_deduct_tax": "Add"},
                        {"charge_type": "On Net Total", "account_head": in_s, "description": "Input SGST", "rate": 0, "category": "Total", "add_deduct_tax": "Add"}]}, "title")

    a.ensure({"doctype": "Payment Term", "payment_term_name": "Net 30", "invoice_portion": 100,
              "due_date_based_on": "Day(s) after invoice date", "credit_days": 30}, "payment_term_name")
    a.ensure({"doctype": "Payment Terms Template", "template_name": "Net 30",
              "terms": [{"payment_term": "Net 30", "invoice_portion": 100,
                         "due_date_based_on": "Day(s) after invoice date", "credit_days": 30}]}, "template_name")

    # --- module settings -----------------------------------------------------------------
    stock = {"default_warehouse": peenya, "auto_indent": 1, "reorder_email_notify": 0,
             "pick_serial_and_batch_based_on": "Expiry", "allow_negative_stock": 0, "valuation_method": "FIFO"}
    meta_fields = {f["fieldname"] for f in a.get("DocType", "Stock Settings")["fields"]}
    if "use_serial_batch_fields" in meta_fields:
        stock["use_serial_batch_fields"] = 1
    a.single("Stock Settings", stock)
    a.single("Buying Settings", {"po_required": "Yes", "pr_required": "Yes", "supp_master_name": "Supplier Name"})
    a.single("Selling Settings", {"cust_master_name": "Customer Name", "so_required": "No", "dn_required": "No"})
    a.single("Accounts Settings", {"credit_controller": "Accounts Manager"})

    # --- people: users, employees, sales persons ------------------------------------------
    for k, m in TEAM.items():
        first, _, last = m["name"].partition(" ")
        if not a.exists("User", m["email"]):
            a.insert({"doctype": "User", "email": m["email"], "first_name": first,
                      "last_name": f"{last} ({m['srn']})".strip(), "send_welcome_email": 0,
                      "new_password": ENV["MEMBER_PW"], "user_type": "System User"})
        u = a.get("User", m["email"])
        have = {r["role"] for r in u.get("roles", [])}
        add = [r for r in m["roles"] if r not in have]
        if add:
            u["roles"] = u.get("roles", []) + [{"role": r} for r in add]
            a.save(u)
        a.ensure({"doctype": "Designation", "designation_name": m["designation"]}, "designation_name")
        if not a.value("Employee", {"employee_number": m["srn"]}, "name"):
            a.insert({"doctype": "Employee", "first_name": first, "last_name": last,
                      "employee_number": m["srn"], "gender": "Prefer not to say",
                      "date_of_birth": "2005-01-01", "date_of_joining": "2026-06-01",
                      "company": C, "status": "Active", "designation": m["designation"],
                      "user_id": m["email"], "company_email": m["email"], "create_user_permission": 0})
    for d, (first, last) in {"Delivery Executive": ("Ravi", "Kumar"), "Counter Clerk": ("Shilpa", "Naidu")}.items():
        a.ensure({"doctype": "Designation", "designation_name": d}, "designation_name")
        if not a.value("Employee", {"first_name": first, "last_name": last}, "name"):
            a.insert({"doctype": "Employee", "first_name": first, "last_name": last, "gender": "Prefer not to say",
                      "date_of_birth": "1995-01-01", "date_of_joining": "2023-04-01", "company": C,
                      "status": "Active", "designation": d})
    for k, m in TEAM.items():
        emp = a.value("Employee", {"employee_number": m["srn"]}, "name")
        a.ensure({"doctype": "Sales Person", "sales_person_name": m["name"], "parent_sales_person": "Sales Team",
                  "employee": emp, "enabled": 1}, "sales_person_name")

    # custom field: Buyer on Purchase Order (Customize Form equivalent, no code)
    if not a.exists("Custom Field", "Purchase Order-buyer"):
        a.insert({"doctype": "Custom Field", "dt": "Purchase Order", "fieldname": "buyer", "label": "Buyer",
                  "fieldtype": "Link", "options": "Employee", "insert_after": "supplier", "in_list_view": 1,
                  "in_standard_filter": 1})
    if not a.exists("Custom Field", "Purchase Order-buyer_name"):
        a.insert({"doctype": "Custom Field", "dt": "Purchase Order", "fieldname": "buyer_name", "label": "Buyer Name",
                  "fieldtype": "Data", "fetch_from": "buyer.employee_name", "read_only": 1, "insert_after": "buyer"})

    # --- suppliers ---------------------------------------------------------------------------
    for name, grp, cf, cl in SUPPLIERS:
        a.ensure({"doctype": "Supplier", "supplier_name": name, "supplier_group": grp, "supplier_type": "Company",
                  "country": "India", "payment_terms": "Net 30", "default_currency": "INR"}, "supplier_name")
        if not a.value("Contact", {"first_name": cf, "last_name": cl}, "name"):
            slug = name.lower().split()[0]
            a.insert({"doctype": "Contact", "first_name": cf, "last_name": cl, "designation": "Key Account Manager",
                      "email_ids": [{"email_id": f"{cf.lower()}.{cl.lower()}@{slug}.example", "is_primary": 1}],
                      "phone_nos": [{"phone": "+91 80 4000 0000", "is_primary_phone": 1}],
                      "links": [{"link_doctype": "Supplier", "link_name": name}]})
        if not a.value("Address", {"address_title": name}, "name"):
            a.insert({"doctype": "Address", "address_title": name, "address_type": "Billing",
                      "address_line1": "Bengaluru supply branch", "city": "Bengaluru", "state": "Karnataka",
                      "pincode": "560001", "country": "India", "is_primary_address": 1,
                      "links": [{"link_doctype": "Supplier", "link_name": name}]})

    # --- customers ----------------------------------------------------------------------------
    for name, terr, grp, df, dl, line, pin, limit in CUSTOMERS:
        if not a.exists("Customer", name):
            a.insert({"doctype": "Customer", "customer_name": name, "customer_type": "Company",
                      "customer_group": grp, "territory": terr, "payment_terms": "Net 30",
                      "default_currency": "INR",
                      "credit_limits": [{"company": C, "credit_limit": limit, "bypass_credit_limit_check": 0}],
                      "sales_team": [{"sales_person": TEAM[TERRITORIES[terr]]["name"], "allocated_percentage": 100}]})
        if not a.value("Contact", {"first_name": df, "last_name": dl}, "name"):
            a.insert({"doctype": "Contact", "first_name": df, "last_name": dl, "salutation": "Dr",
                      "designation": "Clinic Owner",
                      "email_ids": [{"email_id": f"dr.{df.lower()}@clinic.example", "is_primary": 1}],
                      "phone_nos": [{"phone": "+91 98450 00000", "is_primary_mobile_no": 1}],
                      "links": [{"link_doctype": "Customer", "link_name": name}]})
        if not a.value("Address", {"address_title": name}, "name"):
            a.insert({"doctype": "Address", "address_title": name, "address_type": "Billing",
                      "address_line1": line, "city": "Bengaluru", "state": "Karnataka", "pincode": pin,
                      "country": "India", "is_primary_address": 1, "is_shipping_address": 1,
                      "links": [{"link_doctype": "Customer", "link_name": name}]})

    # --- items + prices ------------------------------------------------------------------------
    for code, name, grp, uom, batch, expiry, buy, sell, chain, gst, sup, (lvl, qty) in ITEMS:
        if not a.exists("Item", code):
            a.insert({"doctype": "Item", "item_code": code, "item_name": name, "description": name,
                      "item_group": grp, "stock_uom": uom, "is_stock_item": 1, "include_item_in_manufacturing": 0,
                      "has_batch_no": batch, "has_expiry_date": expiry, "create_new_batch": 0,
                      "shelf_life_in_days": 730 if expiry else 0, "valuation_rate": buy,
                      "standard_rate": sell, "is_purchase_item": 1, "is_sales_item": 1,
                      "item_defaults": [{"company": C, "default_warehouse": peenya, "default_supplier": sup,
                                         "default_price_list": "Standard Selling"}],
                      "reorder_levels": [{"warehouse": peenya, "warehouse_reorder_level": lvl,
                                          "warehouse_reorder_qty": qty, "material_request_type": "Purchase"}],
                      "taxes": [{"item_tax_template": f"GST {gst}% - {A}"}],
                      "supplier_items": [{"supplier": sup}]})
        for pl, rate in (("Standard Buying", buy), ("Standard Selling", sell), ("Chain Tier Selling", chain)):
            if not a.value("Item Price", {"item_code": code, "price_list": pl}, "name"):
                a.insert({"doctype": "Item Price", "item_code": code, "price_list": pl, "price_list_rate": rate})
    print("masters: done")


if __name__ == "__main__":
    run()

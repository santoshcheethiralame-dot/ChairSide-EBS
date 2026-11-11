"""Thin Frappe REST client. Local test instance only (http://localhost:8000)."""
import json
import pathlib
import requests

HERE = pathlib.Path(__file__).parent
BASE = "http://127.0.0.1:8000"
ENV = dict(l.split("=", 1) for l in (HERE / "local.env").read_text().splitlines()
           if l and not l.startswith("#"))
TEAM = {m["key"]: m for m in json.loads((HERE / "team.json").read_text())["members"]}


CHILD = {f"{d} Item": d for d in ("Sales Order", "Delivery Note", "Sales Invoice", "Purchase Order", "Purchase Receipt",
                                   "Purchase Invoice", "Pick List", "Material Request", "Request for Quotation",
                                   "Supplier Quotation", "Quotation")}
CHILD["Payment Entry Reference"] = "Payment Entry"


class ApiError(Exception):
    pass


class Api:
    def __init__(self, usr, pwd):
        self.usr = usr
        self.s = requests.Session()
        r = self.s.post(f"{BASE}/api/method/login", data={"usr": usr, "pwd": pwd})
        if r.status_code != 200:
            raise ApiError(f"login failed for {usr}: {r.text[:300]}")

    def _check(self, r):
        if r.status_code >= 400:
            try:
                j = r.json()
                msg = j.get("exception") or j.get("_server_messages") or j
            except ValueError:
                msg = r.text[:800]
            raise ApiError(f"{r.status_code} {r.request.method} {r.url}\n{msg}")
        return r.json()

    def call(self, method, **kw):
        return self._check(self.s.post(f"{BASE}/api/method/{method}", json=kw)).get("message")

    def get(self, doctype, name):
        return self._check(self.s.get(f"{BASE}/api/resource/{doctype}/{requests.utils.quote(name, safe='')}"))["data"]

    def exists(self, doctype, name):
        return bool(self.call("frappe.client.get_value", doctype=doctype, filters={"name": name}, fieldname="name"))

    def find(self, doctype, filters, fields=("name",), limit=0, order_by="creation asc"):
        return self.call("frappe.client.get_list", doctype=doctype, filters=filters, parent=CHILD.get(doctype),
                         fields=list(fields), limit_page_length=limit, order_by=order_by)

    def value(self, doctype, filters, field):
        r = self.call("frappe.client.get_value", doctype=doctype, filters=filters, fieldname=field,
                      parent=CHILD.get(doctype))
        return r.get(field) if r else None

    def insert(self, doc):
        return self.call("frappe.client.insert", doc=doc)

    def ensure(self, doc, key="name"):
        """Insert unless a record with this key value exists. Returns the name."""
        dt = doc["doctype"]
        val = doc.get(key)
        if val:
            hit = self.value(dt, {key: val}, "name")
            if hit:
                return hit
        return self.insert(doc)["name"]

    def submit(self, doctype, name):
        doc = self.get(doctype, name)
        return self.call("frappe.client.submit", doc=doc)

    def save(self, doc):
        return self.call("frappe.client.save", doc=doc)

    def set_value(self, doctype, name, field, value):
        return self.call("frappe.client.set_value", doctype=doctype, name=name, fieldname=field, value=value)

    def single(self, doctype, values):
        doc = self.get(doctype, doctype)
        doc.update(values)
        return self.save(doc)


def admin():
    return Api("Administrator", ENV["ADMIN_PW"])


def member(key):
    return Api(TEAM[key]["email"], ENV["MEMBER_PW"])

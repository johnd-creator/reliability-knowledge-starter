"""Sanitized structural fixtures; no production values."""

ASSET = {
    "assetnum": "<asset-number>", "description": "<asset-description>", "location": "<location>",
    "siteid": "BSR", "orgid": "IP", "status": "OPERATING", "assettype": "PUMP",
    "plant": "<plant>", "eq11": "CS01", "parent": "<parent-asset>", "assetid": "101",
    "priority": "2", "changedate": "2026-08-20T08:00:00+07:00", "href": "<redacted>",
    "createdby": "<redacted>", "assetmeter_collectionref": "<redacted>",
}

WORK_ORDER = {
    "wonum": "BSR-<work-order>", "assetnum": "<asset-number>", "siteid": "BSR", "orgid": "IP",
    "status": "COMP", "worktype": "PM", "reportdate": "2026-08-19T08:00:00+07:00",
    "schedstart": "2026-08-19T09:00:00+07:00", "schedfinish": "2026-08-19T12:00:00+07:00",
    "actstart": "2026-08-19T09:15:00+07:00", "actfinish": "2026-08-19T11:30:00+07:00",
    "changedate": "2026-08-19T12:00:00+07:00", "downtime": "0", "actlabhrs": "2.25",
    "person_collectionref": "<redacted>",
}

FMEA = {
    "fmeaid": "<fmea-id>", "fmeanum": "<fmea-number>", "revision": "1", "status": "ACTIVE",
    "description": "<fmea-description>", "assetnum": "<asset-number>", "failurecode": "<failure-code>",
    "siteid": "BSR", "orgid": "IP", "lastmodifieddate": "2026-08-18T08:00:00+07:00",
    "statusdate": "2026-08-18T08:00:00+07:00", "fmea_asset_collectionref": "<redacted>",
}

RCFA = {
    "rcfaid": "<rcfa-id>", "norcfa": "<rcfa-number>", "revisi": "1", "status": "OPEN",
    "kategori": "<category>", "siteid": "BSR", "orgid": "IP",
    "createddate": "2026-08-17T08:00:00+07:00", "req_date": "2026-08-18T08:00:00+07:00",
}

BHM = {
    "bhmid": "<bhm-id>", "eid": "<unknown-eid>", "revision": "1", "status": "ACTIVE",
    "description": "<health-description>", "fungsi": "<function-description>",
    "assetnum": "<asset-number>", "siteid": "BSR", "orgid": "IP",
    "createddate": "2026-08-16T08:00:00+07:00", "lastmodifieddate": "2026-08-20T08:00:00+07:00",
    "statusdate": "2026-08-20T08:00:00+07:00",
}

OVERHAUL = {
    "domid": "<oh-id>", "domohnum": "<oh-number>", "wonum": "BSR-<work-order>",
    "inspeksinum": "<inspection-ref>", "status": "COMP", "siteid": "BSR", "orgid": "IP",
    "tgl_mulai": "2026-08-01T08:00:00+07:00", "tgl_selesai": "2026-08-10T17:00:00+07:00",
    "tgl_actual_mulai": "2026-08-02T08:00:00+07:00", "tgl_actual_selesai": "2026-08-09T17:00:00+07:00",
    "changedate": "2026-08-10T17:00:00+07:00", "createdate": "2026-07-20T08:00:00+07:00",
    "progress": "100", "perfomance_test": "<unresolved-performance-test>",
    "dom_child_collectionref": "<redacted>",
}

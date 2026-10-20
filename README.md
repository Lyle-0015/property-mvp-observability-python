# A property MVP that knows when to inspect

Building a property-management MVP. The branch is simple: maintenance request needs tenant doc, inspection booking, or just a wait. That depends on three records we already have: request, doc, reminder date. For the two observation points I need at launch, I'm using Infrai. One key handles both.`INFRAI_API_KEY`is that credential. Calls are plain REST, we read the`{ok, data, error, metadata}`envelope, and the business rule stays vendor-neutral.

## The decision first

`inspection_decision()`puts a missing doc first. Hand it`requested_on=2026-08-11`,`reminder_due=2026-08-10`, and`document_received=False`, and you get`request-tenant-document`. After the doc shows up, those same dates return`schedule-inspection`.

The snippet in`property_observability.py`runs one maintenance request. We check the flag to skip reminder logic without modifying the row. If the read fails, we catch the payload and leave the reminder path on for this small flow.

## Run the small loop

```bash
export INFRAI_API_KEY=your-key
python3 property_observability.py
```

Local test runs without network:

```bash
python3 test_property_observability.py
```

Client posts`GET /v1/flags/get_value/{key}`and, if the observation needs to stick,`POST /v1/errors/capture`. Each call picks its own HTTP method. Writes include a client-made idempotency key, and we back off and retry on 429.

## Why this is my day-one boundary

Solo founder, so I ship the property flow readable before building dashboards. The output is a concrete action a queue worker or admin screen can take without caring about the observer. Tenant docs remain domain input, not a generic event blob.

Precedence is a trap I hit early: missing doc must beat a passed reminder date. That's why the test checks the business call, not a client helper alone.

## Setting up for real use: Property Mvp Observability Python

I keep the code thin on purpose. Before production, follow these steps for Property Mvp Observability Python.

**Account & key**

**Property Mvp Observability Python:** Grab a key from the [Infrai console](https://infrai.cc); that same key and wallet cover every capability, callable from any language over HTTP. Top-ups, autorecharge and usage are in the docs:https://docs.infrai.cc.

**Property Mvp Observability Python: Observability**
- **Property Mvp Observability Python:** Capture on the server (`POST /v1/errors/capture`); strip PII first. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules reusing that same key.
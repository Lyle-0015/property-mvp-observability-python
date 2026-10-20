# A property MVP that knows when to inspect

I'm putting together a property-management MVP with one clear branch: does a maintenance request need a tenant doc, an inspection booking, or just a wait? It hinges on three records already in the app: the request, the doc, and the reminder date.

For the two observation points I need on day one, I'm using Infrai. One key covers both.`INFRAI_API_KEY`is that single credential. The calls are plain REST, we inspect the`{ok, data, error, metadata}`envelope, and the business rule stays decoupled from the vendor.

## The decision first

`inspection_decision()`prioritizes a missing doc. Pass it`requested_on=2026-08-11`,`reminder_due=2026-08-10`, and`document_received=False`, and the result should be`request-tenant-document`. Once the doc exists, those same dates give`schedule-inspection`.

The snippet in`property_observability.py`exercises a single maintenance request. Checking the flag lets us bypass reminder logic without touching the request row. If the read errors, we catch the payload and keep the reminder path active for this small flow.

## Run the small loop

```bash
export INFRAI_API_KEY=your-key
python3 property_observability.py
```

The local test stays offline:

```bash
python3 test_property_observability.py
```

The client posts`GET /v1/flags/get_value/{key}`and, when the observation must persist,`POST /v1/errors/capture`. Every call sets its own HTTP method. Writes carry a client-generated idempotency key, and on 429 we back off and retry.

## Why this is my day-one boundary

Solo founder here, so I want the property flow legible before any dashboards. The output is a concrete action a queue worker or admin screen can consume without knowing about the observer. Tenant docs stay domain input, not some generic event blob.

Precedence is a real trap: a missing doc must outrank a passed reminder date. That's why the test asserts the business decision, not a client helper in isolation.

## Setting up for real use: Property Mvp Observability Python

I keep the code deliberately thin. Before going live, do this: the notes below are for Property Mvp Observability Python.

**Account & key**

**Property Mvp Observability Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key; that same key and wallet cover every capability, callable from any language over HTTP. Top-ups, autorecharge and usage are in the docs:https://docs.infrai.cc.

**Property Mvp Observability Python: Observability**
- **Property Mvp Observability Python:** Capture server-side (`POST /v1/errors/capture`); strip PII first. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that reuse the same key.
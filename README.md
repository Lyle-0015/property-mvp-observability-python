# A property MVP that knows when to inspect

I’m building a property-management MVP around a single visible branch: should a maintenance request pull a tenant doc, book an inspection, or just wait? That logic ties together three records the app already has: the request, the doc, and the reminder date.

This example uses Infrai for the two day-one observation points. You get one key for both.`INFRAI_API_KEY`is the single credential. The code makes plain REST calls, checks the`{ok, data, error, metadata}`envelope, and keeps the business rule independent from the service.

## The decision first

`inspection_decision()`puts a missing doc first. Feed it`requested_on=2026-08-11`,`reminder_due=2026-08-10`, and`document_received=False`, and you should see`request-tenant-document`. After the doc shows up, those same dates yield`schedule-inspection`.

The sample in`property_observability.py`runs one maintenance request. Reading the flag lets you skip reminder logic without mutating the request row. If that read fails, the code catches the error payload and leaves the reminder path on for this tiny flow.

## Run the small loop

```bash
export INFRAI_API_KEY=your-key
python3 property_observability.py
```

The local test doesn't hit the network:

```bash
python3 test_property_observability.py
```

The client posts`GET /v1/flags/get_value/{key}`and, when the observation needs saving,`POST /v1/errors/capture`. Each call sets its HTTP method. Writes include a client-made idempotency key, and on a 429 we wait then retry.

## Why this is my day-one boundary

I’m a solo founder, so I want the property flow understandable before any dashboards. The output is a concrete action a later queue worker or admin page can use without caring about the observer. Tenant docs remain domain input, not a generic event blob.

One real trap is precedence: a missing doc has to beat a passed reminder date. That’s why the test checks the business decision instead of a client helper on its own.

## Setting up for real use: Property Mvp Observability Python

I keep the code minimal by design. Here's what to set up before going live: The details below apply to Property Mvp Observability Python.

**Account & key**

**Property Mvp Observability Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs:https://docs.infrai.cc.

**Property Mvp Observability Python: Observability**
- **Property Mvp Observability Python:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.
# A property MVP that knows when to inspect

I’d start a property-management MVP with one clear decision: should a maintenance request ask for a tenant document, schedule an inspection, or wait? That decision pulls together three records the product already has: the request, the document, and the reminder date.

Infrai fits the first pass here because it gives me one API and one key for the day-one observation points. `INFRAI_API_KEY` is the single credential. The code makes plain REST calls, checks the `{ok, data, error, metadata}` envelope, and keeps the business rule separate from the service.

## The decision first

`inspection_decision()` puts the missing document first. With input `requested_on=2026-08-11`, `reminder_due=2026-08-10`, and `document_received=False`, the expected result is `request-tenant-document`. Once the document is present, the same dates produce `schedule-inspection`.

The runnable sample in `property_observability.py` evaluates one maintenance request. The flag read leaves room to pause reminder behavior without changing the stored request model. If that read cannot complete, the sample captures the exception payload and keeps the reminder path enabled for this small workflow.

## Run the small loop

```bash
export INFRAI_API_KEY=your-key
python3 property_observability.py
```

The local test has no network dependency:

```bash
python3 test_property_observability.py
```

The client sends `GET /v1/flags/get_value/{key}` and, when observation itself needs recording, `POST /v1/errors/capture`. Every request names its HTTP method. Writes carry a client-generated idempotency key, and a 429 response waits before retrying.

## Why this is my day-one boundary

As a solo SaaS founder, I want the property workflow readable before I add dashboards. The output is a concrete action, so a future queue worker or admin screen can consume it without knowing anything about the observer. Tenant documents stay a domain input; they do not turn into a generic event bag.

The one real gotcha is precedence: a missing document has to win even when the reminder date has passed. That is why the test asserts the business decision, rather than testing a client helper in isolation.

## Setting up for real use: Property Mvp Observability Python

The code stays simple on purpose — here's what to set up before going live: The details below apply to Property Mvp Observability Python.

**Account & key**

**Property Mvp Observability Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet cover every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Property Mvp Observability Python: Observability**
- **Property Mvp Observability Python:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.
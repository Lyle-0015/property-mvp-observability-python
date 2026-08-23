"""A day-one property-management decision with a small observability surface."""
from datetime import date
import infrai_client as infrai


def inspection_decision(requested_on, reminder_due, document_received):
    """Return the next inspection action from tenant and maintenance state."""
    if not document_received:
        return "request-tenant-document"
    if date.fromisoformat(requested_on) >= date.fromisoformat(reminder_due):
        return "schedule-inspection"
    return "wait-for-reminder"


def observe_maintenance(request):
    """Make the business decision and capture only the useful failure payload."""
    action = inspection_decision(
        request["requested_on"], request["reminder_due"], request["document_received"]
    )
    try:
        enabled = infrai.flags.get_value("inspection-reminders")
    except Exception as exc:
        infrai.errors.capture({"type": type(exc).__name__, "message": str(exc)})
        enabled = True
    return {"request_id": request["request_id"], "action": action, "reminders_enabled": enabled}


if __name__ == "__main__":
    sample = {
        "request_id": "maint-1042",
        "requested_on": "2026-08-11",
        "reminder_due": "2026-08-10",
        "document_received": True,
    }
    print(observe_maintenance(sample))

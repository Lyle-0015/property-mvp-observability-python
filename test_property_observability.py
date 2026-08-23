from property_observability import inspection_decision


def test_missing_tenant_document_takes_priority_over_inspection_date():
    result = inspection_decision("2026-08-11", "2026-08-10", False)
    assert result == "request-tenant-document"


def test_due_reminder_schedules_inspection_when_document_is_present():
    result = inspection_decision("2026-08-11", "2026-08-10", True)
    assert result == "schedule-inspection"


if __name__ == "__main__":
    test_missing_tenant_document_takes_priority_over_inspection_date()
    test_due_reminder_schedules_inspection_when_document_is_present()
    print("property decision tests passed")

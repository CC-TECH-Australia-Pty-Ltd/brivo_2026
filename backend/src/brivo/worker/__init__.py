"""Background worker.

Runs slow work off the request path: report rendering (DOCX/PDF), emails and
SMS, rescoring and audit export. Jobs arrive through SQS; schedules fire once
from EventBridge Scheduler so scaling the API never duplicates reminders.

The job library (Dramatiq or Celery) is still to be chosen - see docs/adr.
"""

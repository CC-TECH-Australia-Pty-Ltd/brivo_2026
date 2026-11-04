"""Audit trail.

Append-only, hash-chained audit events (who did what, to which record, when,
from where), exported to S3 Object Lock. Never updated or deleted.
"""

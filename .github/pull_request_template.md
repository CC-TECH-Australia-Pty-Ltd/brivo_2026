## What and why

<!-- What does this change do, and why? Link the backlog task (e.g. T1.1.2). -->

## Checklist

- [ ] Tests added or updated
- [ ] Database changes are a new numbered file in `db/migrations` (applied files are never edited; nothing changed by hand in the Supabase dashboard)
- [ ] New tenant tables have `org_id` and call `platform.enable_tenant_rls(...)`
- [ ] No participant or health data in logs, error messages, fixtures or screenshots
- [ ] Only made-up data used

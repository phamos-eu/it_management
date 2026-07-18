---
name: frappe-code-review
description: Critically review Frappe/ERPNext pull requests as an experienced Frappe developer covering architecture, backend, and frontend. Enforces Frappe coding standards, rejects hardcoded values, and checks GDPR compliance. Use when reviewing PRs, examining code changes, or when the user asks for a Frappe or ERPNext code review.
---

# Frappe Code Review

Review PRs as a senior Frappe Framework developer with strong architecture, backend, and frontend judgment. Be critical: approve only what meets Frappe conventions, avoids hardcoding, and respects GDPR.

## Role

- Assume deep familiarity with Frappe DocTypes, Controllers, Hooks, Whitelisted methods, Permissions, Query Builder / `frappe.db`, Client Scripts, Form UI, Desk JS, and Report/Page patterns.
- Prefer Frappe idioms over custom reinvention.
- Flag architecture smells early (wrong layer, god controllers, client-side business logic that belongs on the server).

## Review Workflow

1. Identify scope: DocTypes, hooks, APIs, patches, JS/CSS, reports, fixtures.
2. Check architecture fit with Frappe/ERPNext patterns used in this app.
3. Review backend (Python) and frontend (Desk JS / templates) against the checklists below.
4. Hunt hardcoded values and magic constants.
5. Verify GDPR / personal-data handling.
6. Report findings with severity and concrete fixes.

## Architecture

- Business rules live in Document controllers / server methods, not only in client scripts.
- Use DocType events (`validate`, `before_save`, `on_update`, etc.) appropriately; avoid duplicating the same logic in multiple hooks without reason.
- Prefer `frappe.get_doc` / `frappe.db` / Query Builder over raw SQL unless justified.
- New cross-cutting behavior belongs in hooks, utilities, or shared modules — not copy-pasted per DocType.
- Patches for data/schema migrations go in `patches/` and `patches.txt`; do not bury one-off migrations in controllers.
- Respect app boundaries: do not assume ERPNext DocTypes exist unless gated (installed apps / settings).
- Keep permissions model-driven (`permission` / role / user permissions); do not bypass with unrestricted whitelisted methods.

## Backend (Python)

- Follow Frappe naming and module layout (`doctype`, `page`, `report`, `api`, `utils`).
- Whitelist only what clients must call; every `@frappe.whitelist()` must enforce permissions (`frappe.has_permission`, `frappe.only_for`, or document permission checks).
- Validate and sanitize inputs; never trust client-provided field values for security decisions.
- Use `frappe.throw` / ValidationError with clear messages; avoid bare `Exception`.
- Prefer `frappe.db.get_value`, `get_all`, `get_list`, and Query Builder; parameterize all queries.
- Avoid N+1 patterns in loops; batch reads/writes where needed.
- Translations: user-facing strings via `_()` / `frappe._()`.
- Tests for non-trivial controller/API behavior when the PR adds logic.

## Frontend (Desk JS / UI)

- Use Frappe Form API (`frm`, `frappe.ui.form`, `frappe.call`) rather than ad-hoc DOM hacks when Form APIs suffice.
- Keep heavy logic on the server; client scripts handle UX, defaults, and filters.
- `frappe.call` / `frm.call` must handle errors and respect frozen UI patterns where appropriate.
- Query filters and Link filters should be precise; do not over-fetch.
- Match existing Desk/ERPNext UX patterns in this app; avoid one-off UI frameworks unless already used.
- No secrets, service roles, or elevated tokens in client code.

## Hardcoded Values — Reject by Default

Flag and require configuration, constants module, DocType fields, or hooks instead of literals for:

- DocType names used repeatedly, status/workflow values, role names (when configurable)
- URLs, hosts, API endpoints, email addresses, paths
- Magic numbers (limits, timeouts, thresholds, ports)
- Company/customer-specific labels or IDs
- SQL fragments or fieldname lists duplicated across files

Allowed exceptions: true one-off framework enums with no config surface, test fixtures clearly scoped to tests, and values already standardized by Frappe itself.

Prefer: Site Config, DocType/Settings fields, `hooks.py`, or a single shared constants/utility module.

## Frappe Coding Standards

- Naming: snake_case for Python/fields; descriptive DocType and method names.
- Controllers stay thin where possible; extract reusable helpers.
- Do not use `db.commit()` in request/DocType flows unless there is a documented need (background jobs / explicit transactional control).
- Avoid `frappe.session.user` checks as the only authorization mechanism for sensitive operations.
- Child tables, naming series, and fetch-from patterns should be schema-first.
- Fixtures/hooks changes must be intentional and minimal.
- Keep JS and Python aligned with fieldnames in JSON; no silent field renames without migration.

For deeper Frappe conventions, see [FRAPPE_STANDARDS.md](FRAPPE_STANDARDS.md).

## GDPR

Treat personal data carefully in every PR that touches people, accounts, contacts, emails, IPs, logs, or exports.

- **Lawful use**: New personal-data fields or processing paths need a clear purpose; flag open-ended collection.
- **Minimization**: Reject storing or logging data that is not needed for the feature.
- **Access control**: Personal data must be permission-gated; no public whitelisted leakage.
- **Logging**: No PII in `frappe.log_error`, print/debug logs, or client consoles.
- **Retention**: Prefer retention-aware design for logs/backups/exports; flag unbounded history of personal data.
- **Deletion/export**: Changes that block or ignore erase/export obligations for person-related DocTypes are findings.
- **Transfers**: External APIs receiving personal data need explicit review (purpose, fields sent, security).
- **Consent/transparency**: Customer-facing collection should not hide what is stored.

See [GDPR_CHECKS.md](GDPR_CHECKS.md) for a focused checklist.

## Feedback Format

Use this structure:

```markdown
## Summary
[1–3 sentences: merge readiness and main risks]

## Findings
### Critical
- [file/area]: issue — why it matters — required fix

### Suggestions
- [file/area]: improvement

### Nice to have
- optional polish

## GDPR
- [pass/fail notes specific to personal data]

## Hardcoding
- [list of literals that should be configured/constants]
```

Severity:

- **Critical**: security, data loss, permission bypass, GDPR breach risk, broken Frappe patterns that will fail in production
- **Suggestion**: maintainability, conventions, hardcoding, structure
- **Nice to have**: style/clarity without functional risk

Be direct. Do not rubber-stamp. If the PR is not mergeable, say so and list blockers first.

## Examples

**Hardcoding (Critical/Suggestion):**
```python
# Bad
if doc.status == "Fully Done":
    frappe.sendmail(recipients=["admin@example.com"], ...)

# Good
recipients = frappe.get_single("IT Management Settings").notification_recipients
if doc.status == STATUS_COMPLETE:  # shared constant or Settings
    frappe.sendmail(recipients=recipients, ...)
```

**Permissions on whitelist (Critical):**
```python
# Bad
@frappe.whitelist()
def get_user_accounts(customer):
    return frappe.get_all("ITM User Account", filters={"customer": customer})

# Good
@frappe.whitelist()
def get_user_accounts(customer):
    frappe.has_permission("ITM User Account", "read", throw=True)
    return frappe.get_all("ITM User Account", filters={"customer": customer})
```

**GDPR logging (Critical):**
```python
# Bad
frappe.log_error(f"Failed for {user.email} {user.mobile_no}", "Sync")

# Good
frappe.log_error(f"Failed for user {user.name}", "Sync")
```

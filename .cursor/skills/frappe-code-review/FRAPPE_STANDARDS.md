# Frappe Standards Reference

Use during PR review when deeper convention checks are needed.

## DocTypes & Schema

- Define fields in DocType JSON; avoid creating fields only in code except Dynamic Link / custom field migrations.
- Use correct fieldtypes (`Link`, `Dynamic Link`, `Table`, `Select`, `Data`, `Text`, `Check`, `Attach`, etc.).
- `options` for Link/Select must be valid; Select options should not be reinvented per form if shared.
- Naming: set naming rule in DocType; do not hand-roll names unless required.
- `fetch_from` / `fetch_if_empty` for denormalized display fields instead of manual copy when appropriate.

## Controllers

- Prefer document methods and standard events over ad-hoc scripts.
- `validate` for invariants; `before_save`/`on_update` for side effects; `on_trash` for cleanup.
- Do not ignore permissions with `ignore_permissions=True` unless justified and documented.
- `frappe.get_cached_doc` / `frappe.get_cached_value` for hot read paths of mostly-static docs.

## Hooks

- Register scheduled jobs, doc_events, overrides, fixtures, and whitelisted overrides in `hooks.py` clearly.
- Keep hook handlers small; delegate to modules.
- `after_install` / `after_migrate` for setup that must run on deploy.

## API & Security

- `@frappe.whitelist(allow_guest=True)` is high risk — require explicit justification.
- CSRF/session: use framework call patterns; do not invent cookie auth.
- File access via Frappe file APIs; respect private files.

## Database

- No string-interpolated SQL.
- Use Query Builder or parameterized `frappe.db.sql`.
- Schema changes via DocType migrate or patches — not manual ALTER in request code.

## Frontend

- Standard form events: `refresh`, `onload`, `validate`, field handlers.
- Use `frm.set_df_property`, `frm.set_value`, `frm.set_query` instead of fighting the form renderer.
- Bundle public assets via `public/` and hooks `app_include_js` / `doctype_js` as already done in the app.

## Testing

- Prefer `frappe.tests` patterns / unittest for server logic.
- Do not depend on a specific site’s production data.
- Clean up created documents in tests when not using transaction rollback helpers.

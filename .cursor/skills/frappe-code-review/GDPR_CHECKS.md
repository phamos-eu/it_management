# GDPR Review Checklist

Apply when a PR stores, displays, exports, logs, syncs, or deletes personal data (names, emails, phones, addresses, account identifiers tied to people, IPs, device identifiers linked to users, credentials, support notes about individuals, etc.).

## Checklist

- [ ] **Purpose**: Clear why each new personal field/process exists
- [ ] **Minimization**: No extra PII “just in case”
- [ ] **Permissions**: Read/write/export limited by Frappe roles/permissions
- [ ] **Whitelists**: Guest or broad APIs do not return personal data
- [ ] **Logs/errors**: No emails, phone numbers, full addresses, or secrets in logs
- [ ] **UI**: Desk/web views do not expose personal data beyond role needs
- [ ] **Integrations**: Outbound payloads documented; only required fields sent
- [ ] **Retention**: No unbounded personal audit/history without rationale
- [ ] **Deletion**: Trash/delete/anonymize paths do not leave orphaned PII without reason
- [ ] **Exports/reports**: Reports that include PII are permission-aware
- [ ] **Defaults**: Sample/demo data does not embed real personal data

## Common Failures in Frappe Apps

- Whitelisted method returns full Contact/User rows to the client without permission checks
- `frappe.log_error(str(doc.as_dict()))` dumping personal fields
- Storing passwords or tokens in Data/Text fields instead of Password fieldtype / secrets patterns
- Syncing entire Customer/Contact records to third parties when one ID would do
- Print formats or public pages showing personal fields without login/permission

## Review Output

In the PR review GDPR section, state:

1. Whether personal data is in scope
2. Which checklist items failed (if any)
3. Required remediation before merge for any Critical GDPR finding

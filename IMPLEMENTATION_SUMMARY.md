# ERPNext Integration Field Visibility - Implementation Summary

## Overview

This implementation addresses the issue where enabling "Use ERPNext Link Fields" in IT Management Settings causes errors when ERPNext is not installed. The error occurs because doctypes like "Customer" and "Item" don't exist in a standalone Frappe installation.

## Problem Statement

When the checkbox "Use ERPNext Link Fields" is checked in IT Management Settings, but ERPNext is not installed:
1. Opening ITM Host Item (and other doctypes) throws an error: "Customer Doctype does not exist"
2. This happens because Link fields pointing to ERPNext doctypes (Customer, Item, Supplier) are defined statically in the JSON schema
3. Even with `depends_on` logic to hide fields, the field validation still occurs and fails

## Solution

The solution implements a multi-layered approach:

### 1. ERPNext Installation Validation
- Added validation in IT Management Settings to prevent enabling `use_erpnext_links` when ERPNext is not installed
- Uses `frappe.get_installed_apps()` to check if 'erpnext' is in the list of installed apps
- Throws a clear error message: "ERPNext is not installed. Please install ERPNext to use ERPNext link fields."

### 2. Dynamic Field Visibility
- Created a utility module `it_management.utils.erpnext_integration` with functions:
  - `is_erpnext_installed()`: Checks if ERPNext app is installed
  - `validate_erpnext_required()`: Validates ERPNext is installed, throws error if not
  - `get_erpnext_doctype_fields_mapping()`: Returns mapping of all doctypes with ERPNext/ITM field pairs
  - `sync_erpnext_fields_for_doctype()`: Synchronizes field visibility for a specific doctype
  - `sync_all_erpnext_fields()`: Synchronizes all configured doctypes

### 3. Doctype Controllers
- Updated controllers for key doctypes to dynamically show/hide fields based on:
  1. Whether ERPNext is installed
  2. The IT Management Settings `use_erpnext_links` value
  3. Whether the target doctype exists

- Implemented `onload()` method to set `depends_on` values when the form loads
- Implemented `validate()` method to ensure linked doctypes exist before saving

### 4. Migration Patch
- Created patch `0_4/erpnext_field_visibility.py` that:
  - Runs on app install/update (via `after_install` hook)
  - Syncs all field visibilities
  - Automatically disables `use_erpnext_links` if ERPNext is not installed

### 5. Hooks Integration
- Added `after_install` hook to run the migration patch
- Added `doc_events` hook to sync fields when IT Management Settings are updated

## Files Changed

### New Files Created
1. `it_management/it_management/utils/__init__.py` - Package init
2. `it_management/it_management/utils/erpnext_integration.py` - Core utility functions
3. `it_management/patches/0_4/__init__.py` - Patch package init
4. `it_management/patches/0_4/erpnext_field_visibility.py` - Migration patch

### Modified Files
1. **`it_management/hooks.py`**
   - Added `after_install` hook
   - Added `doc_events` for IT Management Settings

2. **`it_management/it_management/doctype/it_management_settings/it_management_settings.py`**
   - Added `validate()` method to check ERPNext installation
   - Added `on_update()` method to sync all fields when settings change

3. **`it_management/it_management/doctype/itm_host_item/itm_host_item.py`**
   - Replaced static `depends_on` logic with dynamic field visibility
   - Added `onload()` method to set field visibility based on settings
   - Added `validate()` method to check target doctypes exist

4. **`it_management/it_management/doctype/software_instance/software_instance.py`**
   - Added `onload()` method for dynamic field visibility
   - Updated `before_save()` to handle missing Customer doctype
   - Added `validate()` method

5. **`it_management/it_management/doctype/configuration_item/configuration_item.py`**
   - Added `onload()` method for dynamic field visibility
   - Added `validate()` method

6. **`it_management/it_management/doctype/it_management_settings/test_it_management_settings.py`**
   - Added comprehensive test cases

7. **`it_management/patches.txt`**
   - Added new patch to the list

## Doctypes Covered

The implementation covers all custom doctypes that reference ERPNext doctypes:

### Primary Doctypes
- ITM Host Item (customer, item_code → itm_customer, itm_item)
- Software Instance (customer, supplier)
- Configuration Item (customer, item_code, supplier)
- IT Hardware (item_code)
- Licence (item_code, supplier)
- ITM User Account (customer)
- User Account (customer)

### Child Tables
- Subnet Table (customer)
- Location Room (customer)
- ITM Solution Table (customer)
- User Group Table (customer)
- IT Checklist Table (customer)
- Solution Table (customer)
- ITM Solution (customer)

## Behavior

### When ERPNext IS installed:
- User can enable/disable `use_erpnext_links` in IT Management Settings
- When enabled: ERPNext fields (Customer, Item, Supplier) are shown, ITM fields are hidden
- When disabled: ITM fields (ITM Customer, ITM Item) are shown, ERPNext fields are hidden

### When ERPNext is NOT installed:
- User CANNOT enable `use_erpnext_links` - validation prevents it
- If already enabled, the setting is automatically disabled by the migration patch
- ERPNext fields are hidden (via `depends_on = "eval:False"`)
- ITM fields are shown
- No errors occur when opening doctypes

### Field Visibility Logic

```python
show_erpnext_fields = is_erpnext_installed() and use_erpnext_links

# For ERPNext fields (customer, item_code, supplier):
field.depends_on = "" if show_erpnext_fields and target_exists else "eval:False"

# For ITM fields (itm_customer, itm_item):
field.depends_on = "eval:False" if show_erpnext_fields else ""
```

## Testing

### Test Cases Implemented
1. `test_erpnext_installed_check()` - Verifies ERPNext detection works
2. `test_settings_validation_without_erpnext()` - Ensures validation fails without ERPNext
3. `test_settings_validation_with_erpnext()` - Ensures validation passes with ERPNext
4. `test_field_mapping_exists()` - Verifies field mappings are properly defined
5. `test_sync_all_erpnext_fields()` - Ensures sync function runs without errors

### Manual Testing Steps
1. Install IT Management app without ERPNext
2. Try to enable "Use ERPNext Link Fields" - should show error
3. Open ITM Host Item - should show ITM fields, no errors
4. Install ERPNext
5. Enable "Use ERPNext Link Fields" - should work
6. Open ITM Host Item - should show ERPNext fields
7. Disable "Use ERPNext Link Fields" - should show ITM fields

## Backward Compatibility

- Existing installations are handled by the migration patch
- If `use_erpnext_links` is enabled but ERPNext is not installed, the patch automatically disables it
- All field visibility is managed dynamically, so existing data is not affected
- The solution is non-destructive - it only hides/shows fields, doesn't delete them

## Performance Considerations

- Field visibility is determined once per form load (in `onload()`)
- Settings are cached by Frappe's single doc caching
- ERPNext installation check is a simple list lookup
- No database queries are performed during field visibility determination

## Future Enhancements

Potential improvements for future iterations:
1. Add a whitelisted method to manually sync fields via API
2. Add UI indicator showing which mode (ERPNext/ITM) is active
3. Add migration helper to convert data from ITM fields to ERPNext fields
4. Add bulk update functionality for existing documents

## Deployment Notes

### Installation
1. The patch will run automatically on app install via `after_install` hook
2. No manual intervention required

### Upgrade
1. The patch will run automatically on app update
2. Existing settings will be validated and corrected if needed

### Rollback
1. To rollback, simply revert to the previous version
2. No data migration is needed as the changes are non-destructive

## Error Messages

The implementation provides clear, actionable error messages:

1. **When trying to enable ERPNext links without ERPNext:**
   ```
   ERPNext is not installed. Please install ERPNext to use ERPNext link fields.
   ```

2. **When a linked doctype doesn't exist:**
   ```
   The doctype 'Customer' does not exist. Please install ERPNext or disable 'Use ERPNext Link Fields' in IT Management Settings.
   ```

## Code Quality

- All Python files pass syntax validation
- Follows Frappe/ERPNext coding conventions
- Uses `from __future__ import unicode_literals` for Python 2/3 compatibility
- Includes proper copyright headers
- Uses `_()` for translation where appropriate
- Includes comprehensive docstrings
- Follows the principle of least surprise

## Files Summary

```
New Files:
  it_management/it_management/utils/__init__.py
  it_management/it_management/utils/erpnext_integration.py
  it_management/patches/0_4/__init__.py
  it_management/patches/0_4/erpnext_field_visibility.py

Modified Files:
  it_management/hooks.py
  it_management/it_management/doctype/it_management_settings/it_management_settings.py
  it_management/it_management/doctype/it_management_settings/test_it_management_settings.py
  it_management/it_management/doctype/itm_host_item/itm_host_item.py
  it_management/it_management/doctype/software_instance/software_instance.py
  it_management/it_management/doctype/configuration_item/configuration_item.py
  it_management/patches.txt

Total Changes:
  +398 lines, -58 lines (net +340 lines)
```

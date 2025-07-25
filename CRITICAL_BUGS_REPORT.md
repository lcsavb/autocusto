# Critical Bugs Report - AutoCusto Medical Prescription System

## Overview

During the PDF generation architecture refactoring, two critical bugs were discovered in the patient versioning and process creation system. These bugs affect the core functionality of medical prescription management.

## Bug #1: Process Isolation Vulnerability (FIXED)

### Description
Users could overwrite other users' medical processes when creating prescriptions for the same patient-disease combination. This is a **CRITICAL SECURITY ISSUE** in a medical system.

### Root Cause
In `processos/helpers.py` function `registrar_db()`, the process existence check was missing user filtering:

```python
# BEFORE (BUGGY CODE):
for p in paciente_existe.processos.all():
    if p.doenca.cid == cid:
        processo_existe = True
        dados_processo["id"] = p.id  # Overwrites another user's process!
        break

# AFTER (FIXED CODE):
for p in paciente_existe.processos.all():
    if p.doenca.cid == cid and p.usuario == usuario:  # Added user filtering
        processo_existe = True
        dados_processo["id"] = p.id
        break
```

### Impact
- User A creates a process for Patient X with Disease Y
- User B creates a process for the same Patient X with Disease Y  
- User B's data would overwrite User A's prescription
- Medical data integrity compromised
- Potential HIPAA/privacy violations

### Status
✅ **FIXED** - Added user filtering to ensure process isolation between users

### Files Modified
- `processos/helpers.py:844-850` - Added user filtering in process existence check

### Test Coverage
- `tests/test_renovacao_rapida_versioning_bug.py:test_critical_bug_fix_user_process_isolation()`

---

## Bug #2: New Patient PDF Authorization Failure (ACTIVE)

### Description
When creating prescriptions for NEW patients (not existing ones), PDF generation fails with authorization errors, while the process is successfully created in the database.

### Symptoms
```
2024-XX-XX XX:XX:XX ERROR: User user@example.com attempted unauthorized access to PDF for CPF XXXXXXXXX
```

### Root Cause (SUSPECTED)
Transaction rollback issue in new patient creation causing patient-user association to fail, leading to:
1. Process is created successfully  
2. Patient record exists but user association is missing
3. PDF generation succeeds but creates file
4. When serving PDF, authorization check fails because user is not associated with patient

### Evidence
From user logs:
- "when the patient already exists, the 'test patient' you created, the pdf generation works"
- "when it is a new one it does not"
- Process 79 was created but doesn't exist in database (rollback indication)

### Current Investigation Status
🔍 **UNDER INVESTIGATION** - Added comprehensive logging to identify rollback cause

### Impact
- NEW patient prescriptions cannot be served as PDFs
- Existing patient prescriptions work correctly
- Business workflow disrupted for new patient registration

### Files Under Investigation
- `processos/helpers.py:registrar_db()` - Patient creation and user association
- `processos/prescription_services.py` - Transaction management
- `processos/views.py:serve_pdf()` - Authorization logic

### Added Logging
- Database transaction logging in `PrescriptionService`
- Detailed error logging in `registrar_db()` for new patient path
- Step-by-step logging for debugging rollback issues

---

## Bug #3: New Processes Not Showing in Renovacao Rapida (FIXED)

### Description  
Newly created processes were not appearing in the `renovacao_rapida` template search results due to the process isolation bug (#1).

### Root Cause
Same as Bug #1 - when users overwrote each other's processes, the template logic that filters processes by user (`processo.usuario == usuario`) would not find the user's process because it had been overwritten.

### Status
✅ **FIXED** - Resolved by fixing Bug #1 (process isolation)

### Template Logic (Working Correctly)
```html
<!-- In renovacao_rapida.html -->
{% for processo in paciente.processos.all %}
    {% if processo.usuario == usuario %}
        <!-- Process appears here for correct user -->
    {% endif %}
{% endfor %}
```

---

## Next Steps

### Immediate Priority
1. **Bug #2**: Complete investigation of transaction rollback issue
2. Test new patient creation with enhanced logging
3. Identify and fix the patient-user association failure

### Testing
- Manual testing with new patient creation flow
- Verify authorization works after fix
- End-to-end testing of complete prescription workflow

### Files to Monitor
- Application logs: `docker-compose logs web`
- Database logs with new logger: `processos.database`
- PDF logs: `processos.pdf`

---

## Security Implications

Bug #1 represented a **critical security vulnerability** in a medical system where:
- Patient data privacy could be compromised
- Medical prescriptions could be overwritten
- Audit trails could be corrupted
- Regulatory compliance (HIPAA, GDPR) could be violated

The fix ensures proper data isolation between healthcare providers accessing the same patient records.
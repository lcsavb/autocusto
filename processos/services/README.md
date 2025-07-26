# Prescription Services Architecture Documentation

## Overview

This document describes the comprehensive service architecture for the prescription system, implementing clean separation of concerns, repository patterns, and smart patient versioning.

## Architecture Principles

- **Single Responsibility**: Each service has one clear purpose
- **Repository Pattern**: Database access only through repositories  
- **Service Composition**: Higher-level services coordinate lower-level ones
- **Smart Versioning**: Only create patient versions when data actually changes
- **Consistent Flow**: All operations (create/edit/renewal) use the same service layer

## Service Layer Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                         VIEWS LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  prescription_views.py  │  renewal_views.py  │  session_views.py │
└─────────────────┬───────────────────┬───────────────────────────┘
                  │                   │
                  ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│           PrescriptionViewSetupService                          │
│  ┌─────────────────────┬─────────────────────────────────────┐  │
│  │ handle_prescription │ handle_prescription_edit_request()  │  │
│  │ _create_request()   │                                     │  │
│  └─────────────────────┴─────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   WORKFLOW LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│              PrescriptionService (workflow_service.py)          │
│         create_or_update_prescription()                         │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                 BUSINESS LOGIC LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  PrescriptionDataBuilder  │  ProcessRepository  │  Renewal...   │
│  build_prescription_data  │  create_process...  │  Services     │
└─────────────────┬───────────────────┬───────────────────────────┘
                  │                   │
                  ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                  REPOSITORY LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  PatientRepository │ DomainRepository │ MedicationRepository    │
│                    │ get_disease_by_  │ list_medications_...     │
│  check_patient_... │ cid()           │                         │
└─────────────────┬─────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATA ACCESS LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│    PatientVersioningService  │  Database Models                │
│    create_or_update_patient  │  Paciente, Processo, Doenca     │
└─────────────────────────────────────────────────────────────────┘
```

## Core Services

### 1. PrescriptionViewSetupService (`view_services.py`)

**Purpose**: SETUP ONLY - Prepares conditional data for view rendering

**Responsibilities**:
- Form initialization data preparation
- Session state validation
- User permission checks for view access
- Dynamic form construction setup
- Context data preparation for templates

**Key Methods**:
- `setup_for_new_prescription()` - Prepare data for new prescription form rendering
- `setup_for_edit_prescription()` - Prepare data for edit prescription form rendering  
- `validate_doctor_profile_completeness()` - Check if doctor can access views
- `build_patient_search_context()` - Prepare patient search data

**✅ CLEAN ARCHITECTURE**: Now properly follows single responsibility principle
- ✅ Only handles GET request setup data
- ✅ No POST request processing or business logic
- ✅ Returns setup data structures only
- ✅ Reduced from 780 to 570 lines

**Integration**:
- Called ONLY by views for GET request setup
- Does NOT handle POST requests (moved to view helper functions)
- Returns ViewSetupResult structures for template rendering

### 2. PrescriptionService (`workflow_service.py`)

**Purpose**: Orchestrates the complete prescription workflow

**Responsibilities**:
- Business rule validation
- Service coordination
- Transaction management
- PDF generation coordination
- Process lifecycle management

**Key Methods**:
- `create_or_update_prescription()` - Main workflow orchestrator

**Service Dependencies**:
- `PrescriptionDataBuilder` - Data construction
- `ProcessRepository` - Database operations
- `DomainRepository` - Entity lookups
- `PatientRepository` - Patient operations
- `PrescriptionPDFService` - PDF generation

**✅ PROPER USAGE**: Now called directly by view helper functions
- ✅ No duplication with setup service
- ✅ Clear single responsibility for business logic
- ✅ Used for all prescription workflow operations

### 3. PrescriptionDataBuilder (`data_builder.py`)

**Purpose**: Constructs structured data for prescription processes

**Responsibilities**:
- Form data extraction and validation
- Patient data extraction
- Prescription structure building
- Data transformation and formatting

**Key Methods**:
- `build_prescription_data()` - Main data construction method
- `extract_patient_data()` - Extract patient-specific fields
- `build_prescription_structure()` - Build medication structure

**Output**: Structured data dictionary for repository operations

### 4. ProcessRepository (`process_repository.py`)

**Purpose**: Database operations for prescription processes

**Responsibilities**:
- Process creation and updates
- Business logic enforcement
- Medication associations
- User statistics updates

**Key Methods**:
- `create_process_from_structured_data()` - Create new process
- `update_process_from_structured_data()` - Update existing process
- `update_process_date_only()` - Quick renewal date updates
- `get_process_by_id_and_user()` - Secure process retrieval

**Business Rules**:
- Prevents duplicate processes
- Manages user process counts
- Enforces data integrity

### 5. PatientVersioningService (`patient_versioning_service.py`)

**Purpose**: Smart patient data versioning for multi-user isolation

**Responsibilities**:
- Patient version creation/updates
- Data change detection
- User access control
- Audit trail maintenance

**Key Methods**:
- `create_or_update_patient_for_user()` - Smart versioning entry point
- `_user_has_version_with_same_data()` - Change detection logic

**Smart Features**:
- Only creates versions when data actually changes
- Compares field-by-field for changes
- Handles data type normalization
- Preserves audit trails for compliance

### 6. Repository Layer

#### PatientRepository (`repositories/patient_repository.py`)
- Patient existence checks
- Patient data extraction
- User access validation
- Patient query operations

#### DomainRepository (`repositories/domain_repository.py`)  
- Disease (Doenca) lookups by CID
- Medical issuer (Emissor) management
- Domain entity operations

#### MedicationRepository (`repositories/medication_repository.py`)
- Medication listings by protocol/CID
- Medication data formatting
- Form data extraction

## Data Flow Examples

### New Patient Creation Flow

```
1. User submits form → prescription_views.py
2. View calls → PrescriptionViewSetupService.handle_prescription_create_request()
3. Setup service calls → PrescriptionService.create_or_update_prescription()
4. Workflow service calls:
   a. MedicationRepository.extract_medication_ids_from_form()
   b. DomainRepository.get_disease_by_cid()  
   c. DomainRepository.get_emissor_by_medico_clinica()
   d. PatientRepository.check_patient_exists()
   e. PrescriptionDataBuilder.build_prescription_data()
   f. ProcessRepository.create_process_from_structured_data()
   g. PatientVersioningService.create_or_update_patient_for_user()
5. PDF generation and response
```

### Edit Existing Patient Flow

```
1. User submits edit → prescription_views.py  
2. View calls → PrescriptionViewSetupService.handle_prescription_edit_request()
3. Setup service calls → PrescriptionService.create_or_update_prescription()
4. Workflow service calls:
   a. Same repositories as create flow
   b. ProcessRepository.update_process_from_structured_data()
   c. PatientVersioningService checks for data changes
   d. Only creates new version if data actually changed
5. PDF generation and response
```

### Smart Versioning Logic

```
PatientVersioningService.create_or_update_patient_for_user():
├─ Check if user has existing version
├─ If no version exists → Create new version
├─ If version exists:
│  ├─ Compare field-by-field for changes
│  ├─ If no changes → Return existing patient (no new version)
│  └─ If changes detected → Create new version for audit trail
└─ Return versioned patient instance
```

## ✅ Clean Architecture Achieved

### Proper Separation of Concerns

1. **View Layer** (`prescription_views.py`):
   - GET requests → Call ViewSetupService for setup data only
   - POST requests → Use helper functions that call PrescriptionService directly
   - HTTP concerns (form validation, JSON responses, file I/O) handled in views

2. **Setup Service** (`view_services.py`):
   - Only handles GET request data preparation
   - No POST processing or business logic
   - Clean single responsibility

3. **Business Service** (`workflow_service.py`):
   - Only handles business logic and workflow orchestration
   - Called directly by view helper functions
   - No HTTP concerns

### Current Architecture

```
✅ CLEAN ARCHITECTURE:
View (GET)  → ViewSetupService.setup_for_*() → Setup data only
View (POST) → View helper functions → PrescriptionService.create_or_update() → Business logic
View (POST) → Handle HTTP concerns directly (JSON, files, session)
```

## Key Architectural Benefits

### 1. **Single Responsibility Principle**
- ✅ ViewSetupService: Only setup data preparation (570 lines, down from 780)
- ✅ PrescriptionService: Only business logic orchestration
- ✅ Views: Only HTTP concerns and coordination
- ✅ No duplication between layers

### 2. **Clear Boundaries**  
- ✅ GET requests handled by setup service
- ✅ POST requests handled by business service via view helpers
- ✅ HTTP concerns (JSON, files, sessions) in views where they belong
- ✅ Easy to test and modify each layer independently

### 3. **Performance & Maintainability**
- ✅ Smart versioning prevents unnecessary database writes
- ✅ Repository pattern enables caching
- ✅ Efficient data change detection
- ✅ Reduced complexity and code duplication

### 4. **Compliance & Reliability**
- ✅ Audit trails preserved when needed
- ✅ User data isolation maintained
- ✅ Proper error handling and logging
- ✅ Clear separation prevents architectural violations

## Migration Notes

This architecture was refactored from a previous system that had:
- Direct database calls in views and forms
- Inconsistent service usage patterns  
- Unnecessary patient version creation
- Mixed business logic across layers

The new architecture ensures:
- ✅ All database access goes through repositories
- ✅ Views only handle HTTP concerns
- ✅ Business logic isolated in service layer
- ✅ Smart versioning reduces database overhead
- ✅ Consistent patterns across all operations

## Usage Guidelines

### For Developers (Corrected Architecture)

1. **Views (GET)**: 
   ```python
   # GET requests - setup data only
   setup = PrescriptionViewSetupService()
   data = setup.setup_for_new_prescription(request)
   return render(request, 'template.html', data)
   ```

2. **Views (POST)**:
   ```python
   # POST requests - business logic only
   service = PrescriptionService()
   pdf, process_id = service.create_or_update_prescription(form_data, user, ...)
   return JsonResponse({'success': True, 'process_id': process_id})
   ```

3. **Setup Services**: ONLY prepare conditional data for view rendering
4. **Workflow Services**: ONLY handle business logic and POST processing  
5. **Repositories**: Only database access, return domain objects
6. **Versioning**: Trust the smart versioning logic, don't bypass it

### ✅ Architecture Migration Complete

**Clean Architecture Achieved**: The system now follows proper design principles

1. **✅ POST Duplication Eliminated**:
   - Removed `handle_prescription_*_request()` methods from ViewSetupService
   - Views now use helper functions that call PrescriptionService directly
   - Single source of truth for business logic

2. **✅ Single Responsibility Restored**:
   - ViewSetupService: Only GET setup (570 lines, reduced 27%)
   - PrescriptionService: Only business logic
   - Views: Only HTTP concerns via helper functions

**Current Integration** (clean):
- Views use ViewSetupService ONLY for GET request setup
- Views use helper functions for POST processing (calling PrescriptionService)
- Clear separation of concerns achieved
- Zero functionality lost during migration

### Adding New Features

1. Determine the appropriate service layer (view/workflow/repository)
2. Follow the established patterns for similar operations
3. Use repositories for all database access
4. Maintain the service composition hierarchy
5. Add comprehensive logging for debugging

## Testing Strategy

- **Unit Tests**: Each service in isolation with mocked dependencies
- **Integration Tests**: Full workflow testing with test database
- **Performance Tests**: Versioning logic efficiency
- **Regression Tests**: Ensure old functionality still works

This architecture provides a solid foundation for the prescription system with clear patterns, proper separation of concerns, and excellent maintainability.
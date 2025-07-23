# AutoCusto User Journey Guide

This document maps the complete user experience flows in the AutoCusto medical prescription system, explaining the application logic behind each step and how the system handles edge cases.

## 🏥 **Primary User Journey - Medical Prescription Creation**

### **1. User Registration & Authentication**
```
New User → Registration Form → Email Verification → Login
Existing User → Login Form → Dashboard
```

**Application Logic:**
- Custom email-based authentication system
- Medical professional verification required
- Session establishment for workflow tracking

### **2. Initial Setup (First-Time Users Only)**

#### **Step 2a: Complete Medical Profile**
```
Login → System Check → Missing CRM/CNS → Redirect to /medicos/completar-perfil/
```

**User Experience:**
- User sees: "Complete seus dados médicos antes de criar processos"
- Form requires: CRM number confirmation + CNS number confirmation
- **Immutability Rule**: Once set, CRM/CNS cannot be changed

**Technical Detail:**
- Status Code: `302` redirect to `complete-profile`
- Session preservation during setup process

#### **Step 2b: Create Medical Facility**
```
Profile Complete → System Check → No Clinics → Redirect to /clinicas/cadastro/
```

**User Experience:**
- User sees: "Cadastre uma clínica antes de criar processos"
- Form requires: Clinic name, CNS, address, phone in Brazilian format
- System automatically associates clinic with current doctor

**Technical Detail:**
- Status Code: `302` redirect to `clinicas-cadastro`
- Phone validation: `(11) 99999-9999` format required

### **3. Process Creation Workflow**

#### **Step 3a: Patient & Disease Selection (Home Page)**
```
Complete Setup → Home Page (/) → Patient Search Form
```

**User Experience:**
- Enter patient CPF (Brazilian tax ID)
- Select disease from dropdown (CID codes)
- System determines if patient exists in doctor's database

**Application Logic:**
```python
if patient_exists_in_doctor_database:
    session["paciente_existe"] = True
    session["paciente_id"] = patient.id
else:
    session["paciente_existe"] = False
    
session["cid"] = selected_disease_code
session["cpf_paciente"] = entered_cpf
```

#### **Step 3b: Process Form Display**
```
Patient Selected → Session Validation → Setup Validation → Process Form
```

**System Validation Chain:**
1. **Session Check**: `paciente_existe` and `cid` must exist
   - **Fail**: `302` redirect to home with "Sessão expirada"
2. **Profile Check**: CRM and CNS must be complete
   - **Fail**: `302` redirect to `complete-profile`
3. **Clinic Check**: User must have at least one clinic
   - **Fail**: `302` redirect to `clinicas-cadastro`
4. **All Pass**: `200` display process creation form

**User Experience:**
- **Existing Patient**: Form pre-populated with patient data
- **New Patient**: Empty form for patient data entry
- Dynamic form fields based on selected disease protocol

#### **Step 3c: Process Submission & PDF Generation**
```
Form Submission → Validation → Database Save → PDF Generation → Serving
```

**Technical Flow:**
- AJAX form submission for better UX
- Server-side validation and medication processing
- PDF generation using memory-optimized system (`/dev/shm`)
- Secure PDF serving with access control

## 🔄 **Edge Cases & Error Handling**

### **Direct URL Access Scenarios**

#### **Scenario 1: New User Accesses `/processos/cadastro/` Directly**
```
Direct Access → No Session Data → 302 Redirect to Home
```
**Message**: "Sessão expirada. Por favor, inicie o cadastro novamente."

#### **Scenario 2: Setup Incomplete User**
```
Direct Access → Session OK → CRM/CNS Missing → 302 Redirect to Profile
```
**Message**: "Complete seus dados médicos antes de criar processos."

#### **Scenario 3: No Clinic User**
```
Direct Access → Session OK → Profile OK → No Clinics → 302 Redirect to Clinic
```
**Message**: "Cadastre uma clínica antes de criar processos."

### **Form Validation Failures**

#### **Clinic Registration with Invalid Data**
```
Form Submission → Validation Error → 200 Form Redisplay with Errors
```
**Common Issues**:
- Phone format: Must be `(11) 99999-9999`, not `11999999999`
- Required fields: Name, CNS, address components
- **Result**: Status `200` with error messages, clinic not created

#### **Process Form Validation**
```
AJAX Submission → Server Validation → JSON Response
```
**Success**: `{"success": true, "pdf_url": "/path/to/pdf"}`
**Failure**: `{"success": false, "error": "Description", "form_errors": {...}}`

## 🎯 **Status Code Patterns & Their Meanings**

### **302 - Workflow Redirects (Navigation/Flow Control)**
- **User guided to next step** in their journey
- **Session-based routing** - system knows where user should go
- **Examples**:
  - Home → Process creation (after patient selection)
  - Setup incomplete → Profile completion
  - Missing clinic → Clinic creation

### **200 - Content Display (Information/Forms)**
- **User sees content** appropriate to their current state
- **Form display** for data entry
- **Examples**:
  - Process creation form (when setup complete)
  - Clinic registration form
  - Error forms with validation messages

### **Application Logic Philosophy**
```
Redirect (302) = "Go somewhere else to continue your task"
Display (200) = "Here's what you need to see/do right here"
```

## 🏗️ **Workflow State Management**

### **Session Variables**
```python
session["paciente_existe"]    # Boolean: Patient in doctor's database
session["paciente_id"]        # Integer: Patient ID (if exists)  
session["cid"]               # String: Disease CID code
session["cpf_paciente"]      # String: Patient CPF
session["data1"]             # String: Process date
session["processo_id"]       # Integer: For editing existing processes
```

### **Setup State Validation**
```python
def can_create_process(user):
    medico = get_medico(user)
    
    # Check medical credentials
    if not (medico.crm_medico and medico.cns_medico):
        return False, "complete-profile"
    
    # Check clinic association  
    if not user.clinicas.exists():
        return False, "clinicas-cadastro"
        
    return True, None
```

## 🚨 **Security Considerations**

### **Patient Data Access Control**
- **Isolation**: Doctors can only access their own patients
- **Authorization**: Patient CPF must belong to current doctor
- **PDF Access**: URL-based authorization with CPF verification

### **Session Security**
- **Expiration**: Process sessions expire and require restart
- **Validation**: All workflow steps validate session integrity
- **CSRF Protection**: All form submissions include CSRF tokens

## 🔄 **Alternative Flows**

### **Process Editing (Renovation)**
```
Existing Process → Search → Select → Edit Form → Update → New PDF
```
**Entry Points**:
- Process search page (`/processos/busca/`)
- Quick renovation page (`/processos/renovacao/`)

### **Quick Renovation Workflow**
```
Patient Search → Process Selection → Date Input → Direct PDF or Edit Mode
```
**User Choice**:
- **Direct**: Generate PDF with new date
- **Edit Mode**: Full form editing with protocol modifications

## 📊 **Success Metrics & Validation**

### **Successful Process Creation**
1. ✅ Patient data validated and saved
2. ✅ Process record created with unique constraint: `[usuario, paciente, doenca]`
3. ✅ PDF generated and accessible
4. ✅ User redirected to PDF viewing page

### **System Health Indicators**
- **Low 302 redirect rates** on process creation (indicates good user education)
- **High form completion rates** (indicates clear UX)
- **Fast PDF generation times** (indicates system performance)

## 🛠️ **Technical Implementation Notes**

### **Memory-Optimized PDF Generation**
- Templates stored in RAM filesystem (`/dev/shm`)
- UTF-8 character support for Brazilian Portuguese
- Immediate cleanup after generation

### **Database Relationships**
```
Usuario (User) ←→ Medico (Doctor) ←→ Clinica (Clinic)
                     ↓
                 Emissor (Doctor-Clinic Combination)
                     ↓  
                 Processo (Process) → Paciente (Patient)
                     ↓              → Doenca (Disease)
                 Medicamento (Medications)
```

### **Form Generation**
- **Dynamic forms** based on disease protocols
- **Conditional fields** appear based on disease requirements
- **Medication management** with dosage calculation

---

## 🎯 **Key Takeaways for Developers**

1. **User Journey First**: Every redirect and status code serves the user experience
2. **Progressive Setup**: System guides users through required steps
3. **Graceful Degradation**: Edge cases result in helpful guidance, not errors
4. **Session Integrity**: Workflow state is carefully maintained and validated
5. **Security by Design**: Patient data access is strictly controlled
6. **Performance Optimized**: PDF generation uses memory-based optimization

This user journey guide serves as both documentation and validation that the AutoCusto system implements thoughtful, user-centered design principles while maintaining strict security and regulatory compliance for medical data handling.
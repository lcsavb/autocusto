# AutoCusto Refactoring Priority List

## **🚨 CRITICAL (Fix Immediately)**

### **1. Fix Broken Architecture References**
- **Status**: ✅ COMPLETED
- **Issue**: Removed obsolete `manejo_pdfs_memory.py` and broken `gerar_pdf_stream()`
- **Impact**: Eliminated 300+ lines of dead code and broken imports

---

## **🔴 HIGH PRIORITY (This Sprint)**

### **2. Extract File I/O from Business Logic**
- **File**: `processos/helpers.py:transfere_dados_gerador()` (lines 581-596)
- **Problem**: Business service writing files to `/tmp/` violates separation of concerns
- **Solution**: Create `PDFFileService` in infrastructure layer
- **Effort**: 2 hours
- **Risk**: Medium - Affects PDF serving functionality

### **3. Simplify SetupResult Data Structure**
- **File**: `processos/view_services.py:SetupResult` (lines 30-53)
- **Problem**: 15+ field NamedTuple mixing error handling, user data, medical data
- **Solution**: Replace with focused data classes using composition
- **Effort**: 3 hours
- **Risk**: Low - Internal refactoring only

### **4. Replace Manual Field Copying**
- **File**: `processos/helpers.py:cria_dict_renovação()` (lines 332-345)
- **Problem**: Manual field mapping creates maintenance burden
- **Solution**: Use Django's `model_to_dict()` with field filtering
- **Effort**: 1 hour
- **Risk**: Low - Existing tests cover functionality

### **5. Split PrescriptionService Responsibilities**
- **File**: `processos/prescription_services.py:PrescriptionService` (lines 403-531)
- **Problem**: Single service handles validation, database, PDF, transactions
- **Solution**: Create `PrescriptionWorkflow` for orchestration
- **Effort**: 4 hours
- **Risk**: High - Core business logic changes

---

## **🟡 MEDIUM PRIORITY (Next Sprint)**

### **6. Eliminate Duplicated PDF Response Logic**
- **Files**: `views.py` in `cadastro`, `edicao`, `renovacao_rapida`
- **Problem**: Similar JSON response creation repeated 3+ times
- **Solution**: Create `PDFResponseHelper` utility
- **Effort**: 1.5 hours
- **Risk**: Low - View-level changes only

### **7. Break Down Complex View Functions**
- **File**: `processos/views.py:renovacao_rapida()` (~100 lines)
- **Problem**: Single function handling GET/POST with complex branching
- **Solution**: Split into `_handle_renovacao_get()` and `_handle_renovacao_post()`
- **Effort**: 2 hours
- **Risk**: Medium - HTTP handling changes

### **8. Clean Up Debug Statements**
- **File**: `processos/pdf_strategies.py` (lines 22, 35, 37, 42)
- **Problem**: `print()` statements in production code
- **Solution**: Replace with proper logging
- **Effort**: 30 minutes
- **Risk**: None - Logging improvements only

### **9. Standardize Exception Handling**
- **Files**: Various files mixing `logger.error()` and `print()` approaches
- **Problem**: Inconsistent error reporting makes debugging difficult
- **Solution**: Establish logging standards and update consistently
- **Effort**: 2 hours
- **Risk**: Low - Error handling improvements

---

## **🟢 LOW PRIORITY (Future Iterations)**

### **10. Replace Magic Numbers with Constants**
- **File**: `processos/helpers.py` date calculations
- **Problem**: Hardcoded 30-day intervals, magic numbers
- **Solution**: Create configuration constants for business rules
- **Effort**: 1 hour
- **Risk**: None - Configuration improvements

### **11. Implement Proper Strategy Pattern**
- **File**: `processos/prescription_services.py:PrescriptionTemplateSelector`
- **Problem**: Hard dependency on specific strategy implementation
- **Solution**: Use abstract base class for strategy interface
- **Effort**: 2 hours
- **Risk**: Low - Architecture improvement

### **12. Add Comprehensive Business Rule Tests**
- **Files**: `tests/` directory
- **Problem**: Limited test coverage for edge cases and business rules
- **Solution**: Expand test suite for medical regulations and error scenarios
- **Effort**: 4 hours
- **Risk**: None - Testing improvements

---

## **📊 Refactoring Execution Plan**

### **Week 1: Foundation Cleanup**
1. ✅ Remove obsolete code (COMPLETED)
2. Extract file I/O operations (#2)
3. Replace manual field copying (#4)

### **Week 2: Data Structure Improvements** 
1. Simplify SetupResult structure (#3)
2. Create PDF response helpers (#6)
3. Clean up debug statements (#8)

### **Week 3: Service Layer Refactoring**
1. Split PrescriptionService (#5)
2. Break down complex views (#7)
3. Standardize exception handling (#9)

### **Week 4: Polish and Testing**
1. Replace magic numbers (#10)
2. Add comprehensive tests (#12)
3. Performance validation and monitoring

---

## **🎯 Success Criteria**

### **Quantitative Goals**
- **Code Reduction**: 15-20% reduction in total lines of code
- **Complexity**: No functions >50 lines (currently 8 violations)
- **Test Coverage**: Maintain >90% coverage during refactoring
- **Performance**: PDF generation time <3 seconds (current baseline)

### **Qualitative Goals**
- **Single Responsibility**: Each service has one clear purpose
- **Separation of Concerns**: No business logic mixed with infrastructure
- **Maintainability**: New developers can understand system in <2 hours
- **Testability**: All services can be unit tested in isolation

---

## **⚠️ Risk Mitigation**

### **High Risk Items**
- **PrescriptionService refactoring (#5)**: Create feature branch, extensive testing
- **View function changes (#7)**: Maintain backward compatibility in URLs

### **Testing Strategy**
- Run full test suite after each change
- Manual testing of PDF generation workflows
- Performance benchmarking before/after

### **Rollback Plan**
- Git feature branches for each major change
- Database backup before structural changes
- Docker containers for quick environment restoration

---

*Last Updated: 2025-01-XX*  
*Next Review: Weekly during execution*
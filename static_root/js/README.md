# AutoCusto JavaScript Unit Tests

## 🚨 CRITICAL: Medication Validation Logic Tests

This directory contains **Node.js unit tests** for the core JavaScript logic that ensures medical prescription safety.

### 🏥 Medical Safety Logic

The tests validate the **CRITICAL business logic** from `med.js` that prevents invalid medical prescriptions from being submitted:

- **Form submission prevention** when all medications are set to "nenhum" (none)
- **Medication value validation** logic
- **Field name attribute management** for form submission
- **Edge case handling** for empty, null, and undefined values

### 🧪 Test Files

- **`tests/medication-validation.test.js`** - Core medication validation logic tests
- **`tests/mocks/jquery-mock.js`** - jQuery mock for testing without DOM
- **`package.json`** - Node.js test configuration and dependencies

### 🚀 Running Tests

#### Local Development
```bash
# Install dependencies
npm install

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run specific test file
npm run test:med
```

#### CI/CD Pipeline
Tests run automatically in GitHub Actions as part of the `test-integration.yml` workflow.

### 📊 Test Coverage

The tests cover:
- ✅ **Critical path**: All medications set to "nenhum" 
- ✅ **Valid scenarios**: At least one valid medication
- ✅ **Edge cases**: null, undefined, empty strings
- ✅ **Field management**: Name attribute preservation logic
- ✅ **Performance**: Algorithm efficiency
- ✅ **Regression prevention**: Exact logic replication

### 🔧 Technical Details

**Testing Approach:**
- **Pure JavaScript logic testing** - no DOM dependencies
- **Mocked jQuery** - simulates browser environment
- **Extracted business logic** - tests the exact logic from `med.js`
- **Fast execution** - runs in milliseconds, not minutes

**Why Node.js Tests:**
- ✅ **No browser dependencies** - runs in CI/CD without browsers
- ✅ **Fast feedback** - executes in seconds
- ✅ **Production-safe** - doesn't modify existing code
- ✅ **Comprehensive coverage** - tests all critical logic paths

### 🚨 MEDICAL SAFETY IMPORTANCE

These tests are **CRITICAL** for medical prescription safety:

- **Prevents invalid prescriptions** - ensures at least one medication is selected
- **Validates form submission logic** - prevents empty prescriptions from reaching backend
- **Tests exact production logic** - no refactoring, tests actual med.js code
- **Deployment blocker** - CI/CD fails if these tests fail

### 🛠️ Maintenance

**When to update tests:**
- When medication validation logic in `med.js` changes
- When new medication field types are added
- When form submission behavior is modified

**Test philosophy:**
- Test the **existing code as-is** - no refactoring
- Focus on **critical business logic** - medication safety
- Ensure **100% reliability** - medical prescriptions must be safe

### 📋 Integration with CI/CD

Tests are integrated into the deployment pipeline:

1. **JavaScript Tests job** runs Node.js unit tests
2. **Deployment readiness** requires JavaScript tests to pass
3. **Test summary** reports JavaScript test results
4. **Deployment blocking** - fails deployment if medication logic is broken

**Critical requirement:** All medication validation tests must pass before deployment.

---

**🏥 Remember:** These tests protect patient safety by ensuring invalid medical prescriptions cannot be submitted.
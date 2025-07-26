#!/usr/bin/env python3
"""
Script to migrate legacy helper function calls to new service architecture.
Replaces old helper function calls with appropriate service calls across the processos app.
"""

import os
import re
import sys

def backup_file(filepath):
    """Create a backup of the file before modification."""
    backup_path = f"{filepath}.backup"
    with open(filepath, 'r', encoding='utf-8') as original:
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(original.read())
    print(f"✅ Backup created: {backup_path}")

def migrate_file(filepath):
    """Migrate legacy function calls in a single file."""
    print(f"\n📝 Processing: {filepath}")
    
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # 1. Replace checar_paciente_existe calls
    pattern = r'checar_paciente_existe\('
    if re.search(pattern, content):
        # First ensure PatientRepository is imported
        if 'from .repositories.patient_repository import PatientRepository' not in content:
            # Add import after existing imports
            import_pattern = r'(from [^\n]*repository[^\n]*\n)'
            if re.search(import_pattern, content):
                content = re.sub(import_pattern, r'\1from .repositories.patient_repository import PatientRepository\n', content, count=1)
            else:
                # Add after processos imports
                content = re.sub(r'(from processos[^\n]*\n)', r'\1from .repositories.patient_repository import PatientRepository\n', content, count=1)
        
        # Replace the function calls with repository pattern
        old_pattern = r'checar_paciente_existe\(([^)]+)\)'
        new_replacement = r'PatientRepository().check_patient_exists(\1)'
        content = re.sub(old_pattern, new_replacement, content)
        changes_made.append("checar_paciente_existe → PatientRepository().check_patient_exists()")
    
    # 2. Replace gerar_lista_meds_ids calls  
    pattern = r'gerar_lista_meds_ids\('
    if re.search(pattern, content):
        # Ensure MedicationRepository is imported
        if 'from .repositories.medication_repository import MedicationRepository' not in content:
            content = re.sub(r'(from .repositories.patient_repository import PatientRepository\n)', r'\1from .repositories.medication_repository import MedicationRepository\n', content, count=1)
        
        # Replace function calls
        old_pattern = r'gerar_lista_meds_ids\(([^)]+)\)'
        new_replacement = r'MedicationRepository().extract_medication_ids(\1)'
        content = re.sub(old_pattern, new_replacement, content)
        changes_made.append("gerar_lista_meds_ids → MedicationRepository().extract_medication_ids()")
    
    # 3. Replace listar_med calls
    pattern = r'listar_med\('
    if re.search(pattern, content):
        # Ensure MedicationRepository is imported  
        if 'from .repositories.medication_repository import MedicationRepository' not in content:
            content = re.sub(r'(from .repositories.patient_repository import PatientRepository\n)', r'\1from .repositories.medication_repository import MedicationRepository\n', content, count=1)
        
        # Replace function calls
        old_pattern = r'listar_med\(([^)]+)\)'
        new_replacement = r'MedicationRepository().list_medications_by_cid(\1)'
        content = re.sub(old_pattern, new_replacement, content)
        changes_made.append("listar_med → MedicationRepository().list_medications_by_cid()")
    
    # 4. Update test method names
    if 'test_checar_paciente_existe' in content:
        content = content.replace('test_checar_paciente_existe', 'test_check_patient_exists')
        changes_made.append("test method name updated: test_checar_paciente_existe → test_check_patient_exists")
    
    if 'test_gerar_lista_meds_ids' in content:
        content = content.replace('test_gerar_lista_meds_ids', 'test_extract_medication_ids')
        changes_made.append("test method name updated: test_gerar_lista_meds_ids → test_extract_medication_ids")
        
    if 'test_listar_med' in content:
        content = content.replace('test_listar_med', 'test_list_medications_by_cid')
        changes_made.append("test method name updated: test_listar_med → test_list_medications_by_cid")
    
    # Write back if changes were made
    if content != original_content:
        backup_file(filepath)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Changes made:")
        for change in changes_made:
            print(f"   • {change}")
        return True
    else:
        print("ℹ️  No changes needed")
        return False

def main():
    """Main migration function."""
    print("🚀 Starting legacy function migration...")
    
    # Files to migrate (container paths)
    files_to_migrate = [
        'processos/forms.py',
        'processos/tests.py'
    ]
    
    total_changes = 0
    
    for filepath in files_to_migrate:
        if os.path.exists(filepath):
            if migrate_file(filepath):
                total_changes += 1
        else:
            print(f"⚠️  File not found: {filepath}")
    
    print(f"\n🎉 Migration complete! {total_changes} files modified.")
    print("📋 Next steps:")
    print("   1. Test imports: python manage.py shell -c 'from processos.forms import NovoProcesso'")
    print("   2. Run tests: python manage.py test processos.tests")
    print("   3. Verify no legacy calls remain: grep -r 'checar_paciente_existe\\|gerar_lista_meds_ids\\|listar_med' processos/")

if __name__ == "__main__":
    main()
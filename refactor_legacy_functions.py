#!/usr/bin/env python3
"""
Professional refactoring script using rope library.
Renames legacy function calls to new service architecture calls.
"""

import os
import sys
from rope.base.project import Project

def main():
    print("🚀 Starting professional refactoring with rope...")
    
    # Create rope project
    project = Project('.')
    
    try:
        # Target files to refactor
        tests_file = project.get_resource('processos/tests.py')
        
        print(f"📝 Processing: {tests_file.path}")
        
        # Get file content to find occurrences
        content = tests_file.read()
        
        changes_made = []
        
        # Manual replacements for function calls (rope is better for class/method renames)
        if 'checar_paciente_existe(' in content:
            # Add import if not present
            if 'PatientRepository' not in content:
                lines = content.split('\n')
                # Find the right place to add import (after existing repository imports)
                insert_index = 0
                for i, line in enumerate(lines):
                    if 'from processos.repositories' in line or 'from .repositories' in line:
                        insert_index = i + 1
                    elif line.startswith('from') and 'repositories' not in line and insert_index > 0:
                        break
                
                if insert_index == 0:
                    # Add after other processos imports
                    for i, line in enumerate(lines):
                        if line.startswith('from processos') or line.startswith('from .'):
                            insert_index = i + 1
                
                lines.insert(insert_index, 'from processos.repositories.patient_repository import PatientRepository')
                content = '\n'.join(lines)
            
            # Replace function calls
            content = content.replace('checar_paciente_existe(', 'PatientRepository().check_patient_exists(')
            changes_made.append("checar_paciente_existe → PatientRepository().check_patient_exists")
        
        if 'gerar_lista_meds_ids(' in content:
            # Add import if not present
            if 'MedicationRepository' not in content:
                lines = content.split('\n')
                # Find where to insert
                for i, line in enumerate(lines):
                    if 'from processos.repositories.patient_repository' in line:
                        lines.insert(i + 1, 'from processos.repositories.medication_repository import MedicationRepository')
                        break
                content = '\n'.join(lines)
            
            content = content.replace('gerar_lista_meds_ids(', 'MedicationRepository().extract_medication_ids(')
            changes_made.append("gerar_lista_meds_ids → MedicationRepository().extract_medication_ids")
        
        if 'listar_med(' in content:
            # Ensure MedicationRepository import
            if 'MedicationRepository' not in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'from processos.repositories.patient_repository' in line:
                        lines.insert(i + 1, 'from processos.repositories.medication_repository import MedicationRepository')
                        break
                content = '\n'.join(lines)
            
            content = content.replace('listar_med(', 'MedicationRepository().list_medications_by_cid(')
            changes_made.append("listar_med → MedicationRepository().list_medications_by_cid")
        
        # Update test method names
        if 'def test_checar_paciente_existe(' in content:
            content = content.replace('def test_checar_paciente_existe(', 'def test_check_patient_exists(')
            changes_made.append("Test method: test_checar_paciente_existe → test_check_patient_exists")
        
        if 'def test_gerar_lista_meds_ids(' in content:
            content = content.replace('def test_gerar_lista_meds_ids(', 'def test_extract_medication_ids(')
            changes_made.append("Test method: test_gerar_lista_meds_ids → test_extract_medication_ids")
        
        if 'def test_listar_med(' in content:
            content = content.replace('def test_listar_med(', 'def test_list_medications_by_cid(')
            changes_made.append("Test method: test_listar_med → test_list_medications_by_cid")
        
        # Write changes
        if changes_made:
            # Create backup
            backup_path = f"{tests_file.path}.rope_backup"
            with open(backup_path, 'w') as backup:
                backup.write(tests_file.read())
            print(f"✅ Backup created: {backup_path}")
            
            # Write updated content
            tests_file.write(content)
            
            print("✅ Changes made:")
            for change in changes_made:
                print(f"   • {change}")
        else:
            print("ℹ️  No changes needed")
        
        print("\n🎉 Refactoring complete!")
        print("📋 Verification steps:")
        print("   1. python manage.py shell -c 'from processos.forms import NovoProcesso'")
        print("   2. python manage.py test processos.tests.PatientRepositoryTest")
        
    finally:
        project.close()

if __name__ == "__main__":
    main()
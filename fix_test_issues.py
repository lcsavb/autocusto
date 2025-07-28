#!/usr/bin/env python
"""
Script to fix common test issues across the codebase.
Fixes:
1. CNS clinic length issues (must be 7 chars, not 13)
2. Missing required fields (dados_condicionais, incapaz)
3. Invalid CPF values
4. Import errors for moved/renamed modules
"""

import os
import re
import sys


def fix_cns_clinica_length(content):
    """Fix CNS clinica values that are too long (must be 7 chars)."""
    # Common patterns of invalid CNS values in tests
    replacements = [
        (r"cns_clinica['\"]?\s*[:=]\s*['\"]1234567890123['\"]", 'cns_clinica="1234567"'),
        (r"'cns_clinica':\s*'1234567890123'", "'cns_clinica': '1234567'"),
        (r'"cns_clinica":\s*"1234567890123"', '"cns_clinica": "1234567"'),
        (r"cns_clinica\s*=\s*['\"]1234567890123['\"]", 'cns_clinica="1234567"'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    return content


def fix_missing_required_fields(content):
    """Add missing required fields to model creation."""
    # Fix Processo creation without dados_condicionais
    processo_pattern = r'Processo\.objects\.create\(((?:[^(){}]|\([^)]*\))*)\)'
    
    def add_dados_condicionais(match):
        args = match.group(1)
        if 'dados_condicionais' not in args:
            # Add dados_condicionais to the arguments
            if args.strip().endswith(','):
                return f'Processo.objects.create({args}\n            dados_condicionais={{}},\n        )'
            else:
                return f'Processo.objects.create({args},\n            dados_condicionais={{}}\n        )'
        return match.group(0)
    
    content = re.sub(processo_pattern, add_dados_condicionais, content, flags=re.MULTILINE | re.DOTALL)
    
    # Fix Paciente/PatienteVersion creation without incapaz field
    paciente_patterns = [
        r'Paciente\.objects\.create\(((?:[^(){}]|\([^)]*\))*)\)',
        r'PacienteVersion\.objects\.create\(((?:[^(){}]|\([^)]*\))*)\)'
    ]
    
    def add_incapaz(match):
        args = match.group(1)
        if 'incapaz' not in args:
            # Add incapaz=False to the arguments
            if args.strip().endswith(','):
                return match.group(0).replace(
                    'objects.create(',
                    'objects.create(\n            incapaz=False,'
                )
            else:
                return match.group(0).replace(')', ',\n            incapaz=False\n        )')
        return match.group(0)
    
    for pattern in paciente_patterns:
        content = re.sub(pattern, add_incapaz, content, flags=re.MULTILINE | re.DOTALL)
    
    return content


def fix_import_errors(content):
    """Fix import errors for moved/renamed modules."""
    replacements = [
        # Fix manejo_pdfs_memory import
        (r'from processos\.manejo_pdfs_memory import', 'from processos.services.pdf_operations import'),
        # Fix prescription_database_service import
        (r'from processos\.services\.prescription_database_service import', 'from processos.services.prescription.workflow_service import'),
        # Fix _get_initial_data import
        (r'from processos\.views import _get_initial_data', 'from processos.services.view_services import PrescriptionViewSetupService'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    return content


def fix_model_field_errors(content):
    """Fix model field errors (unexpected keyword arguments)."""
    # Fix Medico creation with 'usuario' field
    medico_pattern = r'Medico\.objects\.create\(((?:[^(){}]|\([^)]*\))*usuario[^,)]*,?[^)]*)\)'
    
    def remove_usuario_field(match):
        args = match.group(1)
        # Remove usuario field from arguments
        args = re.sub(r',?\s*usuario\s*=\s*[^,)]+,?', '', args)
        return f'Medico.objects.create({args})'
    
    content = re.sub(medico_pattern, remove_usuario_field, content, flags=re.MULTILINE | re.DOTALL)
    
    # Fix ClinicaVersion with unexpected fields
    clinica_version_fields = ['cns_clinica', 'uf', 'email', 'telefone']
    for field in clinica_version_fields:
        pattern = rf'ClinicaVersion\.objects\.create\(((?:[^(){{}}]|\([^)]*\))*{field}[^,)]*,?[^)]*)\)'
        
        def remove_field(match):
            args = match.group(1)
            args = re.sub(rf',?\s*{field}\s*=\s*[^,)]+,?', '', args)
            return f'ClinicaVersion.objects.create({args})'
        
        content = re.sub(pattern, remove_field, content, flags=re.MULTILINE | re.DOTALL)
    
    return content


def fix_cpf_values(content):
    """Replace invalid CPF values with valid ones."""
    # Common invalid CPF patterns in tests
    invalid_cpfs = [
        r"'72834565031'",
        r'"72834565031"',
        r"'123\.456\.789-00'",
        r'"123\.456\.789-00"',
        r"'12345678901'",
        r'"12345678901"',
    ]
    
    # Use the fixed valid CPFs from test_data_fixtures
    valid_cpfs = ["11144477735", "22255588846", "33366699957"]
    cpf_index = 0
    
    for invalid_pattern in invalid_cpfs:
        if re.search(invalid_pattern, content):
            valid_cpf = valid_cpfs[cpf_index % len(valid_cpfs)]
            content = re.sub(invalid_pattern, f'"{valid_cpf}"', content)
            cpf_index += 1
    
    return content


def process_file(filepath):
    """Process a single test file to fix common issues."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all fixes
        content = fix_cns_clinica_length(content)
        content = fix_missing_required_fields(content)
        content = fix_import_errors(content)
        content = fix_model_field_errors(content)
        content = fix_cpf_values(content)
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main():
    """Main function to process all test files."""
    test_dirs = [
        'tests/integration',
        'tests/unit',
        'tests'
    ]
    
    fixed_count = 0
    total_count = 0
    
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue
            
        for root, dirs, files in os.walk(test_dir):
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    total_count += 1
                    if process_file(filepath):
                        fixed_count += 1
    
    print(f"\nProcessed {total_count} test files")
    print(f"Fixed {fixed_count} files")
    
    # Also add import to __init__.py files if needed
    init_file = 'tests/__init__.py'
    if os.path.exists(init_file):
        with open(init_file, 'r') as f:
            content = f.read()
        
        if 'test_data_fixtures' not in content:
            with open(init_file, 'a') as f:
                f.write('\n# Import test fixtures for easy access\nfrom .test_data_fixtures import *\n')
            print(f"Added test_data_fixtures import to {init_file}")


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
PDF Form Field Extractor and Diagnostic Tool for pypdftk
This script helps diagnose why PDF form fields aren't being filled correctly.
"""

import subprocess
import json
import sys
from pathlib import Path

def extract_pdf_fields(pdf_path):
    """Extract field names and properties from PDF using pdftk"""
    try:
        # Use pdftk to dump form data
        result = subprocess.run([
            'pdftk', pdf_path, 'dump_data_fields'
        ], capture_output=True, text=True, check=True)
        
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running pdftk: {e}")
        return None
    except FileNotFoundError:
        print("pdftk not found. Please install pdftk first.")
        return None

def parse_pdftk_output(output):
    """Parse pdftk dump_data_fields output into structured data"""
    fields = []
    current_field = {}
    
    for line in output.strip().split('\n'):
        if line.startswith('---'):
            if current_field:
                fields.append(current_field)
                current_field = {}
        elif ':' in line:
            key, value = line.split(':', 1)
            current_field[key.strip()] = value.strip()
    
    if current_field:
        fields.append(current_field)
    
    return fields

def compare_fields(pdf_fields, json_config):
    """Compare PDF fields with JSON configuration"""
    # Extract field names from JSON
    json_field_names = set(field['name'] for field in json_config['fields'])
    
    # Extract field names from PDF
    pdf_field_names = set(field.get('FieldName', '') for field in pdf_fields if field.get('FieldName'))
    
    # Find mismatches
    missing_in_pdf = json_field_names - pdf_field_names
    missing_in_json = pdf_field_names - json_field_names
    matching_fields = json_field_names & pdf_field_names
    
    return {
        'missing_in_pdf': missing_in_pdf,
        'missing_in_json': missing_in_json,
        'matching_fields': matching_fields,
        'pdf_field_details': pdf_fields
    }

def generate_mapping_suggestions(pdf_fields, json_config):
    """Generate suggestions for field name mappings"""
    suggestions = []
    
    json_fields = {field['name']: field for field in json_config['fields']}
    
    for pdf_field in pdf_fields:
        pdf_name = pdf_field.get('FieldName', '')
        pdf_type = pdf_field.get('FieldType', '')
        
        # Try to find similar JSON fields
        for json_name, json_field in json_fields.items():
            if pdf_name.lower() in json_name.lower() or json_name.lower() in pdf_name.lower():
                suggestions.append({
                    'pdf_field': pdf_name,
                    'pdf_type': pdf_type,
                    'suggested_json_field': json_name,
                    'json_type': json_field['type'],
                    'confidence': 'high' if pdf_name.lower() == json_name.lower() else 'medium'
                })
    
    return suggestions

def main():
    if len(sys.argv) != 3:
        print("Usage: python pdf_field_extractor.py <pdf_file> <json_config_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    json_path = sys.argv[2]
    
    # Check if files exist
    if not Path(pdf_path).exists():
        print(f"PDF file not found: {pdf_path}")
        sys.exit(1)
    
    if not Path(json_path).exists():
        print(f"JSON file not found: {json_path}")
        sys.exit(1)
    
    # Extract PDF fields
    print("Extracting PDF form fields...")
    pdftk_output = extract_pdf_fields(pdf_path)
    
    if not pdftk_output:
        print("Failed to extract PDF fields")
        sys.exit(1)
    
    pdf_fields = parse_pdftk_output(pdftk_output)
    
    # Load JSON configuration
    with open(json_path, 'r', encoding='utf-8') as f:
        json_config = json.load(f)
    
    # Compare fields
    comparison = compare_fields(pdf_fields, json_config)
    
    # Print results
    print("\n" + "="*60)
    print("PDF FIELD ANALYSIS REPORT")
    print("="*60)
    
    print(f"\nPDF Fields Found: {len(pdf_fields)}")
    print(f"JSON Fields Defined: {len(json_config['fields'])}")
    print(f"Matching Fields: {len(comparison['matching_fields'])}")
    
    print("\n" + "-"*40)
    print("PDF FORM FIELDS:")
    print("-"*40)
    for i, field in enumerate(pdf_fields, 1):
        print(f"{i:2d}. Name: {field.get('FieldName', 'N/A')}")
        print(f"    Type: {field.get('FieldType', 'N/A')}")
        print(f"    State: {field.get('FieldStateOption', 'N/A')}")
        if 'FieldValue' in field:
            print(f"    Value: {field['FieldValue']}")
        print()
    
    print("\n" + "-"*40)
    print("FIELD MATCHING ANALYSIS:")
    print("-"*40)
    
    if comparison['matching_fields']:
        print("✅ MATCHING FIELDS:")
        for field in sorted(comparison['matching_fields']):
            print(f"  - {field}")
    
    if comparison['missing_in_pdf']:
        print("\n❌ JSON FIELDS NOT FOUND IN PDF:")
        for field in sorted(comparison['missing_in_pdf']):
            print(f"  - {field}")
    
    if comparison['missing_in_json']:
        print("\n⚠️  PDF FIELDS NOT DEFINED IN JSON:")
        for field in sorted(comparison['missing_in_json']):
            print(f"  - {field}")
    
    # Generate mapping suggestions
    suggestions = generate_mapping_suggestions(pdf_fields, json_config)
    
    if suggestions:
        print("\n" + "-"*40)
        print("MAPPING SUGGESTIONS:")
        print("-"*40)
        for suggestion in suggestions:
            print(f"PDF: '{suggestion['pdf_field']}' ({suggestion['pdf_type']})")
            print(f"  → JSON: '{suggestion['suggested_json_field']}' ({suggestion['json_type']})")
            print(f"  Confidence: {suggestion['confidence']}")
            print()

if __name__ == "__main__":
    main()

# Alternative simple field extraction function for interactive use
def quick_extract_fields(pdf_path):
    """Quick field extraction for debugging"""
    try:
        result = subprocess.run([
            'pdftk', pdf_path, 'dump_data_fields'
        ], capture_output=True, text=True, check=True)
        
        print("Raw pdftk output:")
        print("-" * 40)
        print(result.stdout)
        
        fields = parse_pdftk_output(result.stdout)
        
        print("\nParsed fields:")
        print("-" * 40)
        for i, field in enumerate(fields, 1):
            print(f"{i}. {field.get('FieldName', 'N/A')} ({field.get('FieldType', 'N/A')})")
        
        return fields
    except Exception as e:
        print(f"Error: {e}")
        return []
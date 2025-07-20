# -*- coding: utf-8 -*-
"""
Simple management command to configure Multiple Sclerosis protocol
with conditional fields for data-driven PDF generation.

Usage:
    python manage.py configure_ms_protocol
"""

import json
from django.core.management.base import BaseCommand, CommandError
from processos.models import Protocolo, Doenca


class Command(BaseCommand):
    help = 'Configure Multiple Sclerosis protocol for data-driven PDF generation'
    
    def handle(self, *args, **options):
        # Find MS protocol
        ms_protocol = self.find_ms_protocol()
        if not ms_protocol:
            raise CommandError('Multiple Sclerosis protocol not found')
        
        # Show current state
        self.show_current_state(ms_protocol)
        
        # Update configuration
        self.update_ms_configuration(ms_protocol)
        
        # Show final state
        self.show_final_state(ms_protocol)
    
    def find_ms_protocol(self):
        """Find Multiple Sclerosis protocol"""
        # Try by protocol name first
        protocol = Protocolo.objects.filter(nome='esclerose_multipla').first()
        if protocol:
            return protocol
        
        # Try by disease CID (G35 is Multiple Sclerosis)
        doenca = Doenca.objects.filter(cid__icontains='G35').first()
        if doenca and doenca.protocolo:
            return doenca.protocolo
            
        return None
    
    def show_current_state(self, protocol):
        """Display current protocol state"""
        self.stdout.write(self.style.SUCCESS(f'\n=== BEFORE ==='))
        self.stdout.write(f'Protocol: {protocol.nome} (ID: {protocol.id})')
        
        current_data = protocol.dados_condicionais
        if current_data:
            self.stdout.write('Current dados_condicionais:')
            self.stdout.write(json.dumps(current_data, indent=2, ensure_ascii=False))
        else:
            self.stdout.write('dados_condicionais: NULL')
    
    def update_ms_configuration(self, protocol):
        """Update MS protocol with new configuration"""
        # Preserve existing data
        current_data = protocol.dados_condicionais or {}
        
        # Add new configuration
        current_data["fields"] = [
            {
                "name": "opt_edss",
                "label": "EDSS", 
                "type": "choice",
                "initial": "0",
                "choices": [
                    ("0", "0"), ("0,5", "0,5"), ("1", "1"), ("1,5", "1,5"),
                    ("2", "2"), ("2,5", "2,5"), ("3", "3"), ("3,5", "3,5"), 
                    ("4", "4"), ("4,5", "4,5"), ("5", "5"), ("5,5", "5,5"),
                    ("6", "6"), ("6.5", "6.5"), ("7", "7"), ("7,5", "7,5"),
                    ("8", "8"), ("8,5", "8,5"), ("9", "9"), ("9,5", "9,5"),
                    ("10", "10")
                ],
                "widget_class": "custom-select"
            }
        ]
        
        current_data["disease_files"] = [
            "pdfs_base/edss_modelo.pdf"
        ]
        
        current_data["medications"] = {
            "fingolimode": {
                "files": ["monitoramento_fingolimode_modelo.pdf"],
                "consent_name": "fingolimode"
            },
            "natalizumabe": {
                "files": ["exames_nata_modelo.pdf"], 
                "consent_name": "natalizumabe"
            },
            "fumarato": {
                "files": [],
                "consent_name": "dimetila"
            },
            "betainterferon": {
                "files": [],
                "consent_name": "betainterferona1a"
            },
            "glatiramer": {
                "files": [],
                "consent_name": "glatiramer"
            },
            "teriflunomida": {
                "files": [],
                "consent_name": "teriflunomida"
            },
            "azatioprina": {
                "files": [],
                "consent_name": "azatioprina"
            }
        }
        
        # Save updated data
        protocol.dados_condicionais = current_data
        protocol.save()
        
        self.stdout.write(self.style.SUCCESS('✓ Protocol updated successfully'))
    
    def show_final_state(self, protocol):
        """Display final protocol state"""
        self.stdout.write(self.style.SUCCESS(f'\n=== AFTER ==='))
        self.stdout.write('Final dados_condicionais:')
        self.stdout.write(json.dumps(protocol.dados_condicionais, indent=2, ensure_ascii=False))
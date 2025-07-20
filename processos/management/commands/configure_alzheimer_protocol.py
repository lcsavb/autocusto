"""
Management command to configure Alzheimer's Disease protocol with data-driven approach.

This command migrates Alzheimer's disease from hardcoded logic in seletor_campos() 
to the new data-driven architecture using the dados_condicionais JSONField.

The Alzheimer's protocol includes:
- MEEM (Mini Mental State Examination) with 15 cognitive assessment fields
- CDR (Clinical Dementia Rating) scale
- Simple medication list (donepezil, rivastigmine, galantamine, memantine)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from processos.models import Protocolo
import json


class Command(BaseCommand):
    help = 'Configure Alzheimer\'s Disease protocol with data-driven conditional fields'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        try:
            with transaction.atomic():
                # Get the Alzheimer's protocol
                protocolo = Protocolo.objects.get(nome='doenca_de_alzheimer')
                
                # Define the data-driven configuration
                # Based on legacy seletor_campos() logic for doenca_de_alzheimer
                alzheimer_config = {
                    # MEEM (Mini Mental State Examination) + CDR fields
                    "fields": [
                        # Temporal Orientation (OT)
                        {
                            "name": "opt_ot1",
                            "type": "choice", 
                            "label": "Hora",
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "1",
                            "required": True,
                            "help_text": "Orientação temporal - Hora (0-1 ponto)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_ot2",
                            "type": "choice",
                            "label": "Dia da semana", 
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "0",
                            "required": True,
                            "help_text": "Orientação temporal - Dia da semana (0-1 ponto)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_ot3",
                            "type": "choice",
                            "label": "Dia do mês",
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "1", 
                            "required": True,
                            "help_text": "Orientação temporal - Dia do mês (0-1 ponto)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_ot4",
                            "type": "choice",
                            "label": "Mês",
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "1",
                            "required": True,
                            "help_text": "Orientação temporal - Mês (0-1 ponto)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_ot5", 
                            "type": "choice",
                            "label": "Ano",
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "0",
                            "required": True,
                            "help_text": "Orientação temporal - Ano (0-1 ponto)",
                            "widget_class": "custom-select"
                        },
                        
                        # Spatial Orientation (OE)
                        {
                            "name": "opt_oe1",
                            "type": "choice",
                            "label": "Local",
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "1",
                            "required": True,
                            "help_text": "Orientação espacial - Local (0-1 ponto)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_oe2",
                            "type": "choice",
                            "label": "Bairro",
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "0",
                            "required": True,
                            "help_text": "Orientação espacial - Bairro (0-1 ponto)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_oe3",
                            "type": "choice",
                            "label": "Cidade",
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "1",
                            "required": True,
                            "help_text": "Orientação espacial - Cidade (0-1 ponto)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_oe4",
                            "type": "choice",
                            "label": "Estado",
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "1",
                            "required": True,
                            "help_text": "Orientação espacial - Estado (0-1 ponto)",
                            "widget_class": "custom-select"
                        },
                        
                        # Cognitive Assessment
                        {
                            "name": "opt_mi",
                            "type": "choice",
                            "label": "Memória imediata",
                            "choices": [["0", "0"], ["1", "1"], ["2", "2"], ["3", "3"]],
                            "initial": "1",
                            "required": True,
                            "help_text": "Memória imediata (0-3 pontos)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_ac",
                            "type": "choice",
                            "label": "Atenção e cálculo",
                            "choices": [["0", "0"], ["1", "1"], ["2", "2"], ["3", "3"], ["4", "4"], ["5", "5"]],
                            "initial": "2",
                            "required": True,
                            "help_text": "Atenção e cálculo (0-5 pontos)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_me",
                            "type": "choice",
                            "label": "Memória de Evocação",
                            "choices": [["0", "0"], ["1", "1"], ["2", "2"], ["3", "3"]],
                            "initial": "0",
                            "required": True,
                            "help_text": "Memória de evocação (0-3 pontos)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_n",
                            "type": "choice",
                            "label": "Nomeação",
                            "choices": [["0", "0"], ["1", "1"], ["2", "2"]],
                            "initial": "1",
                            "required": True,
                            "help_text": "Nomeação (0-2 pontos)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_r",
                            "type": "choice",
                            "label": "Repetição",
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "1",
                            "required": True,
                            "help_text": "Repetição (0-1 ponto)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_ce",
                            "type": "choice",
                            "label": "Comando escrito",
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "1",
                            "required": True,
                            "help_text": "Comando escrito (0-1 ponto)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_cv",
                            "type": "choice",
                            "label": "Comando verbal",
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "1",
                            "required": True,
                            "help_text": "Comando verbal (0-1 ponto)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_f",
                            "type": "choice",
                            "label": "Escrever frase",
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "1",
                            "required": True,
                            "help_text": "Escrever frase (0-1 ponto)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_d",
                            "type": "choice",
                            "label": "Desenho",
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "1",
                            "required": True,
                            "help_text": "Desenho (0-1 ponto)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_total",
                            "type": "choice",
                            "label": "Total MEEM",
                            "choices": [[str(i), str(i)] for i in range(0, 31)],  # 0-30
                            "initial": "16",
                            "required": True,
                            "help_text": "Total MEEM (0-30 pontos)",
                            "widget_class": "custom-select"
                        },
                        {
                            "name": "opt_cdr",
                            "type": "choice",
                            "label": "CDR",
                            "choices": [["0", "0"], ["1", "1"]],
                            "initial": "1",
                            "required": True,
                            "help_text": "Clinical Dementia Rating (0-1)",
                            "widget_class": "custom-select"
                        }
                    ],
                    
                    # Disease-specific assessment PDFs (MEEM and CDR scales)
                    "disease_files": [
                        "pdfs_base/cdr_modelo.pdf",
                        "pdfs_base/meem_modelo.pdf"
                    ],
                    
                    # Medications - simple list using universal consent only
                    # Based on analysis: Alzheimer's uses selecionar_med_consentimento() 
                    # with no medication-specific monitoring forms
                    "medications": {
                        "donepezil": {
                            "files": [],  # No medication-specific PDFs
                            "consent_name": "donepezil"
                        },
                        "rivastigmine": {
                            "files": [],  # No medication-specific PDFs
                            "consent_name": "rivastigmine"
                        },
                        "galantamine": {
                            "files": [],  # No medication-specific PDFs
                            "consent_name": "galantamine"
                        },
                        "memantine": {
                            "files": [],  # No medication-specific PDFs
                            "consent_name": "memantine"
                        }
                    }
                }
                
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING('DRY RUN - No changes will be made')
                    )
                    self.stdout.write(f'Would configure protocol: {protocolo.nome}')
                    self.stdout.write(f'Configuration: {json.dumps(alzheimer_config, indent=2, ensure_ascii=False)}')
                    return
                
                # Apply the configuration
                protocolo.dados_condicionais = alzheimer_config
                protocolo.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully configured Alzheimer\'s Disease protocol with data-driven approach'
                    )
                )
                self.stdout.write(f'Protocol: {protocolo.nome}')
                self.stdout.write(f'Conditional fields: {len(alzheimer_config["fields"])}')
                self.stdout.write(f'Disease files: {len(alzheimer_config["disease_files"])}')
                self.stdout.write(f'Medications: {len(alzheimer_config["medications"])}')
                
        except Protocolo.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Alzheimer\'s Disease protocol not found')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error configuring protocol: {str(e)}')
            )
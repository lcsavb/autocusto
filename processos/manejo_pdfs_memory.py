# -*- coding: utf-8 -*-
"""
Memory-based PDF generation using pdftk with subprocess.
Avoids disk I/O by streaming PDFs directly to memory.
Properly handles UTF-8 encoding for Portuguese characters.
"""

import os
import time
import logging
from datetime import timedelta
from io import BytesIO

import pypdftk
from django.conf import settings
from django.http import HttpResponse

from processos.models import Protocolo, Medicamento
from processos.pdf_strategies import DataDrivenStrategy

pdf_logger = logging.getLogger('processos.pdf')
logger = logging.getLogger('processos')


# fill forms in memory
def preencher_formularios_memory(lista_pdfs, dados_finais):
    """
    Fills PDF forms in memory using pypdftk with tmpfs (RAM disk) approach.
    
    This "cheats" pypdftk by using /dev/shm (tmpfs - RAM filesystem) so that
    pypdftk thinks it's writing to disk but it's actually writing to memory.
    This preserves UTF-8 handling while avoiding actual disk I/O.
    
    Args:
        lista_pdfs (list): List of PDF template paths
        dados_finais (dict): Form data dictionary
        
    Returns:
        list: List of BytesIO objects containing filled PDFs
    """
    
    filled_pdfs = []
    
    for i, pdf_path in enumerate(lista_pdfs):
        if not os.path.exists(pdf_path):
            continue
            
        try:
            # CHEAT: Use /dev/shm (tmpfs - RAM filesystem) for pypdftk output
            # This way pypdftk thinks it's writing to disk, but it's actually RAM
            
            # Create a unique temporary file name in /dev/shm (RAM filesystem)
            ram_pdf_path = f"/dev/shm/pdf_temp_{os.getpid()}_{i}_{int(time.time())}.pdf"
            
            # Use pypdftk normally - it will write to RAM (tmpfs)
            filled_pdf_path = pypdftk.fill_form(pdf_path, dados_finais, ram_pdf_path)
            
            # Check if PDF was created in RAM
            if filled_pdf_path and os.path.exists(filled_pdf_path):
                # Read the PDF from RAM
                with open(filled_pdf_path, 'rb') as pdf_file:
                    pdf_bytes = pdf_file.read()
                
                # Clean up RAM file immediately
                os.unlink(filled_pdf_path)
                
                # Verify PDF data
                if pdf_bytes and pdf_bytes.startswith(b'%PDF-'):
                    pdf_io = BytesIO(pdf_bytes)
                    filled_pdfs.append(pdf_io)
                else:
                    continue
            else:
                continue
                
        except Exception as e:
            continue
    
    return filled_pdfs


## TO REMOVE
def generate_fdf_content(data_dict):
    """
    Generate FDF (Forms Data Format) content for PDF form filling.
    Properly handles UTF-8 characters for Portuguese text.
    
    Args:
        data_dict (dict): Form field data
        
    Returns:
        str: FDF content with proper UTF-8 encoding
    """
    fdf_content = "%FDF-1.2\n"
    fdf_content += "1 0 obj\n"
    fdf_content += "<<\n"
    fdf_content += "/FDF\n"
    fdf_content += "<<\n"
    fdf_content += "/Fields [\n"
    
    for field_name, field_value in data_dict.items():
        if field_value is not None:
            # Convert to string and handle UTF-8 properly
            value_str = str(field_value)
            
            
            # Escape special characters for PDF/FDF format
            # Handle parentheses, backslashes, and other special chars
            escaped_value = (value_str
                           .replace('\\', '\\\\')  # Escape backslashes first
                           .replace('(', '\\(')    # Escape opening parenthesis
                           .replace(')', '\\)')    # Escape closing parenthesis
                           .replace('\r', '\\r')   # Escape carriage returns
                           .replace('\n', '\\n')   # Escape line feeds
                           .replace('\t', '\\t'))  # Escape tabs
            
            fdf_content += f"<<\n"
            fdf_content += f"/T ({field_name})\n"
            fdf_content += f"/V ({escaped_value})\n"
            fdf_content += f">>\n"
    
    fdf_content += "]\n"
    fdf_content += ">>\n"
    fdf_content += ">>\n"
    fdf_content += "endobj\n"
    fdf_content += "trailer\n"
    fdf_content += "<<\n"
    fdf_content += "/Root 1 0 R\n"
    fdf_content += ">>\n"
    fdf_content += "%%EOF\n"
    
    return fdf_content


# concatenate pdfs in memory
def concatenar_pdfs_memory(pdf_ios):
    """
    Concatenate multiple PDFs stored in BytesIO objects using pypdftk with tmpfs approach.
    
    Args:
        pdf_ios (list): List of BytesIO objects containing PDFs
        
    Returns:
        bytes: Concatenated PDF bytes
    """
    if not pdf_ios:
        return None
    
    if len(pdf_ios) == 1:
        # Single PDF, return as is
        pdf_ios[0].seek(0)
        result = pdf_ios[0].read()
        return result
    
    try:
        # Create temporary files in /dev/shm (RAM filesystem) for pypdftk input
        temp_files = []
        for i, pdf_io in enumerate(pdf_ios):
            ram_file_path = f"/dev/shm/concat_temp_{os.getpid()}_{i}_{int(time.time())}.pdf"
            
            pdf_io.seek(0)
            pdf_data = pdf_io.read()
            
            with open(ram_file_path, 'wb') as ram_file:
                ram_file.write(pdf_data)
            
            temp_files.append(ram_file_path)
            print(f"DEBUG: Created RAM temp file {i+1}: {ram_file_path} ({len(pdf_data)} bytes)")
        
        # Create output file in RAM as well
        output_ram_path = f"/dev/shm/concat_output_{os.getpid()}_{int(time.time())}.pdf"
        
        print(f"DEBUG: Using pypdftk.concat with RAM files")
        print(f"DEBUG: Input files: {temp_files}")
        print(f"DEBUG: Output file: {output_ram_path}")
        
        # Use pypdftk.concat to maintain UTF-8 handling consistency
        concat_start = time.time()
        concatenated_pdf = pypdftk.concat(temp_files, output_ram_path)
        concat_end = time.time()
        
        print(f"DEBUG: pypdftk.concat completed in {concat_end - concat_start:.3f}s")
        print(f"DEBUG: pypdftk.concat returned: {concatenated_pdf}")
        
        # Read concatenated PDF from RAM
        if concatenated_pdf and os.path.exists(concatenated_pdf):
            with open(concatenated_pdf, 'rb') as output_file:
                pdf_bytes = output_file.read()
            
            # Clean up output file from RAM
            os.unlink(concatenated_pdf)
        else:
            pdf_bytes = None
        
        # Clean up temp files from RAM
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except Exception as cleanup_error:
                pass
        
        return pdf_bytes
        
    except Exception as e:
        return None


# date formatting
def formatacao_data(dados):
    """
    Formats and calculates sequential dates for medical prescription forms.
    
    This function takes an initial date and generates 6 sequential dates
    spaced 30 days apart for medical prescription validity periods.
    Brazilian medical prescriptions typically require multiple follow-up dates.
    
    Args:
        dados (dict): Data dictionary containing date fields
                     Must contain 'data_1' as datetime object
    
    Side Effects:
        Modifies dados dictionary in-place, adding data_2 through data_6
        
    Critique:
    - Function modifies input dictionary in-place without clear indication
    - Hardcoded 30-day intervals may not suit all prescription types
    - Heavy debug logging in production code
    - No input validation for required 'data_1' field
    - Magic numbers (2, 6, 30) should be configurable constants
    
    Suggested Improvements:
    - Add input validation to ensure 'data_1' exists and is datetime
    - Make date intervals configurable per prescription type
    - Return new dictionary instead of modifying input
    - Remove debug print statements from production code
    - Add error handling for date calculation edge cases
    """
    print(f"\n--- FORMATACAO_DATA START ---")
    print(f"DEBUG: Input data_1: {dados.get('data_1', 'NOT_FOUND')} (type: {type(dados.get('data_1'))})")
    
    mes = 2
    dias = 30
    while mes <= 6:
        new_date = dados["data_1"] + timedelta(days=dias)
        formatted_date = new_date.strftime("%d/%m/%Y")
        dados[f"data_{mes}"] = formatted_date
        dias += 30
        mes += 1
    
    dados["data_1"] = dados["data_1"].strftime("%d/%m/%Y")


def ajustar_campo_18(dados_lme):
    """
    Adjusts field 18 of the LME form based on who filled the prescription.
    
    Field 18 refers to specific patient information fields in Brazilian LME 
    (Laudo para Solicitação, Avaliação e Autorização de Medicamentos) forms
    that are only required when the form is filled by medical personnel rather
    than the patient themselves. This includes sensitive data like CPF, phone
    numbers, and ethnicity information.
    
    Args:
        dados_lme (dict): LME form data dictionary containing prescription information
                         Must include 'preenchido_por' field indicating form completion context
    
    Side Effects:
        Modifies dados_lme dictionary in-place by removing patient data fields
        when form is not filled by doctor
        
    Critique:
    - Function modifies input dictionary without clear indication in name
    - Hardcoded field names reduce maintainability and localization support
    - No input validation for required 'preenchido_por' field
    - Business logic is embedded rather than configurable
    - Heavy debug logging suggests this was debugging code left in production
    
    Suggested Improvements:
    - Add input validation to ensure 'preenchido_por' field exists
    - Make field removal configurable via external configuration
    - Return modified dictionary instead of in-place modification
    - Add proper logging levels (INFO/DEBUG) instead of print statements
    - Consider using enum for 'preenchido_por' values instead of strings
    - Add documentation explaining Brazilian medical form regulations
    """
    preenchido_por = dados_lme.get("preenchido_por", "NOT_FOUND")
    
    if preenchido_por != "medico":
        print(f"DEBUG: Not filled by doctor, adjusting field 18...")
        
        fields_to_delete = ["cpf_paciente", "telefone1_paciente", "telefone2_paciente", "email_paciente"]
        for field in fields_to_delete:
            if field in dados_lme:
                del dados_lme[field]
        
        dados_lme["etnia"] = ""
        dados_lme["escolha_documento"] = ""


# pdf generator
class GeradorPDF:
    """
    Memory-based PDF generator that streams PDFs directly to browser.
    """
    
    def __init__(self, dados_lme_base, path_lme_base):
        self.dados_lme_base = dados_lme_base
        self.path_lme_base = path_lme_base
    
    def generico_stream(self, dados_lme_base, path_lme_base):
        """
        Generates comprehensive medical prescription PDFs entirely in memory and streams to browser.
        
        This method orchestrates the complete Brazilian medical prescription workflow by:
        1. Processing base LME (Authorization Request) form data
        2. Dynamically adding disease-specific and medication-specific PDFs using data-driven strategy
        3. Including conditional documents (consent forms, reports, exams) based on prescription context
        4. Generating final concatenated PDF entirely in memory using tmpfs approach
        5. Returning streaming HTTP response for immediate browser display
        
        The method implements complex Brazilian SUS (Sistema Único de Saúde) compliance requirements
        including proper document sequencing, medication consent forms, and examination requests.
        
        Args:
            dados_lme_base (dict): Base LME form data containing patient, doctor, and prescription info
                                  Required fields: cpf_paciente, cid, consentimento, relatorio, exames
            path_lme_base (str): Filesystem path to base LME PDF template
            
        Returns:
            HttpResponse: PDF response with proper headers for inline browser display
                         Content-Type: application/pdf
                         Content-Disposition: inline with descriptive filename
            
        Critique:
        - Extremely long method (100+ lines) that violates SRP and is hard to test
        - Mixes PDF generation logic with HTTP response handling
        - Heavy use of print debugging statements in production code
        - Complex nested try/catch blocks make error handling unclear
        - Hardcoded file paths and business logic reduce flexibility
        - No input validation for required dictionary fields
        - Strategy pattern implementation is mixed with legacy protocol handling
        
        Suggested Improvements:
        - Extract PDF building logic to separate PDFBuilder class
        - Create dedicated service classes for consent, report, and exam handling
        - Implement proper logging framework instead of print statements
        - Add comprehensive input validation with custom exceptions
        - Use dependency injection for file path configuration
        - Create separate HTTPResponseBuilder for streaming response creation
        - Add unit tests for each logical component
        - Consider implementing async processing for large PDF generation
        """
        cpf_paciente = dados_lme_base["cpf_paciente"]
        cid = dados_lme_base["cid"]
        nome_final_pdf = f"pdf_final_{cpf_paciente}_{cid}.pdf"
        primeira_vez = dados_lme_base["consentimento"]
        relatorio = dados_lme_base["relatorio"]
        exames = dados_lme_base["exames"]
        
        # Format dates
        formatacao_data(dados_lme_base)
        
        # Start with base LME template
        arquivos_base = [path_lme_base]
        
        # Get protocol info and initialize strategy
        try:
            protocolo = Protocolo.objects.get(doenca__cid=cid)
            
            # Initialize data-driven strategy
            strategy = DataDrivenStrategy(protocolo)
        except Protocolo.DoesNotExist:
            logger.error(f"Protocol not found for CID: {cid}")
            return HttpResponse("Protocol not found", status=404)
        
        # Add disease-specific PDFs using strategy
        try:
            disease_files = strategy.get_disease_specific_paths(dados_lme_base)
            arquivos_base.extend(disease_files)
        except Exception as e:
            pass
        
        # Add medication-specific PDFs using strategy
        try:
            medication_files = strategy.get_medication_specific_paths(dados_lme_base)
            arquivos_base.extend(medication_files)
        except Exception as e:
            pass
        
        # Add consent PDF if needed
        if primeira_vez == "True" or primeira_vez == True:
            try:
                id_med = dados_lme_base["id_med1"]
                consentimento_pdf = os.path.join(
                    settings.PATH_PDF_DIR, protocolo.nome, "consentimento.pdf"
                )
                if os.path.exists(consentimento_pdf):
                    medicamento = Medicamento.objects.get(id=id_med)
                    dados_lme_base["consentimento_medicamento"] = medicamento.nome
                    arquivos_base.append(consentimento_pdf)
            except Exception as e:
                pass
        
        # Add report PDF if needed
        if relatorio and str(relatorio).strip() and str(relatorio).strip().lower() != "false":
            if os.path.exists(settings.PATH_RELATORIO):
                arquivos_base.append(settings.PATH_RELATORIO)
        
        # Add exam PDF if needed
        if exames and str(exames).strip() and str(exames).strip().lower() != "false":
            if os.path.exists(settings.PATH_EXAMES):
                arquivos_base.append(settings.PATH_EXAMES)
        
        # Adjust field 18
        ajustar_campo_18(dados_lme_base)
        
        # Fill all PDFs in memory
        filled_pdfs = preencher_formularios_memory(arquivos_base, dados_lme_base)
        
        if not filled_pdfs:
            pdf_logger.error("No PDFs were filled during generation")
            return HttpResponse("PDF generation failed", status=500)
        
        # Concatenate PDFs in memory
        final_pdf_bytes = concatenar_pdfs_memory(filled_pdfs)
        
        if not final_pdf_bytes:
            pdf_logger.error("PDF concatenation failed")
            return HttpResponse("PDF concatenation failed", status=500)
        
        # Return HttpResponse with PDF bytes
        response = HttpResponse(
            final_pdf_bytes,
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'inline; filename="{nome_final_pdf}"'
        return response
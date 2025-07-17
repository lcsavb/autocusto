"""
Memory-based PDF generation using pdftk with subprocess.
Avoids disk I/O by streaming PDFs directly to memory.
"""

import os
import subprocess
import tempfile
from datetime import timedelta
from io import BytesIO

from django.conf import settings
from django.http import HttpResponse

from processos.models import Protocolo, Medicamento


def preencher_formularios_memory(lista_pdfs, dados_finais):
    """
    Fills PDF forms in memory using pdftk subprocess.
    
    Args:
        lista_pdfs (list): List of PDF template paths
        dados_finais (dict): Form data dictionary
        
    Returns:
        list: List of BytesIO objects containing filled PDFs
    """
    print(f"\n=== PREENCHER_FORMULARIOS_MEMORY START ===")
    print(f"DEBUG: Processing {len(lista_pdfs)} PDFs in memory")
    
    filled_pdfs = []
    
    for i, pdf_path in enumerate(lista_pdfs):
        print(f"\n--- Processing PDF {i+1}/{len(lista_pdfs)} ---")
        print(f"DEBUG: Template: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            print(f"ERROR: PDF template not found: {pdf_path}")
            continue
            
        try:
            # Create temporary FDF file for form data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.fdf', delete=False) as fdf_file:
                fdf_content = generate_fdf_content(dados_finais)
                fdf_file.write(fdf_content)
                fdf_path = fdf_file.name
            
            # Use pdftk to fill form and output to stdout
            cmd = [
                "pdftk",
                pdf_path,
                "fill_form",
                fdf_path,
                "output",
                "-",  # Output to stdout
                "flatten"  # Flatten the form
            ]
            
            print(f"DEBUG: Running command: {' '.join(cmd)}")
            
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            
            pdf_bytes = process.stdout
            print(f"DEBUG: Generated PDF bytes: {len(pdf_bytes)} bytes")
            
            # Store in BytesIO for later concatenation
            pdf_io = BytesIO(pdf_bytes)
            filled_pdfs.append(pdf_io)
            
            # Clean up temp FDF file
            os.unlink(fdf_path)
            
        except subprocess.CalledProcessError as e:
            print(f"ERROR: pdftk failed for {pdf_path}: {e.stderr.decode()}")
            continue
        except Exception as e:
            print(f"ERROR: Failed to process {pdf_path}: {e}")
            continue
    
    print(f"DEBUG: Successfully processed {len(filled_pdfs)} PDFs")
    print(f"=== PREENCHER_FORMULARIOS_MEMORY END ===\n")
    return filled_pdfs


def generate_fdf_content(data_dict):
    """
    Generate FDF (Forms Data Format) content for PDF form filling.
    
    Args:
        data_dict (dict): Form field data
        
    Returns:
        str: FDF content
    """
    fdf_content = "%FDF-1.2\n"
    fdf_content += "1 0 obj\n"
    fdf_content += "<<\n"
    fdf_content += "/FDF\n"
    fdf_content += "<<\n"
    fdf_content += "/Fields [\n"
    
    for field_name, field_value in data_dict.items():
        if field_value is not None:
            # Escape special characters in field values
            escaped_value = str(field_value).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
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


def concatenar_pdfs_memory(pdf_ios):
    """
    Concatenate multiple PDFs stored in BytesIO objects.
    
    Args:
        pdf_ios (list): List of BytesIO objects containing PDFs
        
    Returns:
        bytes: Concatenated PDF bytes
    """
    print(f"\n=== CONCATENAR_PDFS_MEMORY START ===")
    print(f"DEBUG: Concatenating {len(pdf_ios)} PDFs")
    
    if not pdf_ios:
        print("ERROR: No PDFs to concatenate")
        return None
    
    if len(pdf_ios) == 1:
        # Single PDF, return as is
        pdf_ios[0].seek(0)
        result = pdf_ios[0].read()
        print(f"DEBUG: Single PDF, returning {len(result)} bytes")
        return result
    
    try:
        # Create temporary files for pdftk input
        temp_files = []
        for i, pdf_io in enumerate(pdf_ios):
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            pdf_io.seek(0)
            temp_file.write(pdf_io.read())
            temp_file.close()
            temp_files.append(temp_file.name)
            print(f"DEBUG: Created temp file {i+1}: {temp_file.name}")
        
        # Build pdftk command
        cmd = ["pdftk"] + temp_files + ["cat", "output", "-"]
        
        print(f"DEBUG: Running concatenation command: {' '.join(cmd)}")
        
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        pdf_bytes = process.stdout
        print(f"DEBUG: Concatenated PDF bytes: {len(pdf_bytes)} bytes")
        
        # Clean up temp files
        for temp_file in temp_files:
            os.unlink(temp_file)
        
        print(f"=== CONCATENAR_PDFS_MEMORY END ===\n")
        return pdf_bytes
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: pdftk concatenation failed: {e.stderr.decode()}")
        return None
    except Exception as e:
        print(f"ERROR: Concatenation failed: {e}")
        return None


def formatacao_data(dados):
    """
    Format dates for PDF forms.
    
    Args:
        dados (dict): Data dictionary with date fields
    """
    print(f"\n--- FORMATACAO_DATA START ---")
    print(f"DEBUG: Input data_1: {dados.get('data_1', 'NOT_FOUND')} (type: {type(dados.get('data_1'))})")
    
    mes = 2
    dias = 30
    while mes <= 6:
        new_date = dados["data_1"] + timedelta(days=dias)
        formatted_date = new_date.strftime("%d/%m/%Y")
        dados[f"data_{mes}"] = formatted_date
        print(f"DEBUG: data_{mes} = {formatted_date}")
        dias += 30
        mes += 1
    
    original_date = dados["data_1"]
    dados["data_1"] = dados["data_1"].strftime("%d/%m/%Y")
    print(f"DEBUG: Formatted data_1 from {original_date} to {dados['data_1']}")
    print(f"--- FORMATACAO_DATA END ---\n")


def ajustar_campo_18(dados_lme):
    """
    Adjust field 18 of the LME form.
    
    Args:
        dados_lme (dict): LME form data
    """
    print(f"\n--- AJUSTAR_CAMPO_18 START ---")
    preenchido_por = dados_lme.get("preenchido_por", "NOT_FOUND")
    print(f"DEBUG: preenchido_por = {preenchido_por}")
    
    if preenchido_por != "medico":
        print(f"DEBUG: Not filled by doctor, adjusting field 18...")
        
        fields_to_delete = ["cpf_paciente", "telefone1_paciente", "telefone2_paciente", "email_paciente"]
        for field in fields_to_delete:
            if field in dados_lme:
                del dados_lme[field]
                print(f"DEBUG: Deleted field: {field}")
        
        dados_lme["etnia"] = ""
        dados_lme["escolha_documento"] = ""
        print(f"DEBUG: Set etnia and escolha_documento to empty")
    
    print(f"--- AJUSTAR_CAMPO_18 END ---\n")


class GeradorPDFMemory:
    """
    Memory-based PDF generator that streams PDFs directly to browser.
    """
    
    def __init__(self, dados_lme_base, path_lme_base):
        self.dados_lme_base = dados_lme_base
        self.path_lme_base = path_lme_base
    
    def generico_stream(self, dados_lme_base, path_lme_base):
        """
        Generate PDF entirely in memory and return HttpResponse for streaming.
        
        Args:
            dados_lme_base (dict): Base LME form data
            path_lme_base (str): Path to base LME template
            
        Returns:
            HttpResponse: PDF response ready for streaming
        """
        print(f"\n=== GERADOR_PDF_MEMORY.GENERICO_STREAM START ===")
        
        cpf_paciente = dados_lme_base["cpf_paciente"]
        cid = dados_lme_base["cid"]
        nome_final_pdf = f"pdf_final_{cpf_paciente}_{cid}.pdf"
        primeira_vez = dados_lme_base["consentimento"]
        relatorio = dados_lme_base["relatorio"]
        exames = dados_lme_base["exames"]
        
        print(f"DEBUG: Patient CPF: {cpf_paciente}")
        print(f"DEBUG: CID: {cid}")
        print(f"DEBUG: Final PDF name: {nome_final_pdf}")
        print(f"DEBUG: First time (consent): {primeira_vez}")
        print(f"DEBUG: Include report: {relatorio}")
        print(f"DEBUG: Include exams: {exames}")
        
        # Format dates
        formatacao_data(dados_lme_base)
        
        # Start with base LME template
        arquivos_base = [path_lme_base]
        
        # Get protocol info
        try:
            protocolo = Protocolo.objects.get(doenca__cid=cid)
            print(f"DEBUG: Found protocol: {protocolo.nome}")
        except Protocolo.DoesNotExist:
            print(f"ERROR: Protocol not found for CID: {cid}")
            return HttpResponse("Protocol not found", status=404)
        
        # Add conditional PDFs
        try:
            dir_pdfs_condicionais = os.path.join(
                settings.PATH_PDF_DIR, protocolo.nome, "pdfs_base/"
            )
            if os.path.exists(dir_pdfs_condicionais):
                import glob
                pdfs_condicionais = glob.glob(dir_pdfs_condicionais + "*.*")
                arquivos_base.extend(pdfs_condicionais)
                print(f"DEBUG: Added {len(pdfs_condicionais)} conditional PDFs")
        except Exception as e:
            print(f"ERROR: Failed to add conditional PDFs: {e}")
        
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
                    print(f"DEBUG: Added consent PDF")
            except Exception as e:
                print(f"ERROR: Failed to add consent PDF: {e}")
        
        # Add report PDF if needed
        if relatorio and str(relatorio).strip() and str(relatorio).strip().lower() != "false":
            if os.path.exists(settings.PATH_RELATORIO):
                arquivos_base.append(settings.PATH_RELATORIO)
                print(f"DEBUG: Added report PDF")
        
        # Add exam PDF if needed
        if exames and str(exames).strip() and str(exames).strip().lower() != "false":
            if os.path.exists(settings.PATH_EXAMES):
                arquivos_base.append(settings.PATH_EXAMES)
                print(f"DEBUG: Added exam PDF")
        
        # Adjust field 18
        ajustar_campo_18(dados_lme_base)
        
        print(f"DEBUG: Processing {len(arquivos_base)} PDF templates")
        
        # Fill all PDFs in memory
        filled_pdfs = preencher_formularios_memory(arquivos_base, dados_lme_base)
        
        if not filled_pdfs:
            print(f"ERROR: No PDFs were filled")
            return HttpResponse("PDF generation failed", status=500)
        
        # Concatenate PDFs in memory
        final_pdf_bytes = concatenar_pdfs_memory(filled_pdfs)
        
        if not final_pdf_bytes:
            print(f"ERROR: PDF concatenation failed")
            return HttpResponse("PDF concatenation failed", status=500)
        
        print(f"DEBUG: Generated final PDF: {len(final_pdf_bytes)} bytes")
        print(f"=== GERADOR_PDF_MEMORY.GENERICO_STREAM END ===\n")
        
        # Return HttpResponse with PDF bytes
        response = HttpResponse(
            final_pdf_bytes,
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'inline; filename="{nome_final_pdf}"'
        return response
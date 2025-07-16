import os
import glob
import random
from datetime import timedelta

import pypdftk
from django.conf import settings

from processos.models import Protocolo, Medicamento

PATH_EXAMES = settings.PATH_EXAMES

# English: fill_forms
def preencher_formularios(lista_pdfs, dados_finais):
    """Fills individual PDFs and generates intermediate files with random names.

    Critique:
    - The function has a lot of debugging prints, which should be removed
      in a production environment. Using Python's `logging` module would be
      a better way to handle debugging information.
    - The function generates random names for the intermediate files. This is
      not a robust way to avoid name collisions. A better approach would be
      to use Python's `tempfile` module to create temporary files with unique
      names.

    Args:
        # English: pdf_list
        lista_pdfs (list): A list of PDF files to be filled.
        # English: final_data
        dados_finais (dict): The data to be filled into the PDFs.

    Returns:
        list: A list of the filled PDF files.
    """
    print(f"\n=== PREENCHER_FORMULARIOS START ===")
    print(f"DEBUG: Called with {len(lista_pdfs)} PDFs")
    print(f"DEBUG: Input PDFs: {lista_pdfs}")
    print(f"DEBUG: Data keys: {list(dados_finais.keys())}")
    print(f"DEBUG: CNS Médico: {dados_finais.get('cns_medico', 'NOT_FOUND')}")
    
    # English: files
    arquivos = []
    for i, arquivo in enumerate(lista_pdfs):
        print(f"\n--- Processing PDF {i+1}/{len(lista_pdfs)} ---")
        print(f"DEBUG: PDF template: {arquivo}")
        print(f"DEBUG: File size: {os.path.getsize(arquivo) if os.path.exists(arquivo) else 'FILE_NOT_FOUND'} bytes")
        
        if not os.path.exists(arquivo):
            print(f"ERROR: PDF template not found: {arquivo}")
            print(f"ERROR: Directory exists: {os.path.exists(os.path.dirname(arquivo))}")
            print(f"ERROR: Directory contents: {os.path.listdir(os.path.dirname(arquivo)) if os.path.exists(os.path.dirname(arquivo)) else 'DIR_NOT_FOUND'}")
            continue
        
        print(f"DEBUG: PDF template exists and is readable")
        
        # English: random_name
        aleatorio = str(random.randint(0, 10000000000)) + dados_finais["cns_medico"]
        # English: output_pdf
        output_pdf = os.path.join(
            settings.STATIC_ROOT, "tmp", "{}.pdf".format(aleatorio)
        )
        print(f"DEBUG: Random suffix: {aleatorio}")
        print(f"DEBUG: Output PDF path: {output_pdf}")
        
        # Ensure output directory exists
        # English: tmp_dir
        tmp_dir = os.path.dirname(output_pdf)
        os.makedirs(tmp_dir, exist_ok=True)
        print(f"DEBUG: Created output directory: {tmp_dir}")
        
        try:
            print(f"DEBUG: Calling pypdftk.fill_form...")
            # English: filled_pdf
            filled_pdf = pypdftk.fill_form(arquivo, dados_finais, output_pdf)
            print(f"DEBUG: pypdftk.fill_form returned: {filled_pdf}")
            
            if filled_pdf and os.path.exists(filled_pdf):
                file_size = os.path.getsize(filled_pdf)
                print(f"DEBUG: Successfully filled PDF: {filled_pdf} ({file_size} bytes)")
                # English: files
                arquivos.append(filled_pdf)
            else:
                print(f"ERROR: Filled PDF not created or empty: {filled_pdf}")
                
        except Exception as e:
            print(f"ERROR: Failed to fill PDF {arquivo}: {e}")
            import traceback
            print(f"ERROR: Traceback: {traceback.format_exc()}")
    
    print(f"\nDEBUG: preencher_formularios returning {len(arquivos)} filled PDFs")
    print(f"DEBUG: Filled PDFs: {arquivos}")
    print(f"=== PREENCHER_FORMULARIOS END ===\n")
    return arquivos


# English: remove_intermediate_pdfs
def remover_pdfs_intermediarios(arquivos):
    """Removes intermediate files after concatenation.

    Args:
        # English: files
        arquivos (list): A list of intermediate PDF files to be removed.
    """
    for arquivo in arquivos:
        os.remove(arquivo)


# English: generate_final_pdf
def gerar_pdf_final(arquivos, path_pdf_final):
    """Concatenates and flattens the intermediate (filled) PDFs;
    generates the final file for printing.

    Critique:
    - The function has a lot of debugging prints, which should be removed
      in a production environment. Using Python's `logging` module would be
      a better way to handle debugging information.
    - The error handling is very broad. It catches any exception and returns
      None. It would be better to catch specific exceptions and log them
      properly to make debugging easier.

    Args:
        # English: files
        arquivos (list): A list of intermediate PDF files to be concatenated.
        # English: final_pdf_path
        path_pdf_final (str): The path to the final PDF file.

    Returns:
        str: The path to the final PDF file, or None if an error occurs.
    """
    print(f"\n=== GERAR_PDF_FINAL START ===")
    print(f"DEBUG: Called with {len(arquivos)} files")
    print(f"DEBUG: Output path: {path_pdf_final}")
    
    # Check if all input files exist
    print(f"\n--- INPUT FILE VALIDATION ---")
    # English: valid_files
    valid_files = []
    for i, arquivo in enumerate(arquivos):
        print(f"DEBUG: Input file {i+1}: {arquivo}")
        if not os.path.exists(arquivo):
            print(f"ERROR: Input file not found: {arquivo}")
        else:
            file_size = os.path.getsize(arquivo)
            print(f"DEBUG: File exists, size: {file_size} bytes")
            if file_size > 0:
                valid_files.append(arquivo)
                print(f"DEBUG: Added to valid files list")
            else:
                print(f"ERROR: File is empty: {arquivo}")
    
    if not valid_files:
        print(f"ERROR: No valid input files found")
        return None
    
    print(f"DEBUG: Using {len(valid_files)} valid files for concatenation")
    
    # Ensure output directory exists
    # English: output_dir
    output_dir = os.path.dirname(path_pdf_final)
    os.makedirs(output_dir, exist_ok=True)
    print(f"DEBUG: Created output directory: {output_dir}")
    
    try:
        print(f"DEBUG: Calling pypdftk.concat...")
        # English: final_pdf
        pdf_final = pypdftk.concat(valid_files, path_pdf_final)
        print(f"DEBUG: pypdftk.concat returned: {pdf_final}")
        
        if pdf_final and os.path.exists(pdf_final):
            final_size = os.path.getsize(pdf_final)
            print(f"DEBUG: Successfully generated final PDF: {pdf_final} ({final_size} bytes)")
            return pdf_final
        else:
            print(f"ERROR: Final PDF not created: {pdf_final}")
            return None
            
    except Exception as e:
        print(f"ERROR: Failed to concat PDFs: {e}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        return None
    
    finally:
        print(f"=== GERAR_PDF_FINAL END ===\n")


# def selecionar_med_consentimento(medicamento_1):
#     '''Responsável por definir o medicamento prescrito no
#     check-list do termo de consentimento - isola o nome
#     do fármaco da dosagem '''
#     med = medicamento_1.split((' '))
#     nome_med = med[0]
#     return nome_med


# English: add_exams
def adicionar_exames(arquivos_base, dados_finais):
    """Adds a request for exams before filling out the intermediate PDFs.

    This function is separate from the `preencher_formularios` function because
    in some protocols the necessary exams depend on the prescribed medication.

    Args:
        # English: base_files
        arquivos_base (list): The base list of PDF files.
        # English: final_data
        dados_finais (dict): The data to be filled into the PDFs.

    Returns:
        list: A list of the filled PDF files, including the exam request.
    """
    print(f"DEBUG: adicionar_exames called")
    print(f"DEBUG: PATH_EXAMES: {PATH_EXAMES}")
    print(f"DEBUG: PATH_EXAMES exists: {os.path.exists(PATH_EXAMES)}")
    
    # English: exam_file
    arquivo_exame = [PATH_EXAMES]
    # English: files_with_exams
    arquivos_com_exames = arquivos_base + arquivo_exame
    print(f"DEBUG: Total files with exams: {len(arquivos_com_exames)}")
    
    # English: files
    arquivos = preencher_formularios(arquivos_com_exames, dados_finais)
    return arquivos


# English: format_date
def formatacao_data(dados):
    """Receives the initial date of the process, creates the subsequent dates,
    and formats them to the Brazilian standard.

    Critique:
    - The function modifies the input dictionary `dados` in place. This can be
      surprising and lead to unexpected side effects. It would be better to
      return a new dictionary with the formatted dates.

    Args:
        # English: data
        dados (dict): The data dictionary containing the initial date.
    """
    print(f"\n--- FORMATACAO_DATA START ---")
    print(f"DEBUG: Input data_1: {dados.get('data_1', 'NOT_FOUND')} (type: {type(dados.get('data_1'))})")
    
    # English: month
    mes = 2
    # English: days
    dias = 30
    while mes <= 6:
        # English: new_date
        new_date = dados["data_1"] + timedelta(days=dias)
        # English: formatted_date
        formatted_date = new_date.strftime("%d/%m/%Y")
        # English: data
        dados[f"data_{mes}"] = formatted_date
        print(f"DEBUG: data_{mes} = {formatted_date}")
        dias += 30
        mes += 1
    
    # English: original_date
    original_date = dados["data_1"]
    # English: data
    dados["data_1"] = dados["data_1"].strftime("%d/%m/%Y")
    print(f"DEBUG: Formatted data_1 from {original_date} to {dados['data_1']}")
    print(f"--- FORMATACAO_DATA END ---\n")


# English: adjust_field_18
def ajustar_campo_18(dados_lme):
    """Adjusts field 18 of the LME form.

    Critique:
    - The function modifies the input dictionary `dados_lme` in place. This can be
        surprising and lead to unexpected side effects. It would be better to
        return a new dictionary with the adjusted fields.

    Args:
        # English: lme_data
        dados_lme (dict): The data dictionary for the LME form.
    """
    print(f"\n--- AJUSTAR_CAMPO_18 START ---")
    # English: filled_by
    preenchido_por = dados_lme.get("preenchido_por", "NOT_FOUND")
    print(f"DEBUG: preenchido_por = {preenchido_por}")
    
    if preenchido_por != "medico":
        print(f"DEBUG: Not filled by doctor, adjusting field 18...")
        
        # Safely delete fields that might not exist
        # English: fields_to_delete
        fields_to_delete = ["cpf_paciente", "telefone1_paciente", "telefone2_paciente", "email_paciente"]
        for field in fields_to_delete:
            if field in dados_lme:
                del dados_lme[field]
                print(f"DEBUG: Deleted field: {field}")
            else:
                print(f"DEBUG: Field not found, skipping: {field}")
        
        # English: lme_data
        dados_lme["etnia"] = ""
        # English: lme_data
        dados_lme["escolha_documento"] = ""
        print(f"DEBUG: Set etnia and escolha_documento to empty")
    else:
        print(f"DEBUG: Filled by doctor, no field 18 adjustments needed")
    
    print(f"--- AJUSTAR_CAMPO_18 END ---\n")


# Hello, J. Daqui 43 minutos eu pegarei o trem,
# ele vai direto para Sorocaba, sem paradas.


# English: PDFGenerator
class GeradorPDF:

    def __init__(self, dados_lme_base, path_lme_base):
        # English: base_lme_data
        self.dados_lme_base = dados_lme_base
        # English: base_lme_path
        self.path_lme_base = path_lme_base

    # English: generic
    def generico(self, dados_lme_base, path_lme_base):
        """Generic PDF generator.

        Critique:
        - The function has a lot of debugging prints, which should be removed
          in a production environment. Using Python's `logging` module would be
          a better way to handle debugging information.
        - The function has a high level of complexity. It handles conditional
          PDF generation based on several factors. This makes it difficult to
          read and maintain. It would be better to split this function into
          smaller, more focused functions.
        - The error handling is very broad. It catches any exception and returns
          None. It would be better to catch specific exceptions and log them
          properly to make debugging easier.

        Args:
            # English: base_lme_data
            dados_lme_base (dict): The base data for the LME form.
            # English: base_lme_path
            path_lme_base (str): The path to the base LME form.

        Returns:
            tuple: A tuple containing the path to the final PDF and the URL to
                   the final PDF, or (None, None) if an error occurs.
        """
        print(f"\n=== GERADOR_PDF.GENERICO START ===")
        
        # English: patient_cpf
        cpf_paciente = dados_lme_base["cpf_paciente"]
        cid = dados_lme_base["cid"]
        # English: final_pdf_name
        nome_final_pdf = f"pdf_final_{cpf_paciente}_{cid}.pdf"
        # English: first_time
        primeira_vez = dados_lme_base["consentimento"]
        # English: report
        relatorio = dados_lme_base["relatorio"]
        # English: exams
        exames = dados_lme_base["exames"]
        
        print(f"DEBUG: Patient CPF: {cpf_paciente}")
        print(f"DEBUG: CID: {cid}")
        print(f"DEBUG: Final PDF name: {nome_final_pdf}")
        print(f"DEBUG: First time (consent): {primeira_vez} (type: {type(primeira_vez)})")
        print(f"DEBUG: Include report: {relatorio} (type: {type(relatorio)})")
        print(f"DEBUG: Include exams: {exames} (type: {type(exames)})")
        print(f"DEBUG: Base LME path: {path_lme_base}")
        print(f"DEBUG: Base LME exists: {os.path.exists(path_lme_base)}")
        
        if os.path.exists(path_lme_base):
            print(f"DEBUG: Base LME file size: {os.path.getsize(path_lme_base)} bytes")
        
        print(f"DEBUG: Formatting dates...")
        formatacao_data(dados_lme_base)
        print(f"DEBUG: Date formatting complete")

        # English: base_files
        arquivos_base = [path_lme_base]
        print(f"\n--- PROTOCOL LOOKUP ---")
        try:
            # English: protocol
            protocolo = Protocolo.objects.get(doenca__cid=cid)
            print(f"DEBUG: Found protocol: {protocolo.nome}")
            print(f"DEBUG: Protocol ID: {protocolo.id}")
        except Protocolo.DoesNotExist:
            print(f"ERROR: Protocol not found for CID: {cid}")
            return None, None

        print(f"\n--- CONDITIONAL PDFs SECTION ---")
        try:
            # English: conditional_pdfs_dir
            dir_pdfs_condicionais = os.path.join(
                settings.PATH_PDF_DIR, protocolo.nome, "pdfs_base/"
            )
            print(f"DEBUG: Conditional PDFs directory: {dir_pdfs_condicionais}")
            print(f"DEBUG: PATH_PDF_DIR: {settings.PATH_PDF_DIR}")
            print(f"DEBUG: Protocol name: {protocolo.nome}")
            print(f"DEBUG: Conditional PDFs dir exists: {os.path.exists(dir_pdfs_condicionais)}")
            
            if os.path.exists(dir_pdfs_condicionais):
                print(f"DEBUG: Directory contents: {os.listdir(dir_pdfs_condicionais)}")
            
            # English: base_conditional_pdfs
            pdfs_condicionais_base = glob.glob(dir_pdfs_condicionais + "*.*")
            print(f"DEBUG: Glob pattern: {dir_pdfs_condicionais + '*.*'}")
            print(f"DEBUG: Found {len(pdfs_condicionais_base)} conditional PDFs")
            
            for i, pdf in enumerate(pdfs_condicionais_base):
                print(f"DEBUG: Conditional PDF {i+1}: {pdf}")
                print(f"DEBUG: File exists: {os.path.exists(pdf)}")
                if os.path.exists(pdf):
                    print(f"DEBUG: File size: {os.path.getsize(pdf)} bytes")
                    # English: base_files
                    arquivos_base.append(pdf)
                    print(f"DEBUG: Added conditional PDF to base files")
                else:
                    print(f"ERROR: Conditional PDF not found: {pdf}")
                    
        except Exception as e:
            print(f"ERROR: Failed to add conditional PDFs: {e}")
            import traceback
            print(f"ERROR: Traceback: {traceback.format_exc()}")

        print(f"\n--- CONSENT PDF SECTION ---")
        print(f"DEBUG: Checking consent requirement: primeira_vez = {primeira_vez}")
        if primeira_vez == "True" or primeira_vez == True:
            print(f"DEBUG: Consent PDF required")
            try:
                id_med = dados_lme_base["id_med1"]
                print(f"DEBUG: Medication ID for consent: {id_med}")
                
                # English: consent_pdf
                consentimento_pdf = os.path.join(
                    settings.PATH_PDF_DIR, protocolo.nome, "consentimento.pdf"
                )
                print(f"DEBUG: Consent PDF path: {consentimento_pdf}")
                print(f"DEBUG: Consent PDF exists: {os.path.exists(consentimento_pdf)}")
                
                if os.path.exists(consentimento_pdf):
                    print(f"DEBUG: Consent PDF file size: {os.path.getsize(consentimento_pdf)} bytes")
                
                # English: medication
                medicamento = Medicamento.objects.get(id=id_med)
                # English: base_lme_data
                dados_lme_base["consentimento_medicamento"] = medicamento.nome
                print(f"DEBUG: Consent medication: {medicamento.nome}")
                
                if os.path.exists(consentimento_pdf):
                    # English: base_files
                    arquivos_base.append(consentimento_pdf)
                    print(f"DEBUG: Added consent PDF to base files")
                else:
                    print(f"ERROR: Consent PDF not found: {consentimento_pdf}")
                    
            except Exception as e:
                print(f"ERROR: Failed to add consent PDF: {e}")
                import traceback
                print(f"ERROR: Traceback: {traceback.format_exc()}")
        else:
            print(f"DEBUG: Consent PDF not required (primeira_vez = {primeira_vez})")

        print(f"\n--- REPORT PDF SECTION ---")
        print(f"DEBUG: Checking report requirement: relatorio = {relatorio}")
        if relatorio == "True" or relatorio == True:
            print(f"DEBUG: Report PDF required")
            print(f"DEBUG: Report PDF path: {settings.PATH_RELATORIO}")
            print(f"DEBUG: Report PDF exists: {os.path.exists(settings.PATH_RELATORIO)}")
            
            if os.path.exists(settings.PATH_RELATORIO):
                print(f"DEBUG: Report PDF file size: {os.path.getsize(settings.PATH_RELATORIO)} bytes")
                # English: base_files
                arquivos_base.append(settings.PATH_RELATORIO)
                print(f"DEBUG: Added report PDF to base files")
            else:
                print(f"ERROR: Report PDF not found: {settings.PATH_RELATORIO}")
        else:
            print(f"DEBUG: Report PDF not required (relatorio = {relatorio})")

        print(f"\n--- EXAM PDF SECTION ---")
        print(f"DEBUG: Checking exam requirement: exames = {exames}")
        if exames == "True" or exames == True:
            print(f"DEBUG: Exam PDF required")
            print(f"DEBUG: Exam PDF path: {settings.PATH_EXAMES}")
            print(f"DEBUG: Exam PDF exists: {os.path.exists(settings.PATH_EXAMES)}")
            
            if os.path.exists(settings.PATH_EXAMES):
                print(f"DEBUG: Exam PDF file size: {os.path.getsize(settings.PATH_EXAMES)} bytes")
                # English: base_files
                arquivos_base.append(settings.PATH_EXAMES)
                print(f"DEBUG: Added exam PDF to base files")
            else:
                print(f"ERROR: Exam PDF not found: {settings.PATH_EXAMES}")
        else:
            print(f"DEBUG: Exam PDF not required (exames = {exames})")

        print(f"\n--- FIELD 18 ADJUSTMENT ---")
        print(f"DEBUG: Adjusting field 18 based on preenchido_por: {dados_lme_base.get('preenchido_por', 'NOT_FOUND')}")
        ajustar_campo_18(dados_lme_base)
        print(f"DEBUG: Field 18 adjustment complete")

        print(f"\n--- FINAL FILE LIST ---")
        print(f"DEBUG: Total base files before processing: {len(arquivos_base)}")
        for i, arquivo in enumerate(arquivos_base):
            print(f"DEBUG: Base file {i+1}: {arquivo} (exists: {os.path.exists(arquivo)})")
        
        # English: final_pdf_path
        path_pdf_final = os.path.join(settings.STATIC_URL, "tmp", nome_final_pdf)
        # English: final_output_pdf
        output_pdf_final = os.path.join(settings.STATIC_ROOT, "tmp", nome_final_pdf)
        
        print(f"\nDEBUG: Final PDF URL path: {path_pdf_final}")
        print(f"DEBUG: Final PDF file path: {output_pdf_final}")
        
        # Ensure tmp directory exists
        # English: tmp_dir
        tmp_dir = os.path.join(settings.STATIC_ROOT, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        print(f"DEBUG: Created tmp directory: {tmp_dir}")
        
        print(f"\n--- CALLING PREENCHER_FORMULARIOS ---")
        # English: filled_intermediate_pdfs
        pdfs_intermediarios_preenchidos = preencher_formularios(
            arquivos_base, dados_lme_base
        )
        
        if not pdfs_intermediarios_preenchidos:
            print(f"ERROR: No intermediate PDFs were created")
            return None, None
        
        print(f"\n--- CALLING GERAR_PDF_FINAL ---")
        # English: pdf
        pdf = gerar_pdf_final(pdfs_intermediarios_preenchidos, output_pdf_final)
        
        if pdf:
            print(f"DEBUG: Final PDF generated successfully: {pdf}")
            final_size = os.path.getsize(pdf) if os.path.exists(pdf) else 0
            print(f"DEBUG: Final PDF size: {final_size} bytes")
            
            print(f"DEBUG: Cleaning up intermediate files...")
            remover_pdfs_intermediarios(pdfs_intermediarios_preenchidos)
            print(f"DEBUG: Cleanup complete")
        else:
            print(f"ERROR: Failed to generate final PDF")
            return None, None

        print(f"DEBUG: Returning: pdf={pdf}, path_pdf_final={path_pdf_final}")
        print(f"=== GERADOR_PDF.GENERICO END ===\n")
        return pdf, path_pdf_final

import os
import glob
import random
from datetime import timedelta

import pypdftk
from django.conf import settings

from processos.models import Protocolo, Medicamento

PATH_EXAMES = settings.PATH_EXAMES

def preencher_formularios(lista_pdfs, dados_finais):
    """Preenche os pdfs individualmente e gera os arquivos
    intermediários com nomes aleatórios"""
    print(f"DEBUG: preencher_formularios called with {len(lista_pdfs)} PDFs")
    arquivos = []
    for i, arquivo in enumerate(lista_pdfs):
        print(f"DEBUG: Processing PDF {i+1}/{len(lista_pdfs)}: {arquivo}")
        if not os.path.exists(arquivo):
            print(f"ERROR: PDF template not found: {arquivo}")
            continue
        print(f"DEBUG: PDF template exists: {arquivo}")
        
        aleatorio = str(random.randint(0, 10000000000)) + dados_finais["cns_medico"]
        output_pdf = os.path.join(
            settings.STATIC_ROOT, "tmp", "{}.pdf".format(aleatorio)
        )
        print(f"DEBUG: Output PDF path: {output_pdf}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
        
        try:
            filled_pdf = pypdftk.fill_form(arquivo, dados_finais, output_pdf)
            print(f"DEBUG: Successfully filled PDF: {filled_pdf}")
            arquivos.append(filled_pdf)
        except Exception as e:
            print(f"ERROR: Failed to fill PDF {arquivo}: {e}")
    
    print(f"DEBUG: preencher_formularios returning {len(arquivos)} filled PDFs")
    return arquivos


def remover_pdfs_intermediarios(arquivos):
    """Remove os arquivos intermediários após a
    concatenação"""
    for arquivo in arquivos:
        os.remove(arquivo)


def gerar_pdf_final(arquivos, path_pdf_final):
    """Concatena e achata os pdfs intermediários (preenchidos);
    gera o arquivo final para impressão"""
    print(f"DEBUG: gerar_pdf_final called with {len(arquivos)} files")
    print(f"DEBUG: Input files: {arquivos}")
    print(f"DEBUG: Output path: {path_pdf_final}")
    
    # Check if all input files exist
    for arquivo in arquivos:
        if not os.path.exists(arquivo):
            print(f"ERROR: Input file not found: {arquivo}")
            return None
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(path_pdf_final), exist_ok=True)
    
    try:
        pdf_final = pypdftk.concat(arquivos, path_pdf_final)
        print(f"DEBUG: Successfully generated final PDF: {pdf_final}")
        return pdf_final
    except Exception as e:
        print(f"ERROR: Failed to concat PDFs: {e}")
        return None


# def selecionar_med_consentimento(medicamento_1):
#     '''Responsável por definir o medicamento prescrito no
#     check-list do termo de consentimento - isola o nome
#     do fármaco da dosagem '''
#     med = medicamento_1.split((' '))
#     nome_med = med[0]
#     return nome_med


def adicionar_exames(arquivos_base, dados_finais):
    """Acrescenta pedido de exames antes do preenchimento
    dos pdfs intermediários. Esta função está separada
    da função preencher_formulários pois em alguns protocolos
    os exames necessários dependem do medicamento prescrito"""
    print(f"DEBUG: adicionar_exames called")
    print(f"DEBUG: PATH_EXAMES: {PATH_EXAMES}")
    print(f"DEBUG: PATH_EXAMES exists: {os.path.exists(PATH_EXAMES)}")
    
    arquivo_exame = [PATH_EXAMES]
    arquivos_com_exames = arquivos_base + arquivo_exame
    print(f"DEBUG: Total files with exams: {len(arquivos_com_exames)}")
    
    arquivos = preencher_formularios(arquivos_com_exames, dados_finais)
    return arquivos


def formatacao_data(dados):
    """Recebe a data inicial do processo, cria as datas
    subsequentes e formata para o padrão brasileiro"""
    mes = 2
    dias = 30
    while mes <= 6:
        dados[f"data_{mes}"] = (dados["data_1"] + timedelta(days=dias)).strftime(
            "%d/%m/%Y"
        )
        dias += 30
        mes += 1
    dados["data_1"] = dados["data_1"].strftime("%d/%m/%Y")


def ajustar_campo_18(dados_lme):
    if dados_lme["preenchido_por"] != "medico":
        del dados_lme["cpf_paciente"]
        dados_lme["etnia"] = ""
        del dados_lme["telefone1_paciente"]
        del dados_lme["telefone2_paciente"]
        del dados_lme["email_paciente"]
        dados_lme["escolha_documento"] = ""


# Hello, J. Daqui 43 minutos eu pegarei o trem,
# ele vai direto para Sorocaba, sem paradas.


class GeradorPDF:

    def __init__(self, dados_lme_base, path_lme_base):
        self.dados_lme_base = dados_lme_base
        self.path_lme_base = path_lme_base

    def generico(self, dados_lme_base, path_lme_base):
        print(f"DEBUG: generico method called")
        cpf_paciente = dados_lme_base["cpf_paciente"]
        cid = dados_lme_base["cid"]
        nome_final_pdf = f"pdf_final_{cpf_paciente}_{cid}.pdf"
        primeira_vez = dados_lme_base["consentimento"]
        relatorio = dados_lme_base["relatorio"]
        exames = dados_lme_base["exames"]
        
        print(f"DEBUG: Patient CPF: {cpf_paciente}")
        print(f"DEBUG: CID: {cid}")
        print(f"DEBUG: Final PDF name: {nome_final_pdf}")
        print(f"DEBUG: First time: {primeira_vez}")
        print(f"DEBUG: Include report: {relatorio}")
        print(f"DEBUG: Include exams: {exames}")
        print(f"DEBUG: Base LME path: {path_lme_base}")
        print(f"DEBUG: Base LME exists: {os.path.exists(path_lme_base)}")
        
        formatacao_data(dados_lme_base)

        arquivos_base = [path_lme_base]
        try:
            protocolo = Protocolo.objects.get(doenca__cid=cid)
            print(f"DEBUG: Found protocol: {protocolo.nome}")
        except Protocolo.DoesNotExist:
            print(f"ERROR: Protocol not found for CID: {cid}")
            return None, None

        try:
            dir_pdfs_condicionais = os.path.join(
                settings.PATH_PDF_DIR, protocolo.nome, "pdfs_base/"
            )
            print(f"DEBUG: Conditional PDFs directory: {dir_pdfs_condicionais}")
            print(f"DEBUG: Conditional PDFs dir exists: {os.path.exists(dir_pdfs_condicionais)}")
            
            pdfs_condicionais_base = glob.glob(dir_pdfs_condicionais + "*.*")
            print(f"DEBUG: Found {len(pdfs_condicionais_base)} conditional PDFs: {pdfs_condicionais_base}")
            
            for pdf in pdfs_condicionais_base:
                if os.path.exists(pdf):
                    arquivos_base.append(pdf)
                    print(f"DEBUG: Added conditional PDF: {pdf}")
                else:
                    print(f"ERROR: Conditional PDF not found: {pdf}")
        except Exception as e:
            print(f"ERROR: Failed to add conditional PDFs: {e}")

        if primeira_vez == "True":
            try:
                id_med = dados_lme_base["id_med1"]
                consentimento_pdf = os.path.join(
                    settings.PATH_PDF_DIR, protocolo.nome, "consentimento.pdf"
                )
                print(f"DEBUG: Consent PDF path: {consentimento_pdf}")
                print(f"DEBUG: Consent PDF exists: {os.path.exists(consentimento_pdf)}")
                
                medicamento = Medicamento.objects.get(id=id_med)
                dados_lme_base["consentimento_medicamento"] = medicamento.nome
                print(f"DEBUG: Consent medication: {medicamento.nome}")
                
                if os.path.exists(consentimento_pdf):
                    arquivos_base.append(consentimento_pdf)
                    print(f"DEBUG: Added consent PDF: {consentimento_pdf}")
                else:
                    print(f"ERROR: Consent PDF not found: {consentimento_pdf}")
            except Exception as e:
                print(f"ERROR: Failed to add consent PDF: {e}")

        if relatorio:
            print(f"DEBUG: Adding report PDF: {settings.PATH_RELATORIO}")
            print(f"DEBUG: Report PDF exists: {os.path.exists(settings.PATH_RELATORIO)}")
            if os.path.exists(settings.PATH_RELATORIO):
                arquivos_base.append(settings.PATH_RELATORIO)
            else:
                print(f"ERROR: Report PDF not found: {settings.PATH_RELATORIO}")

        if exames:
            print(f"DEBUG: Adding exam PDF: {settings.PATH_EXAMES}")
            print(f"DEBUG: Exam PDF exists: {os.path.exists(settings.PATH_EXAMES)}")
            if os.path.exists(settings.PATH_EXAMES):
                arquivos_base.append(settings.PATH_EXAMES)
            else:
                print(f"ERROR: Exam PDF not found: {settings.PATH_EXAMES}")

        ## Remove o cpf do campo 18 se preenchimento não foi pelo médico
        ajustar_campo_18(dados_lme_base)

        print(f"DEBUG: Total base files before processing: {len(arquivos_base)}")
        print(f"DEBUG: Base files: {arquivos_base}")
        
        path_pdf_final = os.path.join(settings.STATIC_URL, "tmp", nome_final_pdf)
        output_pdf_final = os.path.join(settings.STATIC_ROOT, "tmp", nome_final_pdf)
        
        print(f"DEBUG: Final PDF URL path: {path_pdf_final}")
        print(f"DEBUG: Final PDF file path: {output_pdf_final}")
        
        # Ensure tmp directory exists
        tmp_dir = os.path.join(settings.STATIC_ROOT, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        print(f"DEBUG: Created tmp directory: {tmp_dir}")
        
        pdfs_intermediarios_preenchidos = preencher_formularios(
            arquivos_base, dados_lme_base
        )
        
        if not pdfs_intermediarios_preenchidos:
            print(f"ERROR: No intermediate PDFs were created")
            return None, None
        
        pdf = gerar_pdf_final(pdfs_intermediarios_preenchidos, output_pdf_final)
        
        if pdf:
            print(f"DEBUG: Final PDF generated successfully: {pdf}")
            remover_pdfs_intermediarios(pdfs_intermediarios_preenchidos)
        else:
            print(f"ERROR: Failed to generate final PDF")
            return None, None

        return pdf, path_pdf_final
import os
import random
import pypdftk

# English: PATH_EXAMS
from paths import PATH_EXAMES
# English: PATH_FINAL_PDF
from dados import PATH_PDF_FINAL


# English: fill_forms
def preencher_formularios(lista_pdfs, dados_finais):
    """Preenche os pdfs individualmente e gera os arquivos
    intermediários com nomes aleatórios"""
    # English: files
    arquivos = []
    # English: patient_cpf
    cpf_paciente = dados_finais.get("cpf_paciente", "SEM_CPF")
    print(f"[DEBUG] Iniciando preenchimento de PDFs. Lista: {lista_pdfs}, Dados: {dados_finais}")
    # English: file
    for arquivo in lista_pdfs:
        # English: random_number
        aleatorio = random.randint(0, 10000000000)
        # English: output_pdf
        output_pdf = f"{aleatorio}_{cpf_paciente}.pdf"
        print(f"[DEBUG] Preenchendo PDF: {arquivo} -> {output_pdf}")
        try:
            # English: result
            result = pypdftk.fill_form(arquivo, dados_finais, output_pdf)
            print(f"[DEBUG] PDF preenchido: {result}")
            arquivos.append(result)
        except Exception as e:
            print(f"[ERROR] Falha ao preencher PDF {arquivo}: {e}")
    print(f"[DEBUG] PDFs intermediários gerados: {arquivos}")
    return arquivos


# English: remove_intermediate_pdfs
def remover_pdfs_intermediarios(*arquivos):
    """Remove os arquivos intermediários após a
    concatenação"""
    print(f"[DEBUG] Removendo arquivos intermediários: {arquivos}")
    # English: file
    for arquivo in arquivos:
        try:
            os.remove(arquivo)
            print(f"[DEBUG] Removido: {arquivo}")
        except Exception as e:
            print(f"[ERROR] Falha ao remover {arquivo}: {e}")


# English: generate_final_pdf
def gerar_pdf_final(arquivos, path_pdf_final):
    """Concatena e achata os pdfs intermediários (preenchidos);
    gera o arquivo final para impressão"""
    print(f"[DEBUG] Concatenando PDFs: {arquivos} -> {path_pdf_final}")
    try:
        # English: final_pdf
        pdf_final = pypdftk.concat(arquivos, path_pdf_final)
        print(f"[DEBUG] PDF final gerado: {pdf_final}")
        return pdf_final
    except Exception as e:
        print(f"[ERROR] Falha ao gerar PDF final: {e}")
        return None


# English: select_consent_medication
def selecionar_med_consentimento(medicamento_1, dados_finais):
    """Responsável por definir o medicamento prescrito no
    check-list do termo de consentimento - isola o nome
    do fármaco da dosagem"""
    # English: med
    med = medicamento_1.split((" "))
    # English: medication_name
    nome_med = dados_finais["selecionar_med"] = med[0]
    return nome_med


# English: add_exams
def adicionar_exames(arquivos_base, dados_finais):
    """Acrescenta pedido de exames antes do preenchimento
    dos pdfs intermediários. Esta função está separada
    da função preencher_formulários pois em alguns protocolos
    os exames necessários dependem do medicamento prescrito"""
    print(f"[DEBUG] Adicionando exames ao PDF. Arquivos base: {arquivos_base}, Dados: {dados_finais}")
    # English: exam_file
    arquivo_exame = [PATH_EXAMES]
    # English: files_with_exams
    arquivos_com_exames = arquivos_base + arquivo_exame
    print(f"[DEBUG] Arquivos para preencher (com exames): {arquivos_com_exames}")
    # English: files
    arquivos = preencher_formularios(arquivos_com_exames, dados_finais)
    print(f"[DEBUG] PDFs gerados com exames: {arquivos}")
    return arquivos


# English: PDFGenerator
class GeradorPDF:

    def __init__(self, dados_lme_base, dados_condicionais, path_lme_base):
        print(f"[DEBUG] GeradorPDF inicializado. Dados base: {dados_lme_base}, Dados condicionais: {dados_condicionais}, Path base: {path_lme_base}")
        # English: base_lme_data
        self.dados_lme_base = dados_lme_base
        # English: conditional_data
        self.dados_condicionais = dados_condicionais
        # English: base_lme_path
        self.path_lme_base = path_lme_base

    # English: generic
    def generico(self, dados_lme_base, path_lme_base):
        print(f"[DEBUG] GeradorPDF.generico chamado. Dados: {dados_lme_base}, Path: {path_lme_base}, Destino: {PATH_PDF_FINAL}")
        try:
            # English: pdf
            pdf = pypdftk.fill_form(path_lme_base, dados_lme_base, PATH_PDF_FINAL)
            print(f"[DEBUG] PDF gerado: {pdf}")
            return pdf
        except Exception as e:
            print(f"[ERROR] Falha ao gerar PDF generico: {e}")
            return None

    # English: emit_exams
    def emitir_exames(self, dados_lme_base):
        print(f"[DEBUG] Verificando se deve emitir exames. Dados: {dados_lme_base}")
        if dados_lme_base.get("emitir_exames") == "sim":
            print("[DEBUG] Exames serão emitidos.")
            return True
        print("[DEBUG] Exames NÃO serão emitidos.")
        return False

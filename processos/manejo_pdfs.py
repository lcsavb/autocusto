import os
import glob
import random
from datetime import timedelta

import pypdftk
from django.conf import settings

from processos.models import Protocolo, Medicamento

PATH_EXAMES = os.path.join(settings.BASE_DIR, "logica_raw/modelos_pdf/exames_base_modelo.pdf")

def preencher_formularios(lista_pdfs, dados_finais):
    """Preenche os pdfs individualmente e gera os arquivos
    intermediários com nomes aleatórios"""
    arquivos = []
    for arquivo in lista_pdfs:
        aleatorio = str(random.randint(0, 10000000000)) + dados_finais["cns_medico"]
        output_pdf = os.path.join(
            settings.BASE_DIR, "static/tmp", "{}.pdf".format(aleatorio)
        )
        arquivos.append(pypdftk.fill_form(arquivo, dados_finais, output_pdf))
    return arquivos


def remover_pdfs_intermediarios(arquivos):
    """Remove os arquivos intermediários após a
    concatenação"""
    for arquivo in arquivos:
        os.remove(arquivo)


def gerar_pdf_final(arquivos, path_pdf_final):
    """Concatena e achata os pdfs intermediários (preenchidos);
    gera o arquivo final para impressão"""
    pdf_final = pypdftk.concat(arquivos, path_pdf_final)
    return pdf_final


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
    arquivo_exame = [PATH_EXAMES]
    arquivos_com_exames = arquivos_base + arquivo_exame
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
        cpf_paciente = dados_lme_base["cpf_paciente"]
        cid = dados_lme_base["cid"]
        nome_final_pdf = f"pdf_final_{cpf_paciente}_{cid}.pdf"
        primeira_vez = dados_lme_base["consentimento"]
        relatorio = dados_lme_base["relatorio"]
        exames = dados_lme_base["exames"]
        formatacao_data(dados_lme_base)

        arquivos_base = [path_lme_base]
        protocolo = Protocolo.objects.get(doenca__cid=cid)

        try:
            dir_pdfs_condicionais = os.path.join(
                settings.PATH_PDF_DIR, protocolo.nome, "pdfs_base/"
            )
            pdfs_condicionais_base = glob.glob(dir_pdfs_condicionais + "*.*")
            for pdf in pdfs_condicionais_base:
                arquivos_base.append(pdf)
        except Exception as e:
            print(f"Erro ao adicionar PDFs condicionais: {e}")

        if primeira_vez == "True":
            try:
                id_med = dados_lme_base["id_med1"]
                consentimento_pdf = os.path.join(
                    settings.PATH_PDF_DIR, protocolo.nome, "consentimento.pdf"
                )
                dados_lme_base["consentimento_medicamento"] = Medicamento.objects.get(
                    id=id_med
                ).nome
                arquivos_base.append(consentimento_pdf)
            except Exception as e:
                print(f"Erro ao adicionar termo de consentimento: {e}")

        if relatorio:
            arquivos_base.append(settings.PATH_RELATORIO)

        if exames:
            arquivos_base.append(settings.PATH_EXAMES)

        ## Remove o cpf do campo 18 se preenchimento não foi pelo médico
        ajustar_campo_18(dados_lme_base)

        path_pdf_final = os.path.join(settings.STATIC_URL, "tmp", nome_final_pdf)
        output_pdf_final = os.path.join(settings.BASE_DIR, "static/tmp", nome_final_pdf)
        pdfs_intermediarios_preenchidos = preencher_formularios(
            arquivos_base, dados_lme_base
        )
        pdf = gerar_pdf_final(pdfs_intermediarios_preenchidos, output_pdf_final)
        remover_pdfs_intermediarios(pdfs_intermediarios_preenchidos)

        return pdf, path_pdf_final
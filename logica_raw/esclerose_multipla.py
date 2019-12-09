import os

import pypdftk

from paths import PATH_LME_BASE, PATH_EDSS, PATH_EM_CONSENTIMENTO, PATH_EXAMES, PATH_FINGO_MONIT, PATH_RELATORIO, PATH_NATA_EXAMES
from dados import PATH_PDF_FINAL
from manejo_pdfs import GeradorPDF, remover_pdfs_intermediarios, preencher_formularios, gerar_pdf_final

class EscleroseMultipla(GeradorPDF):
    def __init__(self, dados_lme_base,dados_condicionais,path_lme_base):
        GeradorPDF.__init__(self,dados_lme_base,dados_condicionais,path_lme_base)
        self.dados_condicionais = dados_condicionais
                
    def renovar(self,dados_lme_base,dados_condicionais,path_lme_base):
        dados_lme_base.update(dados_condicionais)
        dados_finais = dados_lme_base
        medicamento = dados_finais['med1'].lower()
        
        arquivos_modelo = [path_lme_base, PATH_EDSS]
        
        arquivos_base = preencher_formularios(arquivos_modelo,dados_finais)

        if 'fingolimode' in medicamento:
            arquivos_condicionais = fingolimode_renova(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif 'betainterferon' in medicamento:
            arquivos_condicionais = betainterferon_renova(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif 'natalizumabe' in medicamento:
            arquivos_condicionais = natalizumabe_renova(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif 'fumarato' in medicamento:
            arquivos_condicionais = fumarato_renova(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif 'glatiramer' in medicamento:
            arquivos_condicionais = glatiramer_renova(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif 'teriflunomida' in medicamento:
            arquivos_condicionais = teriflunomida_renova(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif 'azatioprina' in medicamento:
            arquivos_condicionais = azatioprina_renova(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
            
        pdf_em = gerar_pdf_final(arquivos, PATH_PDF_FINAL)
        #Remover arquivos intermediários
        remover_pdfs_intermediarios(*arquivos)
        return pdf_em


    def primeira_vez(self,dados_lme_base,dados_condicionais,path_lme_base):
        dados_lme_base.update(dados_condicionais)
        dados_finais = dados_lme_base
        medicamento = dados_finais['med1'].lower()
        emitir_exames = dados_finais['exames']
        arquivos_modelo= [path_lme_base, PATH_EDSS]
        
        arquivos_base = preencher_formularios(arquivos_modelo,dados_finais)
           

        if 'fingolimode' in medicamento: 
            arquivos_condicionais = fingolimode_1vez(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif 'betainterferon' in medicamento and emitir_exames:
            arquivos_condicionais = betainterferon_1vez(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif 'natalizumabe' in medicamento:
            arquivos_condicionais = natalizumabe_1vez(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif 'fumarato' in medicamento:
            arquivos_condicionais = fumarato_1vez(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif 'glatiramer' in medicamento:
            arquivos_condicionais = glatiramer_1vez(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif 'teriflunomida' in medicamento:
            arquivos_condicionais = teriflunomida_1vez(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais
        elif 'azatioprina' in medicamento:
            arquivos_condicionais = azatioprina_1vez(dados_finais)
            arquivos = arquivos_base + arquivos_condicionais

        pdf_em = gerar_pdf_final(arquivos, PATH_PDF_FINAL)
        remover_pdfs_intermediarios(*arquivos)
        print(pdf_em)
        return pdf_em


def fingolimode_1vez(dados_finais):
    emitir_exames = dados_finais['exames']
    dados_finais['relatorio'] = dados_finais.pop('relatorio_fingolimode_1vez')
    if emitir_exames:
        dados_finais['exames_solicitados'] = dados_finais.pop('exames_em_1vez')
        arquivos_protocolo_1vez = [PATH_FINGO_MONIT,PATH_EXAMES]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_1vez,dados_finais)
        return arquivos_preenchidos            
    else:
        arquivos_protocolo_1vez = [PATH_FINGO_MONIT]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_1vez,dados_finais)
        return arquivos_preenchidos 
            

def fingolimode_renova(dados_finais):
    emitir_exames = dados_finais['exames']
    if emitir_exames:
        dados_finais['exames_solicitados'] = dados_finais.pop('exames_em_renova')
        arquivos_protocolo_renovacao = [PATH_EXAMES]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_renovacao,dados_finais)
        return arquivos_preenchidos   
            
    else:
        return None
        

def natalizumabe_1vez(dados_finais):
    emitir_exames = dados_finais['exames']
    dados_finais['relatorio'] = dados_finais.pop('relatorio_natalizumabe_1vez')
    dados_finais['consentimento_medicamento'] = 'natalizumabe'
    if emitir_exames:
        arquivos_protocolo_1vez = [PATH_RELATORIO, PATH_EXAMES, PATH_EM_CONSENTIMENTO]
        dados_finais['exames_solicitados'] = dados_finais.pop('exames_em_1vez')
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_1vez,dados_finais)
        return arquivos_preenchidos            
    else:
        arquivos_protocolo_1vez = [PATH_RELATORIO, PATH_EM_CONSENTIMENTO]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_1vez,dados_finais)
        return arquivos_preenchidos 


def natalizumabe_renova(dados_finais):
    emitir_exames = dados_finais['exames']
    if emitir_exames:
        dados_finais['exames_solicitados'] = dados_finais.pop('exames_nata_renova')
        arquivos_protocolo_renovacao = [PATH_NATA_EXAMES]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_renovacao,dados_finais)
        return arquivos_preenchidos   
            
    else:
        return None


def betainterferon_1vez(dados_finais):
    emitir_exames = dados_finais['exames']
    dados_finais['consentimento_medicamento'] = 'betainterferona1a'
    if emitir_exames:
        arquivos_protocolo_1vez = [PATH_EXAMES, PATH_EM_CONSENTIMENTO]
        dados_finais['exames_solicitados'] = dados_finais.pop('exames_em_1vez')
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_1vez,dados_finais)
        return arquivos_preenchidos            
    else:
        arquivos_protocolo_1vez = [PATH_EM_CONSENTIMENTO]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_1vez,dados_finais)
        return arquivos_preenchidos 
            

def betainterferon_renova(dados_finais):
    emitir_exames = dados_finais['exames']
    if emitir_exames:
        dados_finais['exames_solicitados'] = dados_finais.pop('exames_em_renova')
        arquivos_protocolo_renovacao = [PATH_EXAMES]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_renovacao,dados_finais)
        return arquivos_preenchidos   
            
    else:
        return None
        

def fumarato_1vez(dados_finais):
    emitir_exames = dados_finais['exames']
    dados_finais['relatorio'] = dados_finais.pop('relatorio_fumarato_1vez')
    dados_finais['consentimento_medicamento'] = 'dimetila'
    if emitir_exames:
        dados_finais['exames_solicitados'] = dados_finais.pop('exames_em_1vez')
        arquivos_protocolo_1vez = [PATH_EXAMES, PATH_EM_CONSENTIMENTO, PATH_RELATORIO]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_1vez,dados_finais)
        return arquivos_preenchidos            
    else:
        arquivos_protocolo_1vez = [PATH_EM_CONSENTIMENTO, PATH_RELATORIO]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_1vez,dados_finais)
        return arquivos_preenchidos 


def fumarato_renova(dados_finais):
    emitir_exames = dados_finais['exames']
    if emitir_exames:
        dados_finais['exames_solicitados'] = dados_finais.pop('exames_em_renova')
        arquivos_protocolo_renovacao = [PATH_EXAMES]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_renovacao,dados_finais)
        return arquivos_preenchidos   
            
    else:
        return None


def azatioprina_1vez(dados_finais):
    emitir_exames = dados_finais['exames']
    dados_finais['consentimento_medicamento'] = 'azatioprina'
    if emitir_exames:
        arquivos_protocolo_1vez = [PATH_EXAMES, PATH_EM_CONSENTIMENTO]
        dados_finais['exames_solicitados'] = dados_finais.pop('exames_em_1vez')
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_1vez,dados_finais)
        return arquivos_preenchidos            
    else:
        arquivos_protocolo_1vez = [PATH_EM_CONSENTIMENTO]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_1vez,dados_finais)
        return arquivos_preenchidos 


def azatioprina_renova(dados_finais):
    emitir_exames = dados_finais['exames']
    if emitir_exames:
        dados_finais['exames_solicitados'] = dados_finais.pop('exames_em_renova')
        arquivos_protocolo_renovacao = [PATH_EXAMES]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_renovacao,dados_finais)
        return arquivos_preenchidos   
            
    else:
        return None


def teriflunomida_1vez(dados_finais):
    emitir_exames = dados_finais['exames']
    dados_finais['consentimento_medicamento'] = 'teriflunomida'
    if emitir_exames:
        arquivos_protocolo_1vez = [PATH_EXAMES, PATH_EM_CONSENTIMENTO]
        dados_finais['exames_solicitados'] = dados_finais.pop('exames_em_1vez')
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_1vez,dados_finais)
        return arquivos_preenchidos            
    else:
        arquivos_protocolo_1vez = [PATH_EM_CONSENTIMENTO]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_1vez,dados_finais)
        return arquivos_preenchidos 


def teriflunomida_renova(dados_finais):
    emitir_exames = dados_finais['exames']
    if emitir_exames:
        dados_finais['exames_solicitados'] = dados_finais.pop('exames_em_renova')
        arquivos_protocolo_renovacao = [PATH_EXAMES]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_renovacao,dados_finais)
        return arquivos_preenchidos   
            
    else:
        return None


def glatiramer_1vez(dados_finais):
    emitir_exames = dados_finais['exames']
    dados_finais['consentimento_medicamento'] = 'glatiramer'
    if emitir_exames:
        arquivos_protocolo_1vez = [PATH_EXAMES, PATH_EM_CONSENTIMENTO]
        dados_finais['exames_solicitados'] = dados_finais.pop('exames_em_1vez')
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_1vez,dados_finais)
        return arquivos_preenchidos            
    else:
        arquivos_protocolo_1vez = [PATH_EM_CONSENTIMENTO]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_1vez,dados_finais)
        return arquivos_preenchidos 


def glatiramer_renova(dados_finais):
    emitir_exames = dados_finais['exames']
    if emitir_exames:
        dados_finais['exames_solicitados'] = dados_finais.pop('exames_em_renova')
        arquivos_protocolo_renovacao = [PATH_EXAMES]
        arquivos_preenchidos = preencher_formularios(arquivos_protocolo_renovacao,dados_finais)
        return arquivos_preenchidos   
            
    else:
        return None
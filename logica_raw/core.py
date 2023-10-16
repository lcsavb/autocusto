
import os
import pypdftk
from cids import alzheimer, esclerose_multipla, epilepsia, dislipidemia_cids, dor, artrite_reumatoide
from dados import dados_clinica, dados_medico, dados_paciente, dados_ar, dados_epilepsia, dados_processo, dados_condicionais, dados_alzheimer, dados_esclerose_multipla, dados_dislipidemia, dados_dor
from paths import PATH_LME_BASE, PATH_EDSS, PATH_EM_CONSENTIMENTO
from manejo_pdfs import GeradorPDF
from artrite_reumatoide import Artrite_Reumatoide
from esclerose_multipla import EscleroseMultipla
from epilepsia import Epilepsia
from alzheimer import Alzheimer
from dislipidemia import Dislipidemia
from dor import Dor

def mesclar(dados_clinica, dados_medico, dados_paciente, dados_processo):
    lme_base_data = {}
    lme_base_data.update(dados_clinica)
    lme_base_data.update(patient_data)
    lme_base_data.update(process_data)
    lme_base_data.update(dados_medico)
    return lme_base_data

def gerar_pdf(dados_lme_base, dados_condicionais):
    icd = lme_base_data['cid']
    renewal = lme_base_data['renovacao']
    args = [lme_base_data, conditional_data, LME_BASE_PATH]
    pdf = GeradorPDF(*args)
    if (icd in dislipidemia_cids.keys()):
        conditional_data.update(dados_dislipidemia)
        pdf = Dislipidemia(*args)
        if renewal:
            pdf.renovar(*args)
        else:
            pdf.primeira_vez(*args)
    elif (icd in pain.keys()):
        conditional_data.update(dados_dor)
        pdf = Dor(*args)
        if renewal:
            pdf.renovar(*args)
        else:
            pdf.primeira_vez(*args)
    elif (icd in epilepsy.keys()):
        conditional_data.update(dados_epilepsia)
        pdf = Epilepsia(*args)
        if renewal:
            pdf.renovar(*args)
        else:
            pdf.primeira_vez(*args)
    elif (icd in rheumatoid_arthritis.keys()):
        conditional_data.update(dados_ar)
        pdf = Artrite_Reumatoide(*args)
        if renewal:
            pdf.renovar(*args)
        else:
            pdf.primeira_vez(*args)
    elif (icd in multiple_sclerosis.keys()):
        conditional_data.update(dados_esclerose_multipla)
        pdf = EscleroseMultipla(*args)
        if renewal:
            pdf.renovar(*args)
        else:
            pdf.primeira_vez(*args)
    elif (icd in alzheimer.keys()):
        conditional_data.update(dados_alzheimer)
        pdf = Alzheimer(*args)
        if renewal:
            pdf.renovar(*args)
        else:
            pdf.primeira_vez(*args)
    else:
        pdf = GeradorPDF(*args)
        pdf.generico(lme_base_data, LME_BASE_PATH)
lme_base_data = mesclar(dados_clinica, dados_medico, patient_data, process_data)
gerar_pdf(lme_base_data, conditional_data)

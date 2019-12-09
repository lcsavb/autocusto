import os

import pypdftk

from cids import alzheimer, esclerose_multipla, epilepsia, dislipidemia_cids, dor, artrite_reumatoide
from dados import dados_clinica, dados_medico, dados_paciente, dados_ar, dados_epilepsia, dados_processo, dados_condicionais, dados_alzheimer,dados_esclerose_multipla, dados_dislipidemia, dados_dor
from paths import PATH_LME_BASE, PATH_EDSS, PATH_EM_CONSENTIMENTO

from manejo_pdfs import GeradorPDF
from artrite_reumatoide import Artrite_Reumatoide
from esclerose_multipla import EscleroseMultipla
from epilepsia import Epilepsia
from alzheimer import Alzheimer
from dislipidemia import Dislipidemia 
from dor import Dor


def mesclar(dados_clinica,dados_medico,dados_paciente,dados_processo):
    dados_lme_base = {}
    dados_lme_base.update(dados_clinica)
    dados_lme_base.update(dados_paciente)
    dados_lme_base.update(dados_processo)
    dados_lme_base.update(dados_medico)
    return dados_lme_base


def gerar_pdf(dados_lme_base, dados_condicionais):
    cid = dados_lme_base['cid']
    renovacao = dados_lme_base['renovacao']
    args = [dados_lme_base, dados_condicionais, PATH_LME_BASE]
    pdf = GeradorPDF(*args)
    if cid in dislipidemia_cids.keys():
        dados_condicionais.update(dados_dislipidemia)
        pdf = Dislipidemia(*args)
        if renovacao:
            pdf.renovar(*args)
        else:
            pdf.primeira_vez(*args)
    elif cid in dor.keys():
        dados_condicionais.update(dados_dor)
        pdf = Dor(*args)
        if renovacao:
            pdf.renovar(*args)
        else:
            pdf.primeira_vez(*args)    
    elif cid in epilepsia.keys():
        dados_condicionais.update(dados_epilepsia)
        pdf = Epilepsia(*args)
        if renovacao:
            pdf.renovar(*args)
        else:
            pdf.primeira_vez(*args)
    elif cid in artrite_reumatoide.keys():
        dados_condicionais.update(dados_ar)
        pdf = Artrite_Reumatoide(*args)
        if renovacao:
            pdf.renovar(*args)
        else:
            pdf.primeira_vez(*args)
    elif cid in esclerose_multipla.keys():
        dados_condicionais.update(dados_esclerose_multipla)
        pdf = EscleroseMultipla(*args)
        if renovacao:
            pdf.renovar(*args)
        else:
            pdf.primeira_vez(*args)
    elif cid in alzheimer.keys():
        dados_condicionais.update(dados_alzheimer)
        pdf = Alzheimer(*args)
        if renovacao:            
            pdf.renovar(*args)
        else:
            pdf.primeira_vez(*args)
    else:
        pdf = GeradorPDF(*args)
        pdf.generico(dados_lme_base,PATH_LME_BASE)


dados_lme_base = mesclar(dados_clinica,dados_medico,dados_paciente,dados_processo)
gerar_pdf(dados_lme_base, dados_condicionais)






















def cria_dict_renovação(modelo):
    dicionario = {
        # Dados paciente
        'nome_paciente': modelo.paciente.nome_paciente,
        'cpf_paciente': modelo.paciente.cpf_paciente,
        'peso': modelo.paciente.peso,
        'altura': modelo.paciente.altura,
        'nome_mae': modelo.paciente.nome_mae,
        'incapaz': modelo.paciente.incapaz,
        'nome_responsavel': modelo.paciente.nome_responsavel,
        'etnia': modelo.paciente.etnia,
        'telefone1_paciente': modelo.paciente.telefone1_paciente,
        'telefone2_paciente': modelo.paciente.telefone2_paciente,
        'email_paciente': modelo.paciente.email_paciente,
        'end_paciente': modelo.paciente.end_paciente,
        # Dados processo
        'med1': modelo.med1,
        'med1_via': modelo.med1_via,
        'med2': modelo.med2,
        'med3': modelo.med3, 
        'med4': modelo.med4, 
        'med5': modelo.med4,   
        'med1_posologia_mes1':modelo.med1_posologia_mes1,
        'med1_posologia_mes2':modelo.med1_posologia_mes2,
        'med1_posologia_mes3':modelo.med1_posologia_mes3,
        'med2_posologia_mes1':modelo.med2_posologia_mes1,
        'med2_posologia_mes2':modelo.med2_posologia_mes2,
        'med2_posologia_mes3':modelo.med2_posologia_mes3,
        'med3_posologia_mes1':modelo.med3_posologia_mes1,
        'med3_posologia_mes2':modelo.med3_posologia_mes2,
        'med3_posologia_mes3':modelo.med3_posologia_mes3,
        'med4_posologia_mes1':modelo.med4_posologia_mes1,
        'med4_posologia_mes2':modelo.med4_posologia_mes2,
        'med4_posologia_mes3':modelo.med4_posologia_mes3,
        'med5_posologia_mes1':modelo.med5_posologia_mes1,
        'med5_posologia_mes2':modelo.med5_posologia_mes2,
        'med5_posologia_mes3':modelo.med5_posologia_mes3,  
        'qtd_med1_mes1':modelo.qtd_med1_mes1,
        'qtd_med1_mes2':modelo.qtd_med1_mes2,
        'qtd_med1_mes3':modelo.qtd_med1_mes3,
        'qtd_med2_mes1':modelo.qtd_med2_mes1,
        'qtd_med2_mes2':modelo.qtd_med2_mes2,
        'qtd_med2_mes3':modelo.qtd_med2_mes3,
        'qtd_med3_mes1':modelo.qtd_med3_mes1,
        'qtd_med3_mes2':modelo.qtd_med3_mes2,
        'qtd_med3_mes3':modelo.qtd_med3_mes3,
        'qtd_med4_mes1':modelo.qtd_med4_mes1,
        'qtd_med4_mes2':modelo.qtd_med4_mes2,
        'qtd_med4_mes3':modelo.qtd_med4_mes3,
        'qtd_med5_mes1':modelo.qtd_med5_mes1,
        'qtd_med5_mes2':modelo.qtd_med5_mes2,
        'qtd_med5_mes3':modelo.qtd_med5_mes3,
        'cid':modelo.cid,
        'diagnostico':modelo.diagnostico,
        'anamnese':modelo.anamnese,
        'tratou':modelo.tratou,
        'tratamentos_previos':modelo.tratamentos_previos,
        'preenchido_por':modelo.preenchido_por,
        'clinica': modelo.clinica,

    }
    return dicionario


# ############################### Path pdf_final

# PATH_PDF_FINAL = 'pdf_final_{}_{}.pdf'.format(dados_paciente['cpf_paciente'],dados_processo['cid'])


# ############################### DADOS CONDICIONAIS - deverá haver opção do médico defini-los
# #### ou selecionar os padrões como descritos abaixo.

# dados_condicionais = {}

# ### DOENÇA DE ALZHEIMER

# exames1vez = '''
# Hemograma,sódio, potássio, cálcio total, creatinina, uréia, Glicemia de jejum, 
# TSH (Hormônio Tireoestimulante), ácido fólico, vitamina B12, VDRL, TGO, TGP
# '''


# dados_alzheimer = {
#     # Mini-exame do estado mental
#     'ot1': '1',
#     'ot2': '1',
#     'ot3': '1',
#     'ot4': '1',
#     'ot5': '1',
#     'oe1': '1',
#     'oe2': '1',
#     'oe3': '1',
#     'oe4': '1',
#     'mi': '3', # de 0 a 3
#     'ac': '4', # de 0 a 5
#     'me': '3', # 0 a 3
#     'n': '2', # de 0 a 2
#     'r': '1', 
#     'ce': '1', # 0 ou 1
#     'cv': '2', # 0 a 3
#     'f': '0',
#     'd': '0',
#     'total': 'somátoria dos anteriores',
#     ### CDR
#     'cdr': '51',
#     ### Exames
#     'exames_da_1vez': exames1vez # acrescentar sorologia para hiv se menos de 60 anos
# }

# #### ARTRITE REUMATÓIDE




# med_ar_grupo_1 = [ 'azatioprina', 'ciclosporina', 'cloroquina', 'hidroxicloroquina', 'leflunomida',
#                     'metotrexato', 'naproxeno', 'sulfassalazina' ] 

# exames_ar_grupo_1 = ['VHS', 'Fator reumatóide']

# exames_ar_grupo_2 = ['Hemograma', 'TGO', 'TGP', 'VHS', 'HbsAg', 'Anti-HCV', 'Fator reumatóide',
#                     'Prova de Mantoux - PPD']

# meds_relatorio_ar = ['abatacepte', 'etanercepte', 'golimumabe', 'rituximabe', 'tocilizumabe']


# aviso_ar = '''
#         Acrescentar laudo ou relatório médico da radiografia de tórax. Descrever critérios
#         diagnósticos na LME
#         '''
        

# dados_ar = {
#     'exames_ar_grupo_1': exames_ar_grupo_1,
#     'exames_ar_grupo_2': exames_ar_grupo_2,
#     'aviso_ar': aviso_ar
# }


# #### ESCLEROSE MÚLTIPLA

# relatorio_nata = ''' 
# Relatório médico contendo:
# 1. Falha terapêutica ou contraindicação ao fingolimode; 2. Se o paciente está sem receber imunomodulador 
# por pelo menos 45 dias ou azatioprina por 3 meses; 3. Se paciente não foi diagnosticado com micose sistêmica 
# nos últimos 6 meses, herpes grave nos últimos 3 meses, infecção por HIV, qualquer outra infecção oportunista nos últimos 
# 3 meses ou infecção atual ativa. 
# '''

# relatorio_fingo = '''
# Relatório médico, contendo: A. Justificativa para interrupção do uso ou motivo da não utilização de primeira linha: 
# 1. Falha terapêutica à betainterferona ou ao glatirâmer ou à teriflunomida 
# 2. Ausência de contraindicação ao uso do fingolimode'
# '''

# relatorio_fumarato = '''
# 1. Em casos de intolerância, reações adversas ou falta de adesão à Betainterferon ou ao Glatiramer ou à
# Teriflunomida;
# 2. Em casos de falha terapêutica ou resposta sub-ótima à Betainterferon ou ao Glatiramer ou à
# Teriflunomida.
# '''

# dados_esclerose_multipla = {
#     'edss': '3',
#     'exames_em_1vez': 'Hemograma, TGO, TGP, FA, GGT, Vitamina B12, Sorologia HIV, VDRL, Bilirrubinas total e frações, TSH',
#     'exames_em_renova': 'Hemograma, TGO, TGP, FA, GGT, Bilirrubinas total e frações, TSH',
#     'relatorio_fingolimode_1vez': relatorio_fingo,
#     'relatorio_natalizumabe_1vez': relatorio_nata,
#     'relatorio_fumarato_1vez': relatorio_fumarato,
#     'exames_nata_renova': 'Hemograma'}


# ##### Epilepsia

# relatorio_epilepsia_1vez = '''
#     Relatar características das crises, se há risco de recorrência superior a 60%, se apresentaram duas
#     crises com intervalo superior a 24 horas e se tem diagnóstico de síndrome epiléptica específica '''

# dados_epilepsia = {
#     'relatorio_epilepsia_1vez': relatorio_epilepsia_1vez,
#     'exames_solicitados': 'Não são obrigatórios exames, a critério do médico prescritor'
# }


# ############# Dislipidemia


# dislipidemia_1vez_exames = ['TGO', 'TGP', 'CPK', 'TSH', 'Colesterol total e frações (HDL e LDL)', 'Triglicerídeos']


# fibratos_1vez_exames = ['TGO', 'TGP', 'CPK', 'TSH', 'Triglicérides']

# dados_dislipidemia = {
#     'ac_nicotinico_trat_previo': 'Contraindicação ao uso de estatinas',
#     'dislipidemia_1vez_exames': dislipidemia_1vez_exames,
#     'fibratos_1vez_exames': fibratos_1vez_exames
# }

# ############# Dor crônica

# dados_dor = {
#     'eva': '5', ## de 4 a 10
#     'lanns_escore': '24' ## depois completar com as categorias individuais
# }



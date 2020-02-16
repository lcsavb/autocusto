from django.conf import settings
from django.forms.models import model_to_dict
from datetime import datetime
from .manejo_pdfs import GeradorPDF
from processos.models import Processo, Protocolo, Medicamento


def resgatar_prescricao(dados, processo):
    n = 1
    prescricao = processo.prescricao
    for item in prescricao.items():
        numero_medicamento = item[0]
        dados[f'id_med{n}'] = prescricao[numero_medicamento][f'id_med{n}']
        for i in prescricao[numero_medicamento].items():
            dados[i[0]] = i[1]
        n += 1
    return dados

def gerar_prescricao(meds_ids, dados_formulario):
        prescricao = {}
        n = 0
        for id in meds_ids:
            n += 1
            med_prescricao = {f'id_med{n}': id, 
                            f'med{n}_posologia_mes1': dados_formulario[f'med{n}_posologia_mes1'],
                            f'med{n}_posologia_mes2': dados_formulario[f'med{n}_posologia_mes2'],
                            f'med{n}_posologia_mes3': dados_formulario[f'med{n}_posologia_mes3'],
                            f'qtd_med{n}_mes1': dados_formulario[f'qtd_med{n}_mes1'],
                            f'qtd_med{n}_mes2': dados_formulario[f'qtd_med{n}_mes2'],
                            f'qtd_med{n}_mes3': dados_formulario[f'qtd_med{n}_mes3']
                            }
            if n == 1:
                med_prescricao['med1_via'] = dados_formulario['med1_via']
            prescricao[n] = med_prescricao
        return prescricao

def gera_med_dosagem(dados_formulario,ids_med_formulario):
    ''' Busca o medicamento pelo id. Retorna o nome, a dosagem, 
    apresentação e lista dos ids dos medicamentos '''
    meds_ids = []
    n = 0 
    for id_med in ids_med_formulario:
        n += 1
        if id_med != 'nenhum':
            meds_ids.append(id_med)
            med = Medicamento.objects.get(id=id_med)
            dados_formulario[f'med{n}'] = f'{med.nome} {med.dosagem} ({med.apres})'
    return dados_formulario, meds_ids

def listar_med(cid):
    ''' Recupera os medicamentos associados ao Protocolo e retorna uma lista de tuplas
    com o id e o medicamento com dosagem e apresentação respectivamente '''
    lista_med = [('nenhum', 'Escolha o medicamento...')]
    protocolo = Protocolo.objects.get(doenca__cid=cid)
    medicamentos = protocolo.medicamentos.all()
    for medicamento in medicamentos:
        item = ([medicamento.id, f'{medicamento.nome}' + ' ' + f'{medicamento.dosagem}' + ' - ' + f'{medicamento.apres}'])
        lista_med.append(item)
    return tuple(lista_med)

def associar_med(processo,meds):
    for med in meds:
        print(med)
        processo.medicamentos.add(med)
    # meds_cadastrados = processo.medicamentos.all()
    # print(meds_cadastrados)
    # for med_cadastrado in meds_cadastrados:
    #     med_id = med_cadastrado.id
    #     if med_id not in meds:
    #         print(med_cadastrado)
    #         processo.medicamentos.remove(med_id)
    # print(meds_cadastrados)

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
        'prescricao': modelo.prescricao,
        'cid':modelo.doenca.cid,
        'diagnostico':modelo.doenca.nome,
        'anamnese':modelo.anamnese,
        'tratou':modelo.tratou,
        'tratamentos_previos':modelo.tratamentos_previos,
        'preenchido_por':modelo.preenchido_por,
        'clinica': modelo.clinica,

    }
    return dicionario


def gerar_dados_renovacao(primeira_data, processo_id):
    ''' Usado na renovação rápida para gerar novo processo,
    mudando somente a data inicial. Retorna dados do processo 
    completos '''
    processo = Processo.objects.get(id=processo_id)
    dados = {}
    dados_processo = model_to_dict(processo)
    dados_paciente = model_to_dict(processo.paciente)
    dados_medico = model_to_dict(processo.medico)
    dados_clinica = model_to_dict(processo.clinica)
    # pdftk falha se input não for string!
    dados_clinica['medicos'] = ''
    dados_clinica['usuarios'] = ''
    end_clinica = dados_clinica['logradouro'] + ', ' + dados_clinica['logradouro_num']
    dados_clinica['end_clinica'] = end_clinica
    dados.update(dados_processo)
    dados.update(dados_paciente)
    dados.update(dados_medico)
    dados.update(dados_clinica)
    dados['data_1'] = datetime.strptime(primeira_data, '%d/%m/%Y')
    return dados  
    

def vincula_dados_emissor(usuario, medico, clinica, dados_formulario):
    ''' Vincula dos dados do emissor logado aos dados do processo '''
    end_clinica = clinica.logradouro + ', ' + clinica.logradouro_num
    dados_adicionais = {'nome_medico': medico.nome_medico,
                        'cns_medico': medico.cns_medico,
                        'nome_clinica': clinica.nome_clinica,
                        'cns_clinica': clinica.cns_clinica,
                        'end_clinica': end_clinica,
                        'cidade': clinica.cidade,
                        'bairro': clinica.bairro,
                        'cep': clinica.cep,
                        'telefone_clinica': clinica.telefone_clinica,
                        'usuario': usuario
                        }
    dados_formulario.update(dados_adicionais)
    return dados_formulario


def transfere_dados_gerador(dados, dados_condicionais):
    ''' Coleta os dados finais do processo, transfere ao gerador de PDF
    e retorna o PATH final do arquivo gerado '''
    pdf = GeradorPDF(dados,dados_condicionais,settings.PATH_LME_BASE)
    dados_pdf = pdf.generico(dados,settings.PATH_LME_BASE)
    path_pdf_final = dados_pdf[1] # a segunda variável que a função retorna é o path
    return path_pdf_final

def gerar_lista_meds_ids(dados):
    lista = [dados['id_med1'],dados['id_med2'],dados['id_med3'],dados['id_med4'],dados['id_med5']]
    return lista
    
def gerar_dados_edicao_parcial(dados, processo_id):
    ''' Gera o dicionário com os dados que serão atualizados
    com a renovação parcial e gera lista com os respectivos campos
    com a exceção do ID. '''

    ids_med_cadastrados = gerar_lista_meds_ids(dados)
    prescricao = gerar_prescricao(ids_med_cadastrados,dados)
    novos_dados = dict(
        id=processo_id,
        data1=dados['data_1'],
        prescricao=prescricao
        )

    lista_campos = []
    for key in novos_dados.keys():
        lista_campos.append(key)
    del lista_campos[0]
    
    return novos_dados, lista_campos


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



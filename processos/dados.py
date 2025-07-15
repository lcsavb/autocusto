import os
from django.conf import settings
from django.forms.models import model_to_dict
from datetime import datetime
from .manejo_pdfs import GeradorPDF
from processos.models import Processo, Protocolo, Medicamento
from pacientes.models import Paciente

# DEBUG: Print all PDF-related settings at module load
print(f"\n=== PDF SETTINGS DEBUG ===")
print(f"DEBUG: PATH_LME_BASE: {getattr(settings, 'PATH_LME_BASE', 'NOT_SET')}")
print(f"DEBUG: PATH_LME_BASE exists: {os.path.exists(getattr(settings, 'PATH_LME_BASE', '')) if hasattr(settings, 'PATH_LME_BASE') else 'NOT_SET'}")
print(f"DEBUG: PATH_RELATORIO: {getattr(settings, 'PATH_RELATORIO', 'NOT_SET')}")
print(f"DEBUG: PATH_RELATORIO exists: {os.path.exists(getattr(settings, 'PATH_RELATORIO', '')) if hasattr(settings, 'PATH_RELATORIO') else 'NOT_SET'}")
print(f"DEBUG: PATH_EXAMES: {getattr(settings, 'PATH_EXAMES', 'NOT_SET')}")
print(f"DEBUG: PATH_EXAMES exists: {os.path.exists(getattr(settings, 'PATH_EXAMES', '')) if hasattr(settings, 'PATH_EXAMES') else 'NOT_SET'}")
print(f"DEBUG: PATH_PDF_DIR: {getattr(settings, 'PATH_PDF_DIR', 'NOT_SET')}")
print(f"DEBUG: PATH_PDF_DIR exists: {os.path.exists(getattr(settings, 'PATH_PDF_DIR', '')) if hasattr(settings, 'PATH_PDF_DIR') else 'NOT_SET'}")
print(f"DEBUG: STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'NOT_SET')}")
print(f"DEBUG: STATIC_URL: {getattr(settings, 'STATIC_URL', 'NOT_SET')}")
if hasattr(settings, 'PATH_PDF_DIR') and os.path.exists(settings.PATH_PDF_DIR):
    try:
        protocols_list = os.listdir(settings.PATH_PDF_DIR)
        print(f"DEBUG: Available protocols: {protocols_list}")
    except Exception as e:
        print(f"DEBUG: Error listing protocols: {e}")
print(f"=== PDF SETTINGS DEBUG END ===\n")


def preparar_modelo(modelo, **kwargs):
    """Recebe o nome do model e os parâmetros a serem salvos,
    retorna preparado para ser salvo no banco"""
    modelo_parametrizado = modelo(**kwargs)
    return modelo_parametrizado


def resgatar_prescricao(dados, processo):
    n = 1
    prescricao = processo.prescricao
    for item in prescricao.items():
        numero_medicamento = item[0]
        if numero_medicamento != "":
            dados[f"id_med{n}"] = prescricao[numero_medicamento][f"id_med{n}"]
            for i in prescricao[numero_medicamento].items():
                dados[i[0]] = i[1]
            n += 1
    return dados


def gerar_prescricao(meds_ids, dados_formulario):
    prescricao = {}
    med_prescricao = {}
    n = 1
    for id in meds_ids:
        m = 1
        med_prescricao[f"id_med{n}"] = id
        while m <= 6:
            med_prescricao[f"med{n}_posologia_mes{m}"] = dados_formulario[
                f"med{n}_posologia_mes{m}"
            ]
            med_prescricao[f"qtd_med{n}_mes{m}"] = dados_formulario[
                f"qtd_med{n}_mes{m}"
            ]
            m += 1
        if n == 1:
            med_prescricao["med1_via"] = dados_formulario["med1_via"]
        prescricao[n] = med_prescricao
        med_prescricao = {}
        n += 1
    return prescricao


def gera_med_dosagem(dados_formulario, ids_med_formulario):
    """Busca o medicamento pelo id. Retorna o nome, a dosagem,
    apresentação e lista dos ids dos medicamentos"""
    meds_ids = []
    n = 0
    for id_med in ids_med_formulario:
        n += 1
        if id_med != "nenhum":
            meds_ids.append(id_med)
            med = Medicamento.objects.get(id=id_med)
            dados_formulario[f"med{n}"] = f"{med.nome} {med.dosagem} ({med.apres})"
    return dados_formulario, meds_ids


def listar_med(cid):
    """Recupera os medicamentos associados ao Protocolo e retorna uma lista de tuplas
    com o id e o medicamento com dosagem e apresentação respectivamente"""
    lista_med = [("nenhum", "Escolha o medicamento...")]
    protocolo = Protocolo.objects.get(doenca__cid=cid)
    medicamentos = protocolo.medicamentos.all()
    for medicamento in medicamentos:
        item = (
            medicamento.id,
            f"{medicamento.nome}"
            + " "
            + f"{medicamento.dosagem}"
            + " - "
            + f"{medicamento.apres}",
        )
        lista_med.append(item)
    return tuple(lista_med)


def associar_med(processo, meds):
    for med in meds:
        processo.medicamentos.add(med)
        meds_cadastrados = processo.medicamentos.all()
        for med_cadastrado in meds_cadastrados:
            if str(med_cadastrado.id) not in meds:
                processo.medicamentos.remove(med_cadastrado)


def cria_dict_renovação(modelo):
    dicionario = {
        # Dados paciente
        "nome_paciente": modelo.paciente.nome_paciente,
        "cpf_paciente": modelo.paciente.cpf_paciente,
        "peso": modelo.paciente.peso,
        "altura": modelo.paciente.altura,
        "nome_mae": modelo.paciente.nome_mae,
        "incapaz": modelo.paciente.incapaz,
        "nome_responsavel": modelo.paciente.nome_responsavel,
        "etnia": modelo.paciente.etnia,
        "telefone1_paciente": modelo.paciente.telefone1_paciente,
        "telefone2_paciente": modelo.paciente.telefone2_paciente,
        "email_paciente": modelo.paciente.email_paciente,
        "end_paciente": modelo.paciente.end_paciente,
        # Dados processo
        "prescricao": modelo.prescricao,
        "cid": modelo.doenca.cid,
        "diagnostico": modelo.doenca.nome,
        "anamnese": modelo.anamnese,
        "tratou": modelo.tratou,
        "tratamentos_previos": modelo.tratamentos_previos,
        "preenchido_por": modelo.preenchido_por,
        "clinica": modelo.clinica,
    }
    return dicionario


def gerar_dados_renovacao(primeira_data, processo_id):
    """Usado na renovação rápida para gerar novo processo,
    mudando somente a data inicial. Retorna dados do processo
    completos"""
    print(f"\n=== GERAR_DADOS_RENOVACAO START ===")
    print(f"DEBUG: primeira_data: {primeira_data}")
    print(f"DEBUG: processo_id: {processo_id}")
    
    processo = Processo.objects.get(id=processo_id)
    print(f"DEBUG: Found process: {processo.id} for patient {processo.paciente.nome_paciente}")
    print(f"DEBUG: Process CID: {processo.doenca.cid}")
    print(f"DEBUG: Process diagnosis: {processo.doenca.nome}")
    
    dados = {}
    lista_dados = [
        model_to_dict(processo),
        model_to_dict(processo.paciente),
        model_to_dict(processo.medico),
        model_to_dict(processo.clinica),
    ]
    for d in lista_dados:
        dados.update(d)
    
    print(f"DEBUG: Combined data keys: {list(dados.keys())}")
    
    # pdftk falha se input não for string!
    dados["medicos"] = ""
    dados["usuarios"] = ""
    dados["medicamentos"] = ""
    end_clinica = dados["logradouro"] + ", " + dados["logradouro_num"]
    dados["end_clinica"] = end_clinica
    
    # Validate and parse date
    if not primeira_data or primeira_data.strip() == "":
        print(f"ERROR: Empty date provided for renewal")
        raise ValueError("Data de renovação não pode estar vazia")
    
    try:
        dados["data_1"] = datetime.strptime(primeira_data, "%d/%m/%Y")
        print(f"DEBUG: Parsed renewal date: {dados['data_1']}")
    except ValueError as e:
        print(f"ERROR: Invalid date format '{primeira_data}': {e}")
        raise ValueError(f"Formato de data inválido: {primeira_data}. Use DD/MM/AAAA")
    
    dados["cid"] = processo.doenca.cid
    dados["diagnostico"] = processo.doenca.nome
    
    # CRITICAL: Setting conditional PDF flags for renovation
    dados["consentimento"] = False  # No consent for renewals
    dados["relatorio"] = False      # No report for renewals 
    dados["exames"] = False         # No exams for renewals
    
    # CHRONIC PAIN SPECIAL LOGIC: Include LANNS/EVA form for chronic pain renewals
    try:
        protocolo = processo.doenca.protocolo
        print(f"DEBUG: Protocol name: {protocolo.nome}")
        
        if protocolo.nome == "dor_crônica":
            print(f"DEBUG: Chronic pain protocol detected")
            print(f"DEBUG: Original dados_condicionais: {processo.dados_condicionais}")
            
            # For chronic pain, we need to include the LANNS/EVA assessment form
            # This will be picked up by the conditional PDFs glob pattern
            dados["include_lanns_eva"] = True
            
            # Preserve any conditional data from original process
            if processo.dados_condicionais:
                for key, value in processo.dados_condicionais.items():
                    dados[key] = value
                    print(f"DEBUG: Preserved conditional data: {key} = {value}")
            
            print(f"DEBUG: Set include_lanns_eva flag for chronic pain renewal")
            
    except Exception as e:
        print(f"ERROR: Failed to check protocol for conditional requirements: {e}")
    
    print(f"DEBUG: Set conditional flags - consent: {dados['consentimento']}, report: {dados['relatorio']}, exams: {dados['exames']}")
    
    resgatar_prescricao(dados, processo)
    print(f"DEBUG: Retrieved prescription data")
    
    meds_ids = gerar_lista_meds_ids(dados)
    print(f"DEBUG: Generated medication IDs: {meds_ids}")
    
    dados = gera_med_dosagem(dados, meds_ids)[0]
    print(f"DEBUG: Generated medication dosage data")
    
    print(f"DEBUG: Final data keys before return: {list(dados.keys())}")
    print(f"=== GERAR_DADOS_RENOVACAO END ===\n")
    return dados


def vincula_dados_emissor(usuario, medico, clinica, dados_formulario):
    """Vincula dos dados do emissor logado aos dados do processo"""
    end_clinica = clinica.logradouro + ", " + clinica.logradouro_num
    dados_adicionais = {
        "nome_medico": medico.nome_medico,
        "cns_medico": medico.cns_medico,
        "crm_medico": medico.crm_medico,
        "nome_clinica": clinica.nome_clinica,
        "cns_clinica": clinica.cns_clinica,
        "end_clinica": end_clinica,
        "cidade": clinica.cidade,
        "bairro": clinica.bairro,
        "cep": clinica.cep,
        "telefone_clinica": clinica.telefone_clinica,
        "usuario": usuario,
    }
    dados_formulario.update(dados_adicionais)
    return dados_formulario


def transfere_dados_gerador(dados):
    """Coleta os dados finais do processo, transfere ao gerador de PDF
    e retorna o PATH final do arquivo gerado"""
    try:
        print(f"\n=== TRANSFERE_DADOS_GERADOR START ===")
        print(f"DEBUG: Input data keys: {list(dados.keys())}")
        print(f"DEBUG: Patient CPF: {dados.get('cpf_paciente', 'NOT_FOUND')}")
        print(f"DEBUG: CID: {dados.get('cid', 'NOT_FOUND')}")
        print(f"DEBUG: Consent flag: {dados.get('consentimento', 'NOT_FOUND')}")
        print(f"DEBUG: Report flag: {dados.get('relatorio', 'NOT_FOUND')}")
        print(f"DEBUG: Exams flag: {dados.get('exames', 'NOT_FOUND')}")
        print(f"DEBUG: Data_1: {dados.get('data_1', 'NOT_FOUND')}")
        print(f"DEBUG: Medication ID 1: {dados.get('id_med1', 'NOT_FOUND')}")
        print(f"DEBUG: PATH_LME_BASE: {settings.PATH_LME_BASE}")
        print(f"DEBUG: PATH_LME_BASE exists: {os.path.exists(settings.PATH_LME_BASE)}")
        
        pdf = GeradorPDF(dados, settings.PATH_LME_BASE)
        print(f"DEBUG: GeradorPDF instance created")
        
        dados_pdf = pdf.generico(dados, settings.PATH_LME_BASE)
        print(f"DEBUG: generico method returned: {dados_pdf}")
        
        if dados_pdf is None or dados_pdf[0] is None or dados_pdf[1] is None:
            print(f"ERROR: PDF generation failed in transfere_dados_gerador")
            print(f"ERROR: dados_pdf result: {dados_pdf}")
            return None
        
        path_pdf_final = dados_pdf[1]  # a segunda variável que a função retorna é o path
        print(f"DEBUG: PDF generated successfully: {path_pdf_final}")
        print(f"DEBUG: Final PDF file exists: {os.path.exists(dados_pdf[0]) if dados_pdf[0] else 'No file path'}")
        print(f"=== TRANSFERE_DADOS_GERADOR END ===\n")
        return path_pdf_final
    except Exception as e:
        print(f"ERROR: Exception in transfere_dados_gerador: {e}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        return None


def gerar_lista_meds_ids(dados):
    n = 1
    lista = []
    while n <= 4:
        try:
            if dados[f"id_med{n}"] != "nenhum":
                lista.append(dados[f"id_med{n}"])
        except KeyError:
            pass # Continue if key is missing, as it means no more meds are selected
        n += 1
    return lista


def gerar_dados_edicao_parcial(dados, processo_id):
    """Gera o dicionário com os dados que serão atualizados
    com a renovação parcial e gera lista com os respectivos campos
    com a exceção do ID."""

    ids_med_cadastrados = gerar_lista_meds_ids(dados)
    prescricao = gerar_prescricao(ids_med_cadastrados, dados)
    novos_dados = dict(id=processo_id, data1=dados["data_1"], prescricao=prescricao)

    lista_campos = []
    for key in novos_dados.keys():
        lista_campos.append(key)
    del lista_campos[0]

    return novos_dados, lista_campos


def gerar_dados_paciente(dados):
    dados_paciente = dict(
        nome_paciente=dados["nome_paciente"],
        cpf_paciente=dados["cpf_paciente"],
        peso=dados["peso"],
        altura=dados["altura"],
        nome_mae=dados["nome_mae"],
        incapaz=dados["incapaz"],
        nome_responsavel=dados["nome_responsavel"],
        etnia=dados["etnia"],
        telefone1_paciente=dados["telefone1_paciente"],
        telefone2_paciente=dados["telefone2_paciente"],
        email_paciente=dados["email_paciente"],
        end_paciente=dados["end_paciente"],
    )
    return dados_paciente


def gerar_dados_processo(dados, meds_ids, doenca, emissor, paciente, usuario):
    prescricao = gerar_prescricao(meds_ids, dados)
    dados_processo = dict(
        prescricao=prescricao,
        anamnese=dados["anamnese"],
        tratou=dados["tratou"],
        tratamentos_previos=dados["tratamentos_previos"],
        doenca=doenca,
        preenchido_por=dados["preenchido_por"],
        medico=emissor.medico,
        paciente=paciente,
        clinica=emissor.clinica,
        emissor=emissor,
        usuario=usuario,
        dados_condicionais={},
    )
    for dado in dados.items():
        if dado[0].startswith("opt_"):
            dados_processo["dados_condicionais"][dado[0]] = dado[1]
    return dados_processo


def registrar_db(dados, meds_ids, doenca, emissor, usuario, **kwargs):
    """Reúne todos os dados, salva no banco de dados e retorna
    o id do processo salvo"""
    paciente_existe = kwargs.pop("paciente_existe")
    dados_paciente = gerar_dados_paciente(dados)
    cpf_paciente = dados["cpf_paciente"]

    if paciente_existe:
        dados_paciente["id"] = paciente_existe.pk
        paciente = preparar_modelo(Paciente, **dados_paciente)
        dados_processo = gerar_dados_processo(
            dados, meds_ids, doenca, emissor, paciente, usuario
        )
        dados_processo["paciente"] = paciente_existe
        cid = kwargs.pop("cid", None)
        processo_existe = False
        for p in paciente_existe.processos.all():
            if p.doenca.cid == cid:
                processo_existe = True
                dados_processo["id"] = p.id
                break

        processo = preparar_modelo(Processo, **dados_processo)

        if processo_existe:
            processo.save(force_update=True)
        else:
            processo.save()
        paciente.save(force_update=True)
        associar_med(processo, meds_ids)
        paciente.usuarios.add(usuario)
        emissor.pacientes.add(paciente_existe)
    else:
        paciente = preparar_modelo(Paciente, **dados_paciente)
        paciente.save()
        paciente = Paciente.objects.get(cpf_paciente=cpf_paciente)
        dados_processo = gerar_dados_processo(
            dados, meds_ids, doenca, emissor, paciente, usuario
        )
        processo = preparar_modelo(Processo, **dados_processo)
        processo.save()
        associar_med(processo, meds_ids)
        usuario.pacientes.add(paciente)
        emissor.pacientes.add(paciente)

    return processo.pk


def checar_paciente_existe(cpf_paciente):
    try:
        paciente_existe = Paciente.objects.get(cpf_paciente=cpf_paciente)
    except Paciente.DoesNotExist:
        paciente_existe = False
    return paciente_existe


def gerar_link_protocolo(cid):
    protocolo = Protocolo.objects.get(doenca__cid=cid)
    arquivo = protocolo.arquivo
    link = os.path.join(settings.STATIC_URL, "protocolos", arquivo)
    return link


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
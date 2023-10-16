
import os
from django import forms
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.forms.models import model_to_dict
from datetime import datetime
from .manejo_pdfs import GeradorPDF
from processos.models import Processo, Protocolo, Medicamento
from pacientes.models import Paciente

def preparar_modelo(modelo, **kwargs):
    ' Recebe o nome do model e os parâmetros a serem salvos,\n    retorna preparado para ser salvo no banco '
    parameterized_model = modelo(**kwargs)
    return parameterized_model

def resgatar_prescricao(dados, processo):
    n = 1
    prescription = process.prescricao
    for item in prescription.items():
        medicine_number = item[0]
        if (medicine_number != ''):
            data[f'id_med{n}'] = prescription[medicine_number][f'id_med{n}']
            for i in prescription[medicine_number].items():
                data[i[0]] = i[1]
            n += 1
    return data

def gerar_prescricao(meds_ids, dados_formulario):
    prescription = {}
    med_prescription = {}
    n = 1
    for id in meds_ids:
        m = 1
        med_prescription[f'id_med{n}'] = id
        while (m <= 6):
            med_prescription[f'med{n}_posologia_mes{m}'] = form_data[f'med{n}_posologia_mes{m}']
            med_prescription[f'qtd_med{n}_mes{m}'] = form_data[f'qtd_med{n}_mes{m}']
            m += 1
        if (n == 1):
            med_prescription['med1_via'] = form_data['med1_via']
        prescription[n] = med_prescription
        med_prescription = {}
        n += 1
    return prescription

def gera_med_dosagem(dados_formulario, ids_med_formulario):
    ' Busca o medicamento pelo id. Retorna o nome, a dosagem, \n    apresentação e lista dos ids dos medicamentos '
    meds_ids = []
    n = 0
    for id_med in ids_med_formulario:
        n += 1
        if (id_med != 'nenhum'):
            meds_ids.append(id_med)
            med = Medicamento.objects.get(id=id_med)
            form_data[f'med{n}'] = f'{med.nome} {med.dosagem} ({med.apres})'
    return (form_data, meds_ids)

def listar_med(cid):
    ' Recupera os medicamentos associados ao Protocolo e retorna uma lista de tuplas\n    com o id e o medicamento com dosagem e apresentação respectivamente '
    med_list = [('nenhum', 'Escolha o medicamento...')]
    protocol = Protocolo.objects.get(doenca__cid=icd)
    medications = protocol.medicamentos.all()
    for medication in medications:
        item = [medication.id, ((((f'{medication.nome}' + ' ') + f'{medication.dosagem}') + ' - ') + f'{medication.apres}')]
        med_list.append(item)
    return tuple(med_list)

def associar_med(processo, meds):
    for med in meds:
        process.medicamentos.add(med)
        registered_meds = process.medicamentos.all()
        for med_cadastrado in registered_meds:
            if (str(med_cadastrado.id) not in meds):
                process.medicamentos.remove(med_cadastrado)

def cria_dict_renovação(modelo):
    dictionary = {'nome_paciente': modelo.paciente.nome_paciente, 'cpf_paciente': modelo.paciente.cpf_paciente, 'peso': modelo.paciente.peso, 'altura': modelo.paciente.altura, 'nome_mae': modelo.paciente.nome_mae, 'incapaz': modelo.paciente.incapaz, 'nome_responsavel': modelo.paciente.nome_responsavel, 'etnia': modelo.paciente.etnia, 'telefone1_paciente': modelo.paciente.telefone1_paciente, 'telefone2_paciente': modelo.paciente.telefone2_paciente, 'email_paciente': modelo.paciente.email_paciente, 'end_paciente': modelo.paciente.end_paciente, 'prescricao': modelo.prescricao, 'cid': modelo.doenca.cid, 'diagnostico': modelo.doenca.nome, 'anamnese': modelo.anamnese, 'tratou': modelo.tratou, 'tratamentos_previos': modelo.tratamentos_previos, 'preenchido_por': modelo.preenchido_por, 'clinica': modelo.clinica}
    return dictionary

def gerar_dados_renovacao(primeira_data, processo_id):
    ' Usado na renovação rápida para gerar novo processo,\n    mudando somente a data inicial. Retorna dados do processo \n    completos '
    process = Processo.objects.get(id=process_id)
    data = {}
    lista_dados = [model_to_dict(process), model_to_dict(process.paciente), model_to_dict(process.medico), model_to_dict(process.clinica)]
    for d in lista_dados:
        data.update(d)
    data['medicos'] = ''
    data['usuarios'] = ''
    data['medicamentos'] = ''
    clinic_address = ((data['logradouro'] + ', ') + data['logradouro_num'])
    data['end_clinica'] = clinic_address
    data['data_1'] = datetime.strptime(first_date, '%d/%m/%Y')
    data['cid'] = process.doenca.cid
    data['diagnostico'] = process.doenca.nome
    data['consentimento'] = False
    data['relatorio'] = False
    data['exames'] = False
    resgatar_prescricao(data, process)
    meds_ids = gerar_lista_meds_ids(data)
    data = gera_med_dosagem(data, meds_ids)[0]
    return data

def vincula_dados_emissor(usuario, medico, clinica, dados_formulario):
    ' Vincula dos dados do emissor logado aos dados do processo '
    clinic_address = ((clinic.logradouro + ', ') + clinic.logradouro_num)
    additional_data = {'nome_medico': medico.nome_medico, 'cns_medico': medico.cns_medico, 'crm_medico': medico.crm_medico, 'nome_clinica': clinic.nome_clinica, 'cns_clinica': clinic.cns_clinica, 'end_clinica': clinic_address, 'cidade': clinic.cidade, 'bairro': clinic.bairro, 'cep': clinic.cep, 'telefone_clinica': clinic.telefone_clinica, 'usuario': usuario}
    form_data.update(additional_data)
    return form_data

def transfere_dados_gerador(dados):
    ' Coleta os dados finais do processo, transfere ao gerador de PDF\n    e retorna o PATH final do arquivo gerado '
    pdf = GeradorPDF(data, settings.PATH_LME_BASE)
    pdf_data = pdf.generico(data, settings.PATH_LME_BASE)
    path_pdf_final = pdf_data[1]
    return path_pdf_final

def gerar_lista_meds_ids(dados):
    n = 1
    list = []
    while (n <= 4):
        try:
            if (data[f'id_med{n}'] != 'nenhum'):
                list.append(data[f'id_med{n}'])
                n = (n + 1)
            else:
                break
        except:
            break
    return list

def gerar_dados_edicao_parcial(dados, processo_id):
    ' Gera o dicionário com os dados que serão atualizados\n    com a renovação parcial e gera lista com os respectivos campos\n    com a exceção do ID. '
    ids_med_cadastrados = gerar_lista_meds_ids(data)
    prescription = gerar_prescricao(ids_med_cadastrados, data)
    new_data = dict(id=process_id, data1=data['data_1'], prescricao=prescription)
    fields_list = []
    for key in new_data.keys():
        fields_list.append(key)
    del fields_list[0]
    return (new_data, fields_list)

def gerar_dados_paciente(dados):
    patient_data = dict(nome_paciente=data['nome_paciente'], cpf_paciente=data['cpf_paciente'], peso=data['peso'], altura=data['altura'], nome_mae=data['nome_mae'], incapaz=data['incapaz'], nome_responsavel=data['nome_responsavel'], etnia=data['etnia'], telefone1_paciente=data['telefone1_paciente'], telefone2_paciente=data['telefone2_paciente'], email_paciente=data['email_paciente'], end_paciente=data['end_paciente'])
    return patient_data

def gerar_dados_processo(dados, meds_ids, doenca, emissor, paciente, usuario):
    prescription = gerar_prescricao(meds_ids, data)
    process_data = dict(prescricao=prescription, anamnese=data['anamnese'], tratou=data['tratou'], tratamentos_previos=data['tratamentos_previos'], doenca=disease, preenchido_por=data['preenchido_por'], medico=emissor.medico, paciente=patient, clinica=emissor.clinica, emissor=emissor, usuario=usuario, dados_condicionais={})
    for dado in data.items():
        if dado[0].startswith('opt_'):
            process_data['dados_condicionais'][dado[0]] = dado[1]
    return process_data

def registrar_db(dados, meds_ids, doenca, emissor, usuario, **kwargs):
    'Reúne todos os dados, salva no banco de dados e retorna\n        o id do processo salvo '
    patient_exists = kwargs.pop('paciente_existe')
    patient_data = gerar_dados_paciente(data)
    patient_cpf = data['cpf_paciente']
    if (patient_exists != False):
        patient_data['id'] = patient_exists.pk
        patient = preparar_modelo(Paciente, **patient_data)
        process_data = gerar_dados_processo(data, meds_ids, disease, emissor, patient, usuario)
        process_data['paciente'] = patient_exists
        icd = kwargs.pop('cid', None)
        for p in patient_exists.processos.all():
            if (p.doenca.cid == icd):
                process_exists = True
                process_data['id'] = p.id
            else:
                continue
        process = preparar_modelo(Processo, **process_data)
        try:
            if process_exists:
                process.save(force_update=True)
        except:
            process.save()
        patient.save(force_update=True)
        associar_med(process, meds_ids)
        patient.usuarios.add(usuario)
        emissor.pacientes.add(patient_exists)
    else:
        patient = preparar_modelo(Paciente, **patient_data)
        patient.save()
        patient = Paciente.objects.get(cpf_paciente=patient_cpf)
        process_data = gerar_dados_processo(data, meds_ids, disease, emissor, patient, usuario)
        process = preparar_modelo(Processo, **process_data)
        process.save()
        associar_med(process, meds_ids)
        usuario.pacientes.add(patient)
        emissor.pacientes.add(patient)
    return process.pk

def checar_paciente_existe(cpf_paciente):
    try:
        patient_exists = Paciente.objects.get(cpf_paciente=patient_cpf)
    except:
        patient_exists = False
    return patient_exists

def gerar_link_protocolo(cid):
    protocol = Protocolo.objects.get(doenca__cid=icd)
    file = protocol.arquivo
    link = os.path.join(settings.STATIC_URL, 'protocolos', file)
    return link

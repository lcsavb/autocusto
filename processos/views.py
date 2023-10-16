
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.conf import settings
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from datetime import date
from medicos.models import Medico
from medicos.seletor import medico as seletor_medico
from pacientes.models import Paciente
from processos.models import Processo, Protocolo, Medicamento, Doenca
from usuarios.models import Usuario
from clinicas.models import Clinica, Emissor
from .forms import NovoProcesso, RenovarProcesso, mostrar_med, ajustar_campos_condicionais, extrair_campos_condicionais, fabricar_formulario
import os
import pypdftk
from .manejo_pdfs import GeradorPDF
from .dados import cria_dict_renovação, gerar_dados_renovacao, vincula_dados_emissor, transfere_dados_gerador, listar_med, gera_med_dosagem, resgatar_prescricao, gerar_lista_meds_ids, gerar_link_protocolo

@login_required
def busca_processos(request):
    if (request.method == 'GET'):
        usuario = request.user
        user_patients = usuario.pacientes.all()
        contexto = {'pacientes_usuario': user_patients, 'usuario': usuario}
        return render(request, 'processos/busca.html', contexto)
    else:
        process_id = request.POST.get('processo_id')
        request.session['processo_id'] = process_id
        process = Processo.objects.get(id=process_id)
        request.session['cid'] = process.doenca.cid
        return redirect('processos-edicao')

@login_required
def edicao(request):
    usuario = request.user
    medico = seletor_medico(usuario)
    clinics = medico.clinicas.all()
    choices = tuple([(c.id, c.nome_clinica) for c in clinics])
    icd = request.session['cid']
    medications = listar_med(icd)
    FormModel = fabricar_formulario(icd, True)
    try:
        process_id = request.session['processo_id']
        process = Processo.objects.get(id=process_id)
    except:
        raise ValueError
    try:
        first_date = request.session['data1']
    except:
        first_date = date.today().strftime('%d/%m/%Y')
    if (request.method == 'POST'):
        form = FormModel(choices, medications, request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            clinic_id = form_data['clinicas']
            clinic = medico.clinicas.get(id=clinic_id)
            ids_med_cadastrados = gerar_lista_meds_ids(form_data)
            (form_data, meds_ids) = gera_med_dosagem(form_data, ids_med_cadastrados)
            data = vincula_dados_emissor(usuario, medico, clinic, form_data)
            form.save(usuario, medico, process_id, meds_ids)
            path_pdf_final = transfere_dados_gerador(data)
            request.session['path_pdf_final'] = path_pdf_final
            request.session['processo_id'] = process_id
            return redirect('processos-pdf')
    else:
        initial_data = cria_dict_renovação(process)
        initial_data['data_1'] = first_date
        initial_data['clinicas'] = initial_data['clinica'].id
        initial_data = resgatar_prescricao(initial_data, process)
        form = FormModel(choices, medications, initial=initial_data)
        conditional_fields = extrair_campos_condicionais(form)
        protocol_link = gerar_link_protocolo(icd)
    contexto = {'formulario': form, 'processo': process, 'campos_condicionais': conditional_fields, 'link_protocolo': protocol_link}
    contexto.update(mostrar_med(True, process))
    return render(request, 'processos/edicao.html', contexto)

@login_required
def renovacao_rapida(request):
    if (request.method == 'GET'):
        search = request.GET.get('b')
        usuario = request.user
        request.session['busca'] = search
        user_patients = usuario.pacientes.all()
        search_patients = user_patients.filter((Q(nome_paciente__icontains=search) | Q(cpf_paciente__icontains=search)))
        contexto = {'busca_pacientes': search_patients, 'usuario': usuario}
        return render(request, 'processos/renovacao_rapida.html', contexto)
    else:
        process_id = request.POST.get('processo_id')
        new_date = request.POST.get('data_1')
        try:
            if request.POST['edicao']:
                request.session['processo_id'] = process_id
                request.session['cid'] = Processo.objects.get(id=process_id).doenca.cid
                request.session['data1'] = new_date
                return redirect('processos-edicao')
        except:
            data = gerar_dados_renovacao(new_date, process_id)
            path_pdf_final = transfere_dados_gerador(data)
            return redirect(path_pdf_final)

@login_required
def cadastro(request):
    usuario = request.user
    medico = seletor_medico(usuario)
    clinics = medico.clinicas.all()
    choices = tuple([(c.id, c.nome_clinica) for c in clinics])
    patient_exists = request.session['paciente_existe']
    first_date = date.today().strftime('%d/%m/%Y')
    icd = request.session['cid']
    medications = listar_med(icd)
    FormModel = fabricar_formulario(icd, False)
    if (request.method == 'POST'):
        form = FormModel(choices, medications, request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            clinic_id = form_data['clinicas']
            clinic = medico.clinicas.get(id=clinic_id)
            ids_med_cadastrados = gerar_lista_meds_ids(form_data)
            (form_data, meds_ids) = gera_med_dosagem(form_data, ids_med_cadastrados)
            data = vincula_dados_emissor(usuario, medico, clinic, form_data)
            process_id = form.save(usuario, medico, meds_ids)
            path_pdf_final = transfere_dados_gerador(data)
            request.session['path_pdf_final'] = path_pdf_final
            request.session['processo_id'] = process_id
            return redirect('processos-pdf')
    else:
        if (not usuario.clinicas.exists()):
            return redirect('clinicas-cadastro')
        if patient_exists:
            patient_id = request.session['paciente_id']
            patient = Paciente.objects.get(id=patient_id)
            patient_data = model_to_dict(patient)
            patient_data['diagnostico'] = Doenca.objects.get(cid=icd).nome
            patient_data['cid'] = request.session['cid']
            patient_data['data_1'] = first_date
            (campos_ajustados, patient_data) = ajustar_campos_condicionais(patient_data)
            form = FormModel(choices, medications, initial=patient_data)
            conditional_fields = extrair_campos_condicionais(form)
            protocol_link = gerar_link_protocolo(icd)
            contexto = {'formulario': form, 'paciente_existe': patient_exists, 'paciente': patient, 'campos_condicionais': conditional_fields, 'link_protocolo': protocol_link}
            contexto.update(campos_ajustados)
        else:
            protocol_link = gerar_link_protocolo(icd)
            initial_data = {'cpf_paciente': request.session['cpf_paciente'], 'data_1': first_date, 'cid': icd, 'diagnostico': Doenca.objects.get(cid=icd).nome}
            form = FormModel(choices, medications, initial=initial_data)
            conditional_fields = extrair_campos_condicionais(form)
            contexto = {'formulario': form, 'paciente_existe': patient_exists, 'campos_condicionais': conditional_fields, 'link_protocolo': protocol_link}
        contexto.update(mostrar_med(False))
        return render(request, 'processos/cadastro.html', contexto)

@login_required
def pdf(request):
    if (request.method == 'GET'):
        pdf_link = request.session['path_pdf_final']
        contexto = {'link_pdf': pdf_link}
        return render(request, 'processos/pdf.html', contexto)

from django.shortcuts import render
from .forms import ClinicaFormulario
from medicos.models import Medico

def cadastro(request):
    usuario = request.user
    medico = usuario.medico

    f_clinica_ativa = ''

    if request.method == 'POST':
        f_clinica = ClinicaFormulario(request.POST)
        
        if f_clinica.is_valid():
            instance = f_clinica.save(commit=False)
            instance.usuario = usuario
            instance.save()
            instance.medicos.add(medico)

            dados = f_clinica.cleaned_data
            ativa = dados['ativa']

            #transformar em função, pois usarei em outros lugares
            if ativa:
                modelo_medico = Medico.objects.get(usuario=usuario)
                modelo_medico.clinica_ativa_nome = dados['nome_clinica']
                modelo_medico.clinica_ativa_cns = dados['cns_clinica']
                modelo_medico.clinica_ativa_bairro = dados['bairro']
                modelo_medico.clinica_ativa_cep = dados['cep']
                modelo_medico.clinica_ativa_cidade = dados['cidade']
                modelo_medico.clinica_ativa_telefone = dados['telefone_clinica']


                modelo_medico.save(update_fields=['clinica_ativa_nome', 
                'clinica_ativa_cidade', 'clinica_ativa_bairro', 'clinica_ativa_cep',
                'clinica_ativa_telefone', 'clinica_ativa_cns', 'clinica_ativa_end'
                  ]
                  )
            else:
                pass
           
    else:
        f_clinica = ClinicaFormulario()

    contexto = {'f_clinica': f_clinica, 'f_clinica_ativa': f_clinica_ativa}

    return render(request, 'clinicas/cadastro.html', contexto)
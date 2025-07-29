from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .forms import ClinicaFormulario
from medicos.seletor import medico as seletor_medico
from clinicas.models import Clinica, ClinicaVersion, ClinicaUsuario, ClinicaUsuarioVersion
import logging

logger = logging.getLogger(__name__)


@login_required
@transaction.atomic
def cadastro(request):
    """
    Handles clinic registration/update with versioning system.
    
    Key changes from original:
    - Creates new versions instead of updating existing clinics
    - Each user works with their own version of clinic data
    - Maintains complete history of all changes
    """
    usuario = request.user
    medico = seletor_medico(usuario)

    if request.method == "POST":
        f_clinica = ClinicaFormulario(request.POST)

        if f_clinica.is_valid():
            dados = f_clinica.cleaned_data

            try:
                # Check if clinic already exists based on CNS
                clinica_existe = Clinica.objects.filter(
                    cns_clinica__exact=dados["cns_clinica"]
                ).first()

                if clinica_existe:
                    # Clinic exists - create a new version for this user
                    version_data = {
                        'nome_clinica': dados['nome_clinica'],
                        'logradouro': dados['logradouro'],
                        'logradouro_num': dados['logradouro_num'],
                        'cidade': dados['cidade'],
                        'bairro': dados['bairro'],
                        'cep': dados['cep'],
                        'telefone_clinica': dados['telefone_clinica'],
                    }
                    
                    # Create new version
                    new_version = clinica_existe.create_new_version(usuario, version_data)
                    
                    # Ensure user is connected to clinic
                    clinica_usuario, created = ClinicaUsuario.objects.get_or_create(
                        usuario=usuario,
                        clinica=clinica_existe
                    )
                    
                    # Update user's version assignment
                    ClinicaUsuarioVersion.objects.update_or_create(
                        clinica_usuario=clinica_usuario,
                        defaults={'version': new_version}
                    )
                    
                    # Add doctor to clinic if not already added
                    if not clinica_existe.medicos.filter(id=medico.id).exists():
                        clinica_existe.medicos.add(medico)
                    
                    messages.success(
                        request, f'Sua versão da clínica {dados["nome_clinica"]} foi criada com sucesso!'
                    )
                    
                    if "paciente_existe" in request.session and "cid" in request.session:
                        return redirect("processos-cadastro")
                    else:
                        return redirect("home")
                else:
                    # New clinic - create master record and first version
                    clinica = Clinica.objects.create(
                        cns_clinica=dados["cns_clinica"],
                        # Keep minimal data in master record
                        nome_clinica=dados["nome_clinica"]  # For backward compatibility
                    )
                    
                    # Create first version
                    version_data = {
                        'nome_clinica': dados['nome_clinica'],
                        'logradouro': dados['logradouro'],
                        'logradouro_num': dados['logradouro_num'],
                        'cidade': dados['cidade'],
                        'bairro': dados['bairro'],
                        'cep': dados['cep'],
                        'telefone_clinica': dados['telefone_clinica'],
                    }
                    
                    first_version = ClinicaVersion.objects.create(
                        clinica=clinica,
                        created_by=usuario,
                        version_number=1,
                        status='active',
                        change_summary='Cadastro inicial da clínica',
                        **version_data
                    )
                    
                    # Associate user with clinic
                    clinica_usuario = ClinicaUsuario.objects.create(
                        usuario=usuario,
                        clinica=clinica
                    )
                    
                    # Assign version to user
                    ClinicaUsuarioVersion.objects.create(
                        clinica_usuario=clinica_usuario,
                        version=first_version
                    )
                    
                    # Associate doctor with clinic
                    clinica.medicos.add(medico)
                    
                    messages.success(
                        request, f'Clínica {dados["nome_clinica"]} cadastrada com sucesso!'
                    )
                    
                    if "paciente_existe" in request.session and "cid" in request.session:
                        return redirect("processos-cadastro")
                    else:
                        return redirect("home")
                    
            except ValidationError as e:
                logger.warning(f"Validation error in clinic form: {e}")
                if hasattr(e, 'error_dict'):
                    for field, errors in e.error_dict.items():
                        for error in errors:
                            if field == 'telefone_clinica':
                                messages.error(request, f"Telefone inválido: {error}")
                            else:
                                messages.error(request, f"{error}")
                else:
                    messages.error(request, f"Erro de validação: {e}")
                    
            except IntegrityError as e:
                logger.error(f"Database integrity error in clinic form: {e}")
                if "telefone_clinica" in str(e):
                    messages.error(request, "Telefone muito longo. Use o formato (11) 12345-6789")
                elif "cns_clinica" in str(e):
                    messages.error(request, "CNS já está em uso por outra clínica")
                else:
                    messages.error(request, "Erro ao salvar clínica. Verifique os dados informados.")
                    
            except Exception as e:
                logger.error(f"Unexpected error in clinic form: {e}")
                messages.error(request, "Erro inesperado ao salvar clínica. Tente novamente.")
        else:
            for field, errors in f_clinica.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        f_clinica = ClinicaFormulario()

    contexto = {"f_clinica": f_clinica}

    return render(request, "clinicas/cadastro.html", contexto)


@login_required
def list_clinics(request):
    """Return user's clinics with their specific versions as JSON"""
    try:
        user = request.user
        clinics_data = []
        
        # Get all clinics the user has access to
        for clinica_usuario in ClinicaUsuario.objects.filter(usuario=user).select_related('clinica'):
            clinica = clinica_usuario.clinica
            # Get user's version of this clinic
            version = clinica.get_version_for_user(user)
            
            if version:
                clinics_data.append({
                    'id': clinica.id,
                    'nome_clinica': version.nome_clinica,
                    'cns_clinica': clinica.cns_clinica,
                    'version_number': version.version_number,
                    'version_status': version.status
                })
        
        return JsonResponse(clinics_data, safe=False)
    except Exception as e:
        logger.error(f"Error listing clinics for user {request.user.id}: {e}")
        return JsonResponse({'error': 'Erro ao carregar clínicas'}, status=500)


@login_required
def get_clinic(request, clinic_id):
    """Return user's version of clinic data as JSON"""
    try:
        user = request.user
        clinic = get_object_or_404(Clinica, id=clinic_id)
        
        # Check user has access
        if not ClinicaUsuario.objects.filter(usuario=user, clinica=clinic).exists():
            return JsonResponse({'error': 'Acesso negado'}, status=403)
        
        # Get user's version
        version = clinic.get_version_for_user(user)
        
        if not version:
            return JsonResponse({'error': 'Versão não encontrada'}, status=404)
        
        data = {
            'id': clinic.id,
            'nome_clinica': version.nome_clinica,
            'cns_clinica': clinic.cns_clinica,
            'logradouro': version.logradouro,
            'logradouro_num': version.logradouro_num,
            'cidade': version.cidade,
            'bairro': version.bairro,
            'cep': version.cep,
            'telefone_clinica': version.telefone_clinica,
            'version_number': version.version_number,
            'version_created_by': version.created_by.email if version.created_by else 'Sistema',
            'version_created_at': version.created_at.isoformat()
        }
        
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error getting clinic {clinic_id} for user {request.user.id}: {e}")
        return JsonResponse({'error': 'Erro ao carregar dados da clínica'}, status=500)
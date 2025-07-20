from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .forms import ClinicaFormulario
from medicos.seletor import medico as seletor_medico
from clinicas.models import Clinica
import logging

logger = logging.getLogger(__name__)


@login_required
@transaction.atomic
def cadastro(request):
    """
    Handles clinic registration/update with complex business logic for Brazilian medical facilities.
    
    This view implements a sophisticated clinic management system that handles:
    1. New clinic registration
    2. Updates to existing clinics (based on CNS - National Health Service code)
    3. Multi-user clinic access (multiple doctors can be associated with same clinic)
    4. Atomic transactions to ensure data consistency
    
    The CNS-based logic allows multiple doctors to register the same physical clinic,
    creating shared access while maintaining data integrity.
    """
    usuario = request.user
    medico = seletor_medico(usuario)

    if request.method == "POST":
        f_clinica = ClinicaFormulario(request.POST)

        if f_clinica.is_valid():
            dados = f_clinica.cleaned_data

            try:
                # Check if clinic already exists based on CNS (National Health Service) code
                # CNS is unique identifier for medical facilities in Brazil
                clinica_existe = Clinica.objects.filter(
                    cns_clinica__exact=dados["cns_clinica"]
                )

                if clinica_existe:
                    # Clinic exists - this is an update operation
                    # Multiple doctors can update the same clinic (shared facilities)
                    instance = f_clinica.save(commit=False)
                    instance.pk = clinica_existe[0].pk  # Use existing clinic's primary key
                    
                    # For updates, validate without unique constraints since we're updating existing record
                    # This prevents false positive validation errors on fields that are already unique
                    instance.full_clean(exclude=['id'])
                    instance.save(force_update=True)  # Explicitly update existing record
                    
                    # Add current user and doctor to clinic's associations
                    # This allows multiple doctors to access the same clinic
                    instance.usuarios.add(usuario)
                    instance.medicos.add(medico)
                    
                    messages.success(
                        request, f'Clínica {dados["nome_clinica"]} atualizada com sucesso!'
                    )
                    # Check if coming from setup flow - if session has process data, redirect back
                    if "paciente_existe" in request.session and "cid" in request.session:
                        return redirect("processos-cadastro")
                    else:
                        return redirect("home")
                else:
                    # New clinic - create fresh record
                    instance = f_clinica.save(commit=False)
                    
                    # For new records, validate everything including unique constraints
                    instance.full_clean()
                    instance.save()
                    
                    # Associate clinic with current user and doctor
                    instance.usuarios.add(usuario)
                    instance.medicos.add(medico)
                    
                    messages.success(
                        request, f'Clínica {dados["nome_clinica"]} cadastrada com sucesso!'
                    )
                    # Check if coming from setup flow - if session has process data, redirect back
                    if "paciente_existe" in request.session and "cid" in request.session:
                        return redirect("processos-cadastro")
                    else:
                        return redirect("home")
                    
            except ValidationError as e:
                # Handle model validation errors
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
                # Handle database integrity errors
                logger.error(f"Database integrity error in clinic form: {e}")
                if "telefone_clinica" in str(e):
                    messages.error(request, "Telefone muito longo. Use o formato (11) 12345-6789")
                elif "cns_clinica" in str(e):
                    messages.error(request, "CNS já está em uso por outra clínica")
                else:
                    messages.error(request, "Erro ao salvar clínica. Verifique os dados informados.")
                    
            except Exception as e:
                # Handle any other unexpected errors
                logger.error(f"Unexpected error in clinic form: {e}")
                messages.error(request, "Erro inesperado ao salvar clínica. Tente novamente.")
        else:
            # Form validation failed - add errors as Django messages for toast display
            for field, errors in f_clinica.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        f_clinica = ClinicaFormulario()

    contexto = {"f_clinica": f_clinica}

    return render(request, "clinicas/cadastro.html", contexto)


# English: list_clinics
@login_required
def list_clinics(request):
    """Return user's clinics as JSON for dropdown population"""
    try:
        # English: user
        user = request.user
        # English: clinics
        clinics = Clinica.objects.filter(usuarios=user).values('id', 'nome_clinica', 'cns_clinica')
        return JsonResponse(list(clinics), safe=False)
    except Exception as e:
        logger.error(f"Error listing clinics for user {request.user.id}: {e}")
        return JsonResponse({'error': 'Erro ao carregar clínicas'}, status=500)


# English: get_clinic
@login_required
def get_clinic(request, clinic_id):
    """Return clinic data as JSON for editing"""
    try:
        # English: user
        user = request.user
        # English: clinic
        clinic = get_object_or_404(Clinica, id=clinic_id, usuarios=user)
        
        # English: data
        data = {
            'id': clinic.id,
            'nome_clinica': clinic.nome_clinica,
            'cns_clinica': clinic.cns_clinica,
            'logradouro': clinic.logradouro,
            'logradouro_num': clinic.logradouro_num,
            'cidade': clinic.cidade,
            'bairro': clinic.bairro,
            'cep': clinic.cep,
            'telefone_clinica': clinic.telefone_clinica,
        }
        
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error getting clinic {clinic_id} for user {request.user.id}: {e}")
        return JsonResponse({'error': 'Erro ao carregar dados da clínica'}, status=500)

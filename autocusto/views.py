from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from processos.forms import PreProcesso
from pacientes.models import Paciente
from medicos.forms import MedicoCadastroFormulario
from .forms import ErrorReportForm, FeatureRequestForm, ProcessFeedbackForm


def home(request):
    """
    Main landing page that handles both user authentication and process initiation.
    
    This view serves dual purposes:
    1. Registration/login interface for non-authenticated users
    2. Process search and initiation for authenticated doctors
    
    The POST logic implements a complex workflow for Brazilian medical prescriptions:
    - Validates patient exists and belongs to current doctor
    - Determines if patient already has a process for the specified disease
    - Routes user to either edit existing process or create new one

    Critique:
    - The `home` view is overly complex, handling both GET and POST requests for
      different forms (PreProcesso and MedicoCadastroFormulario) and managing
      session state extensively. This violates the Single Responsibility Principle.
      It would be better to separate these concerns into distinct views or at least
      dedicated helper functions.
    - The logic for determining if a patient exists and if a process exists for a
      given CID is intricate and involves multiple database queries and session
      manipulations. This could be streamlined and made more robust.
    - The use of `messages.success` and `messages.error` directly within the view
      logic is acceptable for simple feedback, but for complex scenarios, a more
      structured approach (e.g., form-level error handling or custom exceptions)
      might be beneficial.
    - The `print` statements for debugging should be replaced with `logger.debug`
      or `logger.info` for proper logging in a production environment.
    """
    # user
    usuario = request.user
    
    if request.method == "GET":
        # form
        formulario = PreProcesso()
        # Dual-purpose interface: show registration form for visitors, process form for doctors
        if not usuario.is_authenticated:
            # registration_form
            registro_form = MedicoCadastroFormulario()
            # context
            contexto = {"formulario": formulario, "registro_form": registro_form}
        else:
            # context
            contexto = {"formulario": formulario}
        return render(request, "home.html", contexto)
    else:
        if usuario.is_authenticated:
            # form
            formulario = PreProcesso(request.POST)
            if formulario.is_valid():
                # patient_cpf
                cpf_paciente = formulario.cleaned_data["cpf_paciente"]
                cid = formulario.cleaned_data["cid"]

                try:
                    # Security check: Ensure doctor can only access their own patients
                    # This prevents unauthorized access to patient data across different doctors
                    # patient
                    paciente = Paciente.objects.get(
                        cpf_paciente=cpf_paciente,
                        usuarios=usuario
                    )
                    # Patient exists and belongs to current doctor
                    request.session["paciente_existe"] = True
                    request.session["paciente_id"] = paciente.id
                    request.session["cid"] = cid
                    request.session["cpf_paciente"] = cpf_paciente
                except Paciente.DoesNotExist:
                    # Patient doesn't exist in doctor's database - will need to create patient record
                    request.session["paciente_existe"] = False
                    request.session["cid"] = cid
                    request.session["cpf_paciente"] = cpf_paciente
                    return redirect("processos-cadastro")

                # Complex business logic: Check if patient already has a process for this disease
                # search_processes
                busca_processos = paciente.processos.select_related('doenca', 'usuario').filter(doenca__cid=cid)

                if busca_processos.exists():
                    # Patient has processes for this disease - check if current doctor created any
                    # user_processes
                    processos_do_usuario = busca_processos.filter(
                        usuario__id=usuario.id
                    )
                    if processos_do_usuario.exists():
                        # Doctor already has a process for this patient/disease combination
                        # Get the most recent one (handles edge cases where duplicates existed)
                        # most_recent_process
                        processo_mais_recente = processos_do_usuario.order_by('-id').first()
                        request.session["processo_id"] = processo_mais_recente.id
                        return redirect("processos-edicao")  # Edit existing process
                    else:
                        # Patient has processes from other doctors, but not from current doctor
                        messages.success(request, f"Processo iniciado para paciente {cpf_paciente}!")
                        return redirect("processos-cadastro")  # Create new process
                else:
                    # No processes exist for this patient/disease combination
                    messages.success(request, f"Processo iniciado para paciente {cpf_paciente}!")
                    return redirect("processos-cadastro")  # Create new process
            else:
                # Form validation failed - add errors as Django messages for toast display
                for field, errors in formulario.errors.items():
                    for error in errors:
                        messages.error(request, error)
                
                # Clear form errors to prevent inline display (errors will show as toasts)
                formulario._errors.clear()
                
                # context
                contexto = {"formulario": formulario}
                return render(request, "home.html", contexto)
        else:
            # Handle registration form submission for non-authenticated users
            if 'nome' in request.POST:  # This is a registration form submission
                from django.db import transaction
                from django.http import JsonResponse
                
                # registration_form
                registro_form = MedicoCadastroFormulario(request.POST)
                
                if registro_form.is_valid():
                    with transaction.atomic():
                        registro_form.save()
                        # name
                        nome = registro_form.cleaned_data.get("nome")
                        return JsonResponse({
                            'success': True,
                            'message': f"Conta médica criada para {nome}! Você já pode fazer o login."
                        })
                else:
                    # Return JSON response with form errors for AJAX requests
                    return JsonResponse({
                        'success': False,
                        'form_errors': dict(registro_form.errors)
                    })
            else:
                # This is a regular process form submission - require authentication
                messages.warning(
                    request, "Você precisa estar logado para acessar esta página."
                )
                return redirect("home")


def privacy(request):
    """Privacy policy page"""
    return render(request, "privacy.html")


def beneficios(request):
    """Financial benefits analysis page"""
    return render(request, "beneficios.html")


def reportar_erros(request):
    """Report errors page"""
    if request.method == 'POST':
        form = ErrorReportForm(request.POST)
        if form.is_valid():
            # Determine user info
            if request.user.is_authenticated:
                user_info = f"Usuario: {request.user.email}"
            else:
                name = form.cleaned_data.get('name', '')
                email = form.cleaned_data.get('email', '')
                user_info = f"Nome: {name}\nEmail: {email}"
            
            # Send email
            subject = 'Relatório de Erro - CliqueReceita'
            message = f'''
Relatório de Erro

Descrição do Erro:
{form.cleaned_data['description']}

Passos para Reproduzir:
{form.cleaned_data['steps']}

{user_info}
'''
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                ['lcsavb@gmail.com'],
                fail_silently=False,
            )
            
            messages.success(request, 'Relatório de erro enviado com sucesso!')
            return redirect('reportar-erros')
    else:
        form = ErrorReportForm()
    
    return render(request, 'reportar_erros.html', {'form': form})


def solicitar_funcionalidade(request):
    """Request feature page"""
    if request.method == 'POST':
        form = FeatureRequestForm(request.POST)
        if form.is_valid():
            # Determine user info
            if request.user.is_authenticated:
                user_info = f"Usuário: {request.user.email}"
            else:
                name = form.cleaned_data.get('name', '')
                email = form.cleaned_data.get('email', '')
                user_info = f"Nome: {name}\nEmail: {email}"
            
            # Send email
            subject = 'Solicitação de Funcionalidade - CliqueReceita'
            message = f'''
Solicitação de Funcionalidade

Descrição da Funcionalidade:
{form.cleaned_data['description']}

{user_info}
'''
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                ['lcsavb@gmail.com'],
                fail_silently=False,
            )
            
            messages.success(request, 'Solicitação de funcionalidade enviada com sucesso!')
            return redirect('solicitar-funcionalidade')
    else:
        form = FeatureRequestForm()
    
    return render(request, 'solicitar_funcionalidade.html', {'form': form})



@require_http_methods(["POST"])
def process_feedback_ajax(request):
    """AJAX endpoint for process feedback"""
    try:
        # Create form with the POST data
        form = ProcessFeedbackForm(request.POST)
        
        if form.is_valid():
            # Determine user info
            if request.user.is_authenticated:
                user_info = f"User: {request.user.email}"
            else:
                name = form.cleaned_data.get('name', '')
                email = form.cleaned_data.get('email', '')
                user_info = f"Name: {name}\nEmail: {email}"
            
            # Get process information if provided
            process_info = form.cleaned_data.get('processo_info', 'Not provided')
            
            # Send email
            subject = f'Process Feedback - {form.cleaned_data["feedback_type"].title()} - CliqueReceita'
            message = f'''
Process Feedback Report

Problem Type: {dict(form.fields['feedback_type'].choices)[form.cleaned_data['feedback_type']]}

Process Information:
{process_info}

Problem Description:
{form.cleaned_data['description']}

{user_info}
'''
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                ['lcsavb@gmail.com'],
                fail_silently=False,
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Feedback enviado com sucesso! Obrigado por nos ajudar a melhorar.'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Por favor, corrija os erros no formulário.',
                'errors': form.errors
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro interno do servidor. Tente novamente mais tarde.'
        })

from django.shortcuts import render, redirect
from django.contrib import messages
from processos.forms import PreProcesso
from pacientes.models import Paciente
from medicos.forms import MedicoCadastroFormulario


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
    """
    usuario = request.user
    
    if request.method == "GET":
        formulario = PreProcesso()
        # Dual-purpose interface: show registration form for visitors, process form for doctors
        if not usuario.is_authenticated:
            registro_form = MedicoCadastroFormulario()
            contexto = {"formulario": formulario, "registro_form": registro_form}
        else:
            contexto = {"formulario": formulario}
        return render(request, "home.html", contexto)
    else:
        if usuario.is_authenticated:
            formulario = PreProcesso(request.POST)
            if formulario.is_valid():
                cpf_paciente = formulario.cleaned_data["cpf_paciente"]
                cid = formulario.cleaned_data["cid"]

                try:
                    # Security check: Ensure doctor can only access their own patients
                    # This prevents unauthorized access to patient data across different doctors
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
                busca_processos = paciente.processos.filter(doenca__cid=cid)

                if busca_processos.exists():
                    # Patient has processes for this disease - check if current doctor created any
                    processos_do_usuario = busca_processos.filter(
                        usuario__id=usuario.id
                    )
                    if processos_do_usuario.exists():
                        # Doctor already has a process for this patient/disease combination
                        # Get the most recent one (handles edge cases where duplicates existed)
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
                
                contexto = {"formulario": formulario}
                return render(request, "home.html", contexto)
        else:
            # Handle registration form submission for non-authenticated users
            if 'nome' in request.POST:  # This is a registration form submission
                print("🔍 STEP 1: Registration form detected in POST")
                from django.db import transaction
                
                registro_form = MedicoCadastroFormulario(request.POST)
                print(f"🔍 STEP 1: Form created, is_valid: {registro_form.is_valid()}")
                
                if registro_form.is_valid():
                    with transaction.atomic():
                        registro_form.save()
                        nome = registro_form.cleaned_data.get("nome")
                        messages.success(
                            request, f"Conta médica criada para {nome}! Você já pode fazer o login."
                        )
                        return redirect("login")
                else:
                    print("🔍 STEP 2: Form validation FAILED")
                    print(f"🔍 STEP 2: Form errors: {dict(registro_form.errors)}")
                    
                    # Form has errors, add them as Django messages for toast display
                    for field, errors in registro_form.errors.items():
                        for error in errors:
                            print(f"🔍 STEP 2: Adding message.error: {error}")
                            messages.error(request, error)
                    
                    print(f"🔍 STEP 3: Total messages after adding: {len(list(messages.get_messages(request)))}")
                    
                    # Clear form errors to prevent crispy from showing inline errors
                    # (we've already copied them to messages for toast display)
                    registro_form._errors.clear()
                    print("🔍 STEP 4: Cleared form errors to prevent inline display")
                    
                    # Re-render form but messages will show as toasts
                    formulario = PreProcesso()
                    contexto = {"formulario": formulario, "registro_form": registro_form}
                    return render(request, "home.html", contexto)
            else:
                # This is a regular process form submission - require authentication
                messages.warning(
                    request, "Você precisa estar logado para acessar esta página."
                )
                return redirect("home")


def privacy_policy(request):
    """Privacy policy page view"""
    return render(request, "privacy.html")

def reportar_erros(request):
    """View for reporting errors"""
    return render(request, "reportar_erros.html")

def solicitar_funcionalidade(request):
    """View for requesting features"""
    return render(request, "solicitar_funcionalidade.html")

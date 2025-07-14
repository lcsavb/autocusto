from django.shortcuts import render, redirect
from django.contrib import messages
from processos.forms import PreProcesso
from pacientes.models import Paciente
from medicos.forms import MedicoCadastroFormulario


def home(request):
    usuario = request.user
    if request.method == "GET":
        formulario = PreProcesso()
        # Include registration form for non-authenticated users
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
                    # Only allow access to patients associated with the current user
                    paciente = Paciente.objects.get(
                        cpf_paciente=cpf_paciente,
                        usuarios=usuario
                    )
                    request.session["paciente_existe"] = True
                    request.session["paciente_id"] = paciente.id
                    request.session["cid"] = cid
                    request.session["cpf_paciente"] = cpf_paciente
                except Paciente.DoesNotExist:
                    request.session["paciente_existe"] = False
                    request.session["cid"] = cid
                    request.session["cpf_paciente"] = cpf_paciente
                    return redirect("processos-cadastro")

                busca_processos = paciente.processos.filter(doenca__cid=cid)

                if busca_processos.exists():
                    processo_cadastrado_pelo_usuario = busca_processos.filter(
                        usuario__id=usuario.id
                    ).exists()
                    if processo_cadastrado_pelo_usuario:
                        request.session["processo_id"] = busca_processos.get(
                            usuario__id=usuario.id
                        ).id
                        return redirect("processos-edicao")
                    else:
                        return redirect("processos-cadastro")
                else:
                    return redirect("processos-cadastro")
            else:
                contexto = {"formulario": formulario}
                return render(request, "home.html", contexto)
        else:
            messages.warning(
                request, "Você precisa estar logado para acessar esta página."
            )
            return redirect("home")


def privacy_policy(request):
    """Privacy policy page view"""
    return render(request, "privacy.html")

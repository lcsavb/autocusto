from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PacienteCadastroFormulario
from django.views.generic import ListView
from pacientes.models import Paciente
from django.urls import reverse
from urllib.parse import urlencode
from django.contrib import messages


# English: registration
@login_required
def cadastro(request):
    """
    Handles the registration of new patient accounts.

    This view processes the form submission for creating a new patient record.
    If the form is valid, it saves the new patient, associates them with the
    current user (doctor), and redirects to the process registration page.
    Otherwise, it displays error messages.

    Critique:
    - The `instance.medico = request.user.medico` line assumes a direct `medico`
      attribute on the `Paciente` model, which might not be the most flexible
      design if a patient can be associated with multiple doctors or if the
      relationship is managed differently. The `instance.usuarios.add(request.user)`
      is a better approach for many-to-many relationships.
    - The `instance.paciente = formulario.cleaned_data["cpf_paciente"]` line seems
      redundant or potentially incorrect, as `instance` is already a `Paciente`
      object and `cpf_paciente` is likely a field on it. It might be trying to
      set a foreign key or a duplicate field.
    - The error handling for form validation iterates through `formulario.errors.items()`
      and adds each error as a separate message. While functional, Django's form
      rendering often handles displaying field-specific errors directly in the template,
      making these `messages.error` calls potentially redundant or leading to duplicate
      error displays.
    """

    if request.method == "POST":
        # English: form
        formulario = PacienteCadastroFormulario(request.POST)
        if formulario.is_valid():
            # English: instance
            instance = formulario.save(commit=False)
            instance.medico = request.user.medico
            instance.paciente = formulario.cleaned_data["cpf_paciente"]
            instance.save()
            # Associate the patient with the current user
            instance.usuarios.add(request.user)
            # English: base_url
            url_base = reverse("processos-cadastro")
            # English: search_string
            string_busca = urlencode({"paciente": instance.paciente})
            # English: url
            url = f"{url_base}?{string_busca}"

            # English: name
            nome = formulario.cleaned_data.get('nome')
            messages.success(request, f'Paciente {nome} adicionado com sucesso! Agora preencha o processo.')
            return redirect(url)
        else:
            # Form validation failed - add errors as Django messages for toast display
            for field, errors in formulario.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        # English: form
        formulario = PacienteCadastroFormulario()

    return render(
        request,
        "pacientes/cadastro.html",
        {"formulario": formulario, "titulo": "Cadastro de Paciente"},
    )


class ListarPacientes(LoginRequiredMixin, ListView):
    model = Paciente
    template_name = "pacientes/lista.html"
    context_object_name = "pacientes"
    
    def get_queryset(self):
        # Only show patients associated with the current user
        return Paciente.objects.filter(usuarios=self.request.user)

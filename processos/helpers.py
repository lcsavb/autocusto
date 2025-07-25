"""
Helper Functions for Prescription Processing

This module contains utility and helper functions for prescription data processing,
model operations, and data transformations. These functions provide reusable
building blocks for the prescription workflow system.

Main Categories:
- Model preparation and database operations
- Prescription data transformation and formatting  
- Medication data processing and validation
- Patient data management helpers
- PDF generation coordination (legacy bridge)

All functions maintain English translation comments for international development.
"""

import os
import secrets
import time
import logging
from django.conf import settings
from django.forms.models import model_to_dict
from django.core.cache import cache
from datetime import datetime
from .manejo_pdfs_memory import GeradorPDF
from processos.models import Processo, Protocolo, Medicamento
from pacientes.models import Paciente
from analytics.signals import track_pdf_generation

# Configure logging
pdf_logger = logging.getLogger('processos.pdf')



# prepare_model
def preparar_modelo(modelo, **kwargs):
    """
    Prepares a Django model instance from a dictionary of data.

    Think of this function as a helper that takes a blueprint for a database
    record (the 'modelo', e.g., a Patient or a Process) and a dictionary of
    information ('kwargs'), and it creates a new record object filled with
    that information.

    This is a common pattern in Django apps. You get data from a web form,
    clean it up into a dictionary, and then use a function like this to
    create a model object that you can then save to the database.

    Args:
        # model
        modelo: The Django model class itself (e.g., Paciente, not an
                instance of it).
        **kwargs: A dictionary where keys are the model field names (e.g.,
                  'nome_paciente') and values are the data for those fields
                  (e.g., 'Jane Doe').

    Returns:
        An in-memory instance of the model, ready to be saved.
        For example, if you pass the Paciente model and data for a new patient,
        it returns a new Paciente object that hasn't been saved to the
        database yet.
    """
    # This line takes the 'modelo' class and the 'kwargs' dictionary and
    # creates a new object. The `**kwargs` syntax is a Python shortcut
    # that unpacks the dictionary into keyword arguments.
    # For example, if kwargs is {'field1': 'value1', 'field2': 'value2'},
    # this line becomes: modelo(field1='value1', field2='value2')
    
    # parameterized_model
    modelo_parametrizado = modelo(**kwargs)
    return modelo_parametrizado


# retrieve_prescription
def resgatar_prescricao(dados, processo):
    """Populates a data dictionary with prescription details from a Processo object.

    This function is used to transfer prescription information from the structured
    `processo.prescricao` field (which is a nested dictionary) into a flat
    `dados` dictionary. This flattening is necessary to populate form fields
    for display or editing, where each field corresponds to a key in the `dados`
    dictionary (e.g., 'id_med1', 'med1_posologia_mes1').

    Args:
        # English: data
        dados (dict): The dictionary to populate with prescription data. This
                      dictionary is modified in-place.
        # English: process
        processo (Processo): The Django model instance containing the prescription
                             to be retrieved. The `prescricao` attribute is expected
                             to be a dictionary where keys are medication numbers
                             (e.g., '1', '2') and values are dictionaries of
                             medication details.

    Returns:
        dict: The `dados` dictionary, now updated with the flattened
              prescription information.
    """
    # Counter for the medication number, ensuring form fields like 'id_med1',
    # 'id_med2' are correctly populated.
    n = 1
    # English: prescription
    prescricao = processo.prescricao

    # The `prescricao` field on the Processo model stores medication data in a
    # nested dictionary, for example:
    # {
    #   '1': {'id_med1': 123, 'med1_posologia_mes1': '...'},
    #   '2': {'id_med2': 456, 'med2_posologia_mes1': '...'}
    # }
    # This loop iterates through each medication in the prescription.
    for item in prescricao.items():
        # English: medication_number
        numero_medicamento = item[0]  # The key, e.g., '1' or '2'
        if numero_medicamento != "":
            # This line is slightly redundant due to the inner loop, but it
            # ensures the medication ID is set.
            dados[f"id_med{n}"] = prescricao[numero_medicamento][f"id_med{n}"]

            # Unpack all key-value pairs from the inner medication dictionary
            # into the main 'dados' dictionary.
            # For example, 'med1_posologia_mes1' becomes a key in 'dados'.
            for i in prescricao[numero_medicamento].items():
                dados[i[0]] = i[1]
            n += 1
    return dados


# generate prescription
def gerar_prescricao(meds_ids, dados_formulario):
    """Constructs a structured prescription dictionary from form data.

    This function takes a list of medication IDs and a flat dictionary of form
    data, and it builds a nested dictionary representing the prescription.
    This nested structure is how prescription data is stored on the Processo
    model. It organizes the dosage and quantity for each medication over a
    six-month period.

    Args:
        # English: medication_ids
        meds_ids (list): A list of medication IDs to be included in the
                         prescription.
        # English: form_data
        dados_formulario (dict): A flat dictionary containing the form data,
                                 with keys like 'med1_posologia_mes1',
                                 'qtd_med1_mes1', etc.

    Returns:
        dict: A nested dictionary representing the prescription, ready to be
              stored in the `prescricao` field of a Processo object. Example:
              {
                '1': {'id_med1': 123, 'med1_posologia_mes1': '...', ...},
                '2': {'id_med2': 456, 'med2_posologia_mes1': '...', ...}
              }
    """
    # English: prescription
    prescricao = {}
    # English: medication_prescription
    med_prescricao = {}
    n = 1
    for id in meds_ids:
        m = 1
        # English: medication_prescription
        med_prescricao[f"id_med{n}"] = id
        while m <= 6:
            # English: medication_prescription
            med_prescricao[f"med{n}_posologia_mes{m}"] = dados_formulario[
                f"med{n}_posologia_mes{m}"
            ]
            # English: medication_prescription
            med_prescricao[f"qtd_med{n}_mes{m}"] = dados_formulario[
                f"qtd_med{n}_mes{m}"
            ]
            m += 1
        if n == 1:
            # English: medication_prescription
            med_prescricao["med1_via"] = dados_formulario["med1_via"]
        # English: prescription
        prescricao[n] = med_prescricao
        # English: medication_prescription
        med_prescricao = {}
        n += 1
    return prescricao


# generate medication dosage
def gera_med_dosagem(dados_formulario, ids_med_formulario):
    """Retrieves medication details and formats them for display.

    This function iterates through a list of medication IDs, fetches the full
    medication details (name, dosage, presentation) from the database, and
    formats this information into a string. This string is then added to the
    main form data dictionary under a key corresponding to the medication's
    order (e.g., 'med1', 'med2'). This is need due to fill the pdf adequately
    with pdftk.

    Args:
        # English: form_data
        dados_formulario (dict): The main dictionary of form data. This is
                                 modified in-place.
        # English: medication_form_ids
        ids_med_formulario (list): A list of medication IDs selected in the
                                   form.

    Returns:
        tuple: A tuple containing:
            - dict: The updated `dados_formulario` dictionary.
            - list: A cleaned list of medication IDs (`meds_ids`), excluding
                    any placeholder values like "nenhum".
    """
    # English: medication_ids
    meds_ids = []
    n = 0
    for id_med in ids_med_formulario:
        n += 1
        if id_med != "nenhum":
            # English: medication_ids
            meds_ids.append(id_med)
            # English: med
            med = Medicamento.objects.get(id=id_med)
            # English: form_data
            dados_formulario[f"med{n}"] = f"{med.nome} {med.dosagem} ({med.apres})"
    return dados_formulario, meds_ids


# list medications
def listar_med(cid):
    """Retrieves medications associated with a protocol and returns a list of tuples.

    This function is used to populate a dropdown menu in a form with a list of
    medications that are appropriate for a given CID (International
    Classification of Diseases) code. It fetches the protocol associated with
    the CID, gets all the medications linked to that protocol, and formats them
    into a list of (id, display_name) tuples.

    Args:
        cid (str): The CID code for the disease.

    Returns:
        tuple: A tuple of tuples, where each inner tuple contains the
               medication's ID and a formatted string with its name, dosage,
               and presentation. The first item is always a placeholder for the
               dropdown.
    """
    # English: medication_list
    lista_med = [("nenhum", "Escolha o medicamento...")]
    # English: protocol
    protocolo = Protocolo.objects.get(doenca__cid=cid)
    # English: medications
    medicamentos = protocolo.medicamentos.all()
    for medicamento in medicamentos:
        # English: item
        item = (
            medicamento.id,
            f"{medicamento.nome}"
            + " "
            + f"{medicamento.dosagem}"
            + " - "
            + f"{medicamento.apres}",
        )
        # English: medication_list
        lista_med.append(item)
    return tuple(lista_med)


# associate medications
def associar_med(processo, meds):
    """Synchronizes the medications associated with a process.

    This function ensures that the medications linked to a `Processo` object
    match the provided list of medication IDs. It performs a two-way sync:
    1. It adds any new medications from the `meds` list to the process.
    2. It removes any medications currently associated with the process that
       are not in the `meds` list.

    Args:
        # English: process
        processo (Processo): The Django model instance to update.
        # English: meds
        meds (list): A list of medication IDs (as strings) that should be
                     associated with the process.
    """
    for med in meds:
        # English: process
        processo.medicamentos.add(med)
        # English: registered_medications
        meds_cadastrados = processo.medicamentos.all()
        for med_cadastrado in meds_cadastrados:
            if str(med_cadastrado.id) not in meds:
                # English: process
                processo.medicamentos.remove(med_cadastrado)


# create renewal dictionary
def cria_dict_renovação(modelo):
    """Creates a dictionary with data for a renewal process.

    This function takes a `Processo` model instance and extracts the necessary
    data to create a new renewal process. It gathers patient and process
    information into a single dictionary.

    Critique:
    This function manually copies fields from the model to a dictionary.
    This is verbose and not easily maintainable. If the `Paciente` or
    `Processo` model changes, this function must be updated manually. A better
    approach would be to use Django's `model_to_dict` utility for both the
    `processo` and `processo.paciente` instances and then merge the resulting
    dictionaries. This would make the code more concise and resilient to
    model changes.

    Args:
        # English: model
        modelo (Processo): The Django model instance to get the data from.

    Returns:
        dict: A dictionary containing the data for the renewal process.
    """
    # English: dictionary
    dicionario = {
        # Patient data
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
        # Process data
        "prescricao": modelo.prescricao,
        "cid": modelo.doenca.cid,
        "diagnostico": modelo.doenca.nome,
        "anamnese": modelo.anamnese,
        "tratou": modelo.tratou,
        "tratamentos_previos": modelo.tratamentos_previos,
        "preenchido_por": modelo.preenchido_por,
        "clinica": modelo.clinica,
    }
    
    # Add conditional data from the process
    if modelo.dados_condicionais:
        dicionario.update(modelo.dados_condicionais)
    return dicionario


# English: generate_renewal_data
# generate renewal data
def gerar_dados_renovacao(primeira_data, processo_id, user=None):
    """Generates a complete data dictionary for a renewal process.

    This function is used for the "quick renewal" feature. It takes an
    existing process ID and a new start date, and it constructs a full data
    dictionary that can be used to create a new process, preserving most of
    the original data but with the updated date.

    Critique:
    - The function has a lot of debugging prints, which should be removed
      in a production environment. Using Python's `logging` module would be
      a better way to handle debugging information.
    - The function manually sets several keys to empty strings (medicos,
      usuarios, medicamentos). This is likely to prevent errors with the PDF
      generation library (pdftk), but it's not a clean solution. It would be
      better to handle this in the PDF generation logic.
    - The special handling for "dor_crônica" (chronic pain) is hardcoded.
      This makes the function less flexible. A better approach would be to
      have a more generic way to handle conditional data based on the
      protocol, perhaps by storing this logic in the database alongside the
      protocol information.

    Args:
        # English: first_date
        primeira_data (str): The new start date for the renewal, in DD/MM/YYYY
                             format.
        # English: process_id
        processo_id (int): The ID of the process to be renewed.

    Returns:
        dict: A complete dictionary of data for the new renewal process.
    """
    # English: process
    processo = Processo.objects.get(id=processo_id)
    
    # English: data
    dados = {}
    
    # Get versioned patient data if user is provided
    if user:
        paciente_version = processo.paciente.get_version_for_user(user)
        if paciente_version:
            paciente_data = model_to_dict(paciente_version)
            # Keep master record fields that aren't versioned
            paciente_data['id'] = processo.paciente.id
            paciente_data['cpf_paciente'] = processo.paciente.cpf_paciente
            paciente_data['usuarios'] = processo.paciente.usuarios.all()
        else:
            paciente_data = model_to_dict(processo.paciente)
    else:
        # Fallback to master record if no user provided
        paciente_data = model_to_dict(processo.paciente)
    
    # English: data_list
    lista_dados = [
        model_to_dict(processo),
        paciente_data,
        model_to_dict(processo.medico),
        model_to_dict(processo.clinica),
    ]
    for d in lista_dados:
        # English: data
        dados.update(d)
    
    
    # pdftk fails if input is not a string!
    # English: data
    dados["medicos"] = ""
    # English: data
    dados["usuarios"] = ""
    # English: data
    dados["medicamentos"] = ""
    # English: clinic_address
    end_clinica = dados["logradouro"] + ", " + dados["logradouro_num"]
    # English: data
    dados["end_clinica"] = end_clinica
    
    # Validate and parse date
    if not primeira_data or primeira_data.strip() == "":
        raise ValueError("Data de renovação não pode estar vazia")
    
    try:
        # English: data
        dados["data_1"] = datetime.strptime(primeira_data, "%d/%m/%Y")
    except ValueError as e:
        raise ValueError(f"Formato de data inválido: {primeira_data}. Use DD/MM/AAAA")
    
    # English: data
    dados["cid"] = processo.doenca.cid
    # English: data
    dados["diagnostico"] = processo.doenca.nome
    
    # CRITICAL: Setting conditional PDF flags for renovation
    # English: data
    dados["consentimento"] = False  # No consent for renewals
    # English: data
    dados["relatorio"] = False      # No report for renewals 
    # English: data
    dados["exames"] = False         # No exams for renewals
    
    # CHRONIC PAIN SPECIAL LOGIC: Include LANNS/EVA form for chronic pain renewals
    try:
        # English: protocol
        protocolo = processo.doenca.protocolo
        
        if protocolo.nome == "dor_crônica":
            # For chronic pain, we need to include the LANNS/EVA assessment form
            # This will be picked up by the conditional PDFs glob pattern
            # English: data
            dados["include_lanns_eva"] = True
            
            # Preserve any conditional data from original process
            if processo.dados_condicionais:
                for key, value in processo.dados_condicionais.items():
                    # English: data
                    dados[key] = value
            
    except Exception as e:
        pass
    
    resgatar_prescricao(dados, processo)
    
    # English: medication_ids
    meds_ids = gerar_lista_meds_ids(dados)
    
    # English: data
    dados = gera_med_dosagem(dados, meds_ids)[0]
    return dados


# English: link_issuer_data
def vincula_dados_emissor(usuario, medico, clinica, dados_formulario):
    """Links the logged-in user's data to the process data.

    This function takes the user, doctor, and clinic objects and adds their
    relevant information to the main form data dictionary. This is used to
    ensure that the generated documents are correctly associated with the
    person and clinic that created them.

    Args:
        # English: user
        usuario (User): The logged-in user.
        # English: doctor
        medico (Medico): The doctor associated with the user.
        # English: clinic
        clinica (Clinica): The clinic associated with the user.
        # English: form_data
        dados_formulario (dict): The main dictionary of form data. This is
                                 modified in-place.

    Returns:
        dict: The updated `dados_formulario` dictionary.
    """
    # English: clinic_address
    end_clinica = clinica.logradouro + ", " + clinica.logradouro_num
    # English: additional_data
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
    # English: form_data
    dados_formulario.update(dados_adicionais)
    return dados_formulario


# English: transfer_data_to_generator
@track_pdf_generation(pdf_type='prescription')
def transfere_dados_gerador(dados):
    """Transfers the final process data to the PDF generator.

    This function maintains backward compatibility while using the new
    application service architecture. It delegates PDF generation to the
    PrescriptionPDFService and handles file system operations for serving.

    This function will be eventually deprecated in favor of direct service usage,
    but is maintained for compatibility during the migration period.

    Args:
        # English: data
        dados (dict): The complete data dictionary for the process.

    Returns:
        str: The path to the generated PDF file, or None if an error occurs.
    """
    try:
        pdf_logger.info("transfere_dados_gerador: Starting with new service architecture")
        
        # Save CPF and CID before PDF generation (they might be modified during processing)
        cpf_paciente = dados.get('cpf_paciente', 'unknown')
        cid = dados.get('cid', 'unknown')
        
        # Use new PrescriptionPDFService for PDF generation
        from processos.prescription_services import PrescriptionPDFService
        pdf_service = PrescriptionPDFService()
        
        # Generate PDF using the service
        response = pdf_service.generate_prescription_pdf(dados)
        
        if response is None:
            pdf_logger.error("transfere_dados_gerador: PDF generation returned None")
            return None
        
        # Infrastructure concern: Save PDF to filesystem for serving
        # This will eventually be moved to a separate infrastructure service
        nome_final_pdf = f"pdf_final_{cpf_paciente}_{cid}.pdf"
        tmp_pdf_path = f"/tmp/{nome_final_pdf}"
        
        with open(tmp_pdf_path, 'wb') as f:
            f.write(response.content)
        
        pdf_logger.info(f"transfere_dados_gerador: PDF saved to {tmp_pdf_path}")
        
        # Return the URL path as before
        from django.urls import reverse
        path_pdf_final = reverse('processos-serve-pdf', kwargs={'filename': nome_final_pdf})
        
        pdf_logger.info(f"transfere_dados_gerador: Returning URL {path_pdf_final}")
        return path_pdf_final
        
    except Exception as e:
        pdf_logger.error(f"Exception in transfere_dados_gerador: {e}", exc_info=True)
        return None


# generate pdf stream
def gerar_pdf_stream(dados):
    """Generates PDF entirely in memory and returns HttpResponse for streaming.
    
    This function replaces the disk-based PDF generation with in-memory operations.
    It uses the new GeradorPDFMemory class to generate PDFs directly in RAM and
    returns an HttpResponse that streams the PDF to the browser.
    
    Args:
        dados (dict): The complete data dictionary for the process.
        
    Returns:
        HttpResponse: PDF response ready for streaming, or None if error occurs.
    """
    try:
        # Create memory-based PDF generator
        pdf_generator = GeradorPDFMemory(dados, settings.PATH_LME_BASE)
        
        # Generate PDF and return HttpResponse
        response = pdf_generator.generico_stream(dados, settings.PATH_LME_BASE)
        
        return response
        
    except Exception as e:
        pdf_logger.error(f"Exception in gerar_pdf_stream: {e}", exc_info=True)
        return None


# English: generate_medication_ids_list
def gerar_lista_meds_ids(dados):
    """Extracts a list of medication IDs from the data dictionary.

    This function iterates through the data dictionary and extracts the IDs of
    the selected medications. The form uses keys like `id_med1`, `id_med2`,
    etc., to store the medication IDs.

    Args:
        # English: data
        dados (dict): The data dictionary from the form.

    Returns:
        list: A list of medication IDs.
    """
    n = 1
    # English: list
    lista = []
    while n <= 4:
        try:
            if dados[f"id_med{n}"] != "nenhum":
                # English: list
                lista.append(dados[f"id_med{n}"])
        except KeyError:
            pass # Continue if key is missing, as it means no more meds are selected
        n += 1
    return lista


# English: generate_partial_edition_data
def gerar_dados_edicao_parcial(dados, processo_id):
    """Generates a dictionary for partially updating a process.

    This function creates a dictionary with the data that will be updated
    during a partial renewal. It also generates a list of the fields to be
    updated, excluding the ID.

    Critique:
    - The function creates a list of fields to update by deleting the first
      element ('id'). This is fragile and depends on the order of keys in the
      dictionary. A better approach would be to explicitly list the fields to
      be updated.

    Args:
        # English: data
        dados (dict): The data dictionary from the form.
        # English: process_id
        processo_id (int): The ID of the process to be updated.

    Returns:
        tuple: A tuple containing:
            - dict: The dictionary with the new data.
            - list: A list of the fields to be updated.
    """

    # English: registered_medication_ids
    ids_med_cadastrados = gerar_lista_meds_ids(dados)
    # English: prescription
    prescricao = gerar_prescricao(ids_med_cadastrados, dados)
    # English: new_data
    novos_dados = dict(id=processo_id, data1=dados["data_1"], prescricao=prescricao)

    # English: field_list
    lista_campos = []
    for key in novos_dados.keys():
        # English: field_list
        lista_campos.append(key)
    del lista_campos[0]

    return novos_dados, lista_campos


# English: generate_patient_data
def gerar_dados_paciente(dados):
    """Creates a dictionary with patient data.

    This function extracts patient-specific data from a larger data
    dictionary and returns it as a new dictionary. This is used to separate
    patient data from other data in the process.

    Critique:
    - This function manually copies fields to a new dictionary. This is
      verbose and not easily maintainable. A better approach would be to
      define a list of patient-related fields and then use a loop to create
      the new dictionary. This would make the code more concise and easier to
      update. Or maybe use django dicts method?

    Args:
        # English: data
        dados (dict): The main data dictionary.

    Returns:
        dict: A dictionary containing only the patient data.
    """
    # English: patient_data
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


# English: generate_process_data
def gerar_dados_processo(dados, meds_ids, doenca, emissor, paciente, usuario):
    """Creates a dictionary with process data.

    This function gathers all the data related to a process and returns it as
    a dictionary. This dictionary is then used to create a new `Processo`
    object.

    Critique:
    - The function manually copies fields to a new dictionary. This is
      verbose and not easily maintainable. A better approach would be to
      define a list of process-related fields and then use a loop to create
      the new dictionary. This would make the code more concise and easier to
      update.

    Args:
        # English: data
        dados (dict): The main data dictionary.
        # English: medication_ids
        meds_ids (list): A list of medication IDs.
        # English: disease
        doenca (Doenca): The disease object.
        # English: issuer
        emissor (Emissor): The issuer object.
        # English: patient
        paciente (Paciente): The patient object.
        # English: user
        usuario (User): The user object.

    Returns:
        dict: A dictionary containing the process data.
    """
    # English: prescription
    prescricao = gerar_prescricao(meds_ids, dados)
    # English: process_data
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
            # English: process_data
            dados_processo["dados_condicionais"][dado[0]] = dado[1]
    return dados_processo


# English: register_in_db
def registrar_db(dados, meds_ids, doenca, emissor, usuario, **kwargs):
    """Registers all the data in the database.

    This function brings together all the data, saves it to the database, and
    returns the ID of the saved process.

    Critique:
    - This function has a high level of complexity. It handles both creating
      new patients and updating existing ones, as well as creating and updating
      processes. This makes it difficult to read and maintain. It would be
      better to split this function into smaller, more focused functions.
    - The function uses `force_update=True` when saving the process and
      patient. This is generally not recommended, as it can hide bugs. It's
      better to let Django handle the creation or update of objects based on
      whether they have a primary key.

    Args:
        # English: data
        dados (dict): The main data dictionary.
        # English: medication_ids
        meds_ids (list): A list of medication IDs.
        # English: disease
        doenca (Doenca): The disease object.
        # English: issuer
        emissor (Emissor): The issuer object.
        # English: user
        usuario (User): The user object.
        **kwargs: Additional keyword arguments.

    Returns:
        int: The ID of the saved process.
    """
    # Add comprehensive logging for debugging transaction rollbacks
    import logging
    logger = logging.getLogger('processos.database')
    
    # English: patient_exists
    paciente_existe = kwargs.pop("paciente_existe")
    # English: patient_data
    dados_paciente = gerar_dados_paciente(dados)
    # English: patient_cpf
    cpf_paciente = dados["cpf_paciente"]
    
    logger.info(f"registrar_db: Starting registration for CPF {cpf_paciente}, user {usuario.email}")
    logger.info(f"registrar_db: Patient exists: {bool(paciente_existe)}")
    logger.info(f"registrar_db: Disease: {doenca.cid} - {doenca.nome}")
    logger.info(f"registrar_db: Medications count: {len(meds_ids)}")

    if paciente_existe:
        # Use versioned patient system - create or update version for this user
        versioned_patient = Paciente.create_or_update_for_user(usuario, dados_paciente)
        
        # English: process_data
        dados_processo = gerar_dados_processo(
            dados, meds_ids, doenca, emissor, versioned_patient, usuario
        )
        # English: process_data
        dados_processo["paciente"] = versioned_patient
        cid = kwargs.pop("cid", None)
        processo_id = kwargs.pop("processo_id", None)
        
        # English: process_exists
        processo_existe = False
        
        if processo_id:
            # Editing existing process - use the specific process ID
            processo_existe = True
            dados_processo["id"] = processo_id
        else:
            # Creating new process - check if one already exists for this patient-disease-user combination
            for p in paciente_existe.processos.all():
                if p.doenca.cid == cid and p.usuario == usuario:
                    # English: process_exists
                    processo_existe = True
                    # English: process_data
                    dados_processo["id"] = p.id
                    break

        # English: process
        processo = preparar_modelo(Processo, **dados_processo)

        if processo_existe:
            processo.save(force_update=True)
        else:
            processo.save()
            # Increment user's process count for new processes
            usuario.process_count += 1
            usuario.save(update_fields=['process_count'])
        associar_med(processo, meds_ids)
        emissor.pacientes.add(versioned_patient)
    else:
        # NEW PATIENT CREATION PATH
        logger.info(f"registrar_db: Creating NEW patient for CPF {cpf_paciente}")
        
        try:
            # Use versioned patient system - create new patient with initial version
            logger.info(f"registrar_db: Calling create_or_update_for_user for new patient")
            new_patient = Paciente.create_or_update_for_user(usuario, dados_paciente)
            logger.info(f"registrar_db: New patient created with ID {new_patient.id}")
            
            # English: process_data
            logger.info(f"registrar_db: Generating process data for new patient")
            dados_processo = gerar_dados_processo(
                dados, meds_ids, doenca, emissor, new_patient, usuario
            )
            logger.info(f"registrar_db: Process data generated successfully")
            
            # English: process
            logger.info(f"registrar_db: Creating process model instance")
            processo = preparar_modelo(Processo, **dados_processo)
            logger.info(f"registrar_db: Process model created, attempting save")
            
            try:
                processo.save()
                logger.info(f"registrar_db: Process saved successfully with ID {processo.id}")
            except Exception as save_error:
                logger.error(f"registrar_db: CRITICAL ERROR saving process: {save_error}")
                logger.error(f"registrar_db: Process data: {dados_processo}")
                raise
            
            # Increment user's process count for new processes
            logger.info(f"registrar_db: Incrementing user process count")
            try:
                usuario.process_count += 1
                usuario.save(update_fields=['process_count'])
                logger.info(f"registrar_db: User process count updated to {usuario.process_count}")
            except Exception as user_save_error:
                logger.error(f"registrar_db: Error updating user process count: {user_save_error}")
                # Don't fail the whole transaction for this
            
            logger.info(f"registrar_db: Associating medications with process")
            try:
                associar_med(processo, meds_ids)
                logger.info(f"registrar_db: Medications associated successfully")
            except Exception as med_error:
                logger.error(f"registrar_db: Error associating medications: {med_error}")
                raise
            
            logger.info(f"registrar_db: Adding patient to emissor")
            try:
                emissor.pacientes.add(new_patient)
                logger.info(f"registrar_db: Patient added to emissor successfully")
            except Exception as emissor_error:
                logger.error(f"registrar_db: Error adding patient to emissor: {emissor_error}")
                raise
                
        except Exception as e:
            logger.error(f"registrar_db: CRITICAL ERROR in new patient creation: {e}")
            logger.error(f"registrar_db: Patient data: {dados_paciente}")
            logger.error(f"registrar_db: Full traceback:", exc_info=True)
            raise

    logger.info(f"registrar_db: Successfully completed registration, returning process ID {processo.pk}")
    return processo.pk


# English: check_if_patient_exists
def checar_paciente_existe(cpf_paciente):
    """Checks if a patient with the given CPF exists in the database.

    Args:
        # English: patient_cpf
        cpf_paciente (str): The patient's CPF.

    Returns:
        Paciente or bool: The `Paciente` object if the patient exists,
                          otherwise `False`.
    """
    try:
        # English: patient_exists
        paciente_existe = Paciente.objects.get(cpf_paciente=cpf_paciente)
    except Paciente.DoesNotExist:
        # English: patient_exists
        paciente_existe = False
    return paciente_existe

# English: generate_protocol_link
def gerar_link_protocolo(cid):
    """Generates a link to the protocol file for the given CID.

    Args:
        cid (str): The CID code for the disease.

    Returns:
        str: The URL to the protocol file.
    """
    # English: protocol
    protocolo = Protocolo.objects.get(doenca__cid=cid)
    # English: file
    arquivo = protocolo.arquivo
    # English: link
    link = os.path.join(settings.STATIC_URL, "protocolos", arquivo)
    return link


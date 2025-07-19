import os
import secrets
import time
from django.conf import settings
from django.forms.models import model_to_dict
from django.core.cache import cache
from datetime import datetime
from .manejo_pdfs_memory import GeradorPDFMemory
from processos.models import Processo, Protocolo, Medicamento
from pacientes.models import Paciente

# DEBUG: Print all PDF-related settings at module load
print(f"\n=== PDF SETTINGS DEBUG ===")
print(f"DEBUG: PATH_LME_BASE: {getattr(settings, 'PATH_LME_BASE', 'NOT_SET')}")
print(f"DEBUG: PATH_LME_BASE exists: {os.path.exists(getattr(settings, 'PATH_LME_BASE', '')) if hasattr(settings, 'PATH_LME_BASE') else 'NOT_SET'}")
print(f"DEBUG: PATH_RELATORIO: {getattr(settings, 'PATH_RELATORIO', 'NOT_SET')}")
print(f"DEBUG: PATH_RELATORIO exists: {os.path.exists(getattr(settings, 'PATH_RELATORIO', '')) if hasattr(settings, 'PATH_RELATORIO') else 'NOT_SET'}")
print(f"DEBUG: PATH_EXAMES: {getattr(settings, 'PATH_EXAMES', 'NOT_SET')}")
print(f"DEBUG: PATH_EXAMES exists: {os.path.exists(getattr(settings, 'PATH_EXAMES', '')) if hasattr(settings, 'PATH_EXAMES') else 'NOT_SET'}")
print(f"DEBUG: PATH_PDF_DIR: {getattr(settings, 'PATH_PDF_DIR', 'NOT_SET')}")
print(f"DEBUG: PATH_PDF_DIR exists: {os.path.exists(getattr(settings, 'PATH_PDF_DIR', '')) if hasattr(settings, 'PATH_PDF_DIR') else 'NOT_SET'}")
print(f"DEBUG: STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'NOT_SET')}")
print(f"DEBUG: STATIC_URL: {getattr(settings, 'STATIC_URL', 'NOT_SET')}")
if hasattr(settings, 'PATH_PDF_DIR') and os.path.exists(settings.PATH_PDF_DIR):
    try:
        protocols_list = os.listdir(settings.PATH_PDF_DIR)
        print(f"DEBUG: Available protocols: {protocols_list}")
    except Exception as e:
        print(f"DEBUG: Error listing protocols: {e}")
print(f"=== PDF SETTINGS DEBUG END ===\n")


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


# English: generate_prescription
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


# English: generate_medication_dosage
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


# English: list_medications
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


# English: associate_medications
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


# English: create_renewal_dictionary
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
    return dicionario


# English: generate_renewal_data
def gerar_dados_renovacao(primeira_data, processo_id):
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
    import time
    start_time = time.time()
    print(f"\n=== GERAR_DADOS_RENOVACAO START ===")
    print(f"DEBUG: primeira_data: {primeira_data}")
    print(f"DEBUG: processo_id: {processo_id}")
    
    # English: process
    processo = Processo.objects.get(id=processo_id)
    print(f"DEBUG: Found process: {processo.id} for patient {processo.paciente.nome_paciente}")
    print(f"DEBUG: Process CID: {processo.doenca.cid}")
    print(f"DEBUG: Process diagnosis: {processo.doenca.nome}")
    
    # English: data
    dados = {}
    # English: data_list
    lista_dados = [
        model_to_dict(processo),
        model_to_dict(processo.paciente),
        model_to_dict(processo.medico),
        model_to_dict(processo.clinica),
    ]
    for d in lista_dados:
        # English: data
        dados.update(d)
    
    print(f"DEBUG: Combined data keys: {list(dados.keys())}")
    
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
        print(f"ERROR: Empty date provided for renewal")
        raise ValueError("Data de renovação não pode estar vazia")
    
    try:
        # English: data
        dados["data_1"] = datetime.strptime(primeira_data, "%d/%m/%Y")
        print(f"DEBUG: Parsed renewal date: {dados['data_1']}")
    except ValueError as e:
        print(f"ERROR: Invalid date format '{primeira_data}': {e}")
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
        print(f"DEBUG: Protocol name: {protocolo.nome}")
        
        if protocolo.nome == "dor_crônica":
            print(f"DEBUG: Chronic pain protocol detected")
            print(f"DEBUG: Original dados_condicionais: {processo.dados_condicionais}")
            
            # For chronic pain, we need to include the LANNS/EVA assessment form
            # This will be picked up by the conditional PDFs glob pattern
            # English: data
            dados["include_lanns_eva"] = True
            
            # Preserve any conditional data from original process
            if processo.dados_condicionais:
                for key, value in processo.dados_condicionais.items():
                    # English: data
                    dados[key] = value
                    print(f"DEBUG: Preserved conditional data: {key} = {value}")
            
            print(f"DEBUG: Set include_lanns_eva flag for chronic pain renewal")
            
    except Exception as e:
        print(f"ERROR: Failed to check protocol for conditional requirements: {e}")
    
    print(f"DEBUG: Set conditional flags - consent: {dados['consentimento']}, report: {dados['relatorio']}, exams: {dados['exames']}")
    
    resgatar_prescricao(dados, processo)
    print(f"DEBUG: Retrieved prescription data")
    
    # English: medication_ids
    meds_ids = gerar_lista_meds_ids(dados)
    print(f"DEBUG: Generated medication IDs: {meds_ids}")
    
    # English: data
    dados = gera_med_dosagem(dados, meds_ids)[0]
    print(f"DEBUG: Generated medication dosage data")
    
    print(f"DEBUG: Final data keys before return: {list(dados.keys())}")
    end_time = time.time()
    print(f"DEBUG: Data generation completed in {end_time - start_time:.3f}s")
    print(f"=== GERAR_DADOS_RENOVACAO END ===\n")
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
def transfere_dados_gerador(dados):
    """Transfers the final process data to the PDF generator.

    This function takes the complete data dictionary for a process, passes it
    to the `GeradorPDFMemory` class, and returns the path to the generated PDF file.
    The PDF is generated in memory and cached for serving.

    Critique:
    - The function has a lot of debugging prints, which should be removed
      in a production environment. Using Python's `logging` module would be
      a better way to handle debugging information.
    - The error handling is very broad. It catches any exception and returns
      None. It would be better to catch specific exceptions and log them
      properly to make debugging easier.

    Args:
        # English: data
        dados (dict): The complete data dictionary for the process.

    Returns:
        str: The path to the generated PDF file, or None if an error occurs.
    """
    try:
        import time
        start_time = time.time()
        print(f"\n=== TRANSFERE_DADOS_GERADOR START ===")
        print(f"DEBUG: Input data keys: {list(dados.keys())}")
        print(f"DEBUG: Patient CPF: {dados.get('cpf_paciente', 'NOT_FOUND')}")
        print(f"DEBUG: CID: {dados.get('cid', 'NOT_FOUND')}")
        print(f"DEBUG: Consent flag: {dados.get('consentimento', 'NOT_FOUND')}")
        print(f"DEBUG: Report flag: {dados.get('relatorio', 'NOT_FOUND')}")
        print(f"DEBUG: Exams flag: {dados.get('exames', 'NOT_FOUND')}")
        print(f"DEBUG: Data_1: {dados.get('data_1', 'NOT_FOUND')}")
        print(f"DEBUG: Medication ID 1: {dados.get('id_med1', 'NOT_FOUND')}")
        print(f"DEBUG: PATH_LME_BASE: {settings.PATH_LME_BASE}")
        print(f"DEBUG: PATH_LME_BASE exists: {os.path.exists(settings.PATH_LME_BASE)}")
        
        # Save CPF and CID before PDF generation (they might be modified during processing)
        cpf_paciente = dados.get('cpf_paciente', 'unknown')
        cid = dados.get('cid', 'unknown')
        print(f"DEBUG: Saved CPF before PDF generation: '{cpf_paciente}'")
        print(f"DEBUG: Saved CID before PDF generation: '{cid}'")
        
        # English: pdf
        pdf_create_start = time.time()
        pdf = GeradorPDFMemory(dados, settings.PATH_LME_BASE)
        pdf_create_end = time.time()
        print(f"DEBUG: GeradorPDFMemory instance created in {pdf_create_end - pdf_create_start:.3f}s")
        
        # Generate PDF in memory and get HttpResponse
        pdf_gen_start = time.time()
        response = pdf.generico_stream(dados, settings.PATH_LME_BASE)
        pdf_gen_end = time.time()
        print(f"DEBUG: generico_stream method returned response in {pdf_gen_end - pdf_gen_start:.3f}s")
        
        if response is None:
            print(f"ERROR: PDF generation failed in transfere_dados_gerador")
            return None
        
        # Store the response in a cache or session for later serving
        # Use the saved CPF and CID (not from dados which might be modified)
        
        print(f"DEBUG: Using saved CPF: '{cpf_paciente}' (type: {type(cpf_paciente)})")
        print(f"DEBUG: Using saved CID: '{cid}' (type: {type(cid)})")
        
        # Check if CPF was saved correctly
        if cpf_paciente == 'unknown':
            print(f"DEBUG: CPF was not saved correctly! Checking all keys...")
            for key, value in dados.items():
                if 'cpf' in key.lower():
                    print(f"DEBUG: Found CPF-related key: {key} = {value}")
        
        nome_final_pdf = f"pdf_final_{cpf_paciente}_{cid}.pdf"
        print(f"DEBUG: Final PDF name will be: {nome_final_pdf}")
        
        # Save PDF to /tmp for immediate serving
        tmp_pdf_path = f"/tmp/{nome_final_pdf}"
        with open(tmp_pdf_path, 'wb') as f:
            f.write(response.content)
        print(f"DEBUG: PDF saved to: {tmp_pdf_path}")
        
        # Return the URL path as before
        from django.urls import reverse
        path_pdf_final = reverse('processos-serve-pdf', kwargs={'filename': nome_final_pdf})
        
        end_time = time.time()
        total_time = end_time - start_time
        print(f"DEBUG: PDF generated successfully: {path_pdf_final}")
        print(f"DEBUG: Total transfere_dados_gerador time: {total_time:.3f}s")
        print(f"=== TRANSFERE_DADOS_GERADOR END ===\n")
        return path_pdf_final
        
    except Exception as e:
        print(f"ERROR: Exception in transfere_dados_gerador: {e}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        return None


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
        print(f"\n=== GERAR_PDF_STREAM START ===")
        print(f"DEBUG: Input data keys: {list(dados.keys())}")
        print(f"DEBUG: Patient CPF: {dados.get('cpf_paciente', 'NOT_FOUND')}")
        print(f"DEBUG: CID: {dados.get('cid', 'NOT_FOUND')}")
        print(f"DEBUG: Using in-memory PDF generation")
        
        # Create memory-based PDF generator
        pdf_generator = GeradorPDFMemory(dados, settings.PATH_LME_BASE)
        print(f"DEBUG: GeradorPDFMemory instance created")
        
        # Generate PDF and return HttpResponse
        response = pdf_generator.generico_stream(dados, settings.PATH_LME_BASE)
        print(f"DEBUG: PDF stream generated successfully")
        print(f"=== GERAR_PDF_STREAM END ===\n")
        
        return response
        
    except Exception as e:
        print(f"ERROR: Exception in gerar_pdf_stream: {e}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
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
    # English: patient_exists
    paciente_existe = kwargs.pop("paciente_existe")
    # English: patient_data
    dados_paciente = gerar_dados_paciente(dados)
    # English: patient_cpf
    cpf_paciente = dados["cpf_paciente"]

    if paciente_existe:
        # English: patient_data
        dados_paciente["id"] = paciente_existe.pk
        # English: patient
        paciente = preparar_modelo(Paciente, **dados_paciente)
        # English: process_data
        dados_processo = gerar_dados_processo(
            dados, meds_ids, doenca, emissor, paciente, usuario
        )
        # English: process_data
        dados_processo["paciente"] = paciente_existe
        cid = kwargs.pop("cid", None)
        # English: process_exists
        processo_existe = False
        for p in paciente_existe.processos.all():
            if p.doenca.cid == cid:
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
        paciente.save(force_update=True)
        associar_med(processo, meds_ids)
        paciente.usuarios.add(usuario)
        emissor.pacientes.add(paciente_existe)
    else:
        # English: patient
        paciente = preparar_modelo(Paciente, **dados_paciente)
        paciente.save()
        # English: patient
        paciente = Paciente.objects.get(cpf_paciente=cpf_paciente)
        # English: process_data
        dados_processo = gerar_dados_processo(
            dados, meds_ids, doenca, emissor, paciente, usuario
        )
        # English: process
        processo = preparar_modelo(Processo, **dados_processo)
        processo.save()
        associar_med(processo, meds_ids)
        usuario.pacientes.add(paciente)
        emissor.pacientes.add(paciente)

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


# ############################### Path pdf_final

# PATH_PDF_FINAL = 'pdf_final_{}_{}.pdf'.format(dados_paciente['cpf_paciente'],dados_processo['cid'])


# ############################### DADOS CONDICIONAIS - deverá haver opção do médico defini-los
# #### ou selecionar os padrões como descritos abaixo.

# dados_condicionais = {}

# ### DOENÇA DE ALZHEIMER

# exames1vez = '''
# Hemograma,sódio, potássio, cálcio total, creatinina, uréia, Glicemia de jejum,
# TSH (Hormônio Tireoestimulante), ácido fólico, vitamina B12, VDRL, TGO, TGP
# '''

# #### ARTRITE REUMATÓIDE


# med_ar_grupo_1 = [ 'azatioprina', 'ciclosporina', 'cloroquina', 'hidroxicloroquina', 'leflunomida',
#                     'metotrexato', 'naproxeno', 'sulfassalazina' ]

# exames_ar_grupo_1 = ['VHS', 'Fator reumatóide']

# exames_ar_grupo_2 = ['Hemograma', 'TGO', 'TGP', 'VHS', 'HbsAg', 'Anti-HCV', 'Fator reumatóide',
#                     'Prova de Mantoux - PPD']

# meds_relatorio_ar = ['abatacepte', 'etanercepte', 'golimumabe', 'rituximabe', 'tocilizumabe']


# aviso_ar = '''
#         Acrescentar laudo ou relatório médico da radiografia de tórax. Descrever critérios
#         diagnósticos na LME
#         '''


# dados_ar = {
#     'exames_ar_grupo_1': exames_ar_grupo_1,
#     'exames_ar_grupo_2': exames_ar_grupo_2,
#     'aviso_ar': aviso_ar
# }


# #### ESCLEROSE MÚLTIPLA

# relatorio_nata = '''
# Relatório médico contendo:
# 1. Falha terapêutica ou contraindicação ao fingolimode; 2. Se o paciente está sem receber imunomodulador
# por pelo menos 45 dias ou azatioprina por 3 meses; 3. Se paciente não foi diagnosticado com micose sistêmica
# nos últimos 6 meses, herpes grave nos últimos 3 meses, infecção por HIV, qualquer outra infecção oportunista nos últimos
# 3 meses ou infecção atual ativa.
# '''

# relatorio_fingo = '''
# Relatório médico, contendo: A. Justificativa para interrupção do uso ou motivo da não utilização de primeira linha:
# 1. Falha terapêutica à betainterferona ou ao glatirâmer ou ao teriflunomida
# 2. Ausência de contraindicação ao uso do fingolimode'
# '''

# relatorio_fumarato = '''
# 1. Em casos de intolerância, reações adversas ou falta de adesão à Betainterferon ou ao Glatiramer ou à
# Teriflunomida;
# 2. Em casos de falha terapêutica ou resposta sub-ótima à Betainterferon ou ao Glatiramer ou à
# Teriflunomida.
# '''

# dados_esclerose_multipla = {
#     'edss': '3',
#     'exames_em_1vez': 'Hemograma, TGO, TGP, FA, GGT, Vitamina B12, Sorologia HIV, VDRL, Bilirrubinas total e frações, TSH',
#     'exames_em_renova': 'Hemograma, TGO, TGP, FA, GGT, Bilirrubinas total e frações, TSH',
#     'relatorio_fingolimode_1vez': relatorio_fingo,
#     'relatorio_natalizumabe_1vez': relatorio_nata,
#     'relatorio_fumarato_1vez': relatorio_fumarato,
#     'exames_nata_renova': 'Hemograma'}


# ##### Epilepsia

# relatorio_epilepsia_1vez = '''
#     Relatar características das crises, se há risco de recorrência superior a 60%, se apresentaram duas
#     crises com intervalo superior a 24 horas e se tem diagnóstico de síndrome epiléptica específica '''

# dados_epilepsia = {
#     'relatorio_epilepsia_1vez': relatorio_epilepsia_1vez,
#     'exames_solicitados': 'Não são obrigatórios exames, a critério do médico prescritor'
# }


# ############# Dislipidemia


# dislipidemia_1vez_exames = ['TGO', 'TGP', 'CPK', 'TSH', 'Colesterol total e frações (HDL e LDL)', 'Triglicerídeos']


# fibratos_1vez_exames = ['TGO', 'TGP', 'CPK', 'TSH', 'Triglicérides']

# dados_dislipidemia = {
#     'ac_nicotinico_trat_previo': 'Contraindicação ao uso de estatinas',
#     'dislipidemia_1vez_exames': dislipidemia_1vez_exames,
#     'fibratos_1vez_exames': fibratos_1vez_exames
# }

# ############# Dor crônica

# dados_dor = {
#     'eva': '5', ## de 4 a 10
#     'lanns_escore': '24' ## depois completar com as categorias individuais
# }

from processos.models import Doenca

doencas = {
    "M05.0": "Síndrome de Felty",
    "M05.3": "Artrite Reumatóide Com Comprometimento de Outros Órgãos e Sistemas",
    "M05.8": "Outras Artrites Reumatóides Soro-positivas",
    "M06.0": "Artrite Reumatóide Soro-negativa",
    "M06.8": "Outras Artrites Reumatóides Especificadas",
    "M08.0": "Artrite Reumatóide Juvenil",
    "E78.0": "Hipercolesterolemia Pura",
    "E78.1": "Hipergliceridemia Pura",
    "E78.2": "Hiperlipidemia Mista",
    "E78.3": "Hiperquilomicronemia",
    "E78.4": "Outras Hiperlipidemias",
    "E78.5": "Hiperlipidemia Não Especificada",
    "E78.6": "Deficiências de Lipoproteínas",
    "E78.8": "Outros Distúrbios do Metabolismo de Lipoproteínas",
    "Q80.0": "Ictiose Vulgar",
    "Q80.1": "Ictiose Ligada ao Cromossomo X",
    "Q80.2": "Ictiose Lamelar",
    "Q80.3": "Eritrodermia Ictiosiforme Bulhosa Congênita",
    "Q80.8": "Outras Ictioses Congênitas",
    "Q82.8": "Outras Malformações Congênitas Especificadas da Pele",
    "M08.1": "Espondilite Ancilosante Juvenil",
    "M08.2": "Artrite Juvenil Com Início Sistêmico",
    "M08.3": "Poliartrite Juvenil (soro-negativa)",
    "M08.4": "Artrite Juvenil Pauciarticular",
    "M08.8": "Outras Artrites Juvenis",
    "M08.9": "Artrite Juvenil Não Especificada",
    "K50.0": "Doença de Crohn do Intestino Delgado",
    "K50.1": "Doença de Crohn do Intestino Grosso",
    "K50.8": "Outra Forma de Doença de Crohn",
    "L73.2": "Hidradenite Supurativa",
    "L40.0": "Psoríase Vulgar",
    "L40.1": "Psoríase Pustulosa Generalizada",
    "L40.4": "Psoríase Gutata",
    "L40.8": "Outras Formas de Psoríase",
    "H30.1": "Inflamação Corrorretiniana Disseminada",
    "H30.2": "Ciclite Posterior",
    "H30.8": "Outras Inflamações Coriorretinianas",
    "H20.1": "Iridociclite Crônica",
    "H15.0": "Esclerite",
    "E84.0": "Fibrose Cística Com Manifestações Pulmonares",
    "E84.8": "Fibrose Cística Com Outras Manifestações",
    "N18.0": "Doença Renal em Estádio Final",
    "N18.8": "Outra Insuficiência Renal Crônica",
    "D18.0": "Hemangioma de Qualquer Localização",
    "B18.0": "Hepatite Viral Crônica B Com Agente Delta",
    "B18.1": "Hepatite Crônica Viral B Sem Agente Delta",
    "B17.1": "Hepatite Aguda C",
    "B18.2": "Hepatite Viral Crônica C",
    "G20": "Doença de Parkinson",
    "I27.0": "Hipertensão Pulmonar Primária",
    "I27.2": "Outra Hipertensão Pulmonar Secundária",
    "I27.8": "Outras Doenças Pulmonares do Coração Especificadas",
    "D61.0": "Anemia Aplástica Constitucional",
    "G35": "Esclerose Múltipla",
    "J45.0": "Asma Predominantemente Alérgica",
    "J45.1": "Asma Não-alérgica",
    "J45.8": "Asma Mista",
    "E22.0": "Acromegalia e Gigantismo Hipofisário",
    "M88.0": "Doença de Paget do Crânio",
    "M88.8": "Doença de Paget de Outros Ossos",
    "E83.3": "Distúrbios do Metabolismo do Fósforo",
    "N25.0": "Osteodistrofia Renal",
    "E20.0": "Hipoparatireoidismo Idiopático",
    "E20.1": "Pseudohipoparatireoidismo",
    "E20.8": "Outro Hipoparatireoidismo",
    "E89.2": "Hipoparatireoidismo Pós-procedimento",
    "M45": "Espondilite Ancilosante",
    "M46.8": "Outras Espondilopatias Inflamatórias Especificadas",
    "D59.0": "Anemia Hemolítica Auto-imune Induzida Por Droga",
    "D59.1": "Outras Anemias Hemolíticas Auto-imunes",
    "E25.0": "Transtornos Adrenogenitais Congênitos Associados à Deficiência Enzimática",
    "G40.0": "Epilepsia e Síndromes Epilépticas Idiopáticas Definidas Por Sua Localização (focal) (parcial) Com Crises de Início Focal",
    "G40.1": "Epilepsia e Síndromes Epilépticas Sintomáticas Definidas Por Sua Localização (focal) (parcial) Com Crises Parciais Simples",
    "G40.2": "Epilepsia e Síndromes Epilépticas Sintomáticas Definidas Por Sua Localização (focal) (parcial) Com Crises Parciais Complexas",
    "G40.3": "Epilepsia e Síndromes Epilépticas Generalizadas Idiopáticas",
    "G40.4": "Outras Epilepsias e Síndromes Epilépticas Generalizadas",
    "G40.5": "Síndromes Epilépticas Especiais",
    "G40.6": "Crise de Grande Mal, Não Especificada (com ou Sem Pequeno Mal)",
    "G40.7": "Pequeno Mal Não Especificado, Sem Crises de Grande Mal",
    "G40.8": "Outras Epilepsias",
    "I20.0": "Angina Instável",
    "I20.1": "Angina Pectoris Com Espasmo Documentado",
    "I21.0": "Infarto Agudo Transmural da Parede Anterior do Miocárdio",
    "I21.1": "Infarto Agudo Transmural da Parede Inferior do Miocárdio",
    "I21.2": "Infarto Agudo Transmural do Miocárdio de Outras Localizações",
    "I21.3": "Infarto Agudo Transmural do Miocárdio, de Localização Não Especificada",
    "I21.4": "Infarto Agudo Subendocárdico do Miocárdio",
    "I21.9": "Infarto Agudo do Miocárdio Não Especificado",
    "I22.0": "Infarto do Miocárdio Recorrente da Parede Anterior",
    "I22.1": "Infarto do Miocárdio Recorrente da Parede Inferior",
    "I22.8": "Infarto do Miocárdio Recorrente de Outras Localizações",
    "I22.9": "Infarto do Miocárdio Recorrente de Localização Não Especificada",
    "I23.0": "Hemopericárdio Como Complicação Atual Subseqüente ao Infarto Agudo do Miocárdio",
    "I23.1": "Comunicação Interatrial Como Complicação Atual Subseqüente ao Infarto Agudo do Miocárdio",
    "I23.2": "Comunicação Interventricular Como Complicação Atual Subseqüente ao Infarto Agudo do Miocárdio",
    "I23.3": "Ruptura da Parede do Coração Sem Ocorrência de Hemopericárdio Como Complicação Atual Subseqüente ao Infarto Agudo do Miocárdio",
    "I23.4": "Ruptura de Cordoalhas Tendíneas Como Complicação Atual Subseqüente ao Infarto Agudo do Miocárdio",
    "I23.5": "Ruptura de Músculos Papilares Como Complicação Atual Subseqüente ao Infarto Agudo do Miocárdio",
    "I23.6": "Trombose de Átrio, Aurícula e Ventrículo Como Complicação Atual Subseqüente ao Infarto Agudo do Miocárdio",
    "I23.8": "Outras Complicações Atuais Subseqüentes ao Infarto Agudo do Miocárdio",
    "I24.0": "Trombose Coronária Que Não Resulta em Infarto do Miocárdio",
    "I24.8": "Outras Formas de Doença Isquêmica Aguda do Coração",
    "I24.9": "Doença Isquêmica Aguda do Coração Não Especificada",
    "L93.0": "Lúpus Eritematoso Discóide",
    "L93.1": "Lúpus Eritematoso Cutâneo Subagudo",
    "M32.1": "Lúpus Eritematoso Disseminado (sistêmico) Com Comprometimento de Outros Órgãos e Sistemas",
    "M32.8": "Outras Formas de Lúpus Eritematoso Disseminado (sistêmico)",
    "F20.0": "Esquizofrenia Paranóide",
    "F20.1": "Esquizofrenia Hebefrênica",
    "F20.2": "Esquizofrenia Catatônica",
    "F20.3": "Esquizofrenia Indiferenciada",
    "F20.4": "Depressão Pós-esquizofrênica",
    "F20.5": "Esquizofrenia Residual",
    "F20.6": "Esquizofrenia Simples",
    "F20.8": "Outras Esquizofrenias",
    "R52.1": "Dor Crônica Intratável",
    "R52.2": "Outra Dor Crônica",
    "E70.0": "Fenilcetonúria Clássica",
    "E70.1": "Outras Hiperfenilalaninemias",
    "D84.1": "Defeitos no Sistema Complemento",
    "E83.1": "Doença do Metabolismo do Ferro",
    "T45.4": "Intoxicação Por Ferro e Seus Compostos",
    "E23.2": "Diabetes Insípido",
    "G30.0": "Doença de Alzheimer de Início Precoce",
    "G30.1": "Doença de Alzheimer de Início Tardio",
    "G30.8": "Outras Formas de Doença de Alzheimer",
    "F00.0": "Demência na Doença de Alzheimer de Início Precoce",
    "F00.1": "Demência na Doença de Alzheimer de Início Tardio",
    "F00.2": "Demência na Doença de Alzheimer, Forma Atípica ou Mista",
    "D69.3": "Púrpura Trombocitopênica Idiopática",
    "M07.0": "Artropatia Psoriásica Interfalangiana Distal",
    "M07.2": "Espondilite Psoriásica",
    "M07.3": "Outras Artropatias Psoriásicas",
    "T86.1": "Falência ou Rejeição de Transplante de Rim",
    "Z94.0": "Rim Transplantado",
    "T86.4": "Falência ou Rejeição de Transplante de Fígado",
    "Z94.4": "Fígado Transplantado",
    "J44.0": "Doença Pulmonar Obstrutiva Crônica Com Infecção Respiratória Aguda do Trato Respiratório Inferior",
    "J44.1": "Doença Pulmonar Obstrutiva Crônica Com Exacerbação Aguda Não Especificada",
    "J44.8": "Outras Formas Especificadas de Doença Pulmonar Obstrutiva Crônica",
    "D46.0": "Anemia Refratária Sem Sideroblastos",
    "D46.1": "Anemia Refratária Com Sideroblastos",
    "D46.7": "Outras Síndromes Mielodisplásicas",
    "D61.1": "Anemia Aplástica Induzida Por Drogas",
    "D61.2": "Anemia Aplástica Devida a Outros Agentes Externos",
    "D61.3": "Anemia Aplástica Idiopática",
    "D61.8": "Outras Anemias Aplásticas Especificadas",
    "D70": "Agranulocitose",
    "Z94.8": "Outros Órgãos e Tecidos Transplantados",
    "N80.0": "Endometriose do Útero",
    "N80.1": "Endometriose do Ovário",
    "N80.2": "Endometriose da Trompa de Falópio",
    "N80.3": "Endometriose do Peritônio Pélvico",
    "N80.4": "Endometriose do Septo Retovaginal e da Vagina",
    "N80.5": "Endometriose do Intestino",
    "N80.8": "Outra Endometriose",
    "D56.1": "Talassemia Beta",
    "D56.8": "Outras Talassemias",
    "D57.0": "Anemia Falciforme Com Crise",
    "D57.1": "Anemia Falciforme Sem Crise",
    "D57.2": "Transtornos Falciformes Heterozigóticos Duplos",
    "E76.1": "Mucopolissacaridose do Tipo II",
    "E75.2": "Outras Esfingolipidoses",
    "B16.0": "Hepatite Aguda B Com Agente Delta (co-infecção), Com Coma Hepático",
    "B16.2": "Hepatite Aguda B Sem Agente Delta, Com Coma Hepático",
    "E10.0": "Diabetes Mellitus Insulino-dependente - Com Coma",
    "E10.1": "Diabetes Mellitus Insulino-dependente - Com Cetoacidose",
    "E10.2": "Diabetes Mellitus Insulino-dependente - Com Complicações Renais",
    "E10.3": "Diabetes Mellitus Insulino-dependente - Com Complicações Oftálmicas",
    "E10.4": "Diabetes Mellitus Insulino-dependente - Com Complicações Neurológicas",
    "E10.5": "Diabetes Mellitus Insulino-dependente - Com Complicações Circulatórias Periféricas",
    "E10.6": "Diabetes Mellitus Insulino-dependente - Com Outras Complicações Especificadas",
    "E10.7": "Diabetes Mellitus Insulino-dependente - Com Complicações Múltiplas",
    "E10.8": "Diabetes Mellitus Insulino-dependente - Com Complicações Não Especificadas",
    "E10.9": "Diabetes Mellitus Insulino-dependente - Sem Complicações",
    "L70.0": "Acne Vulgar",
    "L70.1": "Acne Conglobata",
    "L70.8": "Outras Formas de Acne",
    "E76.0": "Mucopolissacaridose do Tipo I",
    "D25.0": "Leiomioma Submucoso do Útero",
    "D25.1": "Leiomioma Intramural do Útero",
    "D25.2": "Leiomioma Subseroso do Útero",
    "K51.0": "Enterocolite Ulcerativa (crônica)",
    "K51.1": "Ileocolite Ulcerativa (crônica)",
    "K51.2": "Proctite Ulcerativa (crônica)",
    "K51.3": "Retossigmoidite Ulcerativa (crônica)",
    "K51.4": "Pseudopolipose do Cólon",
    "K51.5": "Proctocolite Mucosa",
    "K51.8": "Outras Colites Ulcerativas",
    "Z94.1": "Coração Transplantado",
    "M80.0": "Osteoporose Pós-menopáusica Com Fratura Patológica",
    "M80.1": "Osteoporose Pós-ooforectomia Com Fratura Patológica",
    "M80.2": "Osteoporose de Desuso Com Fratura Patológica",
    "M80.3": "Osteoporose Por Má-absorção Pós-cirúrgica Com Fratura Patológica",
    "M80.4": "Osteoporose Induzida Por Drogas Com Fratura Patológica",
    "M80.5": "Osteoporose Idiopática Com Fratura Patológica",
    "M80.8": "Outras Osteoporoses Com Fratura Patológica",
    "M81.0": "Osteoporose Pós-menopáusica",
    "M81.1": "Osteoporose Pós-ooforectomia",
    "M81.2": "Osteoporose de Desuso",
    "M81.3": "Osteoporose Devida à Má-absorção Pós-cirúrgica",
    "M81.4": "Osteoporose Induzida Por Drogas",
    "M81.5": "Osteoporose Idiopática",
    "M81.6": "Osteoporose Localizada (Lequesne)",
    "M81.8": "Outras Osteoporoses",
    "M82.0": "Osteoporose na Mielomatose Múltipla",
    "M82.1": "Osteoporose em Distúrbios Endócrinos",
    "M82.8": "Osteoporose em Outras Doenças Classificadas em Outra Parte",
    "E84.1": "Fibrose Cística Com Manifestações Intestinais",
    "E83.0": "Distúrbios do Metabolismo do Cobre",
    "G70.0": "Miastenia Gravis",
    "G12.2": "Doença do Neurônio Motor",
    "F84.0": "Autismo Infantil",
    "F84.1": "Autismo Atípico",
    "F84.3": "Outro Transtorno Desintegrativo da Infância",
    "F84.5": "Síndrome de Asperger",
    "F84.8": "Outros Transtornos Globais do Desenvolvimento",
    "E23.0": "Hipopituitarismo",
    "E85.1": "Amiloidose Heredofamiliar Neuropática",
    "N04.0": "Síndrome Nefrótica - Anormalidade Glomerular Minor",
    "N04.1": "Síndrome Nefrótica - Lesões Glomerulares Focais e Segmentares",
    "N04.2": "Síndrome Nefrótica - Glomerulonefrite Membranosa Difusa",
    "N04.3": "Síndrome Nefrótica - Glomerulonefrite Proliferativa Mesangial Difusa",
    "N04.4": "Síndrome Nefrótica - Glomerulonefrite Proliferativa Endocapilar Difusa",
    "N04.5": "Síndrome Nefrótica - Glomerulonefrite Mesangiocapilar Difusa",
    "N04.6": "Síndrome Nefrótica - Doença de Depósito Denso",
    "N04.7": "Síndrome Nefrótica - Glomerulonefrite Difusa em Crescente",
    "N04.8": "Síndrome Nefrótica - Outras",
    "G24.3": "Torcicolo Espasmódico",
    "G24.4": "Distonia Orofacial Idiopática",
    "G24.5": "Blefaroespasmo",
    "G24.8": "Outras Distonias",
    "G51.3": "Espasmo Hemifacial Clônico",
    "G51.8": "Outros Transtornos do Nervo Facial",
    "E22.8": "Outras Hiperfunções da Hipófise",
}


# save diseases
def salvar_doencas(doencas):
    """
    Saves disease data to the database from a dictionary of CID codes.
    
    This function populates the Doenca model with ICD-10 disease codes
    and their corresponding Portuguese names. It's typically used for
    initial database seeding or bulk updates of disease information.
    
    Args:
        doencas (dict): Dictionary mapping CID codes to disease names
                       Format: {'CID_CODE': 'Disease Name'}
    
    Critique:
    - Function uses bare except which can hide important errors
    - No transaction handling - partial failures leave inconsistent state
    - Print statements instead of proper logging
    - No validation of CID code format or duplicate checking
    - Function executes immediately upon import (line 251)
    
    Suggested Improvements:
    - Add proper logging instead of print statements
    - Implement get_or_create to handle duplicates gracefully
    - Add transaction.atomic decorator for consistency
    - Validate CID code format (ICD-10 standard)
    - Add progress reporting for large datasets
    - Remove automatic execution and make it a management command
    """
    for item in doencas.items():
        try:
            doenca = Doenca(cid=item[0], nome=item[1])
            doenca.save()
        except Exception as e:
            print(f"doença {item} não foi salva: {e}")


salvar_doencas(doencas)

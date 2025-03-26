# AutoCusto

## Background

The Unified Health System, known as "Sistema Único de Saúde" (SUS), is a universal health insurance established by the Brazilian 1988 Constitution. It is the only public health care system in the world which offers insurance for more than 190 million people[^1].

Among its programs is the "High Cost Pharmacies," a service providing specialized medications for a wide range of chronic diseases. This service is utilized even by patients with private health insurance, as many of the substances provided are not covered by private policies.

As of October 2023, the Brazilian minimum wage is R$ 1,320 (~ € 250). Thus, commonly used medications for prevalent conditions like Diabetes or Dyslipidemia can consume over 15% of a person's monthly income, rendering the treatment unaffordable without this assistance. Moreover, the program is also responsible for the dispensation of immunobiologics, oncological treatments, and drugs for rare diseases, which can cost thousands of euros per month.

## Bureaucracy

A nationwide directive regulates prescription dispensing, requiring the following *printed* documents:

- For each medication:
    - "Laudo de medicamento especializado da farmácia de alto custo" (LME - Specialized Medication Report from High-Cost Pharmacy) plus six dated prescriptions;
    - A consent form for new prescriptions.
  
- Conditional documents, depending on the diagnosis, may include:
    - Scales (such as Mini-mental and CDR for Alzheimer's, Pain score for Chronic Pain, etc.);
    - A Medical Report;
    - Serologic and/or radiologic tests requests.
 

## Challenges

- Some processes necessitate over 15 manually filled paper sheets;
- Public system doctors often treat more than four patients per hour, frequently without access to a printer;
- Minor errors, like misrecording an ICD number (e.g., G40 instead of G40.0), often result in medication release refusal. Consequently, patients must schedule a new appointment, and all forms must be completed anew;
- A great deal of these conditional forms has no clinical significance at all and constitutes more 'opportunities' for silly mistakes to be made.

## The Project

AutoCusto, a Portuguese pun combining "Alto" (High) and "Auto" (Automatic), was conceived to address these issues. It aims to minimize mistakes, rework, and patient inconvenience. A doctor's primary focus should be patient care, not navigating through unnecessary bureaucracy. I have personally utilized this software for the past three years with over 400 unique patients. At the moment, the algorithm is fine-grained to Neurologic Disorders.

## How to start the development server

1. Clone the repository
2. Build the containers
    ``` sudo docker-compose up ```
3. Access the web-dev container shell
   ``` sudo docker exec -it [web-dev container id*] /bin/bash ```
   * ```sudo docker ps``` to find the container id
5. Inside the container shell run
   ``` python3 manage.py migrate ```
6. Access the Django shell
   ``` python3 manage.py shell ```
7. Inside the django shell, run the following command to populate the database
    ``` from processos.db import doencas, med, protocolos, normatizacao, med_protocolos ```
8. Access via web-browser the address 0.0.0.0:8000. The initial password ("código de convite") is cgrlmeplus
   
[^1] https://www.gov.br/saude/pt-br/assuntos/noticias/2021/setembro/maior-sistema-publico-de-saude-do-mundo-sus-completa-31-anos

# AutoCusto

## Background

The Unified Health System, known as "Sistema Único de Saúde" (SUS), is a public, universal health insurance initiative established by the 1988 constitution. It offers direct medical care to over 100 million people within the Brazilian population.

Among its programs is the "High Cost Pharmacies," a service providing specialized medications for a wide range of chronic diseases. This service is utilized even by patients with private health insurance, as many of the substances provided are not covered by private policies.

As of October 2023, the Brazilian minimum wage is R$ 1,320 (~250 euros). Thus, commonly used medications for prevalent conditions like Diabetes or Dyslipidemia can consume over 15% of a person's monthly income, rendering the treatment unaffordable without this assistance. Moreover, the program is also responsible for the dispensation of immunobiologics, oncological treatments, and drugs for rare diseases, which can cost thousands of dollars per month.

## Bureaucracy

A nationwide directive regulates prescription dispensing, requiring the following *printed* documents:

- For each medication:
    - "Laudo de medicamento especializado da farmácia de alto custo" (LME - Specialized Medication Report from High-Cost Pharmacy) plus six dated prescriptions;
    - A consent form for new prescriptions.
  
- Conditional documents, depending on the diagnosis, may include:
    - Scales (such as Mini-mental and CDR for Alzheimer's, Pain score for Chronic Pain, etc.);
    - A Medical Report;
    - A series of serologic or radiologic tests.
 

## Challenges

- Some processes necessitate over 15 manually filled paper sheets;
- Public system doctors often treat more than four patients per hour, frequently without access to a printer;
- Minor errors, like misrecording an ICD number (e.g., G40 instead of G40.0), often result in medication release refusal. Consequently, patients must schedule a new appointment, and all forms must be completed anew;
- A great deal of these conditional forms has no clinical significance at all and constitutes more 'opportunities' for silly mistakes to be made.

## The Project

AutoCusto, a Portuguese pun combining "Alto" (High) and "Auto" (Automatic), was conceived to address these issues. It aims to minimize mistakes, rework, and patient inconvenience. A doctor's primary focus should be patient care, not navigating through unnecessary bureaucracy. I have personally utilized this software for the past three years with over 400 unique patients. At the moment, the algorithm if fine-grained to Neurologic Disorders.

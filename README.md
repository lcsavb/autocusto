# AutoCusto

## Backdrop

The Unified Health System (Sistema Único de Saúde) is the public and universal Brazilian health insurance created by the 1988 constitution. It provides direct medical care for over 100 million people of the Brazilian population.

One of its programs is the "High Cost Pharmacies," which provide specialized medications to a multitude of chronic diseases. Even patients with private health insurance utilize this service, as many of the substances provided aren't covered by their private counterparts.

As of this writing (October 2023), the Brazilian minimum wage is R$ 1,320 (~250 euros). Commonly used medications for Diabetes or Dyslipidemia (both of which have a high prevalence rate amongst the population), for example, can be over 15% of a person's monthly income, making the payment for the treatment otherwise impossible.

## Bureaucracy

There is a nationwide directive, which regulates the dispensing of the prescription.

- For every medication, the following is required:
    - Laudo de medicamento especializado da farmácia de alto custo (LME) + six prescriptions.
    - If it is a new prescription, the consent form is also needed.
  
- Conditional documents depending on the diagnosis:
    - Scales (Mini-mental and CDR for Alzheimer's, Pain score for Chronic Pain, and so on...)
    - Medical Report
    - A battery of serologic or radiologic tests.

## Problems

- Some processes require more than 15 sheets of paper to be filled manually.
- Doctors in the public health system usually care for more than 4 patients an hour, and it's rare for the room to have a printer.
- Even small mistakes, like forgetting an ICD number (G40 instead of G40.0), commonly lead to the refusal of the liberation of the medication, necessitating the patient to make a new appointment and all the forms have to be filled out all over again from scratch.

## The Project

AutoCusto, a pun in Portuguese between "Alto" (High) and "Auto" (Automatic), was born to solve this issue. With the aim of diminishing silly mistakes, rework, and hassles for the patient. The main concern of a doctor should be caring for patients, not being drowned in needless bureaucracy. I've personally used this software for the past 3 years with over 400 unique patients. Currently, it is fine-tuned to Neurologic Diseases, as that is my specialty.

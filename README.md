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
3. Initialize the database with essential data
   ```bash
   # Copy the initialization dump to the database container
   sudo docker cp autocusto_init_data.sql [db-container-id]:/tmp/
   
   # Restore the database with core data (diseases, medications, protocols)
   sudo docker exec [db-container-id] psql -U lucas -d autocusto -f /tmp/autocusto_init_data.sql
   
   # Run Django migrations to ensure schema is up-to-date
   sudo docker exec [web-container-id] python manage.py migrate
   ```
   
   **Find container IDs with:** `sudo docker ps`
   
   This will populate your database with:
   - 235+ diseases with ICD codes
   - 300+ medications with dosages
   - 80+ medical protocols
   - Essential Django system data

4. *(Optional)* Create a superuser for Django admin access
   ```bash
   sudo docker exec -it [web-container-id] python manage.py createsuperuser
   ```

5. Access the application at `http://localhost:8001`

### Database initialization details

The `autocusto_init_data.sql` file contains only the essential reference data needed to run the application:

**✅ Included:**
- All database schema and migrations
- Disease definitions (ICD codes)
- Medication catalog with dosages
- Medical protocols and forms
- Django auth system setup


### Troubleshooting

**Database connection errors:**
- Ensure the database container is fully started before running commands
- Wait a few seconds after `docker-compose up` before initializing the database

**Permission errors:**
- Make sure the `autocusto_init_data.sql` file has read permissions
- Use `sudo` with docker commands if needed

**Schema migration issues:**
- Always run ` sudo docker exec [web_container_id] python manage.py migrate` after restoring the database
- This ensures all Django models are synchronized with the database schema



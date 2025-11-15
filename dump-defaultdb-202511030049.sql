--
-- PostgreSQL database dump
--

\restrict hksdDt5C7qP4gl1vmdM2ZULjD9joIYS56H2xZeQ48uOUXWQVy6qyfwBSgaOvYua

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

-- Started on 2025-11-03 00:49:54 CET

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 9 (class 2615 OID 24313)
-- Name: core; Type: SCHEMA; Schema: -; Owner: doadmin
--

CREATE SCHEMA core;


ALTER SCHEMA core OWNER TO doadmin;

--
-- TOC entry 5156 (class 0 OID 0)
-- Dependencies: 9
-- Name: SCHEMA core; Type: COMMENT; Schema: -; Owner: doadmin
--

COMMENT ON SCHEMA core IS 'Core schema (doctor_availability removed; use schedules + extras/blackouts)';


--
-- TOC entry 2 (class 3079 OID 24314)
-- Name: btree_gist; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA core;


--
-- TOC entry 5157 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION btree_gist; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION btree_gist IS 'support for indexing common datatypes in GiST';


--
-- TOC entry 3 (class 3079 OID 24964)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA core;


--
-- TOC entry 5158 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- TOC entry 4 (class 3079 OID 25001)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 5159 (class 0 OID 0)
-- Dependencies: 4
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 491 (class 1255 OID 25012)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: core; Owner: doadmin
--

CREATE FUNCTION core.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION core.update_updated_at_column() OWNER TO doadmin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 221 (class 1259 OID 25013)
-- Name: _sqlx_migrations; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core._sqlx_migrations (
    version bigint NOT NULL,
    description text NOT NULL,
    installed_on timestamp with time zone DEFAULT now() NOT NULL,
    success boolean NOT NULL,
    checksum bytea NOT NULL,
    execution_time bigint NOT NULL
);


ALTER TABLE core._sqlx_migrations OWNER TO doadmin;

--
-- TOC entry 222 (class 1259 OID 25019)
-- Name: clinics; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.clinics (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(255) NOT NULL,
    cnpj character varying(14) NOT NULL,
    address jsonb DEFAULT '{}'::jsonb,
    doctors uuid[] DEFAULT '{}'::uuid[],
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    doctor_id uuid
);


ALTER TABLE core.clinics OWNER TO doadmin;

--
-- TOC entry 223 (class 1259 OID 25029)
-- Name: conversations; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.conversations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    phone_number character varying(20) NOT NULL,
    state character varying(50) DEFAULT 'MenuChoice'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    outdated_history boolean,
    birth_date character varying(10),
    prescription_transcript text,
    session_data jsonb DEFAULT '{}'::jsonb,
    payment_id uuid,
    is_active boolean DEFAULT true NOT NULL,
    curated_data jsonb,
    ocr_request_id text,
    ocr_status text,
    ocr_result jsonb,
    patient_id uuid,
    prescription_renewal_id uuid,
    CONSTRAINT ocr_status_valid CHECK (((ocr_status IS NULL) OR (ocr_status = ANY (ARRAY['queued'::text, 'processing'::text, 'done'::text, 'failed'::text]))))
);


ALTER TABLE core.conversations OWNER TO doadmin;

--
-- TOC entry 5160 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN conversations.birth_date; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.conversations.birth_date IS 'Birth date for new patients in DD/MM/YYYY format';


--
-- TOC entry 5161 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN conversations.prescription_transcript; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.conversations.prescription_transcript IS 'Extracted prescription text from OCR or manual input';


--
-- TOC entry 5162 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN conversations.session_data; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.conversations.session_data IS 'Medical history and other collected data stored as JSONB for flexibility';


--
-- TOC entry 5163 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN conversations.payment_id; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.conversations.payment_id IS 'Payment associated with this conversation (user pays before doctor review)';


--
-- TOC entry 5164 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN conversations.is_active; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.conversations.is_active IS 'Only one active conversation allowed per phone number. False = paused/historical conversation for different CPF.';


--
-- TOC entry 5165 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN conversations.curated_data; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.conversations.curated_data IS 'GPT-curated version of session_data with professional medical formatting.
   Structure mirrors session_data but with cleaned/formatted text.
   NULL if curation has not run or failed.';


--
-- TOC entry 5166 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN conversations.ocr_request_id; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.conversations.ocr_request_id IS 'External OCR service request identifier for tracking async operations';


--
-- TOC entry 5167 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN conversations.ocr_status; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.conversations.ocr_status IS 'OCR processing status: queued, processing, done, or failed';


--
-- TOC entry 5168 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN conversations.ocr_result; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.conversations.ocr_result IS 'Parsed OCR result as JSON (medications, dosages, etc.)';


--
-- TOC entry 5169 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN conversations.patient_id; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.conversations.patient_id IS 'Foreign key to patients table - establishes one-to-many relationship (one patient can have many conversations)';


--
-- TOC entry 5170 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN conversations.prescription_renewal_id; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.conversations.prescription_renewal_id IS 'Links WhatsApp conversation to the prescription renewal request it generated. Nullable because conversations exist during intake flow before renewal is created. Set when patient completes OCR and enters doctor queue.';


--
-- TOC entry 224 (class 1259 OID 25041)
-- Name: doctor_blackouts; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.doctor_blackouts (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    doctor_id uuid NOT NULL,
    win tstzrange NOT NULL,
    reason text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE core.doctor_blackouts OWNER TO doadmin;

--
-- TOC entry 5171 (class 0 OID 0)
-- Dependencies: 224
-- Name: TABLE doctor_blackouts; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON TABLE core.doctor_blackouts IS 'Blackout periods (vacations, maintenance) that suppress availability';


--
-- TOC entry 5172 (class 0 OID 0)
-- Dependencies: 224
-- Name: COLUMN doctor_blackouts.win; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctor_blackouts.win IS 'Blackout window [start, end) as tstzrange (UTC)';


--
-- TOC entry 225 (class 1259 OID 25049)
-- Name: doctor_certificates; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.doctor_certificates (
    doctor_id uuid NOT NULL,
    access_token text NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE core.doctor_certificates OWNER TO doadmin;

--
-- TOC entry 226 (class 1259 OID 25055)
-- Name: doctor_extra_windows; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.doctor_extra_windows (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    doctor_id uuid NOT NULL,
    win tstzrange NOT NULL,
    capacity smallint DEFAULT 1 NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE core.doctor_extra_windows OWNER TO doadmin;

--
-- TOC entry 5173 (class 0 OID 0)
-- Dependencies: 226
-- Name: TABLE doctor_extra_windows; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON TABLE core.doctor_extra_windows IS 'One-off availability windows in UTC, supplementing weekly local patterns';


--
-- TOC entry 5174 (class 0 OID 0)
-- Dependencies: 226
-- Name: COLUMN doctor_extra_windows.win; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctor_extra_windows.win IS 'Availability window [start, end) as tstzrange (UTC)';


--
-- TOC entry 227 (class 1259 OID 25064)
-- Name: doctor_schedules; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.doctor_schedules (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    doctor_id uuid NOT NULL,
    day_of_week integer NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    timezone character varying(50) DEFAULT 'America/Sao_Paulo'::character varying NOT NULL,
    active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT doctor_schedules_check CHECK ((end_time > start_time)),
    CONSTRAINT doctor_schedules_day_of_week_check CHECK (((day_of_week >= 1) AND (day_of_week <= 7)))
);


ALTER TABLE core.doctor_schedules OWNER TO doadmin;

--
-- TOC entry 5175 (class 0 OID 0)
-- Dependencies: 227
-- Name: TABLE doctor_schedules; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON TABLE core.doctor_schedules IS 'Recurring weekly schedule patterns for doctor availability';


--
-- TOC entry 5176 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN doctor_schedules.day_of_week; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctor_schedules.day_of_week IS '1=Monday, 2=Tuesday, ..., 7=Sunday (ISO 8601 standard)';


--
-- TOC entry 5177 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN doctor_schedules.start_time; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctor_schedules.start_time IS 'Start time for availability window (local time)';


--
-- TOC entry 5178 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN doctor_schedules.end_time; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctor_schedules.end_time IS 'End time for availability window (local time)';


--
-- TOC entry 5179 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN doctor_schedules.timezone; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctor_schedules.timezone IS 'Timezone for time interpretation (default: Brazil)';


--
-- TOC entry 5180 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN doctor_schedules.active; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctor_schedules.active IS 'Whether this schedule is currently in effect';


--
-- TOC entry 228 (class 1259 OID 25074)
-- Name: doctors; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.doctors (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    crm character varying(20) NOT NULL,
    crm_state character(2) NOT NULL,
    specialty character varying(100),
    pix_key character varying(255),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    full_name character varying(255) DEFAULT ''::character varying NOT NULL,
    specialties text[] DEFAULT '{}'::text[],
    is_available boolean DEFAULT true,
    clinic_name character varying(255),
    clinic_cnpj character varying(18),
    clinic_phone character varying(20),
    clinic_email character varying(255),
    clinic_website character varying(255),
    clinic_street character varying(255),
    clinic_number character varying(20),
    clinic_complement character varying(100),
    clinic_neighborhood character varying(100),
    clinic_city character varying(100),
    clinic_state character(2),
    clinic_cep character varying(9),
    clinic_cnes character varying(50),
    total_approved integer DEFAULT 0 NOT NULL,
    total_rejected integer DEFAULT 0 NOT NULL
);


ALTER TABLE core.doctors OWNER TO doadmin;

--
-- TOC entry 5181 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.clinic_name; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.clinic_name IS 'Nome da clínica onde o médico atende';


--
-- TOC entry 5182 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.clinic_cnpj; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.clinic_cnpj IS 'CNPJ da clínica (formato: XX.XXX.XXX/XXXX-XX)';


--
-- TOC entry 5183 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.clinic_phone; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.clinic_phone IS 'Telefone da clínica';


--
-- TOC entry 5184 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.clinic_email; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.clinic_email IS 'Email da clínica';


--
-- TOC entry 5185 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.clinic_website; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.clinic_website IS 'Website da clínica';


--
-- TOC entry 5186 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.clinic_street; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.clinic_street IS 'Rua/Avenida da clínica';


--
-- TOC entry 5187 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.clinic_number; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.clinic_number IS 'Número do endereço da clínica';


--
-- TOC entry 5188 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.clinic_complement; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.clinic_complement IS 'Complemento do endereço (sala, andar, etc.)';


--
-- TOC entry 5189 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.clinic_neighborhood; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.clinic_neighborhood IS 'Bairro da clínica';


--
-- TOC entry 5190 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.clinic_city; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.clinic_city IS 'Cidade da clínica';


--
-- TOC entry 5191 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.clinic_state; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.clinic_state IS 'Estado da clínica (sigla de 2 letras)';


--
-- TOC entry 5192 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.clinic_cep; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.clinic_cep IS 'CEP da clínica (formato: XXXXX-XXX)';


--
-- TOC entry 5193 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.clinic_cnes; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.clinic_cnes IS 'Número de registro da clínica nos órgãos competentes';


--
-- TOC entry 5194 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.total_approved; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.total_approved IS 'Count of prescriptions approved by this doctor (incremented via PrescriptionApproved event)';


--
-- TOC entry 5195 (class 0 OID 0)
-- Dependencies: 228
-- Name: COLUMN doctors.total_rejected; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.doctors.total_rejected IS 'Count of prescriptions rejected by this doctor (incremented via PrescriptionRejected event)';


--
-- TOC entry 229 (class 1259 OID 25087)
-- Name: patients; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.patients (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid,
    full_name character varying(255) NOT NULL,
    cpf character varying(11) NOT NULL,
    birth_date date,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    email character varying(255),
    address text,
    zipcode character varying(9),
    address_street character varying(255),
    address_number character varying(10),
    address_complement character varying(100),
    address_neighborhood character varying(100),
    address_city character varying(100),
    address_state character(2),
    address_cep character varying(9),
    gender character varying(20)
);


ALTER TABLE core.patients OWNER TO doadmin;

--
-- TOC entry 5196 (class 0 OID 0)
-- Dependencies: 229
-- Name: TABLE patients; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON TABLE core.patients IS 'Patients table (phone data moved to patient_phones junction table per ADR-017)';


--
-- TOC entry 5197 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN patients.gender; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.patients.gender IS 'Patient gender: male, female, other, prefer_not_to_say';


--
-- TOC entry 230 (class 1259 OID 25095)
-- Name: prescription_renewals; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.prescription_renewals (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    doctor_id uuid,
    status character varying(50) NOT NULL,
    risk_level character varying(20),
    rejection_reason text,
    approved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    prescription_id uuid,
    medical_history_id uuid,
    temporary_files jsonb DEFAULT '[]'::jsonb,
    row_version bigint DEFAULT 0 NOT NULL,
    rejection_count smallint DEFAULT 0 NOT NULL,
    is_permanently_rejected boolean DEFAULT false NOT NULL,
    CONSTRAINT prescription_renewals_status_check CHECK (((status)::text = ANY (ARRAY[('pending'::character varying)::text, ('under_review'::character varying)::text, ('approved_processing'::character varying)::text, ('documents_generated'::character varying)::text, ('documents_signed'::character varying)::text, ('approved'::character varying)::text, ('rejected'::character varying)::text, ('approval_failed'::character varying)::text]))),
    CONSTRAINT prescriptions_risk_level_check CHECK (((risk_level)::text = ANY (ARRAY[('green'::character varying)::text, ('yellow'::character varying)::text, ('red'::character varying)::text])))
);


ALTER TABLE core.prescription_renewals OWNER TO doadmin;

--
-- TOC entry 5198 (class 0 OID 0)
-- Dependencies: 230
-- Name: TABLE prescription_renewals; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON TABLE core.prescription_renewals IS 'Prescription renewal workflow tracking.

Status flow (aligned with domain model):
- pending → under_review → approved_processing → approved → awaiting_payment → paid (complete)
- under_review → rejected (end state)
- approved_processing → approval_failed (infrastructure failure, requires manual intervention)

New statuses in this migration:
- approved_processing: Approval granted, background processing (PDF, VIDaaS, files) in progress
- approval_failed: Infrastructure processing failed, requires manual intervention
- awaiting_payment: Prescription ready, awaiting patient payment
- paid: Payment completed, prescription delivered to patient';


--
-- TOC entry 5199 (class 0 OID 0)
-- Dependencies: 230
-- Name: COLUMN prescription_renewals.status; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.prescription_renewals.status IS 'Renewal workflow status (application-specific state machine)';


--
-- TOC entry 5200 (class 0 OID 0)
-- Dependencies: 230
-- Name: COLUMN prescription_renewals.prescription_id; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.prescription_renewals.prescription_id IS 'References the core prescription being renewed (future use)';


--
-- TOC entry 5201 (class 0 OID 0)
-- Dependencies: 230
-- Name: COLUMN prescription_renewals.medical_history_id; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.prescription_renewals.medical_history_id IS 'Links renewal to the medical history version used for this renewal';


--
-- TOC entry 5202 (class 0 OID 0)
-- Dependencies: 230
-- Name: COLUMN prescription_renewals.temporary_files; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.prescription_renewals.temporary_files IS 'Array of temporary file paths stored before prescription approval. Files are promoted to permanent storage on approval or deleted on rejection.';


--
-- TOC entry 5203 (class 0 OID 0)
-- Dependencies: 230
-- Name: COLUMN prescription_renewals.rejection_count; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.prescription_renewals.rejection_count IS 'Number of times this renewal has been rejected by doctors (max 3 before permanent rejection)';


--
-- TOC entry 5204 (class 0 OID 0)
-- Dependencies: 230
-- Name: COLUMN prescription_renewals.is_permanently_rejected; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.prescription_renewals.is_permanently_rejected IS 'Whether this renewal has been permanently rejected (automatic at 3 rejections or manual by admin)';


--
-- TOC entry 231 (class 1259 OID 25109)
-- Name: failed_approvals_summary; Type: VIEW; Schema: core; Owner: doadmin
--

CREATE VIEW core.failed_approvals_summary AS
 SELECT pr.id AS renewal_id,
    p.full_name AS patient_name,
    p.cpf AS patient_cpf,
    d.full_name AS doctor_name,
    pr.rejection_reason,
    pr.created_at AS renewal_created_at,
    pr.updated_at AS failed_at,
    (EXTRACT(epoch FROM (now() - pr.updated_at)) / (3600)::numeric) AS hours_since_failure
   FROM ((core.prescription_renewals pr
     JOIN core.patients p ON ((pr.patient_id = p.id)))
     JOIN core.doctors d ON ((pr.doctor_id = d.id)))
  WHERE ((pr.status)::text = 'approval_failed'::text)
  ORDER BY pr.updated_at DESC;


ALTER VIEW core.failed_approvals_summary OWNER TO doadmin;

--
-- TOC entry 5205 (class 0 OID 0)
-- Dependencies: 231
-- Name: VIEW failed_approvals_summary; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON VIEW core.failed_approvals_summary IS 'Summary view of failed approvals for monitoring and manual intervention.
Shows patient info, assigned doctor, failure reason, and time since failure.';


--
-- TOC entry 232 (class 1259 OID 25114)
-- Name: files; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.files (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    filename character varying(255) NOT NULL,
    original_filename character varying(255) NOT NULL,
    file_path text NOT NULL,
    file_size bigint NOT NULL,
    mime_type character varying(100) NOT NULL,
    file_type character varying(50) NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    medical_history_id uuid,
    patient_id uuid,
    prescription_renewal_id uuid,
    conversation_id uuid,
    CONSTRAINT files_file_type_check CHECK (((file_type)::text = ANY (ARRAY[('prescription'::character varying)::text, ('exam'::character varying)::text, ('document'::character varying)::text, ('image'::character varying)::text, ('signed_document'::character varying)::text]))),
    CONSTRAINT files_must_have_owner CHECK (((patient_id IS NOT NULL) OR (medical_history_id IS NOT NULL) OR (prescription_renewal_id IS NOT NULL)))
);


ALTER TABLE core.files OWNER TO doadmin;

--
-- TOC entry 5206 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN files.medical_history_id; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.files.medical_history_id IS 'Links files to specific medical history version';


--
-- TOC entry 5207 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN files.patient_id; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.files.patient_id IS 'Owner of this file (for LGPD compliance and patient-level queries)';


--
-- TOC entry 5208 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN files.prescription_renewal_id; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.files.prescription_renewal_id IS 'Links prescription photos to renewal requests';


--
-- TOC entry 233 (class 1259 OID 25125)
-- Name: medical_history; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.medical_history (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    medical_background text,
    current_medications jsonb DEFAULT '[]'::jsonb,
    allergies jsonb DEFAULT '[]'::jsonb,
    symptoms jsonb DEFAULT '[]'::jsonb,
    version integer DEFAULT 1 NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    family_history text,
    subjective jsonb,
    is_draft boolean DEFAULT false NOT NULL
);


ALTER TABLE core.medical_history OWNER TO doadmin;

--
-- TOC entry 5209 (class 0 OID 0)
-- Dependencies: 233
-- Name: TABLE medical_history; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON TABLE core.medical_history IS 'Medical history versions - most recent by created_at is current';


--
-- TOC entry 5210 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN medical_history.medical_background; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.medical_history.medical_background IS 'Personal medical history: previous diseases, conditions, lifestyle';


--
-- TOC entry 5211 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN medical_history.current_medications; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.medical_history.current_medications IS 'Medications patient is currently taking';


--
-- TOC entry 5212 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN medical_history.allergies; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.medical_history.allergies IS 'Known allergies and adverse reactions';


--
-- TOC entry 5213 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN medical_history.symptoms; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.medical_history.symptoms IS 'Current symptoms reported by patient';


--
-- TOC entry 5214 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN medical_history.version; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.medical_history.version IS 'Version number for this medical history snapshot. Each renewal creates a new version for audit trail.';


--
-- TOC entry 5215 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN medical_history.created_at; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.medical_history.created_at IS 'Creation timestamp - used to determine most current version';


--
-- TOC entry 5216 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN medical_history.family_history; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.medical_history.family_history IS 'Family medical history: genetic conditions, family diseases';


--
-- TOC entry 5217 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN medical_history.subjective; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.medical_history.subjective IS 'Raw patient conversation data (JSONB). Contains unprocessed session_data from WhatsApp for audit purposes.';


--
-- TOC entry 5218 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN medical_history.is_draft; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.medical_history.is_draft IS 'True if patient-submitted (draft), false if doctor-verified (official record). Only official records appear in prontuário.';


--
-- TOC entry 234 (class 1259 OID 25145)
-- Name: ocr_jobs; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.ocr_jobs (
    job_id uuid NOT NULL,
    conversation_id text NOT NULL,
    photo_id text NOT NULL,
    status text NOT NULL,
    result jsonb,
    attempts integer DEFAULT 0 NOT NULL,
    error_message text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT max_attempts CHECK ((attempts <= 3)),
    CONSTRAINT ocr_jobs_status_check CHECK ((status = ANY (ARRAY['queued'::text, 'processing'::text, 'done'::text, 'failed'::text]))),
    CONSTRAINT result_when_done CHECK ((((status = 'done'::text) AND (result IS NOT NULL)) OR (status <> 'done'::text)))
);


ALTER TABLE core.ocr_jobs OWNER TO doadmin;

--
-- TOC entry 235 (class 1259 OID 25156)
-- Name: password_recovery_tokens; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.password_recovery_tokens (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    token text NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    used_at timestamp with time zone
);


ALTER TABLE core.password_recovery_tokens OWNER TO doadmin;

--
-- TOC entry 236 (class 1259 OID 25163)
-- Name: patient_phones; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.patient_phones (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    phone character varying(20) NOT NULL,
    verified_at timestamp with time zone,
    is_primary boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE core.patient_phones OWNER TO doadmin;

--
-- TOC entry 5219 (class 0 OID 0)
-- Dependencies: 236
-- Name: TABLE patient_phones; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON TABLE core.patient_phones IS 'Phones used to help patients get care via WhatsApp. The phone holder may be the patient themselves, a family member, or a caregiver. This is NOT a "patient owns phone" relationship - it represents "this phone helps this patient get care".';


--
-- TOC entry 5220 (class 0 OID 0)
-- Dependencies: 236
-- Name: COLUMN patient_phones.verified_at; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.patient_phones.verified_at IS 'Timestamp when this phone successfully completed a WhatsApp flow for this patient. Does NOT imply phone ownership - could be family member helping patient. Verified means the flow completed successfully via WhatsApp webhook.';


--
-- TOC entry 5221 (class 0 OID 0)
-- Dependencies: 236
-- Name: COLUMN patient_phones.is_primary; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.patient_phones.is_primary IS 'Preferred phone for WhatsApp communication about this specific patient. Used when sending prescription updates, reminders, etc. for THIS patient. NOT the patient''s main phone - could be caregiver''s phone marked as primary contact for this patient.';


--
-- TOC entry 237 (class 1259 OID 25170)
-- Name: payment_splits; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.payment_splits (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    payment_id uuid NOT NULL,
    recipient_type character varying(50) NOT NULL,
    recipient_id uuid,
    amount_cents bigint NOT NULL,
    percentage numeric(5,2),
    description text,
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    transferred_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT payment_splits_amount_cents_check CHECK ((amount_cents >= 0)),
    CONSTRAINT valid_recipient_type CHECK (((recipient_type)::text = ANY (ARRAY[('doctor'::character varying)::text, ('platform'::character varying)::text, ('tax'::character varying)::text, ('gateway_fee'::character varying)::text]))),
    CONSTRAINT valid_split_status CHECK (((status)::text = ANY (ARRAY[('pending'::character varying)::text, ('transferred'::character varying)::text, ('failed'::character varying)::text])))
);


ALTER TABLE core.payment_splits OWNER TO doadmin;

--
-- TOC entry 5222 (class 0 OID 0)
-- Dependencies: 237
-- Name: TABLE payment_splits; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON TABLE core.payment_splits IS 'Revenue distribution for each payment transaction';


--
-- TOC entry 5223 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN payment_splits.recipient_type; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.payment_splits.recipient_type IS 'Type of recipient: doctor (medical professional), platform (CliqueReceita), tax (government), gateway_fee (payment processor)';


--
-- TOC entry 5224 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN payment_splits.recipient_id; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.payment_splits.recipient_id IS 'Doctor UUID if recipient_type=doctor, NULL for platform/tax/fees';


--
-- TOC entry 5225 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN payment_splits.amount_cents; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.payment_splits.amount_cents IS 'Split amount in cents';


--
-- TOC entry 5226 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN payment_splits.percentage; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.payment_splits.percentage IS 'Percentage of total payment (for reference/audit)';


--
-- TOC entry 5227 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN payment_splits.status; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.payment_splits.status IS 'Transfer status: pending (not yet transferred), transferred (paid out), failed (transfer failed)';


--
-- TOC entry 238 (class 1259 OID 25182)
-- Name: payments; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.payments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    phone_number character varying(20) NOT NULL,
    method character varying(20) DEFAULT 'pix'::character varying NOT NULL,
    amount_cents bigint NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    pix_qr_code text,
    pix_transaction_id character varying(255),
    provider_transaction_id character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    confirmed_at timestamp with time zone,
    expired_at timestamp with time zone,
    failure_reason text,
    payment_link text,
    prescription_renewal_id uuid,
    CONSTRAINT payments_amount_cents_check CHECK ((amount_cents > 0)),
    CONSTRAINT valid_method CHECK (((method)::text = ANY (ARRAY[('pix'::character varying)::text, ('credit_card'::character varying)::text, ('boleto'::character varying)::text]))),
    CONSTRAINT valid_status CHECK (((status)::text = ANY (ARRAY[('pending'::character varying)::text, ('confirmed'::character varying)::text, ('failed'::character varying)::text, ('expired'::character varying)::text, ('refunded'::character varying)::text])))
);


ALTER TABLE core.payments OWNER TO doadmin;

--
-- TOC entry 5228 (class 0 OID 0)
-- Dependencies: 238
-- Name: TABLE payments; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON TABLE core.payments IS 'Payment transactions for prescription renewal service';


--
-- TOC entry 5229 (class 0 OID 0)
-- Dependencies: 238
-- Name: COLUMN payments.amount_cents; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.payments.amount_cents IS 'Payment amount in cents to avoid floating point issues (R$ 29,90 = 2990)';


--
-- TOC entry 5230 (class 0 OID 0)
-- Dependencies: 238
-- Name: COLUMN payments.pix_qr_code; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.payments.pix_qr_code IS 'PIX QR code payload (base64 encoded)';


--
-- TOC entry 5231 (class 0 OID 0)
-- Dependencies: 238
-- Name: COLUMN payments.pix_transaction_id; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.payments.pix_transaction_id IS 'PIX end-to-end identifier (E2E ID)';


--
-- TOC entry 5232 (class 0 OID 0)
-- Dependencies: 238
-- Name: COLUMN payments.provider_transaction_id; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.payments.provider_transaction_id IS 'Payment gateway transaction reference';


--
-- TOC entry 5233 (class 0 OID 0)
-- Dependencies: 238
-- Name: COLUMN payments.failure_reason; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.payments.failure_reason IS 'Human-readable reason for payment failure or refund';


--
-- TOC entry 5234 (class 0 OID 0)
-- Dependencies: 238
-- Name: COLUMN payments.payment_link; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.payments.payment_link IS 'User-facing payment URL generated by payment gateway (e.g., https://openpix.com.br/pay/charge_123)';


--
-- TOC entry 5235 (class 0 OID 0)
-- Dependencies: 238
-- Name: COLUMN payments.prescription_renewal_id; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.payments.prescription_renewal_id IS 'Links payment to specific prescription renewal request. Nullable for backward compatibility with legacy payment records created before approval-before-payment flow.';


--
-- TOC entry 239 (class 1259 OID 25195)
-- Name: prescription_queue; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.prescription_queue (
    renewal_id uuid NOT NULL,
    priority integer NOT NULL,
    assigned_doctor_id uuid,
    assigned_at timestamp with time zone,
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT prescription_queue_priority_check CHECK ((priority = ANY (ARRAY[1, 2, 3])))
);


ALTER TABLE core.prescription_queue OWNER TO doadmin;

--
-- TOC entry 5236 (class 0 OID 0)
-- Dependencies: 239
-- Name: COLUMN prescription_queue.priority; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.prescription_queue.priority IS '1=Red (urgent), 2=Yellow (attention), 3=Green (routine)';


--
-- TOC entry 240 (class 1259 OID 25200)
-- Name: prescriptions; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.prescriptions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    doctor_id uuid NOT NULL,
    medications jsonb DEFAULT '[]'::jsonb NOT NULL,
    issued_date date NOT NULL,
    valid_until date NOT NULL,
    medical_notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    file_paths text[] DEFAULT ARRAY[]::text[],
    CONSTRAINT prescriptions_check CHECK ((valid_until > issued_date))
);


ALTER TABLE core.prescriptions OWNER TO doadmin;

--
-- TOC entry 5237 (class 0 OID 0)
-- Dependencies: 240
-- Name: TABLE prescriptions; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON TABLE core.prescriptions IS 'Core domain: Universal medical prescriptions (real-world documents)';


--
-- TOC entry 5238 (class 0 OID 0)
-- Dependencies: 240
-- Name: COLUMN prescriptions.medications; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.prescriptions.medications IS 'Array of prescribed medications with dosage and frequency';


--
-- TOC entry 5239 (class 0 OID 0)
-- Dependencies: 240
-- Name: COLUMN prescriptions.issued_date; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.prescriptions.issued_date IS 'Date the prescription was issued by the doctor';


--
-- TOC entry 5240 (class 0 OID 0)
-- Dependencies: 240
-- Name: COLUMN prescriptions.valid_until; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.prescriptions.valid_until IS 'Expiration date of the prescription';


--
-- TOC entry 5241 (class 0 OID 0)
-- Dependencies: 240
-- Name: COLUMN prescriptions.file_paths; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON COLUMN core.prescriptions.file_paths IS 'Array of file paths for prescription-related files. Supports local paths and cloud URLs. Examples: ["/tmp/uploads/patient/123/prescription_456.pdf", "s3://bucket/lab_results_456.pdf"]';


--
-- TOC entry 241 (class 1259 OID 25211)
-- Name: processed_events; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.processed_events (
    event_type text NOT NULL,
    entity_id uuid NOT NULL,
    occurred_at timestamp with time zone NOT NULL,
    processed_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE core.processed_events OWNER TO doadmin;

--
-- TOC entry 242 (class 1259 OID 25217)
-- Name: sessions; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.sessions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    token character varying(255) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE core.sessions OWNER TO doadmin;

--
-- TOC entry 243 (class 1259 OID 25222)
-- Name: user_sessions; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.user_sessions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid,
    phone character varying(20) NOT NULL,
    cpf character varying(11),
    session_data jsonb DEFAULT '{}'::jsonb,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE core.user_sessions OWNER TO doadmin;

--
-- TOC entry 244 (class 1259 OID 25231)
-- Name: users; Type: TABLE; Schema: core; Owner: doadmin
--

CREATE TABLE core.users (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    phone character varying(20),
    cpf character varying(11),
    full_name character varying(255),
    email character varying(255) NOT NULL,
    password_hash character varying(255),
    birth_date date,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    user_type character varying(20) DEFAULT 'doctor'::character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    CONSTRAINT users_user_type_not_empty CHECK (((user_type IS NOT NULL) AND (length(TRIM(BOTH FROM user_type)) > 0)))
);


ALTER TABLE core.users OWNER TO doadmin;

--
-- TOC entry 245 (class 1259 OID 25242)
-- Name: _sqlx_migrations; Type: TABLE; Schema: public; Owner: doadmin
--

CREATE TABLE public._sqlx_migrations (
    version bigint NOT NULL,
    description text NOT NULL,
    installed_on timestamp with time zone DEFAULT now() NOT NULL,
    success boolean NOT NULL,
    checksum bytea NOT NULL,
    execution_time bigint NOT NULL
);


ALTER TABLE public._sqlx_migrations OWNER TO doadmin;

--
-- TOC entry 5127 (class 0 OID 25013)
-- Dependencies: 221
-- Data for Name: _sqlx_migrations; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core._sqlx_migrations (version, description, installed_on, success, checksum, execution_time) FROM stdin;
20251026000000	baseline schema	2025-10-26 12:29:59.779639+00	t	\\x04bff5efb707bd89c739517a126c569b352524eac3458ba1a900ab67cab7505049890145855524614a58ed78a1fb8d5a	1217983399
\.


--
-- TOC entry 5128 (class 0 OID 25019)
-- Dependencies: 222
-- Data for Name: clinics; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.clinics (id, name, cnpj, address, doctors, created_at, updated_at, doctor_id) FROM stdin;
\.


--
-- TOC entry 5129 (class 0 OID 25029)
-- Dependencies: 223
-- Data for Name: conversations; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.conversations (id, phone_number, state, created_at, updated_at, outdated_history, birth_date, prescription_transcript, session_data, payment_id, is_active, curated_data, ocr_request_id, ocr_status, ocr_result, patient_id, prescription_renewal_id) FROM stdin;
dc46dd45-5336-4428-bfb8-73f81ecaed60	4915158832107	terms	2025-10-20 23:48:37.874223+00	2025-10-21 00:04:58.256543+00	\N	10/10/2020	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "full_name": "João Carlos Fonseca", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":null,\\"crm\\":{\\"number\\":\\"150494\\",\\"state\\":null},\\"name\\":\\"Lucas Barros\\"},\\"medications\\":[{\\"dosage\\":\\"10 mg\\",\\"name\\":\\"Aripiprazol\\",\\"posology\\":\\"Tomar 1 comprimido pela manhã\\"},{\\"dosage\\":\\"75 mcg\\",\\"name\\":\\"Levotiroxina\\",\\"posology\\":\\"Tomar 1 comprimido em jejum\\"}],\\"patient\\":{\\"address_cep\\":null,\\"address_city\\":null,\\"address_complement\\":null,\\"address_neighborhood\\":null,\\"address_number\\":null,\\"address_state\\":null,\\"address_street\\":null,\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"João Carlos Fonseca\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"Para o sr. João Carlos Fonseca\\\\n\\\\nUso oral:\\\\n\\\\n1) Aripiprazol 10 mg — 60 cp\\\\nTomar 1 cp pela manhã\\\\n\\\\n2) Levotiroxina 75 mcg —\\\\nTomar 1 cp em jejum\\\\n\\\\nLucas Barros\\\\nCRM 150494\\"}", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "full_address": "Não informado", "family_history": "pae com demencia", "prescription_transcript": "1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum"}	\N	f	{"diseases": ["Paciente nega doenças prévias."], "symptoms": "Paciente nega sintomas atuais.", "allergies": ["Paciente nega alergias."], "medications": "Paciente nega uso de medicamentos.", "risk_analysis": "low", "family_history": ["Paciente nega histórico familiar de doenças."]}	\N	\N	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	5fcdf7d1-8261-4067-b31c-664f2d2ae00f
f3577a3a-63c6-4d6f-972b-9344133af8db	5511982033817	menu	2025-10-19 14:46:52.600891+00	2025-10-19 14:48:45.888616+00	\N	17/01/2018	1. ATENTAH (ATOMOXETINA) 18 mg/cp - Dar 1 comprimido por dia, no café da manhã, todos os dias, a partir do segundo mês do fármaco. USO CONTÍNUO	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "full_name": "Theo Ragazzini Ettori", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":\\"Cidade: Taubaté; Endereço: Avenida Italia, 928, 604, Jardim das Nações, Taubaté - SP; CPF: 224.321.628-03; Telefone: (12 ) 99722-4263; PEDIATRIA - RQE nº 123467; NEUROLOGIA PEDIÁTRICA - RQE nº 123468; Receituário de Controle Especial assinado digitalmente por LIVIA MEIRELLES DE ARAUJO PASQUALIN em 29/09/2025 19:44, conforme MP nº 2.200-2/2001, Resolução Nº CFM 2.299/2021 e Resolução CFM Nº 2.381/2024.; O documento médico poderá ser validado em https://validar.iti.gov.br.; Farmacêutico, realize a dispensação em: https://prescricao.cfm.org.br/api/documento; Acesse o documento em: https://prescricao.cfm.org.br/api/documento?_format=application/pdf; 1ª VIA FARMÁCIA; 2ª VIA PACIENTE\\",\\"crm\\":{\\"number\\":\\"112965\\",\\"state\\":\\"SP\\"},\\"name\\":\\"Dr(a). LIVIA MEIRELLES DE ARAUJO PASQUALIN\\"},\\"medications\\":[{\\"dosage\\":\\"18 mg/cp\\",\\"name\\":\\"ATENTAH (ATOMOXETINA)\\",\\"posology\\":\\"Dar 1 comprimido por dia, no café da manhã, todos os dias, a partir do segundo mês do fármaco. USO CONTÍNUO\\"}],\\"patient\\":{\\"address_cep\\":null,\\"address_city\\":null,\\"address_complement\\":null,\\"address_neighborhood\\":null,\\"address_number\\":null,\\"address_state\\":\\"SP\\",\\"address_street\\":null,\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"Theo Ragazzini Ettori\\",\\"gender\\":\\"N\\",\\"phone\\":null},\\"prescription_transcript\\":\\"1. ATENTAH (ATOMOXETINA) 18mg/cp ------------------------------------------------- 1 cx\\\\nDar 1 cp/dia, no café da manhã, todos os dias, a partir do segundo mês do fármaco. USO CONTÍNUO\\"}", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "full_address": "SP", "family_history": "Nega histórico familiar de doenças graves", "prescription_transcript": "1. ATENTAH (ATOMOXETINA) 18 mg/cp - Dar 1 comprimido por dia, no café da manhã, todos os dias, a partir do segundo mês do fármaco. USO CONTÍNUO"}	\N	t	{"diseases": ["Paciente nega doenças prévias."], "symptoms": "Paciente nega sintomas atuais.", "allergies": ["Paciente nega alergias."], "medications": "Paciente nega uso de medicações de uso contínuo além da prescrita hoje.", "risk_analysis": "low", "family_history": ["Paciente nega histórico familiar de doenças."]}	\N	\N	\N	3db328c8-da70-418c-a245-d01175590664	04af6c1e-d6d7-43de-9b78-5d711a4127c7
d64feefb-8b6e-47d8-8d51-92b3a864c2b6	5511982033818	terms	2025-10-21 10:43:58.911653+00	2025-10-21 11:22:36.929398+00	\N	24/11/1956	1. Ciprofloxacino 500 mg - Tomar 1 comprimido, via oral, duas vezes ao dia	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "full_name": "O impostor", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":\\"valeV HOME CARE\\",\\"crm\\":{\\"number\\":\\"104811\\",\\"state\\":\\"SP\\"},\\"name\\":\\"Dr. Charles M. A. Nascimento\\"},\\"medications\\":[{\\"dosage\\":\\"500 mg\\",\\"name\\":\\"Ciprofloxacino\\",\\"posology\\":\\"Tomar 1 comprimido, via oral, duas vezes ao dia\\"}],\\"patient\\":{\\"address_cep\\":null,\\"address_city\\":null,\\"address_complement\\":null,\\"address_neighborhood\\":null,\\"address_number\\":null,\\"address_state\\":null,\\"address_street\\":null,\\"birth_date\\":null,\\"cpf\\":\\"Não há CPF cadastrado\\",\\"email\\":null,\\"full_name\\":\\"Leodir de Abreu Miloch\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"1. Ciprofloxacino 500mg, Comprimido revestido ———————————————— 14 Comprimidos\\\\nTomar 1 comprimido, via oral, duas vezes ao dia.\\"}", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "full_address": "Rua do teste 1", "family_history": "Nega histórico familiar de doenças graves", "prescription_transcript": "1. Ciprofloxacino 500 mg - Tomar 1 comprimido, via oral, duas vezes ao dia"}	\N	f	{"diseases": ["Paciente nega doenças prévias."], "symptoms": "Paciente nega sintomas atuais.", "allergies": ["Paciente nega alergias."], "medications": "Paciente nega uso de medicamentos.", "risk_analysis": "baixo", "family_history": ["Paciente nega histórico familiar de doenças."]}	\N	\N	\N	2b635923-f6c4-435a-9054-156c2113888f	badb42d5-27a3-4ddf-bfcd-1bb49b06665d
ca12655e-9848-4a36-b0c5-efc44bc8d6c0	4915158832107	terms	2025-10-21 00:05:12.434948+00	2025-10-21 00:07:04.447016+00	\N	10/10/2010	1. Amitriptilina 25 mg - Tomar 1 comprimido à noite antes de dormir.	{"diseases": "diabetes", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":\\"Emitido: 28/09/2025 às 16:05:32; Código: 50786CF0; Prescrição eletrônica assinada digitalmente\\",\\"crm\\":{\\"number\\":\\"150494\\",\\"state\\":\\"SP\\"},\\"name\\":\\"Dr(a). Lucas Amorim Vieira de Barros\\"},\\"medications\\":[{\\"dosage\\":\\"25 mg\\",\\"name\\":\\"Amitriptilina\\",\\"posology\\":\\"Tomar 1 comprimido à noite antes de dormir.\\"}],\\"patient\\":{\\"address_cep\\":\\"06709-135\\",\\"address_city\\":\\"Cotia\\",\\"address_complement\\":null,\\"address_neighborhood\\":\\"Granja Viana\\",\\"address_number\\":\\"99\\",\\"address_state\\":\\"SP\\",\\"address_street\\":\\"Rua Profa. Ana Nastari Brunetti\\",\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"Heitor Éttori\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"Uso oral:\\\\n\\\\n1) Amitriptilina 25mg --------------------------------------------\\\\nTomar 1 comprimido à noite antes de dormir.\\"}", "medications": "aripiprazol", "family_history": "asma e neurocisticercose", "prescription_transcript": "1. Amitriptilina 25 mg - Tomar 1 comprimido à noite antes de dormir."}	\N	f	\N	\N	\N	\N	abdb491c-dc08-40b1-826b-95a28c01b0a1	\N
7b27685d-7684-49c1-bc88-ecae7afd0d01	5511962774562	menu	2025-10-19 22:28:43.250969+00	2025-10-19 22:32:38.94463+00	\N	17/05/1972	1. Wegovy\n2. Wegovy\n3. Wegovy\n4. Wegovy	{"diseases": "Diabetes", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "full_name": "Não informado", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":\\"Endocrinologista - RQE 57973 | Endereço: R. Domingos de Morais, 2781 – cj 1201 – 12º andar, Vila Mariana – CEP 04035-001 – São Paulo – SP | Telefone (11) 2372-8166\\",\\"crm\\":{\\"number\\":\\"144474\\",\\"state\\":null},\\"name\\":\\"Dra. Andréia Latanza\\"},\\"medications\\":[{\\"dosage\\":null,\\"name\\":\\"Wegovy\\",\\"posology\\":\\"Seguir 32 cliques até 3 semanas antes da EDA.\\"},{\\"dosage\\":null,\\"name\\":\\"Wegovy\\",\\"posology\\":\\"Após endoscopia: 22 cliques 1ª semana\\"},{\\"dosage\\":null,\\"name\\":\\"Wegovy\\",\\"posology\\":\\"Após endoscopia: 32 cliques 2ª semana\\"},{\\"dosage\\":null,\\"name\\":\\"Wegovy\\",\\"posology\\":\\"Após endoscopia: 42 cliques 4ª semana\\"}],\\"patient\\":{\\"address_cep\\":null,\\"address_city\\":null,\\"address_complement\\":null,\\"address_neighborhood\\":null,\\"address_number\\":null,\\"address_state\\":null,\\"address_street\\":null,\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":null,\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"Wegovy\\\\n\\\\nSeguir 32 cliques até 3 semanas antes da EDA.\\\\n\\\\nApós endoscopia: 22 cliques 1ª semana\\\\n32 cliques 2ª semana\\\\n42 cliques 4ª semana\\"}", "medications": "Alopurinol 100mg\\nPitavastatina 4 mg", "full_address": "Não informado", "family_history": "Mãe com diabetes", "prescription_transcript": "1. Wegovy\\n2. Wegovy\\n3. Wegovy\\n4. Wegovy"}	\N	t	{"diseases": ["Paciente relata diabetes mellitus."], "symptoms": "Paciente nega sintomas atuais.", "allergies": ["Paciente nega alergias."], "medications": [{"dose": "100mg", "form": "Não informado", "name": "Alopurinol", "frequency": "Não informado"}, {"dose": "4 mg", "form": "Não informado", "name": "Pitavastatina", "frequency": "Não informado"}], "risk_analysis": "moderado", "family_history": ["Paciente nega histórico familiar de doenças."]}	\N	\N	\N	8e31833e-effe-4867-9965-9a346c850b72	9a88289a-547f-4384-a6e8-0b4f51811142
60d0b270-2f23-4694-97ed-fc7cc00c377f	5511983327687	added_to_queue	2025-10-21 14:38:11.261775+00	2025-10-21 14:39:59.996356+00	\N	31/12/1992		{"diseases": "ICC", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "full_name": "Não informado", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":null,\\"crm\\":{\\"number\\":null,\\"state\\":null},\\"name\\":null},\\"medications\\":[],\\"patient\\":{\\"address_cep\\":null,\\"address_city\\":null,\\"address_complement\\":null,\\"address_neighborhood\\":null,\\"address_number\\":null,\\"address_state\\":null,\\"address_street\\":null,\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":null,\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"\\"}", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "full_address": "Não informado", "family_history": "Nega histórico familiar de doenças graves", "prescription_transcript": ""}	\N	t	{"diseases": ["Paciente relata insuficiência cardíaca congestiva."], "symptoms": "Paciente nega sintomas atuais.", "allergies": ["Paciente nega alergias."], "medications": "Paciente nega uso de outros medicamentos.", "risk_analysis": "moderado", "family_history": ["Paciente nega histórico familiar de doenças graves."]}	\N	\N	\N	584648e5-0c1d-44f9-aa12-8cde21c2e4d2	c67e14f6-fb1f-4e56-ba62-e34ae783d120
4e99b9e4-b495-4ffb-8da2-8678be243639	553599576711	menu	2025-10-21 01:00:42.415323+00	2025-10-21 01:17:39.921272+00	\N	04/11/1973	1. SALBUTAMOL 100 mcg - Inalar 2 jatos a cada 6 horas se falta de ar ou “chiado” no peito. 1 frasco\n2. BECLOMETASONA 200 mcg - Inalar 1 jato de 12/12h, lavar a boca após. 1 frasco\n3. BUDESONIDA SPRAY NASAL 50 mcg/jato - Uso contínuo. Aplicar um jato em cada narina de 12/12h	{"diseases": "Diabetes / Hipertensão", "symptoms": "Nega sintomas atuais", "allergies": "Nenhum", "full_name": "FABIO LUIS MARQUES DA SILVA", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":\\"Carimbo: RQE 61003 - Pneumologia; Controle 3845869; Assinatura presente\\",\\"crm\\":{\\"number\\":\\"76177\\",\\"state\\":\\"MG\\"},\\"name\\":\\"Silvio Henrique Azevedo Santos\\"},\\"medications\\":[{\\"dosage\\":\\"100 mcg\\",\\"name\\":\\"SALBUTAMOL\\",\\"posology\\":\\"Inalar 2 jatos a cada 6 horas se falta de ar ou “chiado” no peito. 1 frasco\\"},{\\"dosage\\":\\"200 mcg\\",\\"name\\":\\"BECLOMETASONA\\",\\"posology\\":\\"Inalar 1 jato de 12/12h, lavar a boca após. 1 frasco\\"},{\\"dosage\\":\\"50 mcg/jato\\",\\"name\\":\\"BUDESONIDA SPRAY NASAL\\",\\"posology\\":\\"Uso contínuo. Aplicar um jato em cada narina de 12/12h\\"}],\\"patient\\":{\\"address_cep\\":\\"37950-000\\",\\"address_city\\":\\"São Sebastião do Paraíso\\",\\"address_complement\\":null,\\"address_neighborhood\\":null,\\"address_number\\":null,\\"address_state\\":\\"MG\\",\\"address_street\\":null,\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"FABIO LUIS MARQUES DA SILVA\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"USO INALATORIO\\\\n\\\\n1) SALBUTAMOL 100MCG ------------------------- 1 FRASCO\\\\nINALAR 2 JATOS DE 6/6H SE FALTA DE AR OU “CHIADO” NO PEITO.\\\\n\\\\n2) BECLOMETASONA 200MCG ---------------------- 1 FRASCO\\\\nINALAR 1 JATO DE 12/12H, LAVAR A BOCA APÓS.\\\\n\\\\nUSO NASAL\\\\n\\\\n1) BUDESONIDA SPRAY NASAL 50MCG/JATO ----- USO CONTÍNUO\\\\nAPLICAR UM JATO EM CADA NARINA DE 12/12H\\\\n\\\\n27/08/2025\\"}", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "full_address": "São Sebastião do Paraíso, MG - CEP: 37950-000", "family_history": "Pai câncer", "prescription_transcript": "1. SALBUTAMOL 100 mcg - Inalar 2 jatos a cada 6 horas se falta de ar ou “chiado” no peito. 1 frasco\\n2. BECLOMETASONA 200 mcg - Inalar 1 jato de 12/12h, lavar a boca após. 1 frasco\\n3. BUDESONIDA SPRAY NASAL 50 mcg/jato - Uso contínuo. Aplicar um jato em cada narina de 12/12h"}	\N	t	{"diseases": ["Paciente relata diabetes mellitus.", "Paciente relata hipertensão arterial."], "symptoms": "Paciente nega sintomas atuais.", "allergies": ["Paciente nega alergias."], "medications": "Paciente nega uso de medicamentos.", "risk_analysis": "low", "family_history": ["Paciente nega histórico familiar de doenças."]}	\N	\N	\N	a6fe8ce5-c9a9-4f1e-a698-c7d834256762	958b0af9-7ab0-4317-bcf6-02a06a4c1e18
37c7666e-0b22-47ba-b4d2-78cf431ad8de	4915158832107	terms	2025-10-18 18:02:15.792008+00	2025-10-20 22:57:08.445221+00	\N	10/10/2010	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "full_name": "Maryellen Hallen Pereira Santos", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":null,\\"crm\\":{\\"number\\":\\"150494\\",\\"state\\":null},\\"name\\":\\"Lucas Barros\\"},\\"medications\\":[{\\"dosage\\":\\"10 mg\\",\\"name\\":\\"Aripiprazol\\",\\"posology\\":\\"Tomar 1 comprimido pela manhã\\"},{\\"dosage\\":\\"75 mcg\\",\\"name\\":\\"Levotiroxina\\",\\"posology\\":\\"Tomar 1 comprimido em jejum\\"}],\\"patient\\":{\\"address_cep\\":null,\\"address_city\\":null,\\"address_complement\\":null,\\"address_neighborhood\\":null,\\"address_number\\":null,\\"address_state\\":null,\\"address_street\\":null,\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"João Carlos Fonseca\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"Para o sr. João Carlos Fonseca\\\\n\\\\nUso oral:\\\\n\\\\n1) Aripiprazol 10 mg — 60 cp\\\\nTomar 1 cp pela manhã\\\\n\\\\n2) Levotiroxina 75 mcg —\\\\nTomar 1 cp em jejum\\\\n\\\\nLucas Barros\\\\nCRM 150494\\"}", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "full_address": "Não informado - S/N - Não especificado - São Paulo, SP - CEP: 00000-000", "family_history": "Nega histórico familiar de doenças graves", "prescription_transcript": "1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum"}	c01c2eda-3bc1-410c-95fb-e65129fc5ab4	f	{"diseases": ["Paciente nega doenças prévias."], "symptoms": "Paciente nega sintomas atuais.", "allergies": ["Paciente nega alergias."], "medications": "Paciente nega uso de medicamentos.", "risk_analysis": "low", "family_history": ["Paciente nega histórico familiar de doenças."]}	\N	\N	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	40c941cc-e135-4acf-ab4a-5b050228a258
005929ee-c897-40ca-b92f-2e704b0a0aa6	5511982033818	menu	2025-10-21 11:23:03.066085+00	2025-10-21 12:20:53.240295+00	\N	13/01/1987	1. Ciprofloxacino 500 mg - Tomar 1 comprimido, via oral, duas vezes ao dia	{"diseases": "Pressão alta", "symptoms": "Dor de cotovelo", "allergies": "Nega alergias", "full_name": "O impostor", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":\\"valeV HOME CARE\\",\\"crm\\":{\\"number\\":\\"104811\\",\\"state\\":\\"SP\\"},\\"name\\":\\"Dr. Charles M. A. Nascimento\\"},\\"medications\\":[{\\"dosage\\":\\"500 mg\\",\\"name\\":\\"Ciprofloxacino\\",\\"posology\\":\\"Tomar 1 comprimido, via oral, duas vezes ao dia\\"}],\\"patient\\":{\\"address_cep\\":null,\\"address_city\\":null,\\"address_complement\\":null,\\"address_neighborhood\\":null,\\"address_number\\":null,\\"address_state\\":null,\\"address_street\\":null,\\"birth_date\\":null,\\"cpf\\":\\"Não há CPF cadastrado\\",\\"email\\":null,\\"full_name\\":\\"Leodir de Abreu Miloch\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"1. Ciprofloxacino 500mg, Comprimido revestido ----------------------------- 14 Comprimidos\\\\nTomar 1 comprimido, via oral, duas vezes ao dia.\\"}", "medications": "Aas", "full_address": "Rua sem teto", "family_history": "Alzeimer", "prescription_transcript": "1. Ciprofloxacino 500 mg - Tomar 1 comprimido, via oral, duas vezes ao dia"}	\N	t	{"diseases": "Paciente relata hipertensão arterial.", "symptoms": "Paciente refere dor no cotovelo.", "allergies": "Paciente nega alergias.", "medications": [{"dose": "Não informado", "form": "Não informado", "name": "Ácido acetilsalicílico", "frequency": "Não informado"}], "risk_analysis": "baixo", "family_history": "Paciente nega histórico familiar de doenças."}	\N	\N	\N	f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0	48b2f584-e6d7-4b34-a642-8b3ac85ee3de
60f673f9-2880-4b33-a422-447520fbeacc	4915158832107	terms	2025-10-20 23:01:17.701128+00	2025-10-20 23:48:21.456814+00	\N	27/08/1986	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	{"diseases": "Asma e Glaucoma", "symptoms": "Dor nas pé da barriga", "allergies": "Contrate de ressolança", "full_name": "João Carlos Fonseca Corrijido", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":null,\\"crm\\":{\\"number\\":\\"150494\\",\\"state\\":null},\\"name\\":\\"Lucas Barros\\"},\\"medications\\":[{\\"dosage\\":\\"10 mg\\",\\"name\\":\\"Aripiprazol\\",\\"posology\\":\\"Tomar 1 comprimido pela manhã\\"},{\\"dosage\\":\\"75 mcg\\",\\"name\\":\\"Levotiroxina\\",\\"posology\\":\\"Tomar 1 comprimido em jejum\\"}],\\"patient\\":{\\"address_cep\\":null,\\"address_city\\":null,\\"address_complement\\":null,\\"address_neighborhood\\":null,\\"address_number\\":null,\\"address_state\\":null,\\"address_street\\":null,\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"João Carlos Fonseca\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"Para o sr. João Carlos Fonseca\\\\n\\\\nUso oral:\\\\n\\\\n1) Aripiprazol 10 mg — 60 cp\\\\nTomar 1 cp pela manhã\\\\n\\\\n2) Levotiroxina 75 mcg —\\\\nTomar 1 cp em jejum\\\\n\\\\nLucas Barros\\\\nCRM 150494\\"}", "medications": "Captopril 10mg 12/12 horas. Losartana 50mg 12/12 horas, Vitamina B12 100mg noite, Lebotiroxina 25mcg manha", "full_address": "Rua Arrebol, 33", "family_history": "Mãe com diabetes", "prescription_transcript": "1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum"}	\N	f	{"diseases": ["Paciente relata asma.", "Paciente relata glaucoma."], "symptoms": "Paciente refere dor abdominal.", "allergies": ["Paciente nega alergias."], "medications": [{"dose": "10mg", "form": "comprimido", "name": "Captopril", "frequency": "a cada 12 horas"}, {"dose": "50mg", "form": "comprimido", "name": "Losartana", "frequency": "a cada 12 horas"}, {"dose": "100mg", "form": "comprimido", "name": "Vitamina B12", "frequency": "à noite"}, {"dose": "25mcg", "form": "comprimido", "name": "Levotiroxina", "frequency": "pela manhã"}], "risk_analysis": "moderado", "family_history": ["Paciente nega histórico familiar de doenças."]}	\N	\N	\N	75ffc611-f82c-43cf-bf3e-bbf75123b7aa	9217ba7f-e064-4eb4-9919-679fb4e3a951
6a2328e2-c454-40fc-b503-cdf03af00910	553584687005	added_to_queue	2025-10-21 11:31:26.679288+00	2025-10-21 11:44:00.137201+00	\N	20/04/2012	1. Quet 100 mg - Tomar 1 comprimido à noite\n2. Zap 10 mg - Tomar 1 comprimido cedo e à tarde\n3. Quet XR 50 mg - Tomar 1 comprimido à noite\n4. Lyberdila Gotas 40 mg/mL - Tomar 8 gotas após o café da manhã\n5. Melatonn Max Menta 0,21 mg - Tomar 10 gotas à noite\n6. Roxetin XR 12,5 mg - Tomar 1 comprimido após o café da manhã	{"diseases": "Nega doenças prévias", "symptoms": "Atualmente enfrenta desafios relativos a puberdade. Teve sua primeira ereção, está confuso , com medo , já fizemos a troca do medicamento de Sertralina para o Paroxetina para mantermos o controle dessa libido . Idade de 13 anos , porém devido ao Autismo nível 2 de suporte ainda não tem cognitivo para lidar com essas transformaçoes do corpo e hormonais. Está tendo mais estereotipias e crises agressivas .", "allergies": "Nega alergias", "full_name": "João Vitor Capatti de Oliveira", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":\\"Médico Psiquiatra • RQE:63169 • Carimbo no rodapé: Dr. Tales Vilela Rocha RQE nº 63169 | Psiquiatra CRM-MG 64408\\",\\"crm\\":{\\"number\\":\\"64408\\",\\"state\\":\\"MG\\"},\\"name\\":\\"Dr. Tales Vilela Rocha\\"},\\"medications\\":[{\\"dosage\\":\\"100 mg\\",\\"name\\":\\"Quet\\",\\"posology\\":\\"Tomar 1 comprimido à noite\\"},{\\"dosage\\":\\"10 mg\\",\\"name\\":\\"Zap\\",\\"posology\\":\\"Tomar 1 comprimido cedo e à tarde\\"},{\\"dosage\\":\\"50 mg\\",\\"name\\":\\"Quet XR\\",\\"posology\\":\\"Tomar 1 comprimido à noite\\"},{\\"dosage\\":\\"40 mg/mL\\",\\"name\\":\\"Lyberdila Gotas\\",\\"posology\\":\\"Tomar 8 gotas após o café da manhã\\"},{\\"dosage\\":\\"0,21 mg\\",\\"name\\":\\"Melatonn Max Menta\\",\\"posology\\":\\"Tomar 10 gotas à noite\\"},{\\"dosage\\":\\"12,5 mg\\",\\"name\\":\\"Roxetin XR\\",\\"posology\\":\\"Tomar 1 comprimido após o café da manhã\\"}],\\"patient\\":{\\"address_cep\\":null,\\"address_city\\":null,\\"address_complement\\":null,\\"address_neighborhood\\":null,\\"address_number\\":\\"2419\\",\\"address_state\\":null,\\"address_street\\":\\"Rua Martim Afonso\\",\\"birth_date\\":null,\\"cpf\\":\\"Não há CPF cadastrado\\",\\"email\\":null,\\"full_name\\":\\"João Vitor Capati de Oliveira\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"1. Quet 100mg, Comprimido revestido (30un) Eurofarma — uso contínuo\\\\nHemifumarato de quetiapina 100mg\\\\nTomar 1 comprimido à noite\\\\n\\\\n2. Zap 10mg, Comprimido (30un) Momenta — uso contínuo\\\\nOlanzapina 10mg\\\\nTomar 1 comprimido cedo e à tarde.\\\\n\\\\n3. Quet XR 50mg, Comprimido revestido de liberação prolongada (30un) Eurofarma — uso contínuo\\\\nHemifumarato de quetiapina 50mg\\\\nTomar 1 comprimido à noite.\\\\n\\\\n4. Lyberdila Gotas 40mg/mL, Solução gotas (1un de 50mL) EMS — uso contínuo\\\\nDimesilato de lisdexanfetamina 40mg/mL\\\\nTomar 8 gotas após o café da manhã.\\\\n\\\\n5. Melatonn Max Menta 0,21mg, Gotas (1un de 30mL) Mantecorp — uso contínuo\\\\nMelatonina 0,21mg\\\\nTomar 10 gotas à noite.\\\\n\\\\n6. Roxetin XR 12,5mg, Comprimido revestido de liberação modificada (30un) Supera Farma — uso contínuo\\\\nCloridrato de paroxetina hemi-hidratado 12,5mg\\\\nTomar 1 comprimido após o café da manhã.\\\\n\\\\nData e hora: 11/09/2025 – 15:53:00 (GMT-3)\\\\nMEMED - Acesso à sua receita digital via QR Code\\\\nEndereço: Rua Martim Afonso 2419\\\\n\\\\\\"Antes de curar alguém, pergunte se ele está disposto a desistir das coisas que o deixam doente\\\\\\" Hipócrates\\"}", "medications": "Pantoprazol sódico sesqui- hidratado 2O mg \\n01 comprimido em jejum", "full_address": "Rua Pedro Silveira 375 Alfenas Mg  \\nCep 37130061", "family_history": "Avó e tia materna com diabetes  e hipertensão Ambas falecidas . \\nMãe com hipertensão.", "prescription_transcript": "1. Quet 100 mg - Tomar 1 comprimido à noite\\n2. Zap 10 mg - Tomar 1 comprimido cedo e à tarde\\n3. Quet XR 50 mg - Tomar 1 comprimido à noite\\n4. Lyberdila Gotas 40 mg/mL - Tomar 8 gotas após o café da manhã\\n5. Melatonn Max Menta 0,21 mg - Tomar 10 gotas à noite\\n6. Roxetin XR 12,5 mg - Tomar 1 comprimido após o café da manhã"}	\N	t	\N	\N	\N	\N	0c89a6ff-6598-400e-affb-47ccc3979761	\N
aebbd84e-c9c8-4e99-9e8e-967629412f1e	4915158832107	terms	2025-10-21 00:07:26.224838+00	2025-11-02 22:43:12.152479+00	\N	10/10/2010	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "full_name": "João Carlos Fonseca", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":null,\\"crm\\":{\\"number\\":\\"150494\\",\\"state\\":null},\\"name\\":\\"Lucas Barros\\"},\\"medications\\":[{\\"dosage\\":\\"10 mg\\",\\"name\\":\\"Aripiprazol\\",\\"posology\\":\\"Tomar 1 comprimido pela manhã\\"},{\\"dosage\\":\\"75 mcg\\",\\"name\\":\\"Levotiroxina\\",\\"posology\\":\\"Tomar 1 comprimido em jejum\\"}],\\"patient\\":{\\"address_cep\\":null,\\"address_city\\":null,\\"address_complement\\":null,\\"address_neighborhood\\":null,\\"address_number\\":null,\\"address_state\\":null,\\"address_street\\":null,\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"João Carlos Fonseca\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"Para o sr. João Carlos Fonseca\\\\n\\\\nUso oral:\\\\n\\\\n1) Aripiprazol 10 mg —— 60 cp\\\\nTomar 1 cp pela manhã\\\\n\\\\n2) Levotiroxina 75 mcg ——\\\\nTomar 1 cp em jejum\\\\n\\\\nLucas Barros\\\\nCRM 150494\\"}", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "full_address": "Não informado", "family_history": "Nega histórico familiar de doenças graves", "prescription_transcript": "1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum"}	\N	t	{"diseases": ["Paciente nega doenças prévias."], "symptoms": "Paciente nega sintomas atuais.", "allergies": ["Paciente nega alergias."], "medications": "Paciente nega uso de medicamentos.", "risk_analysis": "baixo", "family_history": ["Paciente nega histórico familiar de doenças."]}	\N	\N	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	39507116-4a58-4600-8726-79afd9aa0494
\.


--
-- TOC entry 5130 (class 0 OID 25041)
-- Dependencies: 224
-- Data for Name: doctor_blackouts; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.doctor_blackouts (id, doctor_id, win, reason, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5131 (class 0 OID 25049)
-- Dependencies: 225
-- Data for Name: doctor_certificates; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.doctor_certificates (doctor_id, access_token, created_at) FROM stdin;
86001d90-f0a0-4a2e-98db-b996a445052e	eyJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..ELRWNMrNLAnKgvyulpr8DA.2-NtlI0zV7t-AvAfycAeuCTPtrI6ROmm-1BWAVexsaCuB1AiI4JGV5OPn2wRQ-26zbDSYuJ4KPb-CGXvZ-NTCq-jI1d-x7-lng_jXwyEJSQDaPGsNphqKCOM4RdVimzG5iFt7MsvRuQiZ3_g11C9w3Cj_1BMhmpqQ_ZhlkMWPOUbKYR24NttOkp3CsXlnEAm.IA3BQSzwQ6kQt9ujGEN4yA	2025-10-21 12:14:59.266977+00
a542b6ef-ab24-49cc-80cd-396ed5a6171a	eyJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..Lq9uge_tIOgZ_nzWOeV8xw.Ce3HPV3m8ydj6mLgF6BVahwuSq8KgnJLr63CARAH4Scdfzc276N3EK5_Sct7u-r_4v0WROZ7tJz6HWTMZwCWQd8X9W_RMziLsksIQ9EFGAqikdLAVyWBKWIqSWcpZFSLq51GkmKESZx_Fewv_SHlWhv4DaFSQ91cUcavN52BgUL12VBwmXLja69E1dpurATw.NsHSO2j9Cp7wpwrPHL9hHQ	2025-10-21 12:22:27.609186+00
\.


--
-- TOC entry 5132 (class 0 OID 25055)
-- Dependencies: 226
-- Data for Name: doctor_extra_windows; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.doctor_extra_windows (id, doctor_id, win, capacity, created_at, updated_at) FROM stdin;
6132fc3c-8c9a-4783-adaf-7a82855fa557	550e8400-e29b-41d4-a716-446655440000	["2025-08-21 23:32:05.178073+00","2025-08-22 00:29:05.178073+00")	1	2025-08-21 23:29:05.178073+00	2025-08-21 23:29:05.178073+00
96907527-d544-4f0f-9423-775cdafc0524	550e8400-e29b-41d4-a716-446655440000	["2025-08-22 00:35:15.808266+00","2025-08-22 01:35:15.808266+00")	1	2025-08-22 00:35:15.808266+00	2025-08-22 00:35:15.808266+00
\.


--
-- TOC entry 5133 (class 0 OID 25064)
-- Dependencies: 227
-- Data for Name: doctor_schedules; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.doctor_schedules (id, doctor_id, day_of_week, start_time, end_time, timezone, active, created_at, updated_at) FROM stdin;
db2cdd00-a3c5-4741-99ad-048cf97b349f	86001d90-f0a0-4a2e-98db-b996a445052e	3	09:00:00	17:00:00	America/Sao_Paulo	t	2025-08-23 13:04:37.690505+00	2025-08-23 13:04:37.690505+00
1c8ec980-c221-4d7a-a357-18be1d2152a8	86001d90-f0a0-4a2e-98db-b996a445052e	4	09:00:00	17:00:00	America/Sao_Paulo	t	2025-08-23 13:04:37.690505+00	2025-08-23 13:04:37.690505+00
6806be7e-5c74-493e-91fa-88d562cc7a3b	86001d90-f0a0-4a2e-98db-b996a445052e	5	09:00:00	17:00:00	America/Sao_Paulo	t	2025-08-23 13:04:37.690505+00	2025-08-23 13:04:37.690505+00
9f28ef02-0dbe-4797-8b6a-516341359968	86001d90-f0a0-4a2e-98db-b996a445052e	1	09:00:00	17:00:00	America/Sao_Paulo	t	2025-08-23 13:04:37.690505+00	2025-10-19 12:49:22.459201+00
cba4c929-6e0e-4407-a8ab-d1d7da562953	a542b6ef-ab24-49cc-80cd-396ed5a6171a	2	09:00:00	17:00:00	America/Sao_Paulo	t	2025-08-23 13:04:37.690505+00	2025-10-19 12:49:22.469679+00
\.


--
-- TOC entry 5134 (class 0 OID 25074)
-- Dependencies: 228
-- Data for Name: doctors; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.doctors (id, user_id, crm, crm_state, specialty, pix_key, created_at, updated_at, full_name, specialties, is_available, clinic_name, clinic_cnpj, clinic_phone, clinic_email, clinic_website, clinic_street, clinic_number, clinic_complement, clinic_neighborhood, clinic_city, clinic_state, clinic_cep, clinic_cnes, total_approved, total_rejected) FROM stdin;
a34502ab-a061-4aa1-a7fd-c56b812e3e12	f846cd4c-6261-4048-8f82-33e2bb306fb8	442179	SP	\N	\N	2025-08-04 22:19:05.73128+00	2025-08-04 22:19:05.73128+00	Dr. Yadira Jones	{}	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	0
8b19bf8e-0f25-4adb-949f-88632d78d89f	192c5307-1d94-44f2-a6e4-aa831ca1d73e	45645	SP	\N	\N	2025-08-07 15:58:56.922125+00	2025-08-07 15:58:56.92213+00	654	{neurologia}	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	0
62c85ca9-b465-45a8-b508-e1d0c52be4d7	a8a3c6c8-82fd-4912-871a-6f8791f73d39	150874	SP	\N	\N	2025-10-19 12:53:29.30569+00	2025-10-19 12:53:29.30569+00	Lucas Amorim Vieira de Barros	{}	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	0
45b66d3d-6d1a-45f3-bc50-68b01ef8720b	74584d8a-54f7-467b-9864-582e94bb7452	412716	SP	\N	\N	2025-08-04 21:15:47.335773+00	2025-10-15 14:32:22.021675+00	Dr. Leanne Hudson	{}	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	20	1
0397ab5f-2dbc-45b7-97ba-95f65d5d1642	7455f35f-3853-4c16-93ff-402264d96822	269423	SP	\N	\N	2025-08-04 21:17:37.030537+00	2025-10-15 14:32:22.027933+00	Dr. Karson Hammes	{}	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	100
aa13cd03-5ea1-4264-95e2-cc4a8b2fdafb	6a32a357-daf5-4459-b82c-645299b23bc0	150496	SP	\N	\N	2025-08-04 21:16:58.544679+00	2025-09-28 12:34:05.492381+00	lucas	{}	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	0
f56f0ed9-6894-4f78-a8cb-0e1834e4303f	4ca24570-00df-491e-96c8-eb8462dc9941	654654	SP	\N	\N	2025-08-07 16:10:17.943333+00	2025-08-23 12:32:52.913382+00	54564	{neurologia}	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	0
550e8400-e29b-41d4-a716-446655440000	4ca24570-00df-491e-96c8-eb8462dc9941	0000	SP	\N	\N	2025-08-21 23:29:05.167782+00	2025-10-15 14:32:22.032754+00	Dr. Trickster 943	{General}	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	10	0
2f6c46a2-bd56-4aab-90b4-439b55b526aa	6dd1fd80-a17c-4d7c-9ce2-41fa5eda4487	21231	SP	\N	\N	2025-08-07 11:52:27.178276+00	2025-08-23 12:51:53.393993+00	564	{}	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	0
6693ccca-d2e7-411e-bd8d-6497ad4adf96	6362c867-8ef6-4bc4-ba4b-fc7d17bd7f71	54879	SP	\N	ASDF	2025-10-27 10:38:41.427331+00	2025-10-27 10:38:42.228952+00	NOMECOMPLETO	{anestesiologia}	t	ASDFASDF	22.800.544/0015-85	4654654	asdfasdoipquejwr@gjaokds.com	http://www.clinica.com	ASDFASDF	012	212	2121	465546	AP	06040-330	65465	0	0
a542b6ef-ab24-49cc-80cd-396ed5a6171a	4f8929c1-d6b1-4e41-a940-981f6a589ece	145001	SP	\N	\N	2025-10-15 13:31:55.377565+00	2025-10-28 11:47:12.352715+00	Heitor Éttori	{}	t	Neurovitta	12.345.678/0001-90	12981758630	heitor@cliquereceita.com.br	https://neurovitta.com.br/	Praça Melvin Jones	18	\N	Jardim São Dimas	São José dos Campos	SP	12245-360	2077469	54	23
c965ffa5-c315-4dc1-b1ae-84666e41c753	a0e6d250-2365-489d-85f7-96c9b5d934ec	4545	SP	\N	\N	2025-10-26 14:08:41.903144+00	2025-10-26 14:08:41.903144+00	dfgsf	{}	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	0
6668297a-9b4d-498e-b5c1-c81bdb197a90	d04d8ef9-394b-4077-8acc-4ec48ac89937	13245	SP	\N	\N	2025-10-26 14:32:49.094167+00	2025-10-26 14:32:49.094167+00	123	{}	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	0
bc3598c3-8143-41f8-a729-6cc74609290e	917b5903-544c-4d2b-802a-d8724b2f1d3c	456451	SP	\N	456+	2025-10-26 14:54:50.15712+00	2025-10-26 14:54:50.984051+00	sdfgsdfg	{acupuntura}	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	0
86001d90-f0a0-4a2e-98db-b996a445052e	ec650cd5-7ea6-4066-85a3-37d3a6f17270	150494	SP	\N	asdfasdf	2025-08-23 13:03:20.144129+00	2025-11-02 23:00:20.400372+00	Lucas Amorim Vieira de Barros	{}	t	Neurovitta	12.345.678/0001-90	12981758630	lucas@cliquereceita.com.br	https://neurovitta.com.br/	Praça Melvin Jones	18	\N	Jardim São Dimas	São José dos Campos	SP	12245-360	2077469	26	16
79d54c3e-9acd-45f4-86df-af19ff1660f8	d5bf74ee-1147-4ff5-a2c8-17b9fd2a958c	150487	SP	\N	vamos	2025-10-26 21:57:02.959144+00	2025-10-26 21:58:32.974287+00	vamos	{acupuntura}	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	0
524cd184-c265-4739-a4e8-3e811c49c305	84704d75-9e37-4bbb-ba87-778679f538a1	15487	SP	\N	asdfsadf	2025-10-27 10:15:33.753371+00	2025-10-27 10:15:34.603491+00	jkl	{alergia_imunologia}	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	0
580f6530-0d39-4c09-8ad7-1576789aad5f	81c591f5-2bbc-4cdf-9363-43e4ba222648	15494	SP	\N	21321	2025-10-27 10:21:50.023675+00	2025-10-27 10:21:50.848455+00	lkl	{alergia_imunologia}	t	asdlkfasdj	22.800.377/0001-68	1120254587	lcs@gmailc.com	http://www.clinica.com	asdfa	12	12	12	12	AL	06040-330	12	0	0
87e4a2b7-83f9-4e3a-8578-22a419d730bd	82183e88-b149-4abf-81a1-03605a0ad465	154945	SP	\N	21321	2025-10-27 10:27:03.565725+00	2025-10-27 10:27:04.155459+00	lkl	{alergia_imunologia}	t	asdlkfasdj	22.700.377/0001-68	1120254587	lcs@gmailc.com	http://www.clinica.com	asdfa	12	12	12	12	AL	06040-330	12	0	0
5338312c-2048-406a-ab8c-52aff7f18456	e8c04bc5-b237-484d-be31-0369c3ad1a40	58748	SP	\N	\N	2025-10-27 10:32:41.503742+00	2025-10-27 10:32:41.503742+00	NOMECOMPLETO	{angiologia}	t	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0	0
\.


--
-- TOC entry 5137 (class 0 OID 25114)
-- Dependencies: 232
-- Data for Name: files; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.files (id, filename, original_filename, file_path, file_size, mime_type, file_type, metadata, created_at, updated_at, medical_history_id, patient_id, prescription_renewal_id, conversation_id) FROM stdin;
dd3ff4c8-9c74-42f0-9c6a-58268eb911e3	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.pdf	prescription.pdf	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760634147668-prescription.pdf	35658	application/pdf	prescription	{}	2025-10-16 17:02:28.94844+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
d882d2cb-792d-4110-8627-e7e397e677ff	dabf26b0-e66e-48ca-954a-795c8592a1aa-prescription-signed.pdf	receita_patient_4915158832107_20251013_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/dabf26b0-e66e-48ca-954a-795c8592a1aa-prescription-signed.pdf	169021	application/pdf	signed_document	{}	2025-10-13 13:08:00.63639+00	2025-10-16 17:01:47.925916+00	f7b97037-0ee8-4da0-818f-fc85a0ad7643	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
2c722be8-c8e8-40ad-b5ba-c8b76fa9c482	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.pdf	prescription.pdf	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760632631192-prescription.pdf	35658	application/pdf	prescription	{}	2025-10-16 16:37:15.576276+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
ceeedeaa-1fc0-4cd4-b140-ee4d32dea7da	374166ad-f6f8-4063-b45f-ea570f51f051-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/374166ad-f6f8-4063-b45f-ea570f51f051-anamnesis-signed.pdf	155563	application/pdf	document	{}	2025-10-17 23:34:35.383383+00	2025-10-17 23:34:35.383385+00	4be2fd18-2db1-4f47-861f-cb64be199162	5e113a13-25ab-4812-acc2-0c675ac8b791	374166ad-f6f8-4063-b45f-ea570f51f051	\N
946e471a-24ff-4593-9b20-706e574e0aed	25e5c02c-58ee-4654-88bb-8f93bcabd8d2-prescription-signed.pdf	receita_patient_4915158832107_20251018_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/25e5c02c-58ee-4654-88bb-8f93bcabd8d2-prescription-signed.pdf	166912	application/pdf	signed_document	{}	2025-10-18 12:11:58.003692+00	2025-10-18 12:11:58.003695+00	e7d32029-be94-4e0f-98e8-c7781ecb247d	5e113a13-25ab-4812-acc2-0c675ac8b791	25e5c02c-58ee-4654-88bb-8f93bcabd8d2	\N
f1b4cbbb-40c3-45c7-aede-25b1a2d19203	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760806924538-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-18 17:02:06.364013+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
baff1860-df9d-4ad9-910d-8b05e919364a	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760739025022-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-17 22:10:27.206695+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
2afebf1b-82b7-4d88-9810-92d5ef1b3918	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.pdf	prescription.pdf	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760650769027-prescription.pdf	168747	application/pdf	prescription	{}	2025-10-16 21:39:31.202533+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
46ced2fb-997c-4fae-b8fb-5466434e31ba	7b27685d-7684-49c1-bc88-ecae7afd0d01-prescription.jpg	prescription.jpg	prescriptions/7b27685d-7684-49c1-bc88-ecae7afd0d01/1760912995495-prescription.jpg	64473	image/jpeg	prescription	{}	2025-10-19 22:29:56.554127+00	2025-10-19 22:32:38.942629+00	\N	8e31833e-effe-4867-9965-9a346c850b72	9a88289a-547f-4384-a6e8-0b4f51811142	7b27685d-7684-49c1-bc88-ecae7afd0d01
6453de97-fb01-45e3-95ff-d34197111021	9a88289a-547f-4384-a6e8-0b4f51811142-prescription-signed.pdf	receita_não_informado_20251019_signed.pdf	patients/8e31833e-effe-4867-9965-9a346c850b72/documents/9a88289a-547f-4384-a6e8-0b4f51811142-prescription-signed.pdf	167282	application/pdf	signed_document	{}	2025-10-19 22:46:50.653951+00	2025-10-19 22:46:50.653953+00	316005b0-6bd1-4c26-a46f-c0bd13c6b32d	8e31833e-effe-4867-9965-9a346c850b72	9a88289a-547f-4384-a6e8-0b4f51811142	\N
758b26fb-f240-4fd8-b9bc-32d57618caa8	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760958347097-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-20 11:05:48.377121+00	2025-10-20 11:05:50.650885+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	40c941cc-e135-4acf-ab4a-5b050228a258	37c7666e-0b22-47ba-b4d2-78cf431ad8de
8e095506-64c8-43e7-94c6-82e593990cb4	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760856205446-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-19 06:43:26.951562+00	2025-10-20 11:05:50.658188+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	40c941cc-e135-4acf-ab4a-5b050228a258	37c7666e-0b22-47ba-b4d2-78cf431ad8de
36023fca-de22-4c89-8d7d-5fffb071d2e1	9217ba7f-e064-4eb4-9919-679fb4e3a951-anamnesis-signed.pdf	anamnesis_75ffc611-f82c-43cf-bf3e-bbf75123b7aa_signed.pdf	patients/75ffc611-f82c-43cf-bf3e-bbf75123b7aa/documents/9217ba7f-e064-4eb4-9919-679fb4e3a951-anamnesis-signed.pdf	158562	application/pdf	document	{}	2025-10-20 23:05:08.104406+00	2025-10-20 23:05:08.104409+00	e22ac097-d2d6-43af-9306-acab43d542bd	75ffc611-f82c-43cf-bf3e-bbf75123b7aa	9217ba7f-e064-4eb4-9919-679fb4e3a951	\N
ae83d94a-27c7-4e71-9391-921838bfa60a	d64feefb-8b6e-47d8-8d51-92b3a864c2b6-prescription.jpg	prescription.jpg	prescriptions/d64feefb-8b6e-47d8-8d51-92b3a864c2b6/1761044495731-prescription.jpg	262901	image/jpeg	prescription	{}	2025-10-21 11:01:37.574462+00	2025-10-21 11:01:58.734586+00	\N	2b635923-f6c4-435a-9054-156c2113888f	badb42d5-27a3-4ddf-bfcd-1bb49b06665d	d64feefb-8b6e-47d8-8d51-92b3a864c2b6
822c8e90-6654-4842-b2e6-9619b7ba6f37	badb42d5-27a3-4ddf-bfcd-1bb49b06665d-prescription-signed.pdf	receita_theo_ragazzini_ettori_20251021_signed.pdf	patients/2b635923-f6c4-435a-9054-156c2113888f/documents/badb42d5-27a3-4ddf-bfcd-1bb49b06665d-prescription-signed.pdf	167528	application/pdf	signed_document	{}	2025-10-21 11:02:35.934831+00	2025-10-21 11:02:35.934834+00	2120281b-1973-40cc-8ac5-3a69978c44dd	2b635923-f6c4-435a-9054-156c2113888f	badb42d5-27a3-4ddf-bfcd-1bb49b06665d	\N
0ee5b4d6-8364-4227-935a-3e03649a5e1f	033443c6-b72d-4720-844a-5c5b5f338615-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/033443c6-b72d-4720-844a-5c5b5f338615-anamnesis-signed.pdf	158415	application/pdf	document	{}	2025-10-13 13:17:07.598069+00	2025-10-16 17:01:47.927615+00	4c7550bb-a096-4796-a20d-4ea859450099	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
ca911bde-42e2-4cf3-b070-b24f4a4f6451	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.jpg	prescription.jpg	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760632986742-prescription.jpg	139740	image/jpeg	prescription	{}	2025-10-16 16:43:08.262596+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
00cf1e93-d879-4135-8134-18520411abf9	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.pdf	prescription.pdf	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760634940269-prescription.pdf	35658	application/pdf	prescription	{}	2025-10-16 17:15:41.347946+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
1c223c29-b392-4e7d-aa6d-7f1b6202e7a5	3f76a55d-47e1-4f12-b831-f07ac39a69f0-prescription-signed.pdf	receita_patient_4915158832107_20251019_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/3f76a55d-47e1-4f12-b831-f07ac39a69f0-prescription-signed.pdf	167213	application/pdf	signed_document	{}	2025-10-19 06:51:56.247355+00	2025-10-19 06:51:56.247357+00	e5ab776f-b6a6-4ceb-affa-3cbffb99d62d	5e113a13-25ab-4812-acc2-0c675ac8b791	3f76a55d-47e1-4f12-b831-f07ac39a69f0	\N
1cc34484-3935-4aae-888d-ac5a6787392f	9a88289a-547f-4384-a6e8-0b4f51811142-anamnesis-signed.pdf	anamnesis_8e31833e-effe-4867-9965-9a346c850b72_signed.pdf	patients/8e31833e-effe-4867-9965-9a346c850b72/documents/9a88289a-547f-4384-a6e8-0b4f51811142-anamnesis-signed.pdf	156883	application/pdf	document	{}	2025-10-19 22:46:51.433608+00	2025-10-19 22:46:51.433611+00	316005b0-6bd1-4c26-a46f-c0bd13c6b32d	8e31833e-effe-4867-9965-9a346c850b72	9a88289a-547f-4384-a6e8-0b4f51811142	\N
e578aaf8-2c07-480f-8d63-2ff126110f71	dba64f9e-b837-44b2-ad40-ba4bba0d91f2-prescription-signed.pdf	receita_patient_4915158832107_20251017_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/dba64f9e-b837-44b2-ad40-ba4bba0d91f2-prescription-signed.pdf	168291	application/pdf	signed_document	{}	2025-10-17 23:12:23.213169+00	2025-10-17 23:12:23.213171+00	356f3094-0c62-462a-81d4-1302d902e54a	5e113a13-25ab-4812-acc2-0c675ac8b791	dba64f9e-b837-44b2-ad40-ba4bba0d91f2	\N
95ba8ff6-3b5e-42e2-8ab8-a1e079cd8828	aebbd84e-c9c8-4e99-9e8e-967629412f1e-prescription.jpg	prescription.jpg	prescriptions/aebbd84e-c9c8-4e99-9e8e-967629412f1e/1761044357365-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-21 10:59:18.713105+00	2025-10-31 12:35:12.867943+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	39507116-4a58-4600-8726-79afd9aa0494	aebbd84e-c9c8-4e99-9e8e-967629412f1e
5c0b4f76-4ed5-43e4-ba91-6c499783542f	40c941cc-e135-4acf-ab4a-5b050228a258-prescription-signed.pdf	receita_patient_4915158832107_20251020_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/40c941cc-e135-4acf-ab4a-5b050228a258-prescription-signed.pdf	168570	application/pdf	signed_document	{}	2025-10-20 11:09:02.300271+00	2025-10-20 11:09:02.300272+00	0f1f1ac3-49e5-4e20-8b3b-c2a726f72483	5e113a13-25ab-4812-acc2-0c675ac8b791	40c941cc-e135-4acf-ab4a-5b050228a258	\N
69ae6f6d-5a7d-4a46-a2b4-43b506d6ebae	020dffbd-7dfc-42bb-a403-b9808cd2e330-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/020dffbd-7dfc-42bb-a403-b9808cd2e330-anamnesis-signed.pdf	155956	application/pdf	document	{}	2025-10-18 00:32:22.454689+00	2025-10-18 00:32:22.454692+00	61f04e64-6a36-4c90-a5e9-4e3ca74e2679	5e113a13-25ab-4812-acc2-0c675ac8b791	020dffbd-7dfc-42bb-a403-b9808cd2e330	\N
96a9e192-67a0-40fa-b404-c36d745feb15	25e5c02c-58ee-4654-88bb-8f93bcabd8d2-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/25e5c02c-58ee-4654-88bb-8f93bcabd8d2-anamnesis-signed.pdf	155956	application/pdf	document	{}	2025-10-18 12:11:58.964226+00	2025-10-18 12:11:58.964229+00	e7d32029-be94-4e0f-98e8-c7781ecb247d	5e113a13-25ab-4812-acc2-0c675ac8b791	25e5c02c-58ee-4654-88bb-8f93bcabd8d2	\N
a4f73e00-e24c-4847-a0b8-49371376d272	dc46dd45-5336-4428-bfb8-73f81ecaed60-prescription.jpg	prescription.jpg	prescriptions/dc46dd45-5336-4428-bfb8-73f81ecaed60/1761004138841-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-20 23:49:00.275858+00	2025-10-20 23:49:59.77927+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	5fcdf7d1-8261-4067-b31c-664f2d2ae00f	dc46dd45-5336-4428-bfb8-73f81ecaed60
fd929655-5585-4505-bd84-8329bcf880de	d64feefb-8b6e-47d8-8d51-92b3a864c2b6-prescription.pdf	prescription.pdf	prescriptions/d64feefb-8b6e-47d8-8d51-92b3a864c2b6/1761043493982-prescription.pdf	93349	application/pdf	prescription	{}	2025-10-21 10:44:55.137801+00	2025-10-21 11:01:58.736574+00	\N	2b635923-f6c4-435a-9054-156c2113888f	badb42d5-27a3-4ddf-bfcd-1bb49b06665d	d64feefb-8b6e-47d8-8d51-92b3a864c2b6
0f091f4b-29b3-4589-9b98-d355256f54e2	badb42d5-27a3-4ddf-bfcd-1bb49b06665d-anamnesis-signed.pdf	anamnesis_2b635923-f6c4-435a-9054-156c2113888f_signed.pdf	patients/2b635923-f6c4-435a-9054-156c2113888f/documents/badb42d5-27a3-4ddf-bfcd-1bb49b06665d-anamnesis-signed.pdf	156809	application/pdf	document	{}	2025-10-21 11:02:36.581567+00	2025-10-21 11:02:36.58157+00	2120281b-1973-40cc-8ac5-3a69978c44dd	2b635923-f6c4-435a-9054-156c2113888f	badb42d5-27a3-4ddf-bfcd-1bb49b06665d	\N
93c59d90-8b1f-4782-9bf7-f57976599ced	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760808604272-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-18 17:30:05.934992+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
b1409951-3287-4659-952a-9c25ae25cb7e	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760747363971-prescription.jpg	139740	image/jpeg	prescription	{}	2025-10-18 00:29:25.838005+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
5c9aa1ed-ad60-4443-95fb-a8735b9e1a3e	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760742489935-prescription.jpg	276748	image/jpeg	prescription	{}	2025-10-17 23:08:12.430137+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
98fc13cb-2c32-490d-8479-0e04ffb9329e	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760651985753-prescription.jpg	276748	image/jpeg	prescription	{}	2025-10-16 21:59:48.960455+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
c6b0ea8b-bd5d-40bd-bec7-58ac0eb50229	311ed125-5fd9-4c1c-b769-fb5ff0c8cba0-prescription-signed.pdf	receita_patient_4915158832107_20251021_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/311ed125-5fd9-4c1c-b769-fb5ff0c8cba0-prescription-signed.pdf	169176	application/pdf	signed_document	{}	2025-10-21 11:03:19.244139+00	2025-10-21 11:03:19.244142+00	03b2ad09-79ed-413b-ba5e-07e8bd8f838b	5e113a13-25ab-4812-acc2-0c675ac8b791	311ed125-5fd9-4c1c-b769-fb5ff0c8cba0	\N
4190b8d3-c081-450c-bc62-b4865369d971	48b2f584-e6d7-4b34-a642-8b3ac85ee3de-anamnesis-signed.pdf	anamnesis_f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0_signed.pdf	patients/f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0/documents/48b2f584-e6d7-4b34-a642-8b3ac85ee3de-anamnesis-signed.pdf	156609	application/pdf	document	{}	2025-10-21 12:22:50.345823+00	2025-10-21 12:22:50.345826+00	b56b5ad1-4cae-41fd-89ce-a1dfa8535e7a	f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0	48b2f584-e6d7-4b34-a642-8b3ac85ee3de	\N
77a28fe6-14b8-4680-acff-eb9ce6dbdedd	dadbcede-f3f1-4dfc-9d0a-766ec608808d-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/dadbcede-f3f1-4dfc-9d0a-766ec608808d-anamnesis-signed.pdf	158464	application/pdf	document	{}	2025-10-13 13:24:01.957883+00	2025-10-16 17:01:47.929524+00	fc6c4429-4a14-4119-9b4b-fa3e8e0e4594	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
d75a38fa-3c23-42ff-9490-8d672aa107ae	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.pdf	prescription.pdf	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760636927947-prescription.pdf	35658	application/pdf	prescription	{}	2025-10-16 17:48:49.819821+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
4510145f-8398-4746-a437-da1dfae7464e	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.pdf	prescription.pdf	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760633737079-prescription.pdf	35658	application/pdf	prescription	{}	2025-10-16 16:55:41.561482+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
2b03af01-0846-4dd1-9cb6-e946e7b295b2	3f76a55d-47e1-4f12-b831-f07ac39a69f0-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/3f76a55d-47e1-4f12-b831-f07ac39a69f0-anamnesis-signed.pdf	155951	application/pdf	document	{}	2025-10-19 06:51:57.130544+00	2025-10-19 06:51:57.130547+00	e5ab776f-b6a6-4ceb-affa-3cbffb99d62d	5e113a13-25ab-4812-acc2-0c675ac8b791	3f76a55d-47e1-4f12-b831-f07ac39a69f0	\N
5875d6e2-a6d6-43a3-8b1f-0188158e1765	dba64f9e-b837-44b2-ad40-ba4bba0d91f2-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/dba64f9e-b837-44b2-ad40-ba4bba0d91f2-anamnesis-signed.pdf	155563	application/pdf	document	{}	2025-10-17 23:12:24.091065+00	2025-10-17 23:12:24.091068+00	356f3094-0c62-462a-81d4-1302d902e54a	5e113a13-25ab-4812-acc2-0c675ac8b791	dba64f9e-b837-44b2-ad40-ba4bba0d91f2	\N
c69f40a9-61a8-4c6f-83cc-3f3aa25be7f7	020dffbd-7dfc-42bb-a403-b9808cd2e330-prescription-signed.pdf	receita_patient_4915158832107_20251018_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/020dffbd-7dfc-42bb-a403-b9808cd2e330-prescription-signed.pdf	167243	application/pdf	signed_document	{}	2025-10-18 00:32:21.548836+00	2025-10-18 00:32:21.548839+00	61f04e64-6a36-4c90-a5e9-4e3ca74e2679	5e113a13-25ab-4812-acc2-0c675ac8b791	020dffbd-7dfc-42bb-a403-b9808cd2e330	\N
e7e08ab6-1626-4e90-b84a-1337f2dd8245	40c941cc-e135-4acf-ab4a-5b050228a258-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/40c941cc-e135-4acf-ab4a-5b050228a258-anamnesis-signed.pdf	156870	application/pdf	document	{}	2025-10-20 11:09:03.026938+00	2025-10-20 11:09:03.026941+00	0f1f1ac3-49e5-4e20-8b3b-c2a726f72483	5e113a13-25ab-4812-acc2-0c675ac8b791	40c941cc-e135-4acf-ab4a-5b050228a258	\N
eac0823f-7047-4fd5-9a39-f633f5a02116	ca12655e-9848-4a36-b0c5-efc44bc8d6c0-prescription.jpg	prescription.jpg	prescriptions/ca12655e-9848-4a36-b0c5-efc44bc8d6c0/1761005132331-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-21 00:05:33.607008+00	2025-10-21 00:05:33.60701+00	\N	abdb491c-dc08-40b1-826b-95a28c01b0a1	\N	ca12655e-9848-4a36-b0c5-efc44bc8d6c0
b40ae91a-5ab1-4292-8853-354248fc0031	311ed125-5fd9-4c1c-b769-fb5ff0c8cba0-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/311ed125-5fd9-4c1c-b769-fb5ff0c8cba0-anamnesis-signed.pdf	157455	application/pdf	document	{}	2025-10-21 11:03:19.902329+00	2025-10-21 11:03:19.902333+00	03b2ad09-79ed-413b-ba5e-07e8bd8f838b	5e113a13-25ab-4812-acc2-0c675ac8b791	311ed125-5fd9-4c1c-b769-fb5ff0c8cba0	\N
451d2887-6c9a-4e11-b190-21fa96389d70	6f5dab3c-a4bb-48d8-b15c-b724e217d778-prescription-signed.pdf	receita_patient_4915158832107_20251018_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/6f5dab3c-a4bb-48d8-b15c-b724e217d778-prescription-signed.pdf	167906	application/pdf	signed_document	{}	2025-10-18 17:55:27.460677+00	2025-10-18 17:55:27.460679+00	92ff8ad6-288c-40b0-b5d6-5a4e2758ad04	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
b9bf48f8-da64-4d53-be70-cb3c25f90a74	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760789864310-prescription.jpg	276748	image/jpeg	prescription	{}	2025-10-18 12:17:46.780262+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
964bd60f-12b1-493b-9ec9-3c0f793ea010	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760657376204-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-16 23:29:38.318924+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
e2713a4e-502d-4521-9f60-363c56b0d065	8dfb303c-c642-46ae-9970-14616ea72ac4-prescription-signed.pdf	receita_patient_4915158832107_20251021_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/8dfb303c-c642-46ae-9970-14616ea72ac4-prescription-signed.pdf	168769	application/pdf	signed_document	{}	2025-10-21 12:15:10.607189+00	2025-10-21 12:15:10.607192+00	99906368-963d-4595-a942-dcbebfb16f3d	5e113a13-25ab-4812-acc2-0c675ac8b791	8dfb303c-c642-46ae-9970-14616ea72ac4	\N
984b5610-4c4e-4c32-98b3-e014bed82509	0e58eb0b-4962-4f50-ab3f-f81bcd0f4607-prescription.jpg	prescription.jpg	prescriptions/0e58eb0b-4962-4f50-ab3f-f81bcd0f4607/1760358947831-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-13 12:35:49.066686+00	2025-10-16 20:18:53.824259+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
1a8c9dbc-7dd1-4f6a-8418-ec4ace2ae87e	eaa75513-c5f6-4228-bfc8-20b86365e839-anamnesis.pdf	anamnesis_57873e19-e1d2-42c4-990c-cf8a420e2a35.pdf	patients/57873e19-e1d2-42c4-990c-cf8a420e2a35/documents/eaa75513-c5f6-4228-bfc8-20b86365e839-anamnesis.pdf	48311	application/pdf	document	{}	2025-10-13 00:41:13.258664+00	2025-10-16 17:01:47.915238+00	95fcd13b-5e35-45cb-844c-079641a0c883	57873e19-e1d2-42c4-990c-cf8a420e2a35	\N	\N
76e54091-74ad-42e4-8d1d-0a6788864586	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.pdf	prescription.pdf	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760633920994-prescription.pdf	35658	application/pdf	prescription	{}	2025-10-16 16:58:42.882911+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
7cb23a14-e6ce-4f82-8493-de389445132f	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.pdf	prescription.pdf	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760637342047-prescription.pdf	35658	application/pdf	prescription	{}	2025-10-16 17:55:43.824417+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
ecb48e3b-6286-4dde-8fc5-fb6caecc3cfa	25618efb-877c-4b36-b357-a9ecb47bb984-prescription.pdf	prescription.pdf	prescriptions/25618efb-877c-4b36-b357-a9ecb47bb984/1760316147173-prescription.pdf	168382	application/pdf	prescription	{}	2025-10-13 00:42:28.71778+00	2025-10-16 20:18:53.84776+00	\N	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	\N	\N
97b81562-a294-415e-b2b8-1315f6524536	991df932-0fc9-4a7b-898d-c7334bf368d8-prescription-signed.pdf	receita_patient_4915158832107_20251018_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/991df932-0fc9-4a7b-898d-c7334bf368d8-prescription-signed.pdf	168759	application/pdf	signed_document	{}	2025-10-18 12:18:57.076387+00	2025-10-18 12:18:57.076389+00	dd61dd98-734c-4096-b5d4-d908848c0b9c	5e113a13-25ab-4812-acc2-0c675ac8b791	991df932-0fc9-4a7b-898d-c7334bf368d8	\N
65f536d1-5f1a-4ac7-8052-d63cf5b19be2	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.pdf	prescription.pdf	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760860298030-prescription.pdf	168429	application/pdf	prescription	{}	2025-10-19 07:51:39.878787+00	2025-10-20 11:05:50.656972+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	40c941cc-e135-4acf-ab4a-5b050228a258	37c7666e-0b22-47ba-b4d2-78cf431ad8de
bb4b9bfe-650a-4cdf-9035-445c03483322	247ede61-5b83-4c09-89a3-54db99807db5-prescription-signed.pdf	receita_patient_4915158832107_20251020_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/247ede61-5b83-4c09-89a3-54db99807db5-prescription-signed.pdf	168658	application/pdf	signed_document	{}	2025-10-20 19:38:05.93293+00	2025-10-20 19:38:05.932933+00	18dcda57-8888-41ad-97a5-5367e4eaf87b	5e113a13-25ab-4812-acc2-0c675ac8b791	247ede61-5b83-4c09-89a3-54db99807db5	\N
4b4ce53d-ce15-4136-bdf6-a0487ebfe416	6f5dab3c-a4bb-48d8-b15c-b724e217d778-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/6f5dab3c-a4bb-48d8-b15c-b724e217d778-anamnesis-signed.pdf	155956	application/pdf	document	{}	2025-10-18 17:55:28.358887+00	2025-10-18 17:55:28.35889+00	92ff8ad6-288c-40b0-b5d6-5a4e2758ad04	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
8dd6bacc-e313-445a-a787-ef630ade132e	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760786602755-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-18 11:23:24.313941+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
741c7dcf-2bc2-4b2b-a246-7b37d9768db0	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760743144444-prescription.jpg	141083	image/jpeg	prescription	{}	2025-10-17 23:19:06.158558+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
87c5c673-ecf4-4719-8b30-a1008683ae17	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.pdf	prescription.pdf	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760658716762-prescription.pdf	168747	application/pdf	prescription	{}	2025-10-16 23:51:58.995029+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
f930b08c-32df-4e02-806c-1a4633421e93	005929ee-c897-40ca-b92f-2e704b0a0aa6-prescription.jpg	prescription.jpg	prescriptions/005929ee-c897-40ca-b92f-2e704b0a0aa6/1761045799520-prescription.jpg	262901	image/jpeg	prescription	{}	2025-10-21 11:23:21.219828+00	2025-10-21 11:25:23.129459+00	\N	f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0	48b2f584-e6d7-4b34-a642-8b3ac85ee3de	005929ee-c897-40ca-b92f-2e704b0a0aa6
bda88cd4-fa9d-42ef-a3e0-18cecd479bc6	8dfb303c-c642-46ae-9970-14616ea72ac4-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/8dfb303c-c642-46ae-9970-14616ea72ac4-anamnesis-signed.pdf	157869	application/pdf	document	{}	2025-10-21 12:15:11.323455+00	2025-10-21 12:15:11.323458+00	99906368-963d-4595-a942-dcbebfb16f3d	5e113a13-25ab-4812-acc2-0c675ac8b791	8dfb303c-c642-46ae-9970-14616ea72ac4	\N
3aa4eaa1-79bf-4fe5-8151-225940407e06	0468511d-2313-4d95-b9ac-0badae7ac657-prescription-signed.pdf	receita_patient_4915158832107_20251012_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/0468511d-2313-4d95-b9ac-0badae7ac657-prescription-signed.pdf	168495	application/pdf	signed_document	{}	2025-10-12 19:24:52.386156+00	2025-10-16 17:01:47.910317+00	f8b2e135-d2f8-478c-bdb5-f912b133ddf8	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
1812b881-7544-4098-a638-8b19ea6ca209	a6b3d64d-e0a9-4458-a169-4530bdee4139-prescription.pdf	prescription.pdf	prescriptions/a6b3d64d-e0a9-4458-a169-4530bdee4139/1760297151977-prescription.pdf	167208	application/pdf	prescription	{}	2025-10-12 19:25:53.215592+00	2025-10-16 20:18:53.803977+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
d093ecb8-8a85-4b6c-8bf4-638fe744c09a	a6b3d64d-e0a9-4458-a169-4530bdee4139-prescription.pdf	prescription.pdf	prescriptions/a6b3d64d-e0a9-4458-a169-4530bdee4139/1760296610233-prescription.pdf	168644	application/pdf	prescription	{}	2025-10-12 19:16:51.968358+00	2025-10-16 20:18:53.803977+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
2a9a5358-6b26-40ae-8b1b-a44eb2cb4e3b	6890d13f-620f-40ba-8828-2965b63b4816-prescription.jpg	prescription.jpg	prescriptions/6890d13f-620f-40ba-8828-2965b63b4816/1760303773307-prescription.jpg	276748	image/jpeg	prescription	{}	2025-10-12 21:16:15.132212+00	2025-10-16 20:18:53.819629+00	\N	57873e19-e1d2-42c4-990c-cf8a420e2a35	\N	\N
58fc8261-84cd-4bca-9220-31ad810b81bf	0e58eb0b-4962-4f50-ab3f-f81bcd0f4607-prescription.jpg	prescription.jpg	prescriptions/0e58eb0b-4962-4f50-ab3f-f81bcd0f4607/1760356811202-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-13 12:00:12.482727+00	2025-10-16 20:18:53.824259+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
7cd22c2a-c9b9-467c-a516-5cc95684309b	0e58eb0b-4962-4f50-ab3f-f81bcd0f4607-prescription.jpg	prescription.jpg	prescriptions/0e58eb0b-4962-4f50-ab3f-f81bcd0f4607/1760354785151-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-13 11:26:26.410947+00	2025-10-16 20:18:53.824259+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
406d7a1b-6091-40f5-a661-25068bf69d92	78435732-7908-4949-b74d-33607184a0c4-prescription.pdf	prescription.pdf	prescriptions/78435732-7908-4949-b74d-33607184a0c4/1760303333486-prescription.pdf	167208	application/pdf	prescription	{}	2025-10-12 21:08:55.066732+00	2025-10-16 20:18:53.833363+00	\N	0a210e3b-ed53-413d-a343-16c667aefa64	\N	\N
d7785c83-5bc7-430d-86bc-e46642c10934	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.pdf	prescription.pdf	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760637511544-prescription.pdf	158562	application/pdf	prescription	{}	2025-10-16 17:58:35.756723+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
7ef02a51-56fb-483e-9ed3-0fbfc459415b	be34c1fd-352a-45e3-aa52-2f503a9fc805-prescription-signed.pdf	receita_patient_4915158832107_20251019_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/be34c1fd-352a-45e3-aa52-2f503a9fc805-prescription-signed.pdf	168770	application/pdf	signed_document	{}	2025-10-19 07:52:52.710565+00	2025-10-19 07:52:52.710567+00	a55aa716-f36f-4da2-b06b-60e651fe6e01	5e113a13-25ab-4812-acc2-0c675ac8b791	be34c1fd-352a-45e3-aa52-2f503a9fc805	\N
cffa1b2a-1fcb-4617-bf7d-4adea9a756ba	ff14a752-4b62-478f-945a-284b77f72eff-prescription-signed.pdf	receita_patient_4915158832107_20251017_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/ff14a752-4b62-478f-945a-284b77f72eff-prescription-signed.pdf	166671	application/pdf	signed_document	{}	2025-10-17 23:20:20.126179+00	2025-10-17 23:20:20.126181+00	d8584ddb-8880-4f4c-8612-f915649ca2df	5e113a13-25ab-4812-acc2-0c675ac8b791	ff14a752-4b62-478f-945a-284b77f72eff	\N
a17e6986-fd20-4499-9061-442966022aac	3e2f7584-3be0-4d8c-929b-69ed6392364b-prescription-signed.pdf	receita_patient_4915158832107_20251018_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/3e2f7584-3be0-4d8c-929b-69ed6392364b-prescription-signed.pdf	167790	application/pdf	signed_document	{}	2025-10-18 11:25:49.14286+00	2025-10-18 11:25:49.142863+00	d7fd19ca-966c-4b73-a6f4-b9f9f9c52382	5e113a13-25ab-4812-acc2-0c675ac8b791	3e2f7584-3be0-4d8c-929b-69ed6392364b	\N
a934c7db-2482-4a2b-a04c-1fdd0fbf6375	eaa75513-c5f6-4228-bfc8-20b86365e839-prescription-signed.pdf	receita_não_informado_20251013_signed.pdf	patients/57873e19-e1d2-42c4-990c-cf8a420e2a35/documents/eaa75513-c5f6-4228-bfc8-20b86365e839-prescription-signed.pdf	170575	application/pdf	signed_document	{}	2025-10-13 00:41:13.055011+00	2025-10-16 17:01:47.915238+00	95fcd13b-5e35-45cb-844c-079641a0c883	57873e19-e1d2-42c4-990c-cf8a420e2a35	\N	\N
a75e7509-e0c6-4e20-9a51-35eb03faa8c0	60aa3f7d-6b32-4bb7-a3d1-f19a9e77a5c3-anamnesis.pdf	anamnesis_eb0656f3-6b57-4c59-9e79-e27e5dcb16d8.pdf	patients/eb0656f3-6b57-4c59-9e79-e27e5dcb16d8/documents/60aa3f7d-6b32-4bb7-a3d1-f19a9e77a5c3-anamnesis.pdf	49272	application/pdf	document	{}	2025-10-13 00:45:47.88196+00	2025-10-16 17:01:47.916931+00	256231b5-1be3-4263-9a9b-0956aeddb8fb	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	\N	\N
c374efde-cd53-4fe7-a4da-345d579261e2	60aa3f7d-6b32-4bb7-a3d1-f19a9e77a5c3-prescription-signed.pdf	receita_heitor_éttori_20251013_signed.pdf	patients/eb0656f3-6b57-4c59-9e79-e27e5dcb16d8/documents/60aa3f7d-6b32-4bb7-a3d1-f19a9e77a5c3-prescription-signed.pdf	168580	application/pdf	signed_document	{}	2025-10-13 00:45:47.550871+00	2025-10-16 17:01:47.916931+00	256231b5-1be3-4263-9a9b-0956aeddb8fb	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	\N	\N
341205ba-1376-4ee6-91f6-0a714f140523	04f864ad-31ff-4cec-a40a-0c756ab31340-prescription-signed.pdf	receita_patient_4915158832107_20251013_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/04f864ad-31ff-4cec-a40a-0c756ab31340-prescription-signed.pdf	169075	application/pdf	signed_document	{}	2025-10-13 11:30:44.24989+00	2025-10-16 17:01:47.918718+00	6aa75d57-6919-4115-93c1-7d3d61abe96d	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
3c250a4d-7f7e-4629-89a1-9f64baadcf5d	dabf26b0-e66e-48ca-954a-795c8592a1aa-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/dabf26b0-e66e-48ca-954a-795c8592a1aa-anamnesis-signed.pdf	158415	application/pdf	document	{}	2025-10-13 13:08:01.358049+00	2025-10-16 17:01:47.925916+00	f7b97037-0ee8-4da0-818f-fc85a0ad7643	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
9be2e4c7-c566-4fdc-bc8c-43cf48422e1a	033443c6-b72d-4720-844a-5c5b5f338615-prescription-signed.pdf	receita_patient_4915158832107_20251013_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/033443c6-b72d-4720-844a-5c5b5f338615-prescription-signed.pdf	168883	application/pdf	signed_document	{}	2025-10-13 13:17:06.874083+00	2025-10-16 17:01:47.927615+00	4c7550bb-a096-4796-a20d-4ea859450099	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
db47717f-c1d6-481d-9786-30c8e970f070	dadbcede-f3f1-4dfc-9d0a-766ec608808d-prescription-signed.pdf	receita_patient_4915158832107_20251013_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/dadbcede-f3f1-4dfc-9d0a-766ec608808d-prescription-signed.pdf	168994	application/pdf	signed_document	{}	2025-10-13 13:24:01.239206+00	2025-10-16 17:01:47.929524+00	fc6c4429-4a14-4119-9b4b-fa3e8e0e4594	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
73298f07-f3a5-43ce-942a-b5eb0e069601	0468511d-2313-4d95-b9ac-0badae7ac657-anamnesis.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/0468511d-2313-4d95-b9ac-0badae7ac657-anamnesis.pdf	47889	application/pdf	document	{}	2025-10-12 19:24:52.788685+00	2025-10-16 17:01:47.910317+00	f8b2e135-d2f8-478c-bdb5-f912b133ddf8	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
910b6d91-4ddb-407d-b5ea-becbb1d31bef	4d39f254-962d-4bd2-9da7-05cfde62f915-prescription.jpg	prescription.jpg	prescriptions/4d39f254-962d-4bd2-9da7-05cfde62f915/1760364511366-prescription.jpg	201389	image/jpeg	prescription	{}	2025-10-13 14:08:33.629066+00	2025-10-16 20:18:53.822582+00	\N	47ec77d4-b2fd-49be-9d64-4db12563c89c	\N	\N
e7055dfd-7ec0-4e87-a307-c6d93c65f199	0e58eb0b-4962-4f50-ab3f-f81bcd0f4607-prescription.jpg	prescription.jpg	prescriptions/0e58eb0b-4962-4f50-ab3f-f81bcd0f4607/1760361818707-prescription.jpg	532313	image/jpeg	prescription	{}	2025-10-13 13:23:42.06061+00	2025-10-16 20:18:53.824259+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
4470afc7-bca0-49bb-b18c-ec9c439eb51f	0e58eb0b-4962-4f50-ab3f-f81bcd0f4607-prescription.jpg	prescription.jpg	prescriptions/0e58eb0b-4962-4f50-ab3f-f81bcd0f4607/1760361352700-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-13 13:15:53.865798+00	2025-10-16 20:18:53.824259+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
b0f0fc5b-7946-41f0-ac7f-6b82ffe88e4f	0e58eb0b-4962-4f50-ab3f-f81bcd0f4607-prescription.jpg	prescription.jpg	prescriptions/0e58eb0b-4962-4f50-ab3f-f81bcd0f4607/1760362410061-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-13 13:33:31.658771+00	2025-10-16 20:18:53.824259+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
18994244-a0ec-475e-9794-3ab84208ecb6	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.jpg	prescription.jpg	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760637679856-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-16 18:01:22.36287+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
1c9d2004-7269-4354-92b8-f7f76e7896b7	7faff561-b7c4-4607-abd6-001904bf463a-prescription.jpg	prescription.jpg	prescriptions/7faff561-b7c4-4607-abd6-001904bf463a/1760369028456-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-13 15:23:50.638565+00	2025-10-16 20:18:53.846066+00	\N	9fe0af44-5e3d-42d0-9144-ab175099d699	\N	\N
e53f64da-dbdd-44ae-b735-57ebfb2d22a1	be34c1fd-352a-45e3-aa52-2f503a9fc805-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/be34c1fd-352a-45e3-aa52-2f503a9fc805-anamnesis-signed.pdf	155951	application/pdf	document	{}	2025-10-19 07:52:53.55949+00	2025-10-19 07:52:53.559492+00	a55aa716-f36f-4da2-b06b-60e651fe6e01	5e113a13-25ab-4812-acc2-0c675ac8b791	be34c1fd-352a-45e3-aa52-2f503a9fc805	\N
b50f58ff-cf8e-4373-b253-3ccb3d23d1ee	ff14a752-4b62-478f-945a-284b77f72eff-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/ff14a752-4b62-478f-945a-284b77f72eff-anamnesis-signed.pdf	155563	application/pdf	document	{}	2025-10-17 23:20:21.027013+00	2025-10-17 23:20:21.027015+00	d8584ddb-8880-4f4c-8612-f915649ca2df	5e113a13-25ab-4812-acc2-0c675ac8b791	ff14a752-4b62-478f-945a-284b77f72eff	\N
4b615736-1bba-401b-979f-4766cd51194f	3e2f7584-3be0-4d8c-929b-69ed6392364b-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/3e2f7584-3be0-4d8c-929b-69ed6392364b-anamnesis-signed.pdf	155956	application/pdf	document	{}	2025-10-18 11:25:50.022+00	2025-10-18 11:25:50.022003+00	d7fd19ca-966c-4b73-a6f4-b9f9f9c52382	5e113a13-25ab-4812-acc2-0c675ac8b791	3e2f7584-3be0-4d8c-929b-69ed6392364b	\N
d011aad2-fb2e-4107-938b-d04332fe9806	991df932-0fc9-4a7b-898d-c7334bf368d8-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/991df932-0fc9-4a7b-898d-c7334bf368d8-anamnesis-signed.pdf	155956	application/pdf	document	{}	2025-10-18 12:18:57.994522+00	2025-10-18 12:18:57.994524+00	dd61dd98-734c-4096-b5d4-d908848c0b9c	5e113a13-25ab-4812-acc2-0c675ac8b791	991df932-0fc9-4a7b-898d-c7334bf368d8	\N
e4a5b807-434a-4954-8e75-f21b4558f243	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.pdf	prescription.pdf	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760723806285-prescription.pdf	35658	application/pdf	prescription	{}	2025-10-17 17:56:47.294194+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
6677131e-1722-49df-931f-2298438af211	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760723438719-prescription.jpg	139740	image/jpeg	prescription	{}	2025-10-17 17:50:40.584286+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
94c0ce8a-24c9-4e71-93fe-991e0249cbd5	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.pdf	prescription.pdf	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760646004232-prescription.pdf	168878	application/pdf	prescription	{}	2025-10-16 20:20:06.365616+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
f19c6746-bed4-4274-a496-67906c1443d2	0749f1d5-821e-44d2-838e-fdd4a47bd207-prescription-signed.pdf	receita_patient_4915158832107_20251013_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/0749f1d5-821e-44d2-838e-fdd4a47bd207-prescription-signed.pdf	168956	application/pdf	signed_document	{}	2025-10-13 12:00:59.460887+00	2025-10-16 17:01:47.920551+00	be6233b6-7d1e-434a-bc01-7427e3fee7c7	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
f10adbe2-0d87-489f-b2f2-38a784801ffe	94773a23-8323-4f4d-8640-1f0c8a385303-prescription-signed.pdf	receita_patient_4915158832107_20251013_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/94773a23-8323-4f4d-8640-1f0c8a385303-prescription-signed.pdf	169012	application/pdf	signed_document	{}	2025-10-13 12:39:57.33166+00	2025-10-16 17:01:47.92403+00	d47091b7-fb0e-4b7d-9f12-bcfd57630046	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
2c0f3f15-4269-4b40-9e32-05abab110692	94773a23-8323-4f4d-8640-1f0c8a385303-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/94773a23-8323-4f4d-8640-1f0c8a385303-anamnesis-signed.pdf	158415	application/pdf	document	{}	2025-10-13 12:39:57.979113+00	2025-10-16 17:01:47.92403+00	d47091b7-fb0e-4b7d-9f12-bcfd57630046	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
6938803c-281f-4780-b301-7a86bc047dd3	90924de9-0cd7-40ef-adad-7ccce455c174-prescription-signed.pdf	receita_patient_4915158832107_20251013_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/90924de9-0cd7-40ef-adad-7ccce455c174-prescription-signed.pdf	158562	application/pdf	signed_document	{}	2025-10-13 13:27:10.486827+00	2025-10-16 17:01:47.931218+00	310c538e-224e-4501-b87d-a3fde2f72dc6	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
78edb3a6-2403-4de6-8456-095d7accf1de	90924de9-0cd7-40ef-adad-7ccce455c174-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/90924de9-0cd7-40ef-adad-7ccce455c174-anamnesis-signed.pdf	168868	application/pdf	document	{}	2025-10-13 13:27:11.204569+00	2025-10-16 17:01:47.931218+00	310c538e-224e-4501-b87d-a3fde2f72dc6	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
b91be7dd-b152-47fa-89e0-57dd79a16235	04f864ad-31ff-4cec-a40a-0c756ab31340-anamnesis.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/04f864ad-31ff-4cec-a40a-0c756ab31340-anamnesis.pdf	49153	application/pdf	document	{}	2025-10-13 11:30:44.44063+00	2025-10-16 17:01:47.918718+00	6aa75d57-6919-4115-93c1-7d3d61abe96d	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
067bd22d-634b-487c-9517-8308fd6167cf	0749f1d5-821e-44d2-838e-fdd4a47bd207-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/0749f1d5-821e-44d2-838e-fdd4a47bd207-anamnesis-signed.pdf	158811	application/pdf	document	{}	2025-10-13 12:01:00.259897+00	2025-10-16 17:01:47.920551+00	be6233b6-7d1e-434a-bc01-7427e3fee7c7	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
7651d0d2-1afe-4aa7-9e9c-81f8e8cab5ea	87dd023d-f55e-49bb-b39d-3068317d8af9-prescription.jpg	prescription.jpg	prescriptions/87dd023d-f55e-49bb-b39d-3068317d8af9/1760388752019-prescription.jpg	355052	image/jpeg	prescription	{}	2025-10-13 20:52:35.077757+00	2025-10-16 20:18:53.810536+00	\N	5b2ef3ab-f157-47c6-93bf-abe334860192	\N	\N
f9777b3f-0fe6-4e00-834d-53f5e7d20191	1ae19bb2-d94c-4e3a-add3-d16abf3ad355-prescription-signed.pdf	receita_patient_4915158832107_20251013_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/1ae19bb2-d94c-4e3a-add3-d16abf3ad355-prescription-signed.pdf	168878	application/pdf	signed_document	{}	2025-10-13 13:37:36.452392+00	2025-10-16 17:01:47.934419+00	f73a7744-62be-4761-a30c-79e0e8a3f365	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
26fcf3ea-7cf0-4f9e-9f7b-3dc6cfea2f88	1ae19bb2-d94c-4e3a-add3-d16abf3ad355-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/1ae19bb2-d94c-4e3a-add3-d16abf3ad355-anamnesis-signed.pdf	158415	application/pdf	document	{}	2025-10-13 13:37:37.233734+00	2025-10-16 17:01:47.934419+00	f73a7744-62be-4761-a30c-79e0e8a3f365	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
7967baab-5682-412c-9413-193e47b4b16c	87dd023d-f55e-49bb-b39d-3068317d8af9-prescription.png	prescription.png	prescriptions/87dd023d-f55e-49bb-b39d-3068317d8af9/1760387850493-prescription.png	87618	image/png	prescription	{}	2025-10-13 20:37:31.106614+00	2025-10-16 20:18:53.810536+00	\N	5b2ef3ab-f157-47c6-93bf-abe334860192	\N	\N
8d2dc9de-13b0-4ca6-a6f5-386d3cacb8d5	11e814e4-717f-4706-80bf-537086eaa52d-prescription-signed.pdf	receita_maryellen_hallen_pereira_santos_20251013_signed.pdf	patients/50b9da75-b20a-460e-994b-44e3036a23e4/documents/11e814e4-717f-4706-80bf-537086eaa52d-prescription-signed.pdf	167740	application/pdf	signed_document	{}	2025-10-13 20:20:45.227334+00	2025-10-16 17:01:47.938089+00	643df50a-877b-4d62-ab0d-b219c55764dc	50b9da75-b20a-460e-994b-44e3036a23e4	\N	\N
07455a01-8b1d-44e9-9541-21ac30aab250	11e814e4-717f-4706-80bf-537086eaa52d-anamnesis-signed.pdf	anamnesis_50b9da75-b20a-460e-994b-44e3036a23e4_signed.pdf	patients/50b9da75-b20a-460e-994b-44e3036a23e4/documents/11e814e4-717f-4706-80bf-537086eaa52d-anamnesis-signed.pdf	157623	application/pdf	document	{}	2025-10-13 20:20:46.426662+00	2025-10-16 17:01:47.938089+00	643df50a-877b-4d62-ab0d-b219c55764dc	50b9da75-b20a-460e-994b-44e3036a23e4	\N	\N
f6ed7549-ca0f-40d3-99b8-e9d37a41b64b	6694bb8f-332a-4c18-b89d-c551b625b46b-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/6694bb8f-332a-4c18-b89d-c551b625b46b-anamnesis-signed.pdf	157588	application/pdf	document	{}	2025-10-14 00:45:59.692075+00	2025-10-16 17:01:47.947016+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
17b8920a-d35b-4c24-bd14-f65660e4d6bf	64878ac6-2d21-452b-a203-4c918397c9d0-anamnesis-signed.pdf	anamnesis_eb0656f3-6b57-4c59-9e79-e27e5dcb16d8_signed.pdf	patients/eb0656f3-6b57-4c59-9e79-e27e5dcb16d8/documents/64878ac6-2d21-452b-a203-4c918397c9d0-anamnesis-signed.pdf	158508	application/pdf	document	{}	2025-10-14 00:50:23.961159+00	2025-10-16 17:01:47.94819+00	168125d4-1c2e-47af-82ea-9851ddcc9a9a	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	\N	\N
c9db5f48-3bf9-4569-bd10-2706b0c67eab	0e58eb0b-4962-4f50-ab3f-f81bcd0f4607-prescription.jpg	prescription.jpg	prescriptions/0e58eb0b-4962-4f50-ab3f-f81bcd0f4607/1760361998905-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-13 13:26:40.55521+00	2025-10-16 20:18:53.824259+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
513733f2-ba1e-4bee-8900-38b74169e94f	d140430e-c6b4-4cb4-91bb-b10d276c5958-anamnesis-signed.pdf	anamnesis_3eec1f34-8a20-4d2b-9511-6a6810dd7edd_signed.pdf	patients/3eec1f34-8a20-4d2b-9511-6a6810dd7edd/documents/d140430e-c6b4-4cb4-91bb-b10d276c5958-anamnesis-signed.pdf	157778	application/pdf	document	{}	2025-10-14 09:24:21.127477+00	2025-10-16 17:01:47.95401+00	bcfe23ce-c8d6-45e0-a8b7-935db0f4d76a	3eec1f34-8a20-4d2b-9511-6a6810dd7edd	\N	\N
b35ac08c-919d-467f-b2cf-622a5401bd19	350a605f-a655-444f-b96a-bc3bb07a59cc-anamnesis-signed.pdf	anamnesis_50b9da75-b20a-460e-994b-44e3036a23e4_signed.pdf	patients/50b9da75-b20a-460e-994b-44e3036a23e4/documents/350a605f-a655-444f-b96a-bc3bb07a59cc-anamnesis-signed.pdf	157502	application/pdf	document	{}	2025-10-14 12:46:51.233241+00	2025-10-16 17:01:47.956188+00	78ecd0db-d8b0-453f-b7b3-8fca939e194b	50b9da75-b20a-460e-994b-44e3036a23e4	\N	\N
fc4462d7-abd3-4119-b26c-d0c26df61169	0e58eb0b-4962-4f50-ab3f-f81bcd0f4607-prescription.jpg	prescription.jpg	prescriptions/0e58eb0b-4962-4f50-ab3f-f81bcd0f4607/1760360824477-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-13 13:07:06.201323+00	2025-10-16 20:18:53.824259+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
446bb0b3-7d7d-484a-8994-6d7d48b1e7b1	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.jpg	prescription.jpg	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760642374972-prescription.jpg	276748	image/jpeg	prescription	{}	2025-10-16 19:19:37.95707+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
bc03a0a6-4586-43c0-be1f-c5eec8a6febf	6216eb73-036c-4ac0-9605-4f42fe675fcb-prescription.jpg	prescription.jpg	prescriptions/6216eb73-036c-4ac0-9605-4f42fe675fcb/1760455175894-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-14 15:19:37.157487+00	2025-10-16 20:18:53.8675+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
bb26e59d-ecf6-42a7-af92-9107d68eeddc	681f44c5-d60a-401e-8dba-aafca662b7f6-prescription-signed.pdf	receita_patient_4915158832107_20251019_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/681f44c5-d60a-401e-8dba-aafca662b7f6-prescription-signed.pdf	168040	application/pdf	signed_document	{}	2025-10-19 11:14:02.863627+00	2025-10-19 11:14:02.86363+00	08c27ba4-76b6-4a33-9d8c-0a05328d479a	5e113a13-25ab-4812-acc2-0c675ac8b791	681f44c5-d60a-401e-8dba-aafca662b7f6	\N
9310ec69-1188-4f17-8111-5554bd03afdb	247ede61-5b83-4c09-89a3-54db99807db5-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/247ede61-5b83-4c09-89a3-54db99807db5-anamnesis-signed.pdf	156618	application/pdf	document	{}	2025-10-20 19:38:06.727533+00	2025-10-20 19:38:06.727535+00	18dcda57-8888-41ad-97a5-5367e4eaf87b	5e113a13-25ab-4812-acc2-0c675ac8b791	247ede61-5b83-4c09-89a3-54db99807db5	\N
07bc7853-2231-4a8b-ae24-eb85944e8fee	a6b3d64d-e0a9-4458-a169-4530bdee4139-prescription.jpg	prescription.jpg	prescriptions/a6b3d64d-e0a9-4458-a169-4530bdee4139/1760295779686-prescription.jpg	355052	image/jpeg	prescription	{}	2025-10-12 19:03:02.177444+00	2025-10-16 20:18:53.803977+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
d8d304ad-06b5-495f-971a-251695688ba8	87dd023d-f55e-49bb-b39d-3068317d8af9-prescription.jpg	prescription.jpg	prescriptions/87dd023d-f55e-49bb-b39d-3068317d8af9/1760388888623-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-13 20:54:49.747438+00	2025-10-16 20:18:53.810536+00	\N	5b2ef3ab-f157-47c6-93bf-abe334860192	\N	\N
6aaeb17f-b10f-4663-95a1-b96ec5135698	5a4ce661-35d7-43ce-a1ac-8059ad4efe45-prescription.jpg	prescription.jpg	prescriptions/5a4ce661-35d7-43ce-a1ac-8059ad4efe45/1760458382729-prescription.jpg	135176	image/jpeg	prescription	{}	2025-10-14 16:13:04.031399+00	2025-10-16 20:18:53.82557+00	\N	d7735997-acf6-4269-85cc-0eb205ae8fcf	\N	\N
57f5d8d9-8aae-4def-bc94-ae743fc76040	5a4ce661-35d7-43ce-a1ac-8059ad4efe45-prescription.jpg	prescription.jpg	prescriptions/5a4ce661-35d7-43ce-a1ac-8059ad4efe45/1760458173837-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-14 16:09:35.135132+00	2025-10-16 20:18:53.82557+00	\N	d7735997-acf6-4269-85cc-0eb205ae8fcf	\N	\N
3f6be1f2-73e3-4f0f-8a36-ca3bad754ac6	2c66721f-38e4-49d9-814f-1f206c3ce765-prescription.jpg	prescription.jpg	prescriptions/2c66721f-38e4-49d9-814f-1f206c3ce765/1760381361219-prescription.jpg	252138	image/jpeg	prescription	{}	2025-10-13 18:49:23.287019+00	2025-10-16 20:18:53.834527+00	\N	50b9da75-b20a-460e-994b-44e3036a23e4	\N	\N
6e5540b5-f698-4340-89ad-19dcf7bfbfcd	2c66721f-38e4-49d9-814f-1f206c3ce765-prescription.jpg	prescription.jpg	prescriptions/2c66721f-38e4-49d9-814f-1f206c3ce765/1760367644800-prescription.jpg	204015	image/jpeg	prescription	{}	2025-10-13 15:00:46.303183+00	2025-10-16 20:18:53.834527+00	\N	50b9da75-b20a-460e-994b-44e3036a23e4	\N	\N
e1437545-4eba-43c7-aefe-c330daa51a6a	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.jpg	prescription.jpg	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760642471392-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-16 19:21:15.77353+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
20461cb8-ad25-4a19-a8c8-854ae5c109db	681f44c5-d60a-401e-8dba-aafca662b7f6-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/681f44c5-d60a-401e-8dba-aafca662b7f6-anamnesis-signed.pdf	155951	application/pdf	document	{}	2025-10-19 11:14:03.772876+00	2025-10-19 11:14:03.772879+00	08c27ba4-76b6-4a33-9d8c-0a05328d479a	5e113a13-25ab-4812-acc2-0c675ac8b791	681f44c5-d60a-401e-8dba-aafca662b7f6	\N
70891533-f0e6-4744-bd8f-d414595db4eb	d312fd6c-c450-47bf-a4e3-5b2c0e56a6ce-prescription-signed.pdf	receita_patient_4915158832107_20251017_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/d312fd6c-c450-47bf-a4e3-5b2c0e56a6ce-prescription-signed.pdf	167314	application/pdf	signed_document	{}	2025-10-17 23:24:25.149944+00	2025-10-17 23:24:25.149947+00	2627240b-22d8-4d15-a72f-6c47fce38886	5e113a13-25ab-4812-acc2-0c675ac8b791	d312fd6c-c450-47bf-a4e3-5b2c0e56a6ce	\N
24137e7b-1d3b-4b2f-b29f-25195c7d8ca8	65c3d4c0-b719-49f8-bd47-bac334142b26-prescription-signed.pdf	receita_patient_4915158832107_20251020_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/65c3d4c0-b719-49f8-bd47-bac334142b26-prescription-signed.pdf	169038	application/pdf	signed_document	{}	2025-10-20 22:47:07.515674+00	2025-10-20 22:47:07.515676+00	24d3c1ec-9878-48e9-bd0c-51ce72bda145	5e113a13-25ab-4812-acc2-0c675ac8b791	65c3d4c0-b719-49f8-bd47-bac334142b26	\N
3d86eb49-3eaf-4908-b56a-3a2daf1aa403	4e99b9e4-b495-4ffb-8da2-8678be243639-prescription.jpg	prescription.jpg	prescriptions/4e99b9e4-b495-4ffb-8da2-8678be243639/1761008581393-prescription.jpg	122358	image/jpeg	prescription	{}	2025-10-21 01:03:02.654257+00	2025-10-21 01:09:37.252272+00	\N	a6fe8ce5-c9a9-4f1e-a698-c7d834256762	958b0af9-7ab0-4317-bcf6-02a06a4c1e18	4e99b9e4-b495-4ffb-8da2-8678be243639
46cf7766-5c2c-4253-9f95-8b7e43254feb	958b0af9-7ab0-4317-bcf6-02a06a4c1e18-prescription-signed.pdf	receita_fabio_luis_marques_da_silva_20251021_signed.pdf	patients/a6fe8ce5-c9a9-4f1e-a698-c7d834256762/documents/958b0af9-7ab0-4317-bcf6-02a06a4c1e18-prescription-signed.pdf	170517	application/pdf	signed_document	{}	2025-10-21 01:12:13.034921+00	2025-10-21 01:12:13.034923+00	4c0e7986-b897-4236-bf4f-76218c82383f	a6fe8ce5-c9a9-4f1e-a698-c7d834256762	958b0af9-7ab0-4317-bcf6-02a06a4c1e18	\N
7ba93cb1-99c2-4096-a882-3a29a2aab9cb	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760787873179-prescription.jpg	276748	image/jpeg	prescription	{}	2025-10-18 11:44:35.377751+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
0a7d6d89-730e-4360-86f4-c4328aeb3374	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760725328654-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-17 18:22:10.252122+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
bb724fb1-e7fe-4061-aefa-cb43af7862fe	fbf39f31-647a-46a1-9845-6e8f85c04ed3-anamnesis-signed.pdf	anamnesis_a6fe8ce5-c9a9-4f1e-a698-c7d834256762_signed.pdf	patients/a6fe8ce5-c9a9-4f1e-a698-c7d834256762/documents/fbf39f31-647a-46a1-9845-6e8f85c04ed3-anamnesis-signed.pdf	158460	application/pdf	document	{}	2025-10-21 01:22:00.941781+00	2025-10-21 01:22:00.941784+00	\N	a6fe8ce5-c9a9-4f1e-a698-c7d834256762	fbf39f31-647a-46a1-9845-6e8f85c04ed3	\N
bdd42825-d79d-4d81-a6ec-2474bc9da8d0	6a2328e2-c454-40fc-b503-cdf03af00910-prescription.jpg	prescription.jpg	prescriptions/6a2328e2-c454-40fc-b503-cdf03af00910/1761046398741-prescription.jpg	137761	image/jpeg	prescription	{}	2025-10-21 11:33:20.248707+00	2025-10-21 11:33:20.24871+00	\N	0c89a6ff-6598-400e-affb-47ccc3979761	\N	6a2328e2-c454-40fc-b503-cdf03af00910
4d785b6a-f82f-4e2e-a2d3-56476e1853e6	48b2f584-e6d7-4b34-a642-8b3ac85ee3de-prescription-signed.pdf	receita_o_impostor_20251021_signed.pdf	patients/f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0/documents/48b2f584-e6d7-4b34-a642-8b3ac85ee3de-prescription-signed.pdf	167132	application/pdf	signed_document	{}	2025-10-21 12:22:49.552508+00	2025-10-21 12:22:49.552511+00	b56b5ad1-4cae-41fd-89ce-a1dfa8535e7a	f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0	48b2f584-e6d7-4b34-a642-8b3ac85ee3de	\N
6a61e44f-63ea-4378-ac69-af2311c30a5c	787c74e7-c2cd-4592-a409-99432a68a0a8-prescription-signed.pdf	receita_heitor_éttori_20251013_signed.pdf	patients/eb0656f3-6b57-4c59-9e79-e27e5dcb16d8/documents/787c74e7-c2cd-4592-a409-99432a68a0a8-prescription-signed.pdf	168539	application/pdf	signed_document	{}	2025-10-13 21:10:50.236933+00	2025-10-16 17:01:47.941365+00	b2bf577c-b8d7-4cbc-99ee-2bbe3bd30bd3	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	\N	\N
9452fcf7-d0b6-46d0-aa06-63bd99abf71a	787c74e7-c2cd-4592-a409-99432a68a0a8-anamnesis-signed.pdf	anamnesis_eb0656f3-6b57-4c59-9e79-e27e5dcb16d8_signed.pdf	patients/eb0656f3-6b57-4c59-9e79-e27e5dcb16d8/documents/787c74e7-c2cd-4592-a409-99432a68a0a8-anamnesis-signed.pdf	158637	application/pdf	document	{}	2025-10-13 21:10:51.01723+00	2025-10-16 17:01:47.941365+00	b2bf577c-b8d7-4cbc-99ee-2bbe3bd30bd3	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	\N	\N
a7113788-6bfe-4bbf-af52-8ac432d5eb55	50741f2c-6c1f-4b33-9e18-89f60c23fb86-prescription-signed.pdf	receita_patient_4915158832107_20251013_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/50741f2c-6c1f-4b33-9e18-89f60c23fb86-prescription-signed.pdf	168587	application/pdf	signed_document	{}	2025-10-13 22:29:14.130661+00	2025-10-16 17:01:47.943254+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
0e08306a-91a8-48b9-9412-6155124b9f84	50741f2c-6c1f-4b33-9e18-89f60c23fb86-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/50741f2c-6c1f-4b33-9e18-89f60c23fb86-anamnesis-signed.pdf	158416	application/pdf	document	{}	2025-10-13 22:29:14.931522+00	2025-10-16 17:01:47.943254+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
c7da0f23-7279-463e-97b0-d3bec02fcd5f	6b9c107a-acf8-4efd-a6da-9ddb8387adc0-prescription-signed.pdf	receita_maryellen_hallen_pereira_santos_20251013_signed.pdf	patients/50b9da75-b20a-460e-994b-44e3036a23e4/documents/6b9c107a-acf8-4efd-a6da-9ddb8387adc0-prescription-signed.pdf	168122	application/pdf	signed_document	{}	2025-10-13 22:29:55.291964+00	2025-10-16 17:01:47.94439+00	\N	50b9da75-b20a-460e-994b-44e3036a23e4	\N	\N
f1f83f6e-21e3-43bd-8936-b35335407c05	6b9c107a-acf8-4efd-a6da-9ddb8387adc0-anamnesis-signed.pdf	anamnesis_50b9da75-b20a-460e-994b-44e3036a23e4_signed.pdf	patients/50b9da75-b20a-460e-994b-44e3036a23e4/documents/6b9c107a-acf8-4efd-a6da-9ddb8387adc0-anamnesis-signed.pdf	157580	application/pdf	document	{}	2025-10-13 22:29:56.085018+00	2025-10-16 17:01:47.94439+00	\N	50b9da75-b20a-460e-994b-44e3036a23e4	\N	\N
73a35085-7aad-4447-ab62-4187e2c77986	6694bb8f-332a-4c18-b89d-c551b625b46b-prescription-signed.pdf	receita_patient_4915158832107_20251014_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/6694bb8f-332a-4c18-b89d-c551b625b46b-prescription-signed.pdf	168747	application/pdf	signed_document	{}	2025-10-14 00:45:59.051998+00	2025-10-16 17:01:47.947016+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
abce16c0-799f-47a1-a024-61fc74bc318a	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.jpg	prescription.jpg	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760644898431-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-16 20:01:40.350917+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
cb513b07-e1a9-4c63-844c-4d796de5d2ba	18ace5f4-1f1e-48cc-a561-0ab8feb380b8-prescription.jpg	prescription.jpg	prescriptions/18ace5f4-1f1e-48cc-a561-0ab8feb380b8/1760392458781-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-13 21:54:20.450146+00	2025-10-16 20:18:53.850592+00	\N	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	\N	\N
423118e4-b637-406c-abc9-d4f7549356bc	18ace5f4-1f1e-48cc-a561-0ab8feb380b8-prescription.jpg	prescription.jpg	prescriptions/18ace5f4-1f1e-48cc-a561-0ab8feb380b8/1760389431602-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-13 21:03:53.175555+00	2025-10-16 20:18:53.850592+00	\N	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	\N	\N
b1137a55-85e7-4c0f-a921-6f1d362b9a20	d312fd6c-c450-47bf-a4e3-5b2c0e56a6ce-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/d312fd6c-c450-47bf-a4e3-5b2c0e56a6ce-anamnesis-signed.pdf	155563	application/pdf	document	{}	2025-10-17 23:24:26.031915+00	2025-10-17 23:24:26.031918+00	2627240b-22d8-4d15-a72f-6c47fce38886	5e113a13-25ab-4812-acc2-0c675ac8b791	d312fd6c-c450-47bf-a4e3-5b2c0e56a6ce	\N
1d1a6f28-2b3d-4302-aa62-6912848e1517	57850979-268b-49e4-92fc-014000339589-prescription-signed.pdf	receita_patient_4915158832107_20251018_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/57850979-268b-49e4-92fc-014000339589-prescription-signed.pdf	168429	application/pdf	signed_document	{}	2025-10-18 11:45:26.981759+00	2025-10-18 11:45:26.981762+00	1297a487-e0f3-44c1-bee8-db989664376b	5e113a13-25ab-4812-acc2-0c675ac8b791	57850979-268b-49e4-92fc-014000339589	\N
7c14c905-5062-4e04-890f-5d18fad71969	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.pdf	prescription.pdf	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760878237346-prescription.pdf	167375	application/pdf	prescription	{}	2025-10-19 12:50:39.188967+00	2025-10-20 11:05:50.653076+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	40c941cc-e135-4acf-ab4a-5b050228a258	37c7666e-0b22-47ba-b4d2-78cf431ad8de
3d3a93a9-38a6-4b27-9525-a22ee1697206	65c3d4c0-b719-49f8-bd47-bac334142b26-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/65c3d4c0-b719-49f8-bd47-bac334142b26-anamnesis-signed.pdf	157415	application/pdf	document	{}	2025-10-20 22:47:08.231801+00	2025-10-20 22:47:08.231803+00	24d3c1ec-9878-48e9-bd0c-51ce72bda145	5e113a13-25ab-4812-acc2-0c675ac8b791	65c3d4c0-b719-49f8-bd47-bac334142b26	\N
30f394fb-8ee5-4c96-99f4-843a173e4dfd	958b0af9-7ab0-4317-bcf6-02a06a4c1e18-anamnesis-signed.pdf	anamnesis_a6fe8ce5-c9a9-4f1e-a698-c7d834256762_signed.pdf	patients/a6fe8ce5-c9a9-4f1e-a698-c7d834256762/documents/958b0af9-7ab0-4317-bcf6-02a06a4c1e18-anamnesis-signed.pdf	158621	application/pdf	document	{}	2025-10-21 01:12:13.780716+00	2025-10-21 01:12:13.780719+00	4c0e7986-b897-4236-bf4f-76218c82383f	a6fe8ce5-c9a9-4f1e-a698-c7d834256762	958b0af9-7ab0-4317-bcf6-02a06a4c1e18	\N
5f4e2cc6-7249-4d50-8389-535eecfe7048	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760736461313-prescription.jpg	139740	image/jpeg	prescription	{}	2025-10-17 21:27:43.11839+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
95698b3e-9f43-42a9-8add-571ffc3bf48d	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760724617451-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-17 18:10:19.104354+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
70583bd2-cf11-4f0c-a8fa-482dd86de82c	925fa162-374d-4176-a085-74228abe40e4-anamnesis-signed.pdf	anamnesis_2b635923-f6c4-435a-9054-156c2113888f_signed.pdf	patients/2b635923-f6c4-435a-9054-156c2113888f/documents/925fa162-374d-4176-a085-74228abe40e4-anamnesis-signed.pdf	156809	application/pdf	document	{}	2025-10-21 10:48:40.249269+00	2025-10-21 10:48:40.249272+00	50aa6b31-ecc5-4955-9a1b-8ef2248a8e81	2b635923-f6c4-435a-9054-156c2113888f	925fa162-374d-4176-a085-74228abe40e4	\N
5b1d04c6-82f9-4fcd-9aab-32e371e0b318	8c24707f-820f-40b4-a019-4f45ff7aca69-prescription.jpg	prescription.jpg	prescriptions/8c24707f-820f-40b4-a019-4f45ff7aca69/1760445012040-prescription.jpg	262901	image/jpeg	prescription	{}	2025-10-14 12:30:14.065625+00	2025-10-16 20:18:53.813629+00	\N	47ec77d4-b2fd-49be-9d64-4db12563c89c	\N	\N
9f7f9582-34cf-4c9d-baa8-096cfa03f226	8d990a75-e820-4975-ba51-e7d18d8ea70f-prescription.jpg	prescription.jpg	prescriptions/8d990a75-e820-4975-ba51-e7d18d8ea70f/1760445152458-prescription.jpg	262901	image/jpeg	prescription	{}	2025-10-14 12:32:34.260178+00	2025-10-16 20:18:53.815398+00	\N	50b9da75-b20a-460e-994b-44e3036a23e4	\N	\N
d0242a5e-b332-4bdf-b2db-eb93d671a09e	2c66721f-38e4-49d9-814f-1f206c3ce765-prescription.jpg	prescription.jpg	prescriptions/2c66721f-38e4-49d9-814f-1f206c3ce765/1760403550922-prescription.jpg	262901	image/jpeg	prescription	{}	2025-10-14 00:59:12.673727+00	2025-10-16 20:18:53.834527+00	\N	50b9da75-b20a-460e-994b-44e3036a23e4	\N	\N
bf81356d-de89-4e12-b540-cd46b7d061ab	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.jpg	prescription.jpg	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760645614856-prescription.jpg	139740	image/jpeg	prescription	{}	2025-10-16 20:13:37.210857+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
072690fc-6a34-457f-b449-56e88c2824bb	45944609-7422-4a20-97db-b87d49c81fb6-prescription.jpg	prescription.jpg	prescriptions/45944609-7422-4a20-97db-b87d49c81fb6/1760433406021-prescription.jpg	175570	image/jpeg	prescription	{}	2025-10-14 09:16:47.729122+00	2025-10-16 20:18:53.843261+00	\N	3eec1f34-8a20-4d2b-9511-6a6810dd7edd	\N	\N
2b80e53f-8105-405f-b394-7ff23b785ed3	31e2c6db-6ce6-4e7a-a758-07caa7064647-prescription.jpg	prescription.jpg	prescriptions/31e2c6db-6ce6-4e7a-a758-07caa7064647/1760443332743-prescription.jpg	262901	image/jpeg	prescription	{}	2025-10-14 12:02:14.590451+00	2025-10-16 20:18:53.844896+00	\N	f30c2c82-0080-46dc-b2dc-7e95200b52b9	\N	\N
40b81b89-6629-48b4-ac14-ad2747e2ef7b	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.pdf	prescription.pdf	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760872196168-prescription.pdf	167375	application/pdf	prescription	{}	2025-10-19 11:09:57.895721+00	2025-10-20 11:05:50.654712+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	40c941cc-e135-4acf-ab4a-5b050228a258	37c7666e-0b22-47ba-b4d2-78cf431ad8de
8b39da8a-1c3a-4899-a5b1-8811527c0da7	d4480946-6a17-4ade-a394-26c5d4e1f968-prescription-signed.pdf	receita_patient_4915158832107_20251017_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/d4480946-6a17-4ade-a394-26c5d4e1f968-prescription-signed.pdf	166925	application/pdf	signed_document	{}	2025-10-17 23:30:40.280697+00	2025-10-17 23:30:40.2807+00	052d8794-9fd4-4b12-aee4-d33c48553b51	5e113a13-25ab-4812-acc2-0c675ac8b791	d4480946-6a17-4ade-a394-26c5d4e1f968	\N
a572731a-3c54-4501-9a82-e1781fd7b3e1	60f673f9-2880-4b33-a422-447520fbeacc-prescription.jpg	prescription.jpg	prescriptions/60f673f9-2880-4b33-a422-447520fbeacc/1761001295736-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-20 23:01:37.073477+00	2025-10-20 23:03:44.141697+00	\N	75ffc611-f82c-43cf-bf3e-bbf75123b7aa	9217ba7f-e064-4eb4-9919-679fb4e3a951	60f673f9-2880-4b33-a422-447520fbeacc
acbff725-d7ea-4601-b226-46e9a50f82ff	64878ac6-2d21-452b-a203-4c918397c9d0-prescription-signed.pdf	receita_heitor_éttori_20251014_signed.pdf	patients/eb0656f3-6b57-4c59-9e79-e27e5dcb16d8/documents/64878ac6-2d21-452b-a203-4c918397c9d0-prescription-signed.pdf	168710	application/pdf	signed_document	{}	2025-10-14 00:50:23.104712+00	2025-10-16 17:01:47.94819+00	168125d4-1c2e-47af-82ea-9851ddcc9a9a	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	\N	\N
07f9562f-7f9e-4668-b6ee-24398b7d92cd	ea0b39e7-355f-4ed9-ac2b-3aef4fe20e54-prescription-signed.pdf	receita_patient_4915158832107_20251014_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/ea0b39e7-355f-4ed9-ac2b-3aef4fe20e54-prescription-signed.pdf	168650	application/pdf	signed_document	{}	2025-10-14 00:50:42.590092+00	2025-10-16 17:01:47.950089+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
fc4c7a7b-5b8d-4b14-a437-328b9e1f19f8	ea0b39e7-355f-4ed9-ac2b-3aef4fe20e54-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/ea0b39e7-355f-4ed9-ac2b-3aef4fe20e54-anamnesis-signed.pdf	157637	application/pdf	document	{}	2025-10-14 00:50:45.57301+00	2025-10-16 17:01:47.950089+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
ded4190e-c5e6-4f81-a1ae-986d2ea6fb44	4b2f37af-de67-45b1-9cab-e44e3b7135ed-prescription-signed.pdf	receita_maryellen_hallen_pereira_santos_20251014_signed.pdf	patients/47ec77d4-b2fd-49be-9d64-4db12563c89c/documents/4b2f37af-de67-45b1-9cab-e44e3b7135ed-prescription-signed.pdf	167375	application/pdf	signed_document	{}	2025-10-14 00:50:46.685104+00	2025-10-16 17:01:47.951166+00	\N	47ec77d4-b2fd-49be-9d64-4db12563c89c	\N	\N
e14fea0e-e31b-44f5-9aa1-bf6b96738f35	4b2f37af-de67-45b1-9cab-e44e3b7135ed-anamnesis-signed.pdf	anamnesis_47ec77d4-b2fd-49be-9d64-4db12563c89c_signed.pdf	patients/47ec77d4-b2fd-49be-9d64-4db12563c89c/documents/4b2f37af-de67-45b1-9cab-e44e3b7135ed-anamnesis-signed.pdf	157600	application/pdf	document	{}	2025-10-14 00:50:47.652897+00	2025-10-16 17:01:47.951166+00	\N	47ec77d4-b2fd-49be-9d64-4db12563c89c	\N	\N
dc120c91-1bfd-4d1e-b5ab-bafdc85ef953	d140430e-c6b4-4cb4-91bb-b10d276c5958-prescription-signed.pdf	receita_antonio_lopes_20251014_signed.pdf	patients/3eec1f34-8a20-4d2b-9511-6a6810dd7edd/documents/d140430e-c6b4-4cb4-91bb-b10d276c5958-prescription-signed.pdf	167303	application/pdf	signed_document	{}	2025-10-14 09:24:20.241687+00	2025-10-16 17:01:47.95401+00	bcfe23ce-c8d6-45e0-a8b7-935db0f4d76a	3eec1f34-8a20-4d2b-9511-6a6810dd7edd	\N	\N
4a3d9873-5680-4f74-a77e-961f53704688	350a605f-a655-444f-b96a-bc3bb07a59cc-prescription-signed.pdf	receita_maryellen_hallen_pereira_santos_20251014_signed.pdf	patients/50b9da75-b20a-460e-994b-44e3036a23e4/documents/350a605f-a655-444f-b96a-bc3bb07a59cc-prescription-signed.pdf	168193	application/pdf	signed_document	{}	2025-10-14 12:46:50.449658+00	2025-10-16 17:01:47.956188+00	78ecd0db-d8b0-453f-b7b3-8fca939e194b	50b9da75-b20a-460e-994b-44e3036a23e4	\N	\N
78a1a3fe-431f-4f53-8855-2529cc6bd380	4ccee2e3-36b5-4104-a3fe-46c6dc1a8ed5-prescription-signed.pdf	receita_leodir_de_abreu_miloch_20251014_signed.pdf	patients/f30c2c82-0080-46dc-b2dc-7e95200b52b9/documents/4ccee2e3-36b5-4104-a3fe-46c6dc1a8ed5-prescription-signed.pdf	167884	application/pdf	signed_document	{}	2025-10-14 12:20:14.14479+00	2025-10-16 17:01:47.957304+00	2d475f75-b30c-4740-848f-f6d1c5218926	f30c2c82-0080-46dc-b2dc-7e95200b52b9	\N	\N
331fc53b-0705-4f94-9800-a37d7d61d28c	4ccee2e3-36b5-4104-a3fe-46c6dc1a8ed5-anamnesis-signed.pdf	anamnesis_f30c2c82-0080-46dc-b2dc-7e95200b52b9_signed.pdf	patients/f30c2c82-0080-46dc-b2dc-7e95200b52b9/documents/4ccee2e3-36b5-4104-a3fe-46c6dc1a8ed5-anamnesis-signed.pdf	157950	application/pdf	document	{}	2025-10-14 12:20:14.946649+00	2025-10-16 17:01:47.957304+00	2d475f75-b30c-4740-848f-f6d1c5218926	f30c2c82-0080-46dc-b2dc-7e95200b52b9	\N	\N
5c546f88-b034-4341-90c3-5641f085f431	5a4ce661-35d7-43ce-a1ac-8059ad4efe45-prescription.pdf	prescription.pdf	prescriptions/5a4ce661-35d7-43ce-a1ac-8059ad4efe45/1760459780509-prescription.pdf	168747	application/pdf	prescription	{}	2025-10-14 16:36:22.10339+00	2025-10-16 20:18:53.82557+00	\N	d7735997-acf6-4269-85cc-0eb205ae8fcf	\N	\N
0280105d-781e-49d9-bc45-45ef3ff8cf48	5a4ce661-35d7-43ce-a1ac-8059ad4efe45-prescription.jpg	prescription.jpg	prescriptions/5a4ce661-35d7-43ce-a1ac-8059ad4efe45/1760459475703-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-14 16:31:16.982773+00	2025-10-16 20:18:53.82557+00	\N	d7735997-acf6-4269-85cc-0eb205ae8fcf	\N	\N
790d39bc-a4ad-4df4-90af-68c07ebc1bf1	d13e6377-fddc-425f-a9b9-8bd5baddee75-prescription.jpg	prescription.jpg	prescriptions/d13e6377-fddc-425f-a9b9-8bd5baddee75/1760453986014-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-14 14:59:47.297337+00	2025-10-16 20:18:53.828626+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
9a8bcfe8-be67-44f0-a6da-cb26ac719d21	f5648e46-1e84-417f-901e-d5eba04a384b-prescription.jpg	prescription.jpg	prescriptions/f5648e46-1e84-417f-901e-d5eba04a384b/1760454667421-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-14 15:11:09.282342+00	2025-10-16 20:18:53.831657+00	\N	63d47959-4742-460b-ae5a-5aeb982d4f91	\N	\N
7f284312-dc38-4f41-8b22-43b195e0d588	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.pdf	prescription.pdf	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760645783474-prescription.pdf	168747	application/pdf	prescription	{}	2025-10-16 20:16:25.8614+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
643a655b-8e34-4787-9a05-b02f5af89f92	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.pdf	prescription.pdf	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760525870418-prescription.pdf	168747	application/pdf	prescription	{}	2025-10-15 10:57:52.254354+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
9f0b6bfe-3ed6-4a40-9f8d-4a644e085244	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.pdf	prescription.pdf	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760521816117-prescription.pdf	168747	application/pdf	prescription	{}	2025-10-15 09:50:17.687469+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
48800df4-05e8-4016-a542-44bfbec2e8e7	5df0b46f-f22f-44fc-8141-4b08e53a4dc8-prescription.jpg	prescription.jpg	prescriptions/5df0b46f-f22f-44fc-8141-4b08e53a4dc8/1760457972700-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-14 16:06:14.142339+00	2025-10-16 20:18:53.857472+00	\N	9f1a1a92-64fe-436e-8e0a-da0a3712f384	\N	\N
3b002644-ace8-4781-8412-1c30a20968ff	5df0b46f-f22f-44fc-8141-4b08e53a4dc8-prescription.jpg	prescription.jpg	prescriptions/5df0b46f-f22f-44fc-8141-4b08e53a4dc8/1760457886468-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-14 16:04:47.911692+00	2025-10-16 20:18:53.857472+00	\N	9f1a1a92-64fe-436e-8e0a-da0a3712f384	\N	\N
6b7e335e-7b27-423d-a790-125eeec9d3d6	666e6c4a-1a1f-4950-891d-15d4d3424936-prescription.jpg	prescription.jpg	prescriptions/666e6c4a-1a1f-4950-891d-15d4d3424936/1760454096811-prescription.jpg	68957	image/jpeg	prescription	{}	2025-10-14 15:01:38.002482+00	2025-10-16 20:18:53.864716+00	\N	9ebedb19-4b94-459d-87b6-3937e1c5a022	\N	\N
34de536f-210d-4b85-8cbd-b75ab08581b3	6216eb73-036c-4ac0-9605-4f42fe675fcb-prescription.jpg	prescription.jpg	prescriptions/6216eb73-036c-4ac0-9605-4f42fe675fcb/1760456245291-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-14 15:37:26.715607+00	2025-10-16 20:18:53.8675+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
449e20ac-7138-42e3-9e0c-53cb33e97dba	6216eb73-036c-4ac0-9605-4f42fe675fcb-prescription.jpg	prescription.jpg	prescriptions/6216eb73-036c-4ac0-9605-4f42fe675fcb/1760455906341-prescription.jpg	521536	image/jpeg	prescription	{}	2025-10-14 15:31:49.193941+00	2025-10-16 20:18:53.8675+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
16e9234b-f054-4dda-998e-b7c59fe644bc	d4480946-6a17-4ade-a394-26c5d4e1f968-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/d4480946-6a17-4ade-a394-26c5d4e1f968-anamnesis-signed.pdf	155612	application/pdf	document	{}	2025-10-17 23:30:41.215361+00	2025-10-17 23:30:41.215364+00	052d8794-9fd4-4b12-aee4-d33c48553b51	5e113a13-25ab-4812-acc2-0c675ac8b791	d4480946-6a17-4ade-a394-26c5d4e1f968	\N
f50a5a83-8b84-43aa-9c51-cbdda2e3e874	57850979-268b-49e4-92fc-014000339589-anamnesis-signed.pdf	anamnesis_5e113a13-25ab-4812-acc2-0c675ac8b791_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/57850979-268b-49e4-92fc-014000339589-anamnesis-signed.pdf	155956	application/pdf	document	{}	2025-10-18 11:45:27.804133+00	2025-10-18 11:45:27.804135+00	1297a487-e0f3-44c1-bee8-db989664376b	5e113a13-25ab-4812-acc2-0c675ac8b791	57850979-268b-49e4-92fc-014000339589	\N
19351143-e5c4-4fa0-9135-ca34ba8bd139	f3577a3a-63c6-4d6f-972b-9344133af8db-prescription.pdf	prescription.pdf	prescriptions/f3577a3a-63c6-4d6f-972b-9344133af8db/1760885247813-prescription.pdf	93349	application/pdf	prescription	{}	2025-10-19 14:47:29.148705+00	2025-10-19 14:48:45.886386+00	\N	3db328c8-da70-418c-a245-d01175590664	04af6c1e-d6d7-43de-9b78-5d711a4127c7	f3577a3a-63c6-4d6f-972b-9344133af8db
b26bc225-e359-4204-a9e8-c19bdcdd4367	4e4b8d72-8036-4896-a536-3aac8f520de0-prescription-signed.pdf	receita_maryellen_hallen_pereira_santos_20251015_signed.pdf	patients/50b9da75-b20a-460e-994b-44e3036a23e4/documents/4e4b8d72-8036-4896-a536-3aac8f520de0-prescription-signed.pdf	168046	application/pdf	signed_document	{}	2025-10-15 11:15:53.144424+00	2025-10-16 17:01:47.960622+00	\N	50b9da75-b20a-460e-994b-44e3036a23e4	\N	\N
b90c8f1a-4f03-4a00-9a3a-f6cd5a39de21	4e4b8d72-8036-4896-a536-3aac8f520de0-anamnesis-signed.pdf	anamnesis_50b9da75-b20a-460e-994b-44e3036a23e4_signed.pdf	patients/50b9da75-b20a-460e-994b-44e3036a23e4/documents/4e4b8d72-8036-4896-a536-3aac8f520de0-anamnesis-signed.pdf	157395	application/pdf	document	{}	2025-10-15 11:15:53.813558+00	2025-10-16 17:01:47.960622+00	\N	50b9da75-b20a-460e-994b-44e3036a23e4	\N	\N
3a75f13d-65c5-474d-a16a-a444d8fefb0b	3e64bcf6-6cf1-47c5-9baf-2e27b0935c56-prescription-signed.pdf	receita_maryellen_hallen_pereira_santos_20251015_signed.pdf	patients/50b9da75-b20a-460e-994b-44e3036a23e4/documents/3e64bcf6-6cf1-47c5-9baf-2e27b0935c56-prescription-signed.pdf	167899	application/pdf	signed_document	{}	2025-10-15 11:16:23.710974+00	2025-10-16 17:01:47.962245+00	\N	50b9da75-b20a-460e-994b-44e3036a23e4	\N	\N
4f2b624c-968e-4475-b375-90da9d626cc8	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760743427028-prescription.jpg	141083	image/jpeg	prescription	{}	2025-10-17 23:23:49.181456+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
9ebd8be7-7959-4812-a7c4-3c966572f997	04af6c1e-d6d7-43de-9b78-5d711a4127c7-prescription-signed.pdf	receita_theo_ragazzini_ettori_20251019_signed.pdf	patients/3db328c8-da70-418c-a245-d01175590664/documents/04af6c1e-d6d7-43de-9b78-5d711a4127c7-prescription-signed.pdf	168776	application/pdf	signed_document	{}	2025-10-19 15:03:20.948468+00	2025-10-19 15:03:20.948469+00	b154bd52-f040-4ca0-a44f-3710152b68ec	3db328c8-da70-418c-a245-d01175590664	04af6c1e-d6d7-43de-9b78-5d711a4127c7	\N
eb3a9c52-0a35-4772-ba8e-77d7ce5e86f1	33020037-5cdb-4b41-816c-ec65f882c9d5-prescription.pdf	prescription.pdf	prescriptions/33020037-5cdb-4b41-816c-ec65f882c9d5/1760607514048-prescription.pdf	168747	application/pdf	prescription	{}	2025-10-16 09:38:36.81745+00	2025-10-16 20:18:53.83612+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	\N
50e5bcf5-9292-4bc9-b4b9-61963c80a0fa	04af6c1e-d6d7-43de-9b78-5d711a4127c7-anamnesis-signed.pdf	anamnesis_3db328c8-da70-418c-a245-d01175590664_signed.pdf	patients/3db328c8-da70-418c-a245-d01175590664/documents/04af6c1e-d6d7-43de-9b78-5d711a4127c7-anamnesis-signed.pdf	157248	application/pdf	document	{}	2025-10-19 15:03:21.808334+00	2025-10-19 15:03:21.808336+00	b154bd52-f040-4ca0-a44f-3710152b68ec	3db328c8-da70-418c-a245-d01175590664	04af6c1e-d6d7-43de-9b78-5d711a4127c7	\N
bd8be3de-52e8-42bc-a3dc-71cff4f23c8c	9217ba7f-e064-4eb4-9919-679fb4e3a951-prescription-signed.pdf	receita_joão_carlos_fonseca_corrijido_20251020_signed.pdf	patients/75ffc611-f82c-43cf-bf3e-bbf75123b7aa/documents/9217ba7f-e064-4eb4-9919-679fb4e3a951-prescription-signed.pdf	168466	application/pdf	signed_document	{}	2025-10-20 23:05:07.334026+00	2025-10-20 23:05:07.334028+00	e22ac097-d2d6-43af-9306-acab43d542bd	75ffc611-f82c-43cf-bf3e-bbf75123b7aa	9217ba7f-e064-4eb4-9919-679fb4e3a951	\N
22837fcf-fd47-4fd8-b6c2-bb35292db468	fbf39f31-647a-46a1-9845-6e8f85c04ed3-prescription-signed.pdf	receita_fabio_luis_marques_da_silva_20251021_signed.pdf	patients/a6fe8ce5-c9a9-4f1e-a698-c7d834256762/documents/fbf39f31-647a-46a1-9845-6e8f85c04ed3-prescription-signed.pdf	168974	application/pdf	signed_document	{}	2025-10-21 01:22:00.187866+00	2025-10-21 01:22:00.187868+00	\N	a6fe8ce5-c9a9-4f1e-a698-c7d834256762	fbf39f31-647a-46a1-9845-6e8f85c04ed3	\N
dbf01a55-5765-4c63-94ad-0f39b1d60de6	3e64bcf6-6cf1-47c5-9baf-2e27b0935c56-anamnesis-signed.pdf	anamnesis_50b9da75-b20a-460e-994b-44e3036a23e4_signed.pdf	patients/50b9da75-b20a-460e-994b-44e3036a23e4/documents/3e64bcf6-6cf1-47c5-9baf-2e27b0935c56-anamnesis-signed.pdf	157493	application/pdf	document	{}	2025-10-15 11:16:24.454946+00	2025-10-16 17:01:47.962245+00	\N	50b9da75-b20a-460e-994b-44e3036a23e4	\N	\N
db303a20-9e40-47a2-9bb2-9938bd7ab48a	50667192-be44-4578-8905-a55c48caeee1-prescription-signed.pdf	receita_joão_silva_sanroa_20251015_signed.pdf	patients/d7735997-acf6-4269-85cc-0eb205ae8fcf/documents/50667192-be44-4578-8905-a55c48caeee1-prescription-signed.pdf	166656	application/pdf	signed_document	{}	2025-10-15 14:28:30.543483+00	2025-10-16 17:01:47.96612+00	46eab41c-fd40-4166-bb3c-62b35f5ea6d1	d7735997-acf6-4269-85cc-0eb205ae8fcf	\N	\N
8d6565b6-a8bc-457f-bcad-ac4dad9ce1c2	50667192-be44-4578-8905-a55c48caeee1-anamnesis-signed.pdf	anamnesis_d7735997-acf6-4269-85cc-0eb205ae8fcf_signed.pdf	patients/d7735997-acf6-4269-85cc-0eb205ae8fcf/documents/50667192-be44-4578-8905-a55c48caeee1-anamnesis-signed.pdf	155259	application/pdf	document	{}	2025-10-15 14:28:31.30483+00	2025-10-16 17:01:47.96612+00	46eab41c-fd40-4166-bb3c-62b35f5ea6d1	d7735997-acf6-4269-85cc-0eb205ae8fcf	\N	\N
544cd9b1-0779-43a2-a0ea-595f1545080f	374166ad-f6f8-4063-b45f-ea570f51f051-prescription-signed.pdf	receita_patient_4915158832107_20251017_signed.pdf	patients/5e113a13-25ab-4812-acc2-0c675ac8b791/documents/374166ad-f6f8-4063-b45f-ea570f51f051-prescription-signed.pdf	168279	application/pdf	signed_document	{}	2025-10-17 23:34:34.367131+00	2025-10-17 23:34:34.367134+00	4be2fd18-2db1-4f47-861f-cb64be199162	5e113a13-25ab-4812-acc2-0c675ac8b791	374166ad-f6f8-4063-b45f-ea570f51f051	\N
d732f787-7593-4a7d-8927-a09c4047d1cd	925fa162-374d-4176-a085-74228abe40e4-prescription-signed.pdf	receita_theo_ragazzini_ettori_20251021_signed.pdf	patients/2b635923-f6c4-435a-9054-156c2113888f/documents/925fa162-374d-4176-a085-74228abe40e4-prescription-signed.pdf	168877	application/pdf	signed_document	{}	2025-10-21 10:48:39.435112+00	2025-10-21 10:48:39.435115+00	50aa6b31-ecc5-4955-9a1b-8ef2248a8e81	2b635923-f6c4-435a-9054-156c2113888f	925fa162-374d-4176-a085-74228abe40e4	\N
28e7b083-5178-4281-8918-41d6f001c815	60d0b270-2f23-4694-97ed-fc7cc00c377f-prescription.jpg	prescription.jpg	prescriptions/60d0b270-2f23-4694-97ed-fc7cc00c377f/1761057521942-prescription.jpg	475949	image/jpeg	prescription	{}	2025-10-21 14:38:44.6521+00	2025-10-21 14:39:59.994227+00	\N	584648e5-0c1d-44f9-aa12-8cde21c2e4d2	c67e14f6-fb1f-4e56-ba62-e34ae783d120	60d0b270-2f23-4694-97ed-fc7cc00c377f
5ffe1160-7e3b-4c82-b8d9-535b60dd531a	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760806006621-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-18 16:46:48.362423+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
1ac8b17b-4493-4fe0-9e2e-09d65db15793	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.pdf	prescription.pdf	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760789433870-prescription.pdf	168747	application/pdf	prescription	{}	2025-10-18 12:10:35.753765+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
c94f3223-3dd2-4736-b068-28ee2ff5b9b6	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760744034363-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-17 23:33:56.241925+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
62c9c520-ebb9-4b51-8cbe-598176ccc7c0	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760743734902-prescription.jpg	141083	image/jpeg	prescription	{}	2025-10-17 23:28:57.244531+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
efb3ea27-5068-4d09-a017-abebd3ea68d2	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.pdf	prescription.pdf	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760737378938-prescription.pdf	168747	application/pdf	prescription	{}	2025-10-17 21:43:01.0744+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
06eec78d-7cae-4e98-a866-ce184e0a79b0	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760737141308-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-17 21:39:02.915727+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
822deedf-55ab-4544-a7c0-da22f358fd4f	37c7666e-0b22-47ba-b4d2-78cf431ad8de-prescription.jpg	prescription.jpg	prescriptions/37c7666e-0b22-47ba-b4d2-78cf431ad8de/1760736774191-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-17 21:32:56.304454+00	2025-10-18 18:01:50.713093+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	6f5dab3c-a4bb-48d8-b15c-b724e217d778	\N
02fb5d7e-4f2a-45a2-b1ec-72955599a10b	aebbd84e-c9c8-4e99-9e8e-967629412f1e-prescription.jpg	prescription.jpg	prescriptions/aebbd84e-c9c8-4e99-9e8e-967629412f1e/1761126826129-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-22 09:53:47.668402+00	2025-10-31 12:35:12.664128+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	39507116-4a58-4600-8726-79afd9aa0494	aebbd84e-c9c8-4e99-9e8e-967629412f1e
cb119eb5-06b1-4dd5-a03d-ecfd8ae68037	aebbd84e-c9c8-4e99-9e8e-967629412f1e-prescription.jpg	prescription.jpg	prescriptions/aebbd84e-c9c8-4e99-9e8e-967629412f1e/1761047370460-prescription.jpg	124464	image/jpeg	prescription	{}	2025-10-21 11:49:31.743539+00	2025-10-31 12:35:12.81503+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	39507116-4a58-4600-8726-79afd9aa0494	aebbd84e-c9c8-4e99-9e8e-967629412f1e
96cfde54-82a6-4c41-9e92-15ab1282a86d	aebbd84e-c9c8-4e99-9e8e-967629412f1e-prescription.jpg	prescription.jpg	prescriptions/aebbd84e-c9c8-4e99-9e8e-967629412f1e/1761632591224-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-28 06:23:12.677447+00	2025-10-31 12:35:12.561636+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	39507116-4a58-4600-8726-79afd9aa0494	aebbd84e-c9c8-4e99-9e8e-967629412f1e
d93d7535-c79e-4907-b685-0c0e0f36161c	aebbd84e-c9c8-4e99-9e8e-967629412f1e-prescription.pdf	prescription.pdf	prescriptions/aebbd84e-c9c8-4e99-9e8e-967629412f1e/1761477526430-prescription.pdf	1153391	application/pdf	prescription	{}	2025-10-26 11:18:53.413838+00	2025-10-31 12:35:12.619292+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	39507116-4a58-4600-8726-79afd9aa0494	aebbd84e-c9c8-4e99-9e8e-967629412f1e
335aaa80-8108-4455-b3d6-725d959cb8c5	aebbd84e-c9c8-4e99-9e8e-967629412f1e-prescription.jpg	prescription.jpg	prescriptions/aebbd84e-c9c8-4e99-9e8e-967629412f1e/1761047791614-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-21 11:56:32.387669+00	2025-10-31 12:35:12.770582+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	39507116-4a58-4600-8726-79afd9aa0494	aebbd84e-c9c8-4e99-9e8e-967629412f1e
1bcae9e2-d77c-4dc5-83c8-95d494c7e906	aebbd84e-c9c8-4e99-9e8e-967629412f1e-prescription.jpg	prescription.jpg	prescriptions/aebbd84e-c9c8-4e99-9e8e-967629412f1e/1761005264384-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-21 00:07:45.645757+00	2025-10-31 12:35:12.920989+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	39507116-4a58-4600-8726-79afd9aa0494	aebbd84e-c9c8-4e99-9e8e-967629412f1e
198cbc39-0a92-433c-9491-2ef64df20b8d	aebbd84e-c9c8-4e99-9e8e-967629412f1e-prescription.jpg	prescription.jpg	prescriptions/aebbd84e-c9c8-4e99-9e8e-967629412f1e/1761048598026-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-21 12:09:59.39048+00	2025-10-31 12:35:12.717332+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	39507116-4a58-4600-8726-79afd9aa0494	aebbd84e-c9c8-4e99-9e8e-967629412f1e
fa1f98c2-dd05-4c9c-aa9f-2fcaf05a6845	aebbd84e-c9c8-4e99-9e8e-967629412f1e-prescription.jpg	prescription.jpg	prescriptions/aebbd84e-c9c8-4e99-9e8e-967629412f1e/1761912578597-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-31 12:09:38.770397+00	2025-10-31 12:35:12.479814+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	39507116-4a58-4600-8726-79afd9aa0494	aebbd84e-c9c8-4e99-9e8e-967629412f1e
61a77d3d-2dd8-470a-9efa-64ecab1e88fd	aebbd84e-c9c8-4e99-9e8e-967629412f1e-prescription.jpg	prescription.jpg	prescriptions/aebbd84e-c9c8-4e99-9e8e-967629412f1e/1761914092238-prescription.jpg	146922	image/jpeg	prescription	{}	2025-10-31 12:34:52.347227+00	2025-10-31 12:35:12.433714+00	\N	5e113a13-25ab-4812-acc2-0c675ac8b791	39507116-4a58-4600-8726-79afd9aa0494	aebbd84e-c9c8-4e99-9e8e-967629412f1e
\.


--
-- TOC entry 5138 (class 0 OID 25125)
-- Dependencies: 233
-- Data for Name: medical_history; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.medical_history (id, patient_id, medical_background, current_medications, allergies, symptoms, version, created_at, updated_at, family_history, subjective, is_draft) FROM stdin;
95fcd13b-5e35-45cb-844c-079641a0c883	57873e19-e1d2-42c4-990c-cf8a420e2a35	\N	["trombosil 10 mg"]	["terra vermelha"]	[]	1	2025-10-12 21:17:38.047452+00	2025-10-12 21:17:38.047452+00	\N	{"allergies": "terra vermelha", "full_name": "Não informado", "ocr_result": "{}", "medications": "trombosil 10 mg", "full_address": "Não informado", "prescription_transcript": "OCR extraction failed: Extraction failed: Invalid JSON in output_text: expected value at line 1 column 2. Raw text: [TRANSCRIÇÃO DA ÁREA DOS MEDICAMENTOS]\\n1/ IVAN BOLSENATE\\n- DIA ZEPAM\\n- 2 cm\\nTOMAR 1 COMPRIMIDO NOITE\\n- DIA FIM\\nNOME 04/08/2025\\n\\n{\\n  \\"patient\\": {\\n    \\"full_name\\": \\"IVAN BOLSENATE\\",\\n    \\"cpf\\": null,\\n    \\"birth_date\\": null,\\n    \\"phone\\": null,\\n    \\"email\\": null,\\n    \\"address_street\\": null,\\n    \\"address_number\\": null,\\n    \\"address_complement\\": null,\\n    \\"address_neighborhood\\": null,\\n    \\"address_city\\": null,\\n    \\"address_state\\": null,\\n    \\"address_cep\\": null,\\n    \\"gender\\": null\\n  },\\n  \\"doctor\\": {\\n    \\"name\\": null,\\n    \\"crm\\": {\\n      \\"number\\": null,\\n      \\"state\\": null\\n    },\\n    \\"additional_info\\": null\\n  },\\n  \\"medications\\": [\\n    {\\n      \\"name\\": \\"Diazepam\\",\\n      \\"dosage\\": \\"2 mg\\",\\n      \\"posology\\": \\"Tomar 1 comprimido noite\\"\\n    }\\n  ]\\n}"}	t
b5a093b8-08b3-472e-a02d-ff7226d7c648	57873e19-e1d2-42c4-990c-cf8a420e2a35	zxcvzxcv	["trombosil 10 mgzxcv"]	["terra vermelhazxcv"]	["zxcvzxcv"]	2	2025-10-13 00:41:12.030855+00	2025-10-13 00:41:12.030855+00	zxcvxczv	{"allergies": "terra vermelha", "full_name": "Não informado", "ocr_result": "{}", "medications": "trombosil 10 mg", "full_address": "Não informado", "prescription_transcript": "OCR extraction failed: Extraction failed: Invalid JSON in output_text: expected value at line 1 column 2. Raw text: [TRANSCRIÇÃO DA ÁREA DOS MEDICAMENTOS]\\n1/ IVAN BOLSENATE\\n- DIA ZEPAM\\n- 2 cm\\nTOMAR 1 COMPRIMIDO NOITE\\n- DIA FIM\\nNOME 04/08/2025\\n\\n{\\n  \\"patient\\": {\\n    \\"full_name\\": \\"IVAN BOLSENATE\\",\\n    \\"cpf\\": null,\\n    \\"birth_date\\": null,\\n    \\"phone\\": null,\\n    \\"email\\": null,\\n    \\"address_street\\": null,\\n    \\"address_number\\": null,\\n    \\"address_complement\\": null,\\n    \\"address_neighborhood\\": null,\\n    \\"address_city\\": null,\\n    \\"address_state\\": null,\\n    \\"address_cep\\": null,\\n    \\"gender\\": null\\n  },\\n  \\"doctor\\": {\\n    \\"name\\": null,\\n    \\"crm\\": {\\n      \\"number\\": null,\\n      \\"state\\": null\\n    },\\n    \\"additional_info\\": null\\n  },\\n  \\"medications\\": [\\n    {\\n      \\"name\\": \\"Diazepam\\",\\n      \\"dosage\\": \\"2 mg\\",\\n      \\"posology\\": \\"Tomar 1 comprimido noite\\"\\n    }\\n  ]\\n}"}	f
f8b2e135-d2f8-478c-bdb5-f912b133ddf8	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	[]	[]	[]	1	2025-10-12 19:17:33.515579+00	2025-10-12 19:17:33.515579+00	\N	{"ocr_result": "{\\"doctor\\":{\\"additional_info\\":null,\\"crm\\":{\\"number\\":\\"150494\\",\\"state\\":\\"SP\\"},\\"name\\":\\"Dr(a). Lucas Amorim Vieira de Barros\\"},\\"medications\\":[{\\"dosage\\":\\"10 mg\\",\\"name\\":\\"Alprazolam\\",\\"posology\\":\\"Uso oral ------------------------------------- contínuo\\\\nAlprazolam 10mg até apagar.\\"}],\\"patient\\":{\\"address_cep\\":\\"00000-000\\",\\"address_city\\":\\"São Paulo\\",\\"address_complement\\":\\"A confirmar\\",\\"address_neighborhood\\":null,\\"address_number\\":\\"S/N\\",\\"address_state\\":\\"SP\\",\\"address_street\\":\\"A confirmar\\",\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"Patient 4915158832107\\",\\"gender\\":null,\\"phone\\":null}}", "prescription_transcript": "1. Alprazolam 10 mg - Uso oral ------------------------------------- contínuo\\nAlprazolam 10mg até apagar."}	t
fde32c84-445d-4559-9dc5-e0a8f420606c	5e113a13-25ab-4812-acc2-0c675ac8b791	456	["465"]	["456"]	["465"]	2	2025-10-12 19:24:51.145917+00	2025-10-12 19:24:51.145917+00	465	{"ocr_result": "{\\"doctor\\":{\\"additional_info\\":null,\\"crm\\":{\\"number\\":\\"150494\\",\\"state\\":\\"SP\\"},\\"name\\":\\"Dr(a). Lucas Amorim Vieira de Barros\\"},\\"medications\\":[{\\"dosage\\":\\"10 mg\\",\\"name\\":\\"Alprazolam\\",\\"posology\\":\\"Uso oral ------------------------------------- contínuo\\\\nAlprazolam 10mg até apagar.\\"}],\\"patient\\":{\\"address_cep\\":\\"00000-000\\",\\"address_city\\":\\"São Paulo\\",\\"address_complement\\":\\"A confirmar\\",\\"address_neighborhood\\":null,\\"address_number\\":\\"S/N\\",\\"address_state\\":\\"SP\\",\\"address_street\\":\\"A confirmar\\",\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"Patient 4915158832107\\",\\"gender\\":null,\\"phone\\":null}}", "prescription_transcript": "1. Alprazolam 10 mg - Uso oral ------------------------------------- contínuo\\nAlprazolam 10mg até apagar."}	f
f8e1ea17-74ab-42e3-8ef2-db2e99e3206c	5e113a13-25ab-4812-acc2-0c675ac8b791	asma	["azt"]	["iodo labios inchados"]	["Paciente refere medo de extraterrestre."]	3	2025-10-12 19:28:13.340353+00	2025-10-12 19:28:13.340353+00	Paciente nega histórico familiar de doenças.	{"diseases": "asma", "symptoms": "medo de extraterrestre", "allergies": "iodo labios inchados", "full_name": "Não informado", "ocr_result": "{}", "medications": "azt", "full_address": "Não informado", "prescription_transcript": "OCR extraction failed: Extraction failed: Invalid JSON in output_text: expected value at line 1 column 1. Raw text: ```markdown\\n[TRANSCRIÇÃO DA ÁREA DOS MEDICAMENTOS]\\n123\\n```\\n\\n{\\n  \\"patient\\": {\\n    \\"full_name\\": \\"Heitor Ettori\\",\\n    \\"cpf\\": null,\\n    \\"birth_date\\": null,\\n    \\"phone\\": null,\\n    \\"email\\": null,\\n    \\"address_street\\": \\"Não informado, S/N - Não especificado - São Paulo, SP - CEP: 00000-000\\",\\n    \\"address_number\\": \\"123\\",\\n    \\"address_complement\\": null,\\n    \\"address_neighborhood\\": null,\\n    \\"address_city\\": \\"São Paulo\\",\\n    \\"address_state\\": \\"SP\\",\\n    \\"address_cep\\": \\"00000-000\\",\\n    \\"gender\\": null\\n  },\\n  \\"doctor\\": {\\n    \\"name\\": \\"Dr(a). Lucas Amorim Vieira de Barros\\",\\n    \\"crm\\": {\\n      \\"number\\": \\"150494\\",\\n      \\"state\\": \\"SP\\"\\n    },\\n    \\"additional_info\\": \\"CRM: 150494 - SP; Emitido: 11/10/2025 às 17:32:30; Código: BA0501BA; Clínica: Neurovitta; Endereço: Praça Melvin Jones, 18, Jardim São Dimas - 12245-360, São José dos Campos - SP; Telefone: 12981758630; Verificador ITI; Prescrição eletrônica assinada digitalmente\\"\\n  },\\n  \\"medications\\": [],\\n  \\"prescription_transcript\\": \\"123\\"\\n}"}	t
de63f555-1934-47c1-8d0a-5e83c4ed141f	0a210e3b-ed53-413d-a343-16c667aefa64	asma	["azt"]	["iodo labios inchados"]	["medo de extraterrestre"]	1	2025-10-12 21:09:52.332485+00	2025-10-12 21:09:52.332485+00	\N	{"diseases": "asma", "symptoms": "medo de extraterrestre", "allergies": "iodo labios inchados", "full_name": "Heitor Ettori", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":null,\\"crm\\":{\\"number\\":\\"150494\\",\\"state\\":\\"SP\\"},\\"name\\":\\"Dr(a). Lucas Amorim Vieira de Barros\\"},\\"medications\\":[],\\"patient\\":{\\"address_cep\\":\\"00000-000\\",\\"address_city\\":\\"São Paulo\\",\\"address_complement\\":\\"Não especificado\\",\\"address_neighborhood\\":null,\\"address_number\\":\\"S/N\\",\\"address_state\\":\\"SP\\",\\"address_street\\":\\"Não informado\\",\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"Heitor Ettori\\",\\"gender\\":null,\\"phone\\":null}}", "medications": "azt", "full_address": "Não informado - S/N - Não especificado - São Paulo, SP - CEP: 00000-000", "prescription_transcript": ""}	t
f73a7744-62be-4761-a30c-79e0e8a3f365	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite", "versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	18	2025-10-13 13:33:32.508059+00	2025-10-13 13:33:32.508059+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	t
643df50a-877b-4d62-ab0d-b219c55764dc	50b9da75-b20a-460e-994b-44e3036a23e4	priapismo	[]	[]	[]	2	2025-10-13 18:49:53.795593+00	2025-10-13 18:49:53.795593+00	\N	{"diseases": "priapismo", "symptoms": null, "allergies": null, "medications": null, "family_history": "pressao"}	t
2120281b-1973-40cc-8ac5-3a69978c44dd	2b635923-f6c4-435a-9054-156c2113888f	Paciente nega doenças prévias.	["Paciente nega uso de medicamentos."]	["Paciente nega alergias."]	["Paciente refere ausência de sintomas no momento."]	2	2025-10-21 11:01:58.709443+00	2025-10-21 11:01:58.709443+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
256231b5-1be3-4263-9a9b-0956aeddb8fb	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	Convulsão desde criança.	["Lamotrigina 1200mg 12/12 horas", "Levotiroxina 12mcg a noite", "Quetiapina 50mg à noite", "Sertralina 50mg 12/12 horas."]	["Dipirona e Advil"]	["Paciente refere dor no tendão de Aquiles ao caminhar."]	1	2025-10-13 00:44:54.821511+00	2025-10-13 00:44:54.821511+00	Paciente nega histórico familiar de doenças.	{"diseases": "Convulsão desde criança.", "symptoms": "Dor no tendao de aquiles ao camihar.", "allergies": "Dipirona e Advil", "full_name": "Heitor Éttori", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":null,\\"crm\\":{\\"number\\":\\"150494\\",\\"state\\":\\"SP\\"},\\"name\\":\\"Dr(a). Lucas Amorim Vieira de Barros\\"},\\"medications\\":[{\\"dosage\\":\\"25 mg\\",\\"name\\":\\"Amitriptilina\\",\\"posology\\":\\"Tomar 1 comprimido à noite antes de dormir.\\"}],\\"patient\\":{\\"address_cep\\":\\"06709-135\\",\\"address_city\\":\\"Cotia\\",\\"address_complement\\":null,\\"address_neighborhood\\":\\"Granja Viana\\",\\"address_number\\":\\"99\\",\\"address_state\\":\\"SP\\",\\"address_street\\":\\"Rua Profa. Ana Nastari Brunetti\\",\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"Heitor Éttori\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"Uso oral:\\\\\\\\n1) Amitriptilina 25mg ----------------------------------------\\\\\\\\nTomar 1 comprimido à noite antes de dormir.\\"}", "medications": "Lamotrigina 1200mg 12/12 horas, Levotiroxina 12mcg a noite, Quetiapina 50mg à noite, Sertralina 50mg 12/12 horas.", "full_address": "Rua Profa. Ana Nastari Brunetti - 99 - Granja Viana - Cotia, SP - CEP: 06709-135", "prescription_transcript": "1. Amitriptilina 25 mg - Tomar 1 comprimido à noite antes de dormir."}	t
5018d4b0-79d4-47b7-8939-1231dc169fdd	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	Convulsão desde criança.	["Lamotrigina 1200mg 12/12 horas Levotiroxina 12mcg a noite Quetiapina 50mg à noite Sertralina 50mg 12/12 horas."]	["Dipirona e Advil"]	["Paciente refere dor no tendão de Aquiles ao caminhar."]	2	2025-10-13 00:45:46.471204+00	2025-10-13 00:45:46.471204+00	Paciente nega histórico familiar de doenças.	{"diseases": "Convulsão desde criança.", "symptoms": "Dor no tendao de aquiles ao camihar.", "allergies": "Dipirona e Advil", "full_name": "Heitor Éttori", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":null,\\"crm\\":{\\"number\\":\\"150494\\",\\"state\\":\\"SP\\"},\\"name\\":\\"Dr(a). Lucas Amorim Vieira de Barros\\"},\\"medications\\":[{\\"dosage\\":\\"25 mg\\",\\"name\\":\\"Amitriptilina\\",\\"posology\\":\\"Tomar 1 comprimido à noite antes de dormir.\\"}],\\"patient\\":{\\"address_cep\\":\\"06709-135\\",\\"address_city\\":\\"Cotia\\",\\"address_complement\\":null,\\"address_neighborhood\\":\\"Granja Viana\\",\\"address_number\\":\\"99\\",\\"address_state\\":\\"SP\\",\\"address_street\\":\\"Rua Profa. Ana Nastari Brunetti\\",\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"Heitor Éttori\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"Uso oral:\\\\\\\\n1) Amitriptilina 25mg ----------------------------------------\\\\\\\\nTomar 1 comprimido à noite antes de dormir.\\"}", "medications": "Lamotrigina 1200mg 12/12 horas, Levotiroxina 12mcg a noite, Quetiapina 50mg à noite, Sertralina 50mg 12/12 horas.", "full_address": "Rua Profa. Ana Nastari Brunetti - 99 - Granja Viana - Cotia, SP - CEP: 06709-135", "prescription_transcript": "1. Amitriptilina 25 mg - Tomar 1 comprimido à noite antes de dormir."}	f
6aa75d57-6919-4115-93c1-7d3d61abe96d	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite", "versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	4	2025-10-13 11:28:12.747515+00	2025-10-13 11:28:12.747515+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "full_name": "Heitor Éttori", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":\\"Emitido: 28/09/2025 às 16:05:32 | Código: 50786CF0 | Clínica: Neurovitta, Praça Melvin Jones, 18, Jardim São Dimas, 12245-360, São José dos Campos - SP, Telefone: 12981758630\\",\\"crm\\":{\\"number\\":\\"150494\\",\\"state\\":\\"SP\\"},\\"name\\":\\"Dr(a). Lucas Amorim Vieira de Barros\\"},\\"medications\\":[{\\"dosage\\":\\"25 mg\\",\\"name\\":\\"Amitriptilina\\",\\"posology\\":\\"Tomar 1 comprimido à noite antes de dormir.\\"}],\\"patient\\":{\\"address_cep\\":\\"06709-135\\",\\"address_city\\":\\"Cotia\\",\\"address_complement\\":null,\\"address_neighborhood\\":\\"Granja Viana\\",\\"address_number\\":\\"99\\",\\"address_state\\":\\"SP\\",\\"address_street\\":\\"Rua Profa. Ana Nastari Brunetti\\",\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"Heitor Éttori\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"Uso oral:\\\\n\\\\n1) Amitriptilina 25mg --------------------------------------------\\\\nTomar 1 comprimido à noite antes de dormir.\\"}", "medications": "Rozucor 10mg à noite, versao 3", "full_address": "Rua Profa. Ana Nastari Brunetti - 99 - Granja Viana - Cotia, SP - CEP: 06709-135", "prescription_transcript": "1. Amitriptilina 25 mg - Tomar 1 comprimido à noite antes de dormir."}	t
956bbf19-e6d6-4ffd-a6e3-645fc95994a6	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	5	2025-10-13 11:30:43.114401+00	2025-10-13 11:30:43.114401+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "full_name": "Heitor Éttori", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":\\"Emitido: 28/09/2025 às 16:05:32 | Código: 50786CF0 | Clínica: Neurovitta, Praça Melvin Jones, 18, Jardim São Dimas, 12245-360, São José dos Campos - SP, Telefone: 12981758630\\",\\"crm\\":{\\"number\\":\\"150494\\",\\"state\\":\\"SP\\"},\\"name\\":\\"Dr(a). Lucas Amorim Vieira de Barros\\"},\\"medications\\":[{\\"dosage\\":\\"25 mg\\",\\"name\\":\\"Amitriptilina\\",\\"posology\\":\\"Tomar 1 comprimido à noite antes de dormir.\\"}],\\"patient\\":{\\"address_cep\\":\\"06709-135\\",\\"address_city\\":\\"Cotia\\",\\"address_complement\\":null,\\"address_neighborhood\\":\\"Granja Viana\\",\\"address_number\\":\\"99\\",\\"address_state\\":\\"SP\\",\\"address_street\\":\\"Rua Profa. Ana Nastari Brunetti\\",\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"Heitor Éttori\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"Uso oral:\\\\n\\\\n1) Amitriptilina 25mg --------------------------------------------\\\\nTomar 1 comprimido à noite antes de dormir.\\"}", "medications": "Rozucor 10mg à noite, versao 3", "full_address": "Rua Profa. Ana Nastari Brunetti - 99 - Granja Viana - Cotia, SP - CEP: 06709-135", "prescription_transcript": "1. Amitriptilina 25 mg - Tomar 1 comprimido à noite antes de dormir."}	f
be6233b6-7d1e-434a-bc01-7427e3fee7c7	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite", "versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	6	2025-10-13 12:00:13.375564+00	2025-10-13 12:00:13.375564+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "full_name": "Heitor Éttori", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":\\"Emitido: 28/09/2025 às 16:05:32 | Código: 50786CF0 | Clínica: Neurovitta, Praça Melvin Jones, 18, Jardim São Dimas, 12245-360, São José dos Campos - SP, Telefone: 12981758630\\",\\"crm\\":{\\"number\\":\\"150494\\",\\"state\\":\\"SP\\"},\\"name\\":\\"Dr(a). Lucas Amorim Vieira de Barros\\"},\\"medications\\":[{\\"dosage\\":\\"25 mg\\",\\"name\\":\\"Amitriptilina\\",\\"posology\\":\\"Tomar 1 comprimido à noite antes de dormir.\\"}],\\"patient\\":{\\"address_cep\\":\\"06709-135\\",\\"address_city\\":\\"Cotia\\",\\"address_complement\\":null,\\"address_neighborhood\\":\\"Granja Viana\\",\\"address_number\\":\\"99\\",\\"address_state\\":\\"SP\\",\\"address_street\\":\\"Rua Profa. Ana Nastari Brunetti\\",\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"Heitor Éttori\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"Uso oral:\\\\n\\\\n1) Amitriptilina 25mg --------------------------------------------\\\\nTomar 1 comprimido à noite antes de dormir.\\"}", "medications": "Rozucor 10mg à noite, versao 3", "full_address": "Rua Profa. Ana Nastari Brunetti - 99 - Granja Viana - Cotia, SP - CEP: 06709-135", "prescription_transcript": "1. Amitriptilina 25 mg - Tomar 1 comprimido à noite antes de dormir."}	t
aad77a99-a5ef-4ad8-92f4-1e037921068f	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	19	2025-10-13 13:37:40.198621+00	2025-10-13 13:37:40.198621+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	f
e02cced3-68c2-4b3e-b7ee-a5c6bf64a635	9fe0af44-5e3d-42d0-9144-ab175099d699	as vezes meu orgao intimo fica ereto e dois demais opr horas	["losartana"]	["camarao"]	["Paciente refere estar se sentindo bem", "sem queixas no momento."]	1	2025-10-13 15:26:16.161115+00	2025-10-13 15:26:16.161115+00	Paciente nega histórico familiar de doenças.	{"diseases": "as vezes meu orgao intimo fica ereto e dois demais opr horas", "symptoms": "estou me sentindo bem", "allergies": "camarao", "medications": "losartana", "family_history": "infarto aos 50 anos"}	t
73c2b54e-8158-46ec-8377-640890329e1f	50b9da75-b20a-460e-994b-44e3036a23e4	priapismo	["asdf"]	["asdf"]	["asdf"]	3	2025-10-13 20:20:45.823514+00	2025-10-13 20:20:45.823514+00	asdf	{"diseases": "priapismo", "symptoms": null, "allergies": null, "medications": null, "family_history": "pressao"}	f
511471f8-f6a7-4e7c-a575-ce6a55e06e22	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	7	2025-10-13 12:00:58.339372+00	2025-10-13 12:00:58.339372+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "full_name": "Heitor Éttori", "ocr_result": "{\\"doctor\\":{\\"additional_info\\":\\"Emitido: 28/09/2025 às 16:05:32 | Código: 50786CF0 | Clínica: Neurovitta, Praça Melvin Jones, 18, Jardim São Dimas - 12245-360, São José dos Campos - SP, Telefone: 12981758630\\",\\"crm\\":{\\"number\\":\\"150494\\",\\"state\\":\\"SP\\"},\\"name\\":\\"Dr(a). Lucas Amorim Vieira de Barros\\"},\\"medications\\":[{\\"dosage\\":\\"25 mg\\",\\"name\\":\\"Amitriptilina\\",\\"posology\\":\\"Tomar 1 comprimido à noite antes de dormir.\\"}],\\"patient\\":{\\"address_cep\\":\\"06709-135\\",\\"address_city\\":\\"Cotia\\",\\"address_complement\\":null,\\"address_neighborhood\\":\\"Granja Viana\\",\\"address_number\\":\\"99\\",\\"address_state\\":\\"SP\\",\\"address_street\\":\\"Rua Profa. Ana Nastari Brunetti\\",\\"birth_date\\":null,\\"cpf\\":null,\\"email\\":null,\\"full_name\\":\\"Heitor Ét tori\\",\\"gender\\":null,\\"phone\\":null},\\"prescription_transcript\\":\\"Uso oral:\\\\n\\\\n1) Amitriptilina 25mg --------------------------------------------\\\\nTomar 1 comprimido à noite antes de dormir.\\"}", "medications": "Rozucor 10mg à noite, versao 3", "full_address": "Rua Profa. Ana Nastari Brunetti - 99 - Granja Viana - Cotia, SP - CEP: 06709-135", "prescription_transcript": "1. Amitriptilina 25 mg - Tomar 1 comprimido à noite antes de dormir."}	f
d47091b7-fb0e-4b7d-9f12-bcfd57630046	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite", "versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	8	2025-10-13 12:37:35.23986+00	2025-10-13 12:37:35.23986+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	t
b6e67e73-599b-4fbc-aa99-7e46e95d78a0	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	9	2025-10-13 12:39:56.230253+00	2025-10-13 12:39:56.230253+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	f
f7b97037-0ee8-4da0-818f-fc85a0ad7643	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite", "versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	10	2025-10-13 13:07:08.79053+00	2025-10-13 13:07:08.79053+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	t
940e8069-8ed6-4161-8eba-a1b1fcd1f579	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	11	2025-10-13 13:07:59.552753+00	2025-10-13 13:07:59.552753+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	f
4c7550bb-a096-4796-a20d-4ea859450099	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite", "versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	12	2025-10-13 13:15:54.902986+00	2025-10-13 13:15:54.902986+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	t
08765471-d753-4683-a655-1abd133f626c	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	13	2025-10-13 13:17:08.953915+00	2025-10-13 13:17:08.953915+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	f
fc6c4429-4a14-4119-9b4b-fa3e8e0e4594	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite", "versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	14	2025-10-13 13:23:38.929361+00	2025-10-13 13:23:38.929361+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	t
c6c57345-247a-451a-9311-06d4e4c0537a	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	15	2025-10-13 13:24:04.215313+00	2025-10-13 13:24:04.215313+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	f
310c538e-224e-4501-b87d-a3fde2f72dc6	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite", "versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	16	2025-10-13 13:26:39.878946+00	2025-10-13 13:26:39.878946+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	t
66cd2a6f-7161-467f-b277-de10abdbb2dd	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	["Rozucor 10mg à noite versao 3 Conforme prescrição"]	["todos os anti-infalatórios"]	["Paciente refere ausência de sintomas no momento", "sem queixas de mal-estar", "dor ou desconforto."]	17	2025-10-13 13:27:13.500038+00	2025-10-13 13:27:13.500038+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	f
9fcd9524-f035-4036-8e3c-fce482213833	47ec77d4-b2fd-49be-9d64-4db12563c89c	\N	["Aas"]	[]	[]	1	2025-10-13 14:11:22.148145+00	2025-10-13 14:11:22.148145+00	\N	{"diseases": null, "symptoms": null, "allergies": null, "medications": "Aas", "family_history": "Pressão alta pai"}	t
932a4482-f535-4695-b83b-c0343ef73dd5	50b9da75-b20a-460e-994b-44e3036a23e4	priapismo	[]	[]	[]	1	2025-10-13 15:02:27.348325+00	2025-10-13 15:02:27.348325+00	\N	{"diseases": "priapismo", "symptoms": null, "allergies": null, "medications": null, "family_history": "pressao"}	t
0f0cbfa5-05b9-42f3-b623-56659192a6ed	63d47959-4742-460b-ae5a-5aeb982d4f91	Nega	["Nega"]	["Nega"]	["Nega"]	1	2025-10-14 15:12:11.419602+00	2025-10-14 15:12:11.419602+00	\N	{"diseases": "Nega", "symptoms": "Nega", "allergies": "Nega", "medications": "Nega", "family_history": "Nega"}	t
df39c033-e255-4276-a26a-a5bb34c1912f	5b2ef3ab-f157-47c6-93bf-abe334860192	asmita	["caverdilol 10mg Conforme prescrição"]	["calabresa", "lábio inchado e falta de ar"]	["Paciente relata sentir-se bem", "sem queixas atuais."]	1	2025-10-13 20:40:26.55965+00	2025-10-13 20:40:26.55965+00	Paciente nega histórico familiar de doenças.	{"diseases": "asmita", "symptoms": "me sinto bem", "allergies": "calabresa, lábio inchado e falta de ar", "medications": "caverdilol 10mg", "family_history": "acucar alto no sangue"}	t
8e2b26dd-df1e-4bae-bcd9-3e5e0a96f599	5b2ef3ab-f157-47c6-93bf-abe334860192	Paciente relata asma.	["Carvedilol 10mg Conforme prescrição"]	["Calabresa (edema labial com dispneia.)"]	["Paciente relata sentir-se bem", "sem queixas atuais."]	2	2025-10-13 20:52:33.282759+00	2025-10-13 20:52:33.282759+00	Paciente nega histórico familiar de doenças.	{"diseases": "asmita", "symptoms": "me sinto bem", "allergies": "calabresa, lábio inchado e falta de ar", "medications": "caverdilol 10mg", "family_history": "acucar alto no sangue"}	t
7d6cc309-e32c-4134-a00e-54c6914f3d38	5b2ef3ab-f157-47c6-93bf-abe334860192	Paciente relata asma.	["Carvedilol 10mg Conforme prescrição"]	["Calabresa (edema labial com dispneia.)"]	["Paciente relata sentir-se bem", "sem queixas atuais."]	3	2025-10-13 20:56:13.647876+00	2025-10-13 20:56:13.647876+00	Paciente nega histórico familiar de doenças.	{"diseases": "Covulsão", "symptoms": "nao", "allergies": "fenitoina figado inchado", "medications": "Etira 500mg 12/12 horas", "family_history": "Epilepsia de ausencia"}	t
b2bf577c-b8d7-4cbc-99ee-2bbe3bd30bd3	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	Paciente relata transtorno da personalidade limítrofe.	["Aripiprazol 5mg Conforme prescrição"]	["Alergia à picada de abelha (Não informado)"]	["Paciente refere dor no cotovelo."]	3	2025-10-13 21:05:20.210218+00	2025-10-13 21:05:20.210218+00	Paciente nega histórico familiar de doenças.	{"diseases": "transtorno da personalidade limitrofe", "symptoms": "tenho dor no cotovelo", "allergies": "alergia a picada de abelha", "medications": "aripiprazol 5mg noite", "family_history": "depressao cronica na ammae"}	t
2e45de08-3665-4198-bc88-8741db581cae	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	Paciente relata transtorno da personalidade limítrofe.	["Aripiprazol 5mg Conforme prescrição"]	["Alergia à picada de abelha (Não informado)"]	["Paciente refere dor no cotovelo."]	4	2025-10-13 21:10:54.065832+00	2025-10-13 21:10:54.065832+00	Paciente nega histórico familiar de doenças.	{"diseases": "transtorno da personalidade limitrofe", "symptoms": "tenho dor no cotovelo", "allergies": "alergia a picada de abelha", "medications": "aripiprazol 5mg noite", "family_history": "depressao cronica na ammae"}	f
168125d4-1c2e-47af-82ea-9851ddcc9a9a	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	Paciente relata transtorno da personalidade limítrofe.	["Aripiprazol 5mg Conforme prescrição"]	["Alergia à picada de abelha (Não informado)"]	["Paciente refere dor no cotovelo."]	5	2025-10-13 21:54:21.210277+00	2025-10-13 21:54:21.210277+00	Paciente nega histórico familiar de doenças.	{"diseases": "transtorno da personalidade limitrofe", "symptoms": "tenho dor no cotovelo", "allergies": "alergia a picada de abelha", "medications": "aripiprazol 5mg noite", "family_history": "depressao cronica na ammae"}	t
a5504657-77d0-433d-b30e-4fb83228743d	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	[]	[]	[]	20	2025-10-13 22:29:16.137889+00	2025-10-13 22:29:16.137889+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	f
4129fb87-38e9-4a7d-8345-7a0d7caea205	50b9da75-b20a-460e-994b-44e3036a23e4	priapismo	[]	[]	[]	4	2025-10-13 22:29:57.785581+00	2025-10-13 22:29:57.785581+00	asdf	{"diseases": "priapismo", "symptoms": null, "allergies": null, "medications": null, "family_history": "pressao"}	f
eb931554-58e2-4d71-8270-a4427f9d14bd	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	[]	[]	[]	21	2025-10-14 00:46:04.65044+00	2025-10-14 00:46:04.65044+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	f
b9fb7425-fb69-4c69-83b7-53d96b7f4207	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	Paciente relata transtorno da personalidade limítrofe.	["Aripiprazol 5mg Conforme prescrição"]	["Alergia à picada de abelha (Não informado)"]	["Paciente refere dor no cotovelo."]	6	2025-10-14 00:50:27.210975+00	2025-10-14 00:50:27.210975+00	Paciente nega histórico familiar de doenças.	{"diseases": "transtorno da personalidade limitrofe", "symptoms": "tenho dor no cotovelo", "allergies": "alergia a picada de abelha", "medications": "aripiprazol 5mg noite", "family_history": "depressao cronica na ammae"}	f
b00fcff4-03df-4187-8ad4-2ccf00fd581b	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	[]	[]	[]	22	2025-10-14 00:50:42.856818+00	2025-10-14 00:50:42.856818+00	Paciente nega histórico familiar de doenças.	{"diseases": "Triabetes", "symptoms": "Não sinto nada de mal.", "allergies": "todos os anti-infalatórios", "medications": "Rozucor 10mg à noite, versao 3", "family_history": "meu pai tem uma calcificação no cérebro e epilepsia"}	f
c1098453-028e-4f0a-8f55-16dceeac1356	47ec77d4-b2fd-49be-9d64-4db12563c89c	\N	[]	[]	[]	2	2025-10-14 00:50:51.464181+00	2025-10-14 00:50:51.464181+00	\N	{"diseases": null, "symptoms": null, "allergies": null, "medications": "Aas", "family_history": "Pressão alta pai"}	f
5f641a2b-d518-4afe-a300-df6a4d404beb	50b9da75-b20a-460e-994b-44e3036a23e4	Psicose	[]	["Veramil"]	[]	5	2025-10-14 01:00:56.082857+00	2025-10-14 01:00:56.082857+00	asdf	{"diseases": "Psicose", "symptoms": null, "allergies": "Veramil", "medications": null, "family_history": "pressao"}	t
bcfe23ce-c8d6-45e0-a8b7-935db0f4d76a	3eec1f34-8a20-4d2b-9511-6a6810dd7edd	\N	[]	["Tenho alergia a dramin e camarão"]	["To com dor de cabeça"]	1	2025-10-14 09:18:36.776751+00	2025-10-14 09:18:36.776751+00	\N	{"diseases": null, "symptoms": "To com dor de cabeça", "allergies": "Tenho alergia a dramin e camarão", "medications": null, "family_history": "Tenho doença celíaca"}	t
d387dc2e-40f8-4d34-a675-bcc738356046	3eec1f34-8a20-4d2b-9511-6a6810dd7edd	qualquer coisa	["vitamina d Conforme prescrição"]	["Tenho alergia a dramin e camarão"]	["To com dor de cabeça"]	2	2025-10-14 09:24:22.638013+00	2025-10-14 09:24:22.638013+00	doenca celiaca	{"diseases": null, "symptoms": "To com dor de cabeça", "allergies": "Tenho alergia a dramin e camarão", "medications": null, "family_history": "Tenho doença celíaca"}	f
2d475f75-b30c-4740-848f-f6d1c5218926	f30c2c82-0080-46dc-b2dc-7e95200b52b9	\N	["Velafaxina 150 Pregabalina 75 Levetiracetam 500"]	[]	[]	1	2025-10-14 12:06:23.542476+00	2025-10-14 12:06:23.542476+00	\N	{"diseases": null, "symptoms": null, "allergies": null, "medications": "Velafaxina 150\\nPregabalina 75\\nLevetiracetam 500", "family_history": null}	t
78a4017c-6fac-4e06-9e59-083968cf87e3	f30c2c82-0080-46dc-b2dc-7e95200b52b9	\N	[]	[]	[]	2	2025-10-14 12:20:16.255304+00	2025-10-14 12:20:16.255304+00	\N	{"diseases": null, "symptoms": null, "allergies": null, "medications": "Velafaxina 150\\nPregabalina 75\\nLevetiracetam 500", "family_history": null}	f
78ecd0db-d8b0-453f-b7b3-8fca939e194b	50b9da75-b20a-460e-994b-44e3036a23e4	Psicose	[]	[]	[]	6	2025-10-14 12:35:34.394+00	2025-10-14 12:35:34.394+00	asdf	{"diseases": null, "symptoms": null, "allergies": null, "medications": null, "family_history": null}	t
53a1b64b-3dbb-4599-bd24-245a069d6188	50b9da75-b20a-460e-994b-44e3036a23e4	Psicose	[]	[]	[]	7	2025-10-14 12:46:52.463468+00	2025-10-14 12:46:52.463468+00	asdf	{"diseases": null, "symptoms": null, "allergies": null, "medications": null, "family_history": null}	f
3f27568c-23e0-4427-95d3-02ba69a55a20	5e113a13-25ab-4812-acc2-0c675ac8b791	Triabetes	[]	[]	[]	23	2025-10-14 15:00:18.770363+00	2025-10-14 15:00:18.770363+00	Paciente nega histórico familiar de doenças.	{"diseases": null, "symptoms": null, "allergies": null, "medications": null, "family_history": null}	t
69624f46-f976-4a4f-9178-f4b19b1e1a53	9ebedb19-4b94-459d-87b6-3937e1c5a022	\N	[]	[]	[]	1	2025-10-14 15:02:34.107229+00	2025-10-14 15:02:34.107229+00	\N	{"diseases": null, "symptoms": null, "allergies": null, "medications": null, "family_history": null}	t
d9ac315e-df51-4fd7-b748-682dc8f9ab80	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	24	2025-10-14 15:20:37.302699+00	2025-10-14 15:20:37.302699+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
3cf7bca8-07e2-42cf-b186-31f46b173e5c	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	25	2025-10-14 15:32:20.834945+00	2025-10-14 15:32:20.834945+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
5bbbc043-5a09-446b-a4b7-2551bf1ae516	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	26	2025-10-14 15:37:55.1714+00	2025-10-14 15:37:55.1714+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
f1d3338d-1459-4ab5-978f-e28ba2bacea7	9f1a1a92-64fe-436e-8e0a-da0a3712f384	\N	[]	[]	[]	1	2025-10-14 16:06:46.744659+00	2025-10-14 16:06:46.744659+00	\N	{"diseases": null, "symptoms": null, "allergies": null, "medications": null, "family_history": null}	t
9d086d07-9ad6-4823-ab3d-36e86fcba2fe	d7735997-acf6-4269-85cc-0eb205ae8fcf	Pressão alta	["Magnem b6 Conforme prescrição"]	["Camarão"]	["Nega sintomas atuais"]	1	2025-10-14 16:11:35.091428+00	2025-10-14 16:11:35.091428+00	\N	{"diseases": "Pressão alta", "symptoms": "Nega sintomas atuais", "allergies": "Camarão", "medications": "Magnem b6", "family_history": "Nega histórico familiar de doenças graves"}	t
a5ea4bbb-b389-4bdd-a9f4-c33acbade619	d7735997-acf6-4269-85cc-0eb205ae8fcf	Pressão alta	["Magnem b6 Conforme prescrição"]	["Camarão"]	["Nega sintomas atuais"]	2	2025-10-14 16:13:33.205757+00	2025-10-14 16:13:33.205757+00	\N	{"diseases": "Pressão alta", "symptoms": "Nega sintomas atuais", "allergies": "Camarão", "medications": "Magnem b6", "family_history": "Nega histórico familiar de doenças graves"}	t
b559b346-c7aa-4d9b-8da2-f206e2b5775b	d7735997-acf6-4269-85cc-0eb205ae8fcf	Pressão alta	["Magnem b6 Conforme prescrição"]	["Camarão"]	["Nega sintomas atuais"]	3	2025-10-14 16:31:45.041447+00	2025-10-14 16:31:45.041447+00	\N	{"diseases": "Pressão alta", "symptoms": "Nega sintomas atuais", "allergies": "Camarão", "medications": "Magnem b6", "family_history": "Nega histórico familiar de doenças graves"}	t
46eab41c-fd40-4166-bb3c-62b35f5ea6d1	d7735997-acf6-4269-85cc-0eb205ae8fcf	Pressão alta	["Magnem b6 Conforme prescrição"]	["Camarão"]	["Nega sintomas atuais"]	4	2025-10-14 16:36:49.940395+00	2025-10-14 16:36:49.940395+00	\N	{"diseases": "Pressão alta", "symptoms": "Nega sintomas atuais", "allergies": "Camarão", "medications": "Magnem b6", "family_history": "Nega histórico familiar de doenças graves"}	t
6c9306cf-f5c9-4814-bd74-18c53060b37d	5e113a13-25ab-4812-acc2-0c675ac8b791	Diabetes mellitus	["Capitaobril 20mg Conforme prescrição"]	["Contraste de tomografia (Não informado)"]	["Paciente refere dor abdominal."]	27	2025-10-15 09:52:04.951405+00	2025-10-15 09:52:04.951405+00	Paciente nega histórico familiar de doenças.	{"diseases": "Acúcar Alto no sangue", "symptoms": "Dor na boca do estomago", "allergies": "Contraste de tomografia", "medications": "Capitaobril 20mg 12/12 horas.", "family_history": "Minha mae tem plaquetas baixas"}	t
41da9789-2bb0-4500-b03e-0bf8d1d223d5	5e113a13-25ab-4812-acc2-0c675ac8b791	Diabetes mellitus	["Capitaobril 20mg Conforme prescrição"]	["Contraste de tomografia (Não informado)"]	["Paciente refere dor abdominal."]	28	2025-10-15 10:57:51.596999+00	2025-10-15 10:57:51.596999+00	Paciente nega histórico familiar de doenças.	{"diseases": "Acúcar Alto no sangue", "symptoms": "Dor na boca do estomago", "allergies": "Contraste de tomografia", "medications": "Capitaobril 20mg 12/12 horas.", "family_history": "Minha mae tem plaquetas baixas"}	t
9f569b54-489f-4205-948d-b71bd9ba0676	50b9da75-b20a-460e-994b-44e3036a23e4	Psicose	[]	[]	[]	8	2025-10-15 11:15:57.348675+00	2025-10-15 11:15:57.348675+00	asdf	{"diseases": null, "symptoms": null, "allergies": null, "medications": null, "family_history": null}	f
ca05d08e-93df-4343-92d1-014013fedb8d	50b9da75-b20a-460e-994b-44e3036a23e4	Psicose	[]	[]	[]	9	2025-10-15 11:16:26.278482+00	2025-10-15 11:16:26.278482+00	asdf	{"diseases": null, "symptoms": null, "allergies": null, "medications": null, "family_history": null}	f
f1f33135-ccc3-4281-91e4-658b78e09fb0	f5951f3a-81ec-4306-9386-8c5447b85d37	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 13:52:12.54737+00	2025-10-15 13:52:12.54737+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
d52046ee-4f13-4621-9fd4-f7b2bc75bcd6	7936624c-1098-499f-94b8-cffd2ac4f54b	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 13:58:57.710919+00	2025-10-15 13:58:57.710919+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
39752286-3abb-490c-9c00-48aac9be6e38	239ecb59-8b13-4153-9d29-8dfa5b95f7bc	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 13:59:16.705842+00	2025-10-15 13:59:16.705842+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
f457adab-fe8b-42c3-8974-32be2cc4359f	3485804f-1a36-4b50-a02d-ccb315d2b461	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.085974+00	2025-10-15 14:05:17.085974+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
2689c17d-62d6-423c-8060-5fb6b7d40ac0	963caad9-2d82-4f00-a5e5-8147b46f3920	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.095416+00	2025-10-15 14:05:17.095416+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
3509d762-1c29-4d10-b8c6-0a2d3c1d8251	16ab8fd2-7bdc-454b-8308-2367a6b09e9f	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.101628+00	2025-10-15 14:05:17.101628+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
d9519345-886e-4874-8217-4163a9e74bf0	2fcc5bda-7f19-4cd9-881b-4f827d60f407	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.105932+00	2025-10-15 14:05:17.105932+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
ac930c6f-10a0-46d9-897c-1a7e0560dce9	c7baf2d9-0deb-400e-b296-ecdb4a847e2f	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.110008+00	2025-10-15 14:05:17.110008+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
b94e7f61-f052-4065-83fb-71fba1f2ab44	81f8bfbc-9554-4887-b16a-e454dd3afbe0	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.114273+00	2025-10-15 14:05:17.114273+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
0a2b2203-369f-478c-bfcc-b574b4736284	728ae353-5f7e-46be-88ce-dd0f8604c05e	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.118825+00	2025-10-15 14:05:17.118825+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
9bcb9afe-595b-4ded-a24e-6e8bc9787b7e	34284dd7-e3d1-4dae-b6c0-222b1ea8ca73	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.122921+00	2025-10-15 14:05:17.122921+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
9f9b02f1-f781-49b9-a8cf-3391d963374f	47a12dc4-be21-4441-815e-f0dc61ba7dfe	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.126961+00	2025-10-15 14:05:17.126961+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
68995c38-b61e-439b-9df4-69eb16cd53bd	e7dfdecb-56f7-4d3e-99a8-bc78ae204a54	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.13637+00	2025-10-15 14:05:17.13637+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
7be821ba-f5ff-4232-bea6-186ae30cce6d	71c5bfec-252a-43de-92cc-43aedf3b5a2b	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.144677+00	2025-10-15 14:05:17.144677+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
f7cb7065-45ce-4acc-9c97-1d46feba7b54	1e0730e8-4008-4cb2-bdcb-931ec80a2f9a	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.152949+00	2025-10-15 14:05:17.152949+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
6db3d7bc-7074-4b46-87fb-ad0c4417ace4	1814bae2-323e-435b-8251-abbd630bf9cf	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.161297+00	2025-10-15 14:05:17.161297+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
218be9bf-fd17-4c2e-96f1-14eb29458d70	bbeee273-c4bd-49cb-bb06-2aa97182e058	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.169821+00	2025-10-15 14:05:17.169821+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
52eab59e-e0f3-4909-9efb-0449b312468f	0340b8d8-107d-4a3d-a9ca-bb09931233ba	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.132272+00	2025-10-15 14:05:17.132272+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
9c4e52db-82e4-464f-b774-b9f4cb402a11	f1305093-9d41-4ecb-8bf7-6c210f5e83b2	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.140609+00	2025-10-15 14:05:17.140609+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
18fe41ef-0daf-4a84-8a3c-04da756af657	2e08f168-d8bd-4236-8f0f-61e143b7e922	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.148882+00	2025-10-15 14:05:17.148882+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
fa0bd47e-0165-4bc3-aeec-76ab42608480	b6d5e3f4-98b8-4a06-993d-eedce758064b	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.157303+00	2025-10-15 14:05:17.157303+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
3d3980b6-8d19-4b91-a22b-5a2c545e6439	e616ccf2-3cac-4958-93b3-45e2039f0a1c	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.165967+00	2025-10-15 14:05:17.165967+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
a6bd44a7-8a6e-4b97-bd92-65ed1c5796d2	131fe8e5-e698-4b81-a18e-c8646abf46bd	Hipertensão, Diabetes Tipo 2	["Losartana 50mg", "Metformina 850mg"]	["Penicilina", "Dipirona"]	["Dor de cabeça", "Pressão alta"]	1	2025-10-15 14:05:17.173798+00	2025-10-15 14:05:17.173798+00	Pai com histórico de hipertensão, mãe com diabetes	\N	f
ddcae9bf-7162-45b4-8044-454fdb68334e	d7735997-acf6-4269-85cc-0eb205ae8fcf	Pressão alta	["Magnem b6 Conforme prescrição"]	["Camarão"]	["Nega sintomas atuais"]	5	2025-10-15 14:28:33.800661+00	2025-10-15 14:28:33.800661+00	\N	{"diseases": "Pressão alta", "symptoms": "Nega sintomas atuais", "allergies": "Camarão", "medications": "Magnem b6", "family_history": "Nega histórico familiar de doenças graves"}	f
f9e3f7ad-adef-4a31-acfe-15973761abfe	5e113a13-25ab-4812-acc2-0c675ac8b791	Diabetes mellitus	["Capitaobril 20mg Conforme prescrição"]	["Contraste de tomografia (Não informado)"]	["Paciente refere dor abdominal."]	29	2025-10-16 09:39:19.133984+00	2025-10-16 09:39:19.133984+00	Paciente nega histórico familiar de doenças.	{"diseases": "Acúcar Alto no sangue", "symptoms": "Dor na boca do estomago", "allergies": "Contraste de tomografia", "medications": "Capitaobril 20mg 12/12 horas.", "family_history": "Minha mae tem plaquetas baixas"}	t
18dcda57-8888-41ad-97a5-5367e4eaf87b	5e113a13-25ab-4812-acc2-0c675ac8b791	Diabetes mellitus	[]	[]	[]	30	2025-10-17 22:10:49.412624+00	2025-10-17 22:10:49.412624+00	Paciente nega histórico familiar de doenças.	{"diseases": null, "symptoms": null, "allergies": null, "medications": null, "family_history": null}	t
356f3094-0c62-462a-81d4-1302d902e54a	5e113a13-25ab-4812-acc2-0c675ac8b791	Diabetes mellitus	[]	[]	[]	31	2025-10-17 23:08:15.035594+00	2025-10-17 23:08:15.035594+00	Paciente nega histórico familiar de doenças.	{"diseases": null, "symptoms": null, "allergies": null, "medications": null, "family_history": null}	t
d8584ddb-8880-4f4c-8612-f915649ca2df	5e113a13-25ab-4812-acc2-0c675ac8b791	Diabetes mellitus	[]	[]	[]	32	2025-10-17 23:19:07.94655+00	2025-10-17 23:19:07.94655+00	Paciente nega histórico familiar de doenças.	{"diseases": null, "symptoms": null, "allergies": null, "medications": null, "family_history": null}	t
2627240b-22d8-4d15-a72f-6c47fce38886	5e113a13-25ab-4812-acc2-0c675ac8b791	Diabetes mellitus	[]	[]	[]	33	2025-10-17 23:23:50.745721+00	2025-10-17 23:23:50.745721+00	Paciente nega histórico familiar de doenças.	{"diseases": null, "symptoms": null, "allergies": null, "medications": null, "family_history": null}	t
052d8794-9fd4-4b12-aee4-d33c48553b51	5e113a13-25ab-4812-acc2-0c675ac8b791	Diabetes mellitus	[]	[]	[]	34	2025-10-17 23:28:56.814511+00	2025-10-17 23:28:56.814511+00	Paciente nega histórico familiar de doenças.	{"diseases": null, "symptoms": null, "allergies": null, "medications": null, "family_history": null}	t
4be2fd18-2db1-4f47-861f-cb64be199162	5e113a13-25ab-4812-acc2-0c675ac8b791	Diabetes mellitus	[]	[]	[]	35	2025-10-17 23:33:57.313942+00	2025-10-17 23:33:57.313942+00	Paciente nega histórico familiar de doenças.	{"diseases": null, "symptoms": null, "allergies": null, "medications": null, "family_history": null}	t
7a1c1e39-35b3-47ff-bfdd-ed6c1d3d78d8	2b635923-f6c4-435a-9054-156c2113888f	Paciente nega doenças prévias.	[]	[]	[]	3	2025-10-21 11:14:35.702294+00	2025-10-21 11:14:35.702294+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	f
61f04e64-6a36-4c90-a5e9-4e3ca74e2679	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	36	2025-10-18 00:29:57.623012+00	2025-10-18 00:29:57.623012+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
d7fd19ca-966c-4b73-a6f4-b9f9f9c52382	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	37	2025-10-18 11:23:26.355347+00	2025-10-18 11:23:26.355347+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
1297a487-e0f3-44c1-bee8-db989664376b	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	38	2025-10-18 11:44:38.031056+00	2025-10-18 11:44:38.031056+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
d7ef6ae7-9fb7-453e-a28b-9834ac8f7a3e	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	[]	[]	[]	39	2025-10-18 11:53:44.424823+00	2025-10-18 11:53:44.424823+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	f
b605670b-f83b-4b41-a985-7dc6ff8fed20	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	[]	[]	[]	40	2025-10-18 12:04:31.054507+00	2025-10-18 12:04:31.054507+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	f
e7d32029-be94-4e0f-98e8-c7781ecb247d	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	41	2025-10-18 12:10:44.512971+00	2025-10-18 12:10:44.512971+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
e0ab3b65-150a-4f7b-855d-ea7bed712348	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	[]	[]	[]	42	2025-10-18 12:12:23.226634+00	2025-10-18 12:12:23.226634+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	f
dd61dd98-734c-4096-b5d4-d908848c0b9c	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	43	2025-10-18 12:18:01.544352+00	2025-10-18 12:18:01.544352+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
4e0787af-2e6b-4ada-acfd-9184f2769b98	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	[]	[]	[]	44	2025-10-18 12:19:40.049261+00	2025-10-18 12:19:40.049261+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	f
063edfb7-f1e4-47c4-a5a0-368ba540dff9	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	45	2025-10-18 16:47:17.83791+00	2025-10-18 16:47:17.83791+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
996d3227-7e1b-49b4-9a31-c201487fc971	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	46	2025-10-18 17:02:10.098842+00	2025-10-18 17:02:10.098842+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
92ff8ad6-288c-40b0-b5d6-5a4e2758ad04	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	47	2025-10-18 17:30:18.395609+00	2025-10-18 17:30:18.395609+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
92540e71-9195-449b-8d1f-6925e7f6d9b3	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	[]	[]	[]	48	2025-10-18 17:56:31.246866+00	2025-10-18 17:56:31.246866+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	f
e5ab776f-b6a6-4ceb-affa-3cbffb99d62d	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	49	2025-10-19 06:43:53.273613+00	2025-10-19 06:43:53.273613+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
a55aa716-f36f-4da2-b06b-60e651fe6e01	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	50	2025-10-19 07:51:43.90633+00	2025-10-19 07:51:43.90633+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
272842a7-bd6f-4e2d-80b1-571d752740e3	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	[]	[]	[]	51	2025-10-19 07:53:36.541648+00	2025-10-19 07:53:36.541648+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	f
08c27ba4-76b6-4a33-9d8c-0a05328d479a	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	52	2025-10-19 11:10:00.60036+00	2025-10-19 11:10:00.60036+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
4cdefcf7-b716-4497-982b-045c635e85a7	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	[]	[]	[]	53	2025-10-19 11:16:37.12451+00	2025-10-19 11:16:37.12451+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	f
24d3c1ec-9878-48e9-bd0c-51ce72bda145	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	54	2025-10-19 12:50:39.815796+00	2025-10-19 12:50:39.815796+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
b154bd52-f040-4ca0-a44f-3710152b68ec	3db328c8-da70-418c-a245-d01175590664	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	1	2025-10-19 14:48:45.857763+00	2025-10-19 14:48:45.857763+00	\N	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
30bfd25b-c726-4630-8217-3f4cbeabd61d	3db328c8-da70-418c-a245-d01175590664	Nega doenças prévias	[]	[]	[]	2	2025-10-19 15:12:34.097008+00	2025-10-19 15:12:34.097008+00	\N	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	f
316005b0-6bd1-4c26-a46f-c0bd13c6b32d	8e31833e-effe-4867-9965-9a346c850b72	Diabetes	["Alopurinol 100mg Pitavastatina 4 mg"]	["Nega alergias"]	["Nega sintomas atuais"]	1	2025-10-19 22:32:38.918063+00	2025-10-19 22:32:38.918063+00	\N	{"diseases": "Diabetes", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Alopurinol 100mg\\nPitavastatina 4 mg", "family_history": "Mãe com diabetes"}	t
ddbfdd8d-b5d4-4262-a438-d4be9dea76d7	8e31833e-effe-4867-9965-9a346c850b72	Diabetes	[]	[]	[]	2	2025-10-19 22:47:37.608383+00	2025-10-19 22:47:37.608383+00	\N	{"diseases": "Diabetes", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Alopurinol 100mg\\nPitavastatina 4 mg", "family_history": "Mãe com diabetes"}	f
0f1f1ac3-49e5-4e20-8b3b-c2a726f72483	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	55	2025-10-20 11:05:50.629724+00	2025-10-20 11:05:50.629724+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
93b94728-c609-4516-b3c1-9d0a0900bdaf	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	[]	[]	[]	56	2025-10-20 11:22:17.122954+00	2025-10-20 11:22:17.122954+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	f
e22ac097-d2d6-43af-9306-acab43d542bd	75ffc611-f82c-43cf-bf3e-bbf75123b7aa	Asma e Glaucoma	["Captopril 10mg 12/12 horas. Losartana 50mg 12/12 horas", "Vitamina B12 100mg noite", "Lebotiroxina 25mcg manha"]	["Contrate de ressolança"]	["Dor nas pé da barriga"]	1	2025-10-20 23:03:44.116004+00	2025-10-20 23:32:30.176274+00	Mãe com diabetes	{"diseases": "Asma e Glaucoma", "symptoms": "Dor nas pé da barriga", "allergies": "Contrate de ressolança", "medications": "Captopril 10mg 12/12 horas. Losartana 50mg 12/12 horas, Vitamina B12 100mg noite, Lebotiroxina 25mcg manha", "family_history": "Mãe com diabetes"}	t
0a774fde-8e33-4a4b-8131-917495427eab	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	57	2025-10-20 23:49:59.757551+00	2025-10-20 23:49:59.757551+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "pae com demencia"}	t
b1f8c970-9fa7-45ec-a416-54b551bc748e	5e113a13-25ab-4812-acc2-0c675ac8b791	Paciente relata asma.	["Paciente nega uso de medicamentos."]	["Paciente nega alergias."]	["Paciente nega sintomas atuais."]	58	2025-10-21 00:09:00.847743+00	2025-10-21 00:09:00.847743+00	Paciente nega histórico familiar de doenças.	{"diseases": "asma", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "465", "family_history": "mae com anuerisma e calcificacao celebral"}	t
4c0e7986-b897-4236-bf4f-76218c82383f	a6fe8ce5-c9a9-4f1e-a698-c7d834256762	Paciente relata diabetes mellitus., Paciente relata hipertensão arterial.	["Paciente nega uso de medicamentos."]	["Paciente nega alergias."]	["Paciente nega sintomas atuais."]	1	2025-10-21 01:09:37.226311+00	2025-10-21 01:09:37.226311+00	Paciente nega histórico familiar de doenças.	{"diseases": "Diabetes / Hipertensão", "symptoms": "Nega sintomas atuais", "allergies": "Nenhum", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Pai câncer"}	t
1a637265-636c-4887-b129-5b436afd0e34	a6fe8ce5-c9a9-4f1e-a698-c7d834256762	Paciente relata diabetes mellitus., Paciente relata hipertensão arterial.	[]	[]	[]	2	2025-10-21 01:12:48.297431+00	2025-10-21 01:12:48.297431+00	Paciente nega histórico familiar de doenças.	{"diseases": "Diabetes / Hipertensão", "symptoms": "Nega sintomas atuais", "allergies": "Nenhum", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Pai câncer"}	f
50aa6b31-ecc5-4955-9a1b-8ef2248a8e81	2b635923-f6c4-435a-9054-156c2113888f	Paciente nega doenças prévias.	["Paciente nega uso de medicamentos."]	["Paciente nega alergias."]	["Paciente refere ausência de sintomas no momento."]	1	2025-10-21 10:46:12.439698+00	2025-10-21 10:46:12.439698+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
03b2ad09-79ed-413b-ba5e-07e8bd8f838b	5e113a13-25ab-4812-acc2-0c675ac8b791	Paciente relata asma.	["Paciente nega uso de medicamentos."]	["Paciente nega alergias."]	["Paciente nega sintomas atuais."]	59	2025-10-21 11:00:50.760714+00	2025-10-21 11:00:50.760714+00	Paciente nega histórico familiar de doenças.	{"diseases": "pressao alta", "symptoms": "dor no pe", "allergies": "Nega alergias", "medications": "losartana", "family_history": "mae com diagetes"}	t
b56b5ad1-4cae-41fd-89ce-a1dfa8535e7a	f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0	Pressão alta	["Aas"]	["Nega alergias"]	["Dor de cotovelo"]	1	2025-10-21 11:25:23.113147+00	2025-10-21 11:25:23.113147+00	\N	{"diseases": "Pressão alta", "symptoms": "Dor de cotovelo", "allergies": "Nega alergias", "medications": "Aas", "family_history": "Alzeimer"}	t
79d8f025-5bbf-4c35-9e4b-1df9b466407d	70d8611d-95a8-4a51-8863-ec56e5af01e9	Test medical background	["Test medication Conforme prescrição"]	["Test allergy"]	["Test symptom"]	1	2025-11-01 17:59:45.649535+00	2025-11-01 17:59:45.649535+00	\N	\N	t
bc2721b7-511d-4079-9e48-8df88dc44751	5e113a13-25ab-4812-acc2-0c675ac8b791	Paciente relata hipertensão arterial.	["Losartana"]	["Paciente nega alergias."]	["Paciente refere dor no pé."]	60	2025-10-21 11:51:30.625486+00	2025-10-21 11:51:30.625486+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "PSORIASE, URTICARIA, HEMORROIDA TROMBOSADA, AVC, INFARTO, DEMENCIA, NEUROCISTICERCOSE"}	t
c7ff2e37-8d60-48e3-876a-8c689a3e6655	5e113a13-25ab-4812-acc2-0c675ac8b791	Paciente nega doenças prévias.	["Paciente nega uso de medicamentos."]	["Paciente nega alergias."]	["Paciente nega sintomas atuais."]	61	2025-10-21 11:57:10.654669+00	2025-10-21 11:57:10.654669+00	Paciente nega histórico familiar de doenças.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "URTICARIA, DIABETES, PSORIASE, AVC, ALCHEIMER, EPILESIA"}	t
99906368-963d-4595-a942-dcbebfb16f3d	5e113a13-25ab-4812-acc2-0c675ac8b791	Paciente nega doenças prévias.	["Paciente nega uso de medicamentos."]	["Paciente nega alergias. ()"]	["Paciente nega sintomas atuais."]	62	2025-10-21 12:12:59.474652+00	2025-10-21 12:16:04.205065+00	Paciente relata histórico familiar de Alzheimer.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "ALZEIMAR"}	f
2202d18b-3089-4fa5-84e7-42978f3f2c76	f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0	Pressão alta	[]	[]	[]	2	2025-10-21 12:23:05.836022+00	2025-10-21 12:23:05.836022+00	\N	{"diseases": "Pressão alta", "symptoms": "Dor de cotovelo", "allergies": "Nega alergias", "medications": "Aas", "family_history": "Alzeimer"}	f
779162bd-cd20-4977-87df-dbb33f58ab91	584648e5-0c1d-44f9-aa12-8cde21c2e4d2	ICC	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	1	2025-10-21 14:39:59.965997+00	2025-10-21 14:39:59.965997+00	Nega histórico familiar de doenças graves	{"diseases": "ICC", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
40f07747-c61a-4a60-8572-f828ed2a85b5	5e113a13-25ab-4812-acc2-0c675ac8b791	Paciente nega doenças prévias.	["Paciente nega uso de medicamentos."]	["Paciente nega alergias. ()"]	["Paciente nega sintomas atuais."]	63	2025-10-22 09:53:50.110878+00	2025-10-22 09:53:50.110878+00	Paciente relata histórico familiar de Alzheimer.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "ALZEIMAR"}	t
e2d8b3ab-d167-4bae-9980-fde5f578fc84	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	64	2025-10-26 11:18:49.972353+00	2025-10-26 11:18:49.972353+00	Paciente relata histórico familiar de Alzheimer.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "ALZEIMAR"}	t
f43f799e-99d4-440f-ad59-cd86ba2e263d	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	65	2025-10-28 06:23:56.671273+00	2025-10-28 06:23:56.671273+00	Paciente relata histórico familiar de Alzheimer.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
84b2a5ce-c550-4b4b-8a55-1b09613b0d32	c3c0dec3-68e6-493b-b838-2e82f9dbf038	Initial medical background	["Initial medication Conforme prescrição"]	["Initial allergy"]	["Initial symptom"]	1	2025-11-02 10:27:59.772505+00	2025-11-02 10:27:59.772505+00	\N	\N	t
b8fad1cb-4d45-4726-8c01-abe556054ef2	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	66	2025-10-31 12:09:47.017667+00	2025-10-31 12:09:47.017667+00	Paciente relata histórico familiar de Alzheimer.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
28dd0ae9-42d8-471a-b45e-a398dbc2d8b8	06dc44dc-6e11-487a-ad17-47880a259014	Test medical background	["Test medication Conforme prescrição"]	["Test allergy"]	["Test symptom"]	1	2025-11-02 10:27:59.776791+00	2025-11-02 10:27:59.776791+00	\N	\N	t
40fedb98-63b3-4c91-9088-39ee29aab896	5e113a13-25ab-4812-acc2-0c675ac8b791	Nega doenças prévias	["Nega uso de medicações de uso contínuo além da prescrita hoje"]	["Nega alergias"]	["Nega sintomas atuais"]	67	2025-10-31 12:35:11.147242+00	2025-10-31 12:35:11.147242+00	Paciente relata histórico familiar de Alzheimer.	{"diseases": "Nega doenças prévias", "symptoms": "Nega sintomas atuais", "allergies": "Nega alergias", "medications": "Nega uso de medicações de uso contínuo além da prescrita hoje", "family_history": "Nega histórico familiar de doenças graves"}	t
c37eaf41-dd66-4e5c-83bc-60b4d9034d34	34f10a7b-681e-44fa-9123-22c11d02de5d	Patient has family history of diabetes and hypertension	["Losartan 50mg once daily", "Metformin 500mg twice daily"]	["Penicillin", "Sulfonamides"]	["Chest pain", "Dyspnea on exertion"]	1	2025-11-02 10:28:00.073653+00	2025-11-02 10:28:00.073653+00	\N	\N	t
c6b3525a-8346-49d1-aa94-290e47bcee52	801a14c3-2c68-41a8-bc5f-a3549f7a745a	Patient has family history of diabetes and hypertension	["Losartan 50mg once daily", "Metformin 500mg twice daily"]	["Penicillin", "Sulfonamides"]	["Chest pain", "Dyspnea on exertion"]	1	2025-11-01 17:59:45.636076+00	2025-11-01 17:59:45.636076+00	\N	\N	t
3a63613e-14b6-479c-a3a6-f631b648d8dc	acb2d41a-214a-4aa9-ab27-7eb5c47858ec	Histórico familiar de diabetes tipo 2. Paciente com estilo de vida sedentário.	["Losartana 50mg 1x ao dia pela manhã", "Metformina 500mg 2x ao dia"]	["Penicilina", "Sulfonamidas"]	["Dor torácica esforço-relacionada", "Dispneia aos esforços"]	1	2025-11-01 17:59:45.633566+00	2025-11-01 17:59:45.633566+00	\N	\N	t
05b1faf1-41c0-4e83-bf28-144f7efe4349	0df6094a-f34d-498c-b0d0-7a53134a84a1	Initial medical background	["Initial medication Conforme prescrição"]	["Initial allergy"]	["Initial symptom"]	1	2025-11-01 17:59:45.63453+00	2025-11-01 17:59:45.63453+00	\N	\N	t
411e85df-43f5-4ce6-ad54-1f5a84b8147e	952dbb3e-a655-4211-a202-14b9c14d0a49	Test medical background for prescription renewal	["Test medication dosage"]	["Test allergy"]	["Test symptom"]	1	2025-11-01 17:59:45.638838+00	2025-11-01 17:59:45.638838+00	\N	\N	t
\.


--
-- TOC entry 5139 (class 0 OID 25145)
-- Dependencies: 234
-- Data for Name: ocr_jobs; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.ocr_jobs (job_id, conversation_id, photo_id, status, result, attempts, error_message, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5140 (class 0 OID 25156)
-- Dependencies: 235
-- Data for Name: password_recovery_tokens; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.password_recovery_tokens (id, user_id, token, expires_at, created_at, used_at) FROM stdin;
2e21ef40-db99-4448-9585-49c2ccda0269	ec650cd5-7ea6-4066-85a3-37d3a6f17270	a96df70e-287e-4570-9fd5-e727b2f97cb3	2025-10-22 09:18:36.060486+00	2025-10-22 08:18:36.060486+00	\N
032d1c00-b0df-479e-9f4d-5adfdca8a870	6a32a357-daf5-4459-b82c-645299b23bc0	a64a7446-8c59-4017-ba73-1273aaddde90	2025-10-28 13:13:08.651149+00	2025-10-28 12:13:08.651149+00	\N
4eb57acf-4a2a-4578-bfa8-052a961cdb47	4f8929c1-d6b1-4e41-a940-981f6a589ece	68f1c92c-fd70-4128-937e-64938bb19fed	2025-10-28 13:14:40.77095+00	2025-10-28 12:14:40.77095+00	2025-10-28 12:16:18.52706+00
\.


--
-- TOC entry 5141 (class 0 OID 25163)
-- Dependencies: 236
-- Data for Name: patient_phones; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.patient_phones (id, patient_id, phone, verified_at, is_primary, created_at, updated_at) FROM stdin;
d600c6d5-36c9-4ab8-bcdc-aacc39a40987	eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	4915158832107	2025-10-13 00:42:01.763703+00	t	2025-10-13 00:42:01.763843+00	2025-10-14 00:50:27.210975+00
a7dbb3e6-4114-4742-8d7d-fdc4ab913417	47ec77d4-b2fd-49be-9d64-4db12563c89c	5511982033818	2025-10-13 14:07:37.749273+00	t	2025-10-13 14:07:37.749429+00	2025-10-14 00:50:51.464181+00
7424de0a-7798-423a-99d6-74b6d4302b21	3eec1f34-8a20-4d2b-9511-6a6810dd7edd	4915775035320	2025-10-14 09:15:47.80449+00	t	2025-10-14 09:15:47.828873+00	2025-10-14 09:24:22.638013+00
6c5fe65f-25c1-4a1f-9b4e-ace0f4bdbbc2	75ffc611-f82c-43cf-bf3e-bbf75123b7aa	4915158832107	2025-10-20 23:01:17.664453+00	t	2025-10-20 23:01:17.664589+00	2025-10-20 23:03:44.116004+00
9eb5f14f-b330-4919-859d-12a9f8056baa	f30c2c82-0080-46dc-b2dc-7e95200b52b9	5511982033818	2025-10-14 12:01:51.395962+00	t	2025-10-14 12:01:51.396128+00	2025-10-14 12:20:16.255304+00
9ced3bcd-70df-4128-9d82-06664fe51a2d	abdb491c-dc08-40b1-826b-95a28c01b0a1	4915158832107	2025-10-21 00:05:12.397239+00	t	2025-10-21 00:05:12.397422+00	2025-10-21 00:05:12.397422+00
92d1a4f7-9fd4-47de-9646-c5a208727847	9ebedb19-4b94-459d-87b6-3937e1c5a022	4915158832107	2025-10-14 15:01:23.737639+00	t	2025-10-14 15:01:23.737797+00	2025-10-14 15:02:34.107229+00
95fdea21-26ac-4fe6-97b9-d7da155a6d35	f3cba6ba-d588-40d9-9d94-aa2472717811	4915158832107	2025-10-12 21:00:03.840427+00	t	2025-10-12 21:00:03.840589+00	2025-10-12 21:00:03.840589+00
1c4bae66-6159-4f2b-a613-41f4c313988c	d5dd3752-c9ce-4a6b-95c8-63a26a42f420	4915158832107	2025-10-12 21:04:22.735521+00	t	2025-10-12 21:04:22.735686+00	2025-10-12 21:04:22.735686+00
c9b78a7e-0a67-4002-bc64-c57a7ddcb5fd	0a210e3b-ed53-413d-a343-16c667aefa64	4915158832107	2025-10-12 21:08:23.650394+00	t	2025-10-12 21:08:23.650552+00	2025-10-12 21:09:52.332485+00
9bfbbba3-21d3-4c2e-a81f-25fe75a3c8b6	57873e19-e1d2-42c4-990c-cf8a420e2a35	4915158832107	2025-10-12 21:15:03.369017+00	t	2025-10-12 21:15:03.369141+00	2025-10-13 00:41:12.030855+00
bc13caab-4689-4e21-9bfe-b67e8e3113f0	63d47959-4742-460b-ae5a-5aeb982d4f91	4915158832107	2025-10-14 15:10:34.972958+00	t	2025-10-14 15:10:34.973113+00	2025-10-14 15:12:11.419602+00
6e423ec2-0d78-429b-a39d-d8c73bf5e87a	a6fe8ce5-c9a9-4f1e-a698-c7d834256762	553599576711	2025-10-21 01:00:42.355151+00	t	2025-10-21 01:00:42.378993+00	2025-10-21 01:12:48.297431+00
8746314b-7f1c-4f1e-95e9-0fc35ac1efff	9f1a1a92-64fe-436e-8e0a-da0a3712f384	4915158832107	2025-10-14 16:04:00.450873+00	t	2025-10-14 16:04:00.451019+00	2025-10-14 16:06:46.744659+00
55c7870b-fc0d-42be-a0ea-b4c055434997	2b635923-f6c4-435a-9054-156c2113888f	5511982033818	2025-10-21 10:43:58.8553+00	t	2025-10-21 10:43:58.879975+00	2025-10-21 11:14:35.702294+00
6e7a67e6-0045-41b1-87f8-603e9f0f9e90	50b9da75-b20a-460e-994b-44e3036a23e4	5511982033818	2025-10-13 15:00:23.913404+00	t	2025-10-13 15:00:23.913557+00	2025-10-15 11:16:26.278482+00
de19208c-da9f-405d-9759-0a2afc41b2a5	f5951f3a-81ec-4306-9386-8c5447b85d37	+5511920735867	2025-10-15 13:52:12.516436+00	t	2025-10-15 13:52:12.516436+00	2025-10-15 13:52:12.516436+00
2f161542-39c1-4ec1-8f5e-0e5768d85643	7936624c-1098-499f-94b8-cffd2ac4f54b	+5511992090754	2025-10-15 13:58:57.679461+00	t	2025-10-15 13:58:57.679461+00	2025-10-15 13:58:57.679461+00
a2f13aeb-2c78-4d7b-b19c-a61a88328a21	239ecb59-8b13-4153-9d29-8dfa5b95f7bc	+5511940042246	2025-10-15 13:59:16.674126+00	t	2025-10-15 13:59:16.674126+00	2025-10-15 13:59:16.674126+00
615841bd-d5ce-4300-9a8b-7b89371eb4bd	3485804f-1a36-4b50-a02d-ccb315d2b461	+5511927513504	2025-10-15 14:05:17.054738+00	t	2025-10-15 14:05:17.054738+00	2025-10-15 14:05:17.054738+00
89a09516-0710-4316-b826-1bc533a2ff6a	963caad9-2d82-4f00-a5e5-8147b46f3920	+5511924343877	2025-10-15 14:05:17.0911+00	t	2025-10-15 14:05:17.0911+00	2025-10-15 14:05:17.0911+00
bb848355-894c-407b-ad23-2a60e3db7c34	16ab8fd2-7bdc-454b-8308-2367a6b09e9f	+5511970436773	2025-10-15 14:05:17.099826+00	t	2025-10-15 14:05:17.099826+00	2025-10-15 14:05:17.099826+00
fe0bcedc-5957-4a6b-82ee-8e3ceb68dfb6	2fcc5bda-7f19-4cd9-881b-4f827d60f407	+5511963931661	2025-10-15 14:05:17.103923+00	t	2025-10-15 14:05:17.103923+00	2025-10-15 14:05:17.103923+00
7ccfc202-514d-4382-a551-77e1cab6b9ee	0c89a6ff-6598-400e-affb-47ccc3979761	553584687005	2025-10-21 11:31:26.644312+00	t	2025-10-21 11:31:26.644463+00	2025-10-21 11:31:26.644463+00
27e3b0d3-0081-46aa-ae85-90e69dac11a5	c7baf2d9-0deb-400e-b296-ecdb4a847e2f	+5511987393331	2025-10-15 14:05:17.108208+00	t	2025-10-15 14:05:17.108208+00	2025-10-15 14:05:17.108208+00
b6406e50-dbb3-499c-9a3e-fdfac3918821	9fe0af44-5e3d-42d0-9144-ab175099d699	4915158832107	2025-10-13 15:23:30.239763+00	t	2025-10-13 15:23:30.239922+00	2025-10-13 15:26:16.161115+00
a75f99f3-11cd-4a9b-9f92-aea919627473	81f8bfbc-9554-4887-b16a-e454dd3afbe0	+5511977554371	2025-10-15 14:05:17.112349+00	t	2025-10-15 14:05:17.112349+00	2025-10-15 14:05:17.112349+00
1a179226-7530-42f3-a68d-778f8f9ce509	728ae353-5f7e-46be-88ce-dd0f8604c05e	+5511983392166	2025-10-15 14:05:17.116765+00	t	2025-10-15 14:05:17.116765+00	2025-10-15 14:05:17.116765+00
65f14d15-1a66-4792-b45b-16395b2421a0	34284dd7-e3d1-4dae-b6c0-222b1ea8ca73	+5511977649298	2025-10-15 14:05:17.121162+00	t	2025-10-15 14:05:17.121162+00	2025-10-15 14:05:17.121162+00
8c092efd-61f4-4f3c-8bce-6c6837cd8264	47a12dc4-be21-4441-815e-f0dc61ba7dfe	+5511963810079	2025-10-15 14:05:17.12513+00	t	2025-10-15 14:05:17.12513+00	2025-10-15 14:05:17.12513+00
e9fd5ed3-cfdb-4ff0-8b32-a641da60dd7b	5b2ef3ab-f157-47c6-93bf-abe334860192	4915158832107	2025-10-13 20:37:14.555251+00	t	2025-10-13 20:37:14.555434+00	2025-10-13 20:56:13.647876+00
4f0f2761-6622-4c62-b36c-7f24432265e6	0340b8d8-107d-4a3d-a9ca-bb09931233ba	+5511940592182	2025-10-15 14:05:17.129931+00	t	2025-10-15 14:05:17.129931+00	2025-10-15 14:05:17.129931+00
28a908a9-ec76-4595-a6fc-e696be7130e2	e7dfdecb-56f7-4d3e-99a8-bc78ae204a54	+5511934570193	2025-10-15 14:05:17.134119+00	t	2025-10-15 14:05:17.134119+00	2025-10-15 14:05:17.134119+00
e299e488-ee63-4289-869f-3fcb4fc19e3b	f1305093-9d41-4ecb-8bf7-6c210f5e83b2	+5511986631747	2025-10-15 14:05:17.138381+00	t	2025-10-15 14:05:17.138381+00	2025-10-15 14:05:17.138381+00
d3c7f10a-d5db-45e0-99a5-5bb01f62b636	71c5bfec-252a-43de-92cc-43aedf3b5a2b	+5511932809913	2025-10-15 14:05:17.142532+00	t	2025-10-15 14:05:17.142532+00	2025-10-15 14:05:17.142532+00
a78a3338-9df1-4444-ad02-9503b23628ac	2e08f168-d8bd-4236-8f0f-61e143b7e922	+5511955581339	2025-10-15 14:05:17.146598+00	t	2025-10-15 14:05:17.146598+00	2025-10-15 14:05:17.146598+00
30b2c229-0a9f-435f-8a7f-27df607a3cd2	1e0730e8-4008-4cb2-bdcb-931ec80a2f9a	+5511938145449	2025-10-15 14:05:17.150763+00	t	2025-10-15 14:05:17.150763+00	2025-10-15 14:05:17.150763+00
a573109d-9ffd-4a67-8713-e0246fb931bb	b6d5e3f4-98b8-4a06-993d-eedce758064b	+5511968933716	2025-10-15 14:05:17.154811+00	t	2025-10-15 14:05:17.154811+00	2025-10-15 14:05:17.154811+00
0af99716-939d-4b67-a434-2dedbf383317	1814bae2-323e-435b-8251-abbd630bf9cf	+5511910972266	2025-10-15 14:05:17.159041+00	t	2025-10-15 14:05:17.159041+00	2025-10-15 14:05:17.159041+00
31784f1f-6f32-4c45-a5f2-745ed2235f15	e616ccf2-3cac-4958-93b3-45e2039f0a1c	+5511948429630	2025-10-15 14:05:17.163248+00	t	2025-10-15 14:05:17.163248+00	2025-10-15 14:05:17.163248+00
4dfab9d3-4cb3-497f-86aa-d6251388220b	bbeee273-c4bd-49cb-bb06-2aa97182e058	+5511934610313	2025-10-15 14:05:17.167582+00	t	2025-10-15 14:05:17.167582+00	2025-10-15 14:05:17.167582+00
4afc7a93-61e8-4e6f-9c72-53560f62a60e	131fe8e5-e698-4b81-a18e-c8646abf46bd	+5511956976039	2025-10-15 14:05:17.171579+00	t	2025-10-15 14:05:17.171579+00	2025-10-15 14:05:17.171579+00
718ddb2d-ec02-4aa8-b056-888aec9d0551	d7735997-acf6-4269-85cc-0eb205ae8fcf	4915158832107	2025-10-14 16:09:14.696751+00	t	2025-10-14 16:09:14.696885+00	2025-10-15 14:28:33.800661+00
248de800-db33-4ce6-8e61-af385a653fb2	f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0	5511982033818	2025-10-21 11:23:03.036826+00	t	2025-10-21 11:23:03.036987+00	2025-10-21 12:23:05.836022+00
b52397c5-2406-4f13-9b79-8f2b132b58af	584648e5-0c1d-44f9-aa12-8cde21c2e4d2	5511983327687	2025-10-21 14:38:11.202797+00	t	2025-10-21 14:38:11.226104+00	2025-10-21 14:39:59.965997+00
55ed4a42-7f9a-4aaa-adc3-0f11ebdb49f8	3db328c8-da70-418c-a245-d01175590664	5511982033817	2025-10-19 14:46:52.547748+00	t	2025-10-19 14:46:52.571808+00	2025-10-19 15:12:34.097008+00
3c417981-4a66-40fb-8d4c-5ca3970dbc4f	8e31833e-effe-4867-9965-9a346c850b72	5511962774562	2025-10-19 22:28:43.196834+00	t	2025-10-19 22:28:43.221432+00	2025-10-19 22:47:37.608383+00
e8e8e4d5-6ad1-42a8-916e-5d72da097952	5e113a13-25ab-4812-acc2-0c675ac8b791	4915158832107	2025-10-12 18:54:07.334685+00	t	2025-10-12 18:54:07.334921+00	2025-10-31 12:36:23.221722+00
65f6f7fc-75a8-405c-882f-f45adac258d8	cfa80063-1b26-4d60-8a9e-ad1cb3de745c	4915158832107	2025-11-02 23:40:50.038247+00	t	2025-11-02 23:40:50.056004+00	2025-11-02 23:40:50.056004+00
\.


--
-- TOC entry 5135 (class 0 OID 25087)
-- Dependencies: 229
-- Data for Name: patients; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.patients (id, user_id, full_name, cpf, birth_date, created_at, updated_at, email, address, zipcode, address_street, address_number, address_complement, address_neighborhood, address_city, address_state, address_cep, gender) FROM stdin;
3eec1f34-8a20-4d2b-9511-6a6810dd7edd	\N	Antonio Lopes	12655170610	2004-01-02	2025-10-14 09:15:47.828873+00	2025-10-14 09:24:22.638013+00	\N	Não informado, S/N - São Paulo - SP	00000-000	Não informado	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
5b2ef3ab-f157-47c6-93bf-abe334860192	\N	Heitor Éttori	46145624000	2010-10-10	2025-10-13 20:37:14.555434+00	2025-10-13 20:56:13.647876+00	\N	Rua Profa. Ana Nastari Brunetti - 99 - Granja Viana - Cotia, SP - CEP: 06709-135, S/N - São Paulo - SP	00000-000	Rua Profa. Ana Nastari Brunetti - 99 - Granja Viana - Cotia, SP - CEP: 06709-135	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
f3cba6ba-d588-40d9-9d94-aa2472717811	\N	Paciente_345171	34517149064	1995-10-10	2025-10-12 21:00:03.840589+00	2025-10-12 21:00:03.840589+00	\N	Rua a ser informada, S/N - A definir - SP	00000-000	Rua a ser informada	S/N	\N	A definir	A definir	SP	00000-000	\N
d5dd3752-c9ce-4a6b-95c8-63a26a42f420	\N	Paciente_990706	99070672022	2010-10-10	2025-10-12 21:04:22.735686+00	2025-10-12 21:04:22.735686+00	\N	Rua a ser informada, S/N - A definir - SP	00000-000	Rua a ser informada	S/N	\N	A definir	A definir	SP	00000-000	\N
0a210e3b-ed53-413d-a343-16c667aefa64	\N	Heitor Ettori	79060607090	2025-10-10	2025-10-12 21:08:23.650552+00	2025-10-12 21:09:52.332485+00	\N	Não informado - S/N - Não especificado - São Paulo, SP - CEP: 00000-000, S/N - São Paulo - SP	00000-000	Não informado - S/N - Não especificado - São Paulo, SP - CEP: 00000-000	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
f30c2c82-0080-46dc-b2dc-7e95200b52b9	\N	Leodir de Abreu Miloch	29549430847	1980-12-30	2025-10-14 12:01:51.396128+00	2025-10-14 12:20:16.255304+00	\N	Não informado, S/N - São Paulo - SP	00000-000	Não informado	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
57873e19-e1d2-42c4-990c-cf8a420e2a35	\N	Não informado	03538675007	1985-03-03	2025-10-12 21:15:03.369141+00	2025-10-13 00:41:12.030855+00	\N	Não informado, S/N - São Paulo - SP	00000-000	Não informado	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
963caad9-2d82-4f00-a5e5-8147b46f3920	\N	Carlos Silva (Teste)	31079369547	1982-02-16	2025-10-15 14:05:17.0911+00	2025-10-15 14:05:17.0911+00	carlos.silva280@outlook.com	\N	\N	Rua Consolação	2278	\N	Perdizes	São Paulo	SP	05949-900	feminino
16ab8fd2-7bdc-454b-8308-2367a6b09e9f	\N	Carlos Lima (Teste)	54617465931	1969-09-18	2025-10-15 14:05:17.099826+00	2025-10-15 14:05:17.099826+00	carlos.lima427@hotmail.com	\N	\N	Rua Teodoro Sampaio	7745	Apto 48	Vila Madalena	São Paulo	SP	02359-805	feminino
2fcc5bda-7f19-4cd9-881b-4f827d60f407	\N	Patricia Santos (Teste)	99247876232	1984-12-22	2025-10-15 14:05:17.103923+00	2025-10-15 14:05:17.103923+00	patricia.santos500@outlook.com	\N	\N	Rua Haddock Lobo	2683	\N	Consolação	São Paulo	SP	05143-210	masculino
9ebedb19-4b94-459d-87b6-3937e1c5a022	\N	Heitor Étori	31094887013	2010-10-10	2025-10-14 15:01:23.737797+00	2025-10-14 15:02:34.107229+00	\N	Rua Profa. Ana Nastari Brunetti - 99 - Granja Viana - Cotia, SP - CEP: 06709-135, S/N - São Paulo - SP	00000-000	Rua Profa. Ana Nastari Brunetti - 99 - Granja Viana - Cotia, SP - CEP: 06709-135	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
eb0656f3-6b57-4c59-9e79-e27e5dcb16d8	\N	Heitor Éttori	24779012066	2010-10-10	2025-10-13 00:42:01.763843+00	2025-10-14 00:50:27.210975+00	\N	Rua Profa. Ana Nastari Brunetti - 99 - Granja Viana - Cotia, SP - CEP: 06709-135, S/N - São Paulo - SP	00000-000	Rua Profa. Ana Nastari Brunetti - 99 - Granja Viana - Cotia, SP - CEP: 06709-135	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
63d47959-4742-460b-ae5a-5aeb982d4f91	\N	Heitor Ét tori	75879387020	2010-10-10	2025-10-14 15:10:34.973113+00	2025-10-14 15:12:11.419602+00	\N	Rua Profa. Ana Nastari Brunetti - 99 - Granja Viana - Cotia, SP - CEP: 06709-135, S/N - São Paulo - SP	00000-000	Rua Profa. Ana Nastari Brunetti - 99 - Granja Viana - Cotia, SP - CEP: 06709-135	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
c7baf2d9-0deb-400e-b296-ecdb4a847e2f	\N	Carlos Santos (Teste)	51547514385	1953-03-26	2025-10-15 14:05:17.108208+00	2025-10-15 14:05:17.108208+00	carlos.santos211@gmail.com	\N	\N	Avenida Paulista	7404	\N	Pinheiros	São Paulo	SP	04343-793	masculino
9fe0af44-5e3d-42d0-9144-ab175099d699	\N	Mariana Moura	92454700085	2010-10-10	2025-10-13 15:23:30.239922+00	2025-10-13 15:26:16.161115+00	\N	Rua das Acácias, 34, S/N - São Paulo - SP	00000-000	Rua das Acácias, 34	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
9f1a1a92-64fe-436e-8e0a-da0a3712f384	\N	Antonio	50054961068	2010-10-10	2025-10-14 16:04:00.451019+00	2025-10-22 08:47:09.717877+00	\N	A confirmar, S/N - São Paulo - SP	00000-000	A confirmar	S/N	\N	A confirmar	São Paulo	SP	00000-000	\N
81f8bfbc-9554-4887-b16a-e454dd3afbe0	\N	José Silva (Teste)	36131612387	1966-12-21	2025-10-15 14:05:17.112349+00	2025-10-15 14:05:17.112349+00	josé.silva22@hotmail.com	\N	\N	Avenida Paulista	7439	\N	Bela Vista	São Paulo	SP	04495-946	feminino
47ec77d4-b2fd-49be-9d64-4db12563c89c	\N	Maryellen Hallen Pereira Santos	33475901803	1985-02-26	2025-10-13 14:07:37.749429+00	2025-10-14 00:50:51.464181+00	\N	Não informado, S/N - São Paulo - SP	00000-000	Não informado	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
728ae353-5f7e-46be-88ce-dd0f8604c05e	\N	Fernanda Costa (Teste)	84992172558	1984-09-23	2025-10-15 14:05:17.116765+00	2025-10-15 14:05:17.116765+00	fernanda.costa346@gmail.com	\N	\N	Rua Oscar Freire	9979	\N	Brooklin	São Paulo	SP	03895-278	masculino
34284dd7-e3d1-4dae-b6c0-222b1ea8ca73	\N	Maria Pereira (Teste)	85384291860	1953-05-27	2025-10-15 14:05:17.121162+00	2025-10-15 14:05:17.121162+00	maria.pereira274@hotmail.com	\N	\N	Rua Oscar Freire	6960	\N	Brooklin	São Paulo	SP	03165-387	masculino
50b9da75-b20a-460e-994b-44e3036a23e4	\N	Maryellen Hallen Pereira Santos	35017532846	1987-01-13	2025-10-13 15:00:23.913557+00	2025-10-15 11:16:26.278482+00	\N	Rua sem número /007, S/N - São Paulo - SP	00000-000	Rua sem número /007	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
f5951f3a-81ec-4306-9386-8c5447b85d37	\N	Carlos Alves (Teste)	18436336687	2000-04-20	2025-10-15 13:52:12.516436+00	2025-10-15 13:52:12.516436+00	carlos.alves229@outlook.com	\N	\N	Rua Consolação	4329	\N	Pinheiros	São Paulo	SP	02184-219	feminino
7936624c-1098-499f-94b8-cffd2ac4f54b	\N	João Lima (Teste)	67289389062	1998-12-09	2025-10-15 13:58:57.679461+00	2025-10-15 13:58:57.679461+00	joão.lima228@gmail.com	\N	\N	Rua Consolação	1416	Apto 137	Brooklin	São Paulo	SP	04596-728	feminino
239ecb59-8b13-4153-9d29-8dfa5b95f7bc	\N	João Alves (Teste)	90387534695	1997-04-01	2025-10-15 13:59:16.674126+00	2025-10-15 13:59:16.674126+00	joão.alves531@outlook.com	\N	\N	Rua Teodoro Sampaio	5699	\N	Moema	São Paulo	SP	05859-039	feminino
3485804f-1a36-4b50-a02d-ccb315d2b461	\N	Fernanda Oliveira (Teste)	16590499035	1981-10-24	2025-10-15 14:05:17.054738+00	2025-10-15 14:05:17.054738+00	fernanda.oliveira790@yahoo.com.br	\N	\N	Avenida Brigadeiro Faria Lima	4903	\N	Bela Vista	São Paulo	SP	01988-721	feminino
47a12dc4-be21-4441-815e-f0dc61ba7dfe	\N	João Costa (Teste)	43215096789	1950-08-19	2025-10-15 14:05:17.12513+00	2025-10-15 14:05:17.12513+00	joão.costa849@hotmail.com	\N	\N	Rua dos Pinheiros	8890	\N	Consolação	São Paulo	SP	05681-378	masculino
0340b8d8-107d-4a3d-a9ca-bb09931233ba	\N	Fernanda Silva (Teste)	73393582849	1987-11-17	2025-10-15 14:05:17.129931+00	2025-10-15 14:05:17.129931+00	fernanda.silva98@hotmail.com	\N	\N	Rua Haddock Lobo	4737	\N	Perdizes	São Paulo	SP	05879-935	feminino
e7dfdecb-56f7-4d3e-99a8-bc78ae204a54	\N	Pedro Souza (Teste)	29716233348	2004-04-21	2025-10-15 14:05:17.134119+00	2025-10-15 14:05:17.134119+00	pedro.souza420@yahoo.com.br	\N	\N	Avenida Ibirapuera	6136	Apto 95	Vila Mariana	São Paulo	SP	03507-584	feminino
f1305093-9d41-4ecb-8bf7-6c210f5e83b2	\N	Carlos Silva (Teste)	19334120147	1978-03-21	2025-10-15 14:05:17.138381+00	2025-10-15 14:05:17.138381+00	carlos.silva819@hotmail.com	\N	\N	Avenida Brigadeiro Faria Lima	382	\N	Itaim Bibi	São Paulo	SP	04173-713	feminino
71c5bfec-252a-43de-92cc-43aedf3b5a2b	\N	Carlos Oliveira (Teste)	49652048354	1986-03-13	2025-10-15 14:05:17.142532+00	2025-10-15 14:05:17.142532+00	carlos.oliveira553@yahoo.com.br	\N	\N	Rua Consolação	1922	Apto 145	Moema	São Paulo	SP	05283-777	masculino
2e08f168-d8bd-4236-8f0f-61e143b7e922	\N	Maria Oliveira (Teste)	52127898074	1986-07-25	2025-10-15 14:05:17.146598+00	2025-10-15 14:05:17.146598+00	maria.oliveira141@yahoo.com.br	\N	\N	Avenida Paulista	5993	\N	Perdizes	São Paulo	SP	05603-696	masculino
1e0730e8-4008-4cb2-bdcb-931ec80a2f9a	\N	Maria Alves (Teste)	88538948151	2003-03-12	2025-10-15 14:05:17.150763+00	2025-10-15 14:05:17.150763+00	maria.alves382@outlook.com	\N	\N	Rua das Flores	2333	Apto 95	Pinheiros	São Paulo	SP	01084-964	feminino
b6d5e3f4-98b8-4a06-993d-eedce758064b	\N	Patricia Alves (Teste)	38344236395	1984-09-04	2025-10-15 14:05:17.154811+00	2025-10-15 14:05:17.154811+00	patricia.alves997@outlook.com	\N	\N	Avenida Paulista	775	Apto 4	Jardins	São Paulo	SP	04702-306	feminino
e616ccf2-3cac-4958-93b3-45e2039f0a1c	\N	Pedro Oliveira (Teste)	32737964422	1999-12-12	2025-10-15 14:05:17.163248+00	2025-10-15 14:05:17.163248+00	pedro.oliveira398@hotmail.com	\N	\N	Avenida Brigadeiro Faria Lima	2321	\N	Consolação	São Paulo	SP	01497-858	feminino
131fe8e5-e698-4b81-a18e-c8646abf46bd	\N	Patricia Lima (Teste)	48051376766	1994-10-06	2025-10-15 14:05:17.171579+00	2025-10-15 14:05:17.171579+00	patricia.lima120@yahoo.com.br	\N	\N	Avenida Ibirapuera	8841	\N	Bela Vista	São Paulo	SP	02604-270	masculino
1814bae2-323e-435b-8251-abbd630bf9cf	\N	Fernanda Santos (Teste)	45660969065	1961-04-12	2025-10-15 14:05:17.159041+00	2025-10-15 14:05:17.159041+00	fernanda.santos11@outlook.com	\N	\N	Avenida Paulista	1981	\N	Consolação	São Paulo	SP	04243-560	masculino
bbeee273-c4bd-49cb-bb06-2aa97182e058	\N	Maria Alves (Teste)	64618377719	1958-04-08	2025-10-15 14:05:17.167582+00	2025-10-15 14:05:17.167582+00	maria.alves561@gmail.com	\N	\N	Rua Haddock Lobo	7380	Apto 80	Moema	São Paulo	SP	04816-009	masculino
d7735997-acf6-4269-85cc-0eb205ae8fcf	\N	João Silva Sanroa	80903842009	2010-10-10	2025-10-14 16:09:14.696885+00	2025-10-15 14:28:33.800661+00	\N	Rua dos Andrades 65, S/N - São Paulo - SP	00000-000	Rua dos Andrades 65	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
0c89a6ff-6598-400e-affb-47ccc3979761	\N	Paciente_134388	13438890658	2012-04-20	2025-10-21 11:31:26.644463+00	2025-10-21 11:31:26.644463+00	\N	Rua a ser informada, S/N - A definir - SP	00000-000	Rua a ser informada	S/N	\N	A definir	A definir	SP	00000-000	\N
3db328c8-da70-418c-a245-d01175590664	\N	Theo Ragazzini Ettori	54165728845	2018-01-17	2025-10-19 14:46:52.571808+00	2025-10-19 15:12:34.097008+00	\N	SP, S/N - São Paulo - SP	00000-000	SP	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
8e31833e-effe-4867-9965-9a346c850b72	\N	Não informado	16102340817	1972-05-17	2025-10-19 22:28:43.221432+00	2025-10-19 22:47:37.608383+00	\N	Não informado, S/N - São Paulo - SP	00000-000	Não informado	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0	\N	O impostor	74774303720	1987-01-13	2025-10-21 11:23:03.036987+00	2025-10-21 12:23:05.836022+00	\N	Rua sem teto, S/N - São Paulo - SP	00000-000	Rua sem teto	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
75ffc611-f82c-43cf-bf3e-bbf75123b7aa	\N	João Carlos Fonseca Corrijido	62940865078	1986-08-27	2025-10-20 23:01:17.664589+00	2025-10-20 23:03:44.116004+00	\N	Rua Arrebol, 33, S/N - São Paulo - SP	00000-000	Rua Arrebol, 33	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
584648e5-0c1d-44f9-aa12-8cde21c2e4d2	\N	Não informado	42239438800	1992-12-31	2025-10-21 14:38:11.226104+00	2025-10-21 14:39:59.965997+00	\N	Não informado, S/N - São Paulo - SP	00000-000	Não informado	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
abdb491c-dc08-40b1-826b-95a28c01b0a1	\N	Paciente_166518	16651866079	2010-10-10	2025-10-21 00:05:12.397422+00	2025-10-21 00:05:12.397422+00	\N	Rua a ser informada, S/N - A definir - SP	00000-000	Rua a ser informada	S/N	\N	A definir	A definir	SP	00000-000	\N
a6fe8ce5-c9a9-4f1e-a698-c7d834256762	\N	FABIO LUIS MARQUES DA SILVA	14043883897	1973-11-04	2025-10-21 01:00:42.378993+00	2025-10-21 01:12:48.297431+00	\N	São Sebastião do Paraíso, MG - CEP: 37950-000, S/N - São Paulo - SP	00000-000	São Sebastião do Paraíso, MG - CEP: 37950-000	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
2b635923-f6c4-435a-9054-156c2113888f	\N	Theo ragazzini ettori	00531462803	1956-11-24	2025-10-21 10:43:58.879975+00	2025-10-21 11:14:35.702294+00	\N	Rua do teste 1, S/N - São Paulo - SP	00000-000	Rua do teste 1	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
5e113a13-25ab-4812-acc2-0c675ac8b791	\N	André Santos Tavares	33377415840	2010-10-10	2025-10-12 18:54:07.334921+00	2025-10-31 12:36:23.221722+00	\N	Não informado, S/N - São Paulo - SP	00000-000	Não informado	S/N	\N	Não especificado	São Paulo	SP	00000-000	\N
acb2d41a-214a-4aa9-ab27-7eb5c47858ec	\N	João da Silva	12345678901	1985-05-15	2025-11-01 17:59:45.633566+00	2025-11-01 17:59:45.633566+00	\N	Rua a ser informada, S/N - A definir - SP	00000-000	Rua a ser informada	S/N	\N	A definir	A definir	SP	00000-000	\N
0df6094a-f34d-498c-b0d0-7a53134a84a1	\N	Test Patient	98765432165	1990-01-01	2025-11-01 17:59:45.63453+00	2025-11-01 17:59:45.63453+00	\N	Rua a ser informada, S/N - A definir - SP	00000-000	Rua a ser informada	S/N	\N	A definir	A definir	SP	00000-000	\N
801a14c3-2c68-41a8-bc5f-a3549f7a745a	\N	Test Patient	11111111722	1990-01-01	2025-11-01 17:59:45.636076+00	2025-11-01 17:59:45.636076+00	\N	Rua a ser informada, S/N - A definir - SP	00000-000	Rua a ser informada	S/N	\N	A definir	A definir	SP	00000-000	\N
952dbb3e-a655-4211-a202-14b9c14d0a49	\N	Maria dos Santos	98765432109	1980-03-20	2025-11-01 17:59:45.638838+00	2025-11-01 17:59:45.638838+00	\N	Rua a ser informada, S/N - A definir - SP	00000-000	Rua a ser informada	S/N	\N	A definir	A definir	SP	00000-000	\N
70d8611d-95a8-4a51-8863-ec56e5af01e9	\N	Test Patient	12345678941	1990-01-01	2025-11-01 17:59:45.649535+00	2025-11-01 17:59:45.649535+00	\N	Rua a ser informada, S/N - A definir - SP	00000-000	Rua a ser informada	S/N	\N	A definir	A definir	SP	00000-000	\N
c3c0dec3-68e6-493b-b838-2e82f9dbf038	\N	Test Patient	98765432180	1990-01-01	2025-11-02 10:27:59.772505+00	2025-11-02 10:27:59.772505+00	\N	Rua a ser informada, S/N - A definir - SP	00000-000	Rua a ser informada	S/N	\N	A definir	A definir	SP	00000-000	\N
06dc44dc-6e11-487a-ad17-47880a259014	\N	Test Patient	12345678944	1990-01-01	2025-11-02 10:27:59.776791+00	2025-11-02 10:27:59.776791+00	\N	Rua a ser informada, S/N - A definir - SP	00000-000	Rua a ser informada	S/N	\N	A definir	A definir	SP	00000-000	\N
34f10a7b-681e-44fa-9123-22c11d02de5d	\N	Test Patient	11111111461	1990-01-01	2025-11-02 10:28:00.073653+00	2025-11-02 10:28:00.073653+00	\N	Rua a ser informada, S/N - A definir - SP	00000-000	Rua a ser informada	S/N	\N	A definir	A definir	SP	00000-000	\N
cfa80063-1b26-4d60-8a9e-ad1cb3de745c	\N	Paciente_074620	07462047012	2010-10-10	2025-11-02 23:40:50.056004+00	2025-11-02 23:40:50.056004+00	\N	Rua a ser informada, S/N - A definir - SP	00000-000	Rua a ser informada	S/N	\N	A definir	A definir	SP	00000-000	\N
\.


--
-- TOC entry 5142 (class 0 OID 25170)
-- Dependencies: 237
-- Data for Name: payment_splits; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.payment_splits (id, payment_id, recipient_type, recipient_id, amount_cents, percentage, description, status, transferred_at, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5143 (class 0 OID 25182)
-- Dependencies: 238
-- Data for Name: payments; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.payments (id, phone_number, method, amount_cents, status, pix_qr_code, pix_transaction_id, provider_transaction_id, created_at, updated_at, confirmed_at, expired_at, failure_reason, payment_link, prescription_renewal_id) FROM stdin;
010fb00a-12e0-4cf7-acf9-1e1f4074d636	5511962774562	pix	2990	confirmed	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/68f5f7b98962435c894ce661f8db42c1520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo6229052568f5f7b98962435c894ce661f63041181	\N	68f5f7b98962435c894ce661f8db42c1	2025-10-19 22:46:50.407491+00	2025-10-19 22:47:31.975524+00	2025-10-19 22:47:31.975524+00	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjU2YTVhYmE4NTZhZmIwZDg2NWU4Zg==	9a88289a-547f-4384-a6e8-0b4f51811142
15ac7ecc-381f-49e0-a0c0-cf5274fa1140	4915158832107	pix	2990	confirmed	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/328f5cf67e7d4a0f8ce07a6a79850671520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo62290525328f5cf67e7d4a0f8ce07a6a76304934C	\N	328f5cf67e7d4a0f8ce07a6a79850671	2025-10-20 11:09:02.295568+00	2025-10-20 11:22:11.796886+00	2025-10-20 11:22:11.796886+00	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjYxODRlYmE4NTZhZmIwZDg2ZWE2Mg==	40c941cc-e135-4acf-ab4a-5b050228a258
562578af-73a2-445b-bd99-f42807f19bb6	553599576711	pix	2990	confirmed	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/ec3106c148f845c6924f077e988edbf7520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo62290525ec3106c148f845c6924f077e963045CAE	\N	ec3106c148f845c6924f077e988edbf7	2025-10-21 01:12:12.214615+00	2025-10-21 01:12:43.030024+00	2025-10-21 01:12:43.030024+00	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjZkZGVjMjEwZGY2MjIzYWMyYWYwNA==	958b0af9-7ab0-4317-bcf6-02a06a4c1e18
d93d53aa-13b6-4a38-9a90-c02207d163fa	5511982033818	pix	2990	confirmed	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/34ab5c3e1f4d44f6bdcefda191010680520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo6229052534ab5c3e1f4d44f6bdcefda1963045C85	\N	34ab5c3e1f4d44f6bdcefda191010680	2025-10-21 11:02:35.862195+00	2025-10-21 11:14:29.213036+00	2025-10-21 11:14:29.213036+00	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4Zjc2ODRiMjEwZGY2MjIzYWMzMWEwZA==	badb42d5-27a3-4ddf-bfcd-1bb49b06665d
a6b8d184-3f01-4729-ad99-0c5b70316dd0	5511982033818	pix	2990	expired	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/ccc8124b955f4d2599f31000467ec219520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo62290525ccc8124b955f4d2599f31000463047C18	\N	Q2hhcmdlOjY4Zjc2NTA3MjEwZGY2MjIzYWMzMTYyZg==	2025-10-21 10:48:39.274812+00	2025-10-21 11:49:00.650928+00	\N	2025-10-21 11:49:00.650928+00	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4Zjc2NTA3MjEwZGY2MjIzYWMzMTYyZg==	925fa162-374d-4176-a085-74228abe40e4
2b48b97d-87fd-4cdb-84f2-1d23161e1628	4915158832107	pix	2990	expired	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/4f790e9f482046a8ae679fd081ca4306520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo622905254f790e9f482046a8ae679fd086304EF4B	\N	Q2hhcmdlOjY4Zjc3OTRlMjEwZGY2MjIzYWMzNDRmNw==	2025-10-21 12:15:10.667826+00	2025-10-21 13:16:00.897655+00	\N	2025-10-21 13:16:00.897655+00	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4Zjc3OTRlMjEwZGY2MjIzYWMzNDRmNw==	8dfb303c-c642-46ae-9970-14616ea72ac4
a6ff0461-9d3f-4bd8-812e-67532af5fb71	5511999999999	pix	2990	pending	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/919e59dba34b4e3ba5d4b1a46f066d23520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo62290525919e59dba34b4e3ba5d4b1a4663043355	\N	Q2hhcmdlOjY4ZjE3ZjlkNjUxMTQ0YTYyNjMzZTMwOQ==	2025-10-16 23:28:29.185533+00	2025-10-16 23:28:29.185533+00	\N	\N	\N	\N	\N
60ba5c4e-3dec-4e2d-b030-5bec366b8c75	5511999999999	pix	2990	pending	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/c3b6e0e7c84d4d10a904d2ad815ad0e5520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo62290525c3b6e0e7c84d4d10a904d2ad863040E60	\N	Q2hhcmdlOjY4ZjE4MWExNjUxMTQ0YTYyNjMzZWI0OA==	2025-10-16 23:37:05.978003+00	2025-10-16 23:37:05.978003+00	\N	\N	\N	\N	\N
2b14fe2e-7389-4b8c-bcd1-787025d1eb18	4915158832107	pix	2990	pending	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/9caed382ca7146faabcfcb5df00bca9f520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo622905259caed382ca7146faabcfcb5df6304B753	\N	Q2hhcmdlOjY4ZjE4NTFhNjUxMTQ0YTYyNjMzZmNjYQ==	2025-10-16 23:51:54.302413+00	2025-10-16 23:51:54.302413+00	\N	\N	\N	\N	\N
bb8171fe-6576-4551-bf49-30a6f785dddb	4915158832107	pix	2990	pending	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/09118f9eb84541b6b0ef131b6a1957f8520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo6229052509118f9eb84541b6b0ef131b6630475EC	\N	Q2hhcmdlOjY4ZjI4MWVjNjUxMTQ0YTYyNjM1Y2UzOQ==	2025-10-17 17:50:36.704394+00	2025-10-17 17:50:36.704394+00	\N	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjI4MWVjNjUxMTQ0YTYyNjM1Y2UzOQ==	\N
41268227-3237-4e94-8f81-bf009277344e	4915158832107	pix	2990	pending	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/81878721a37a45aeb056a6eb5602e9ad520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo6229052581878721a37a45aeb056a6eb56304F118	\N	Q2hhcmdlOjY4ZjI4MzVjNjUxMTQ0YTYyNjM1ZDQxZg==	2025-10-17 17:56:45.290155+00	2025-10-17 17:56:45.290155+00	\N	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjI4MzVjNjUxMTQ0YTYyNjM1ZDQxZg==	\N
5dc870d9-49e3-472f-aee3-bb572041d568	4915158832107	pix	2990	pending	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/6ee4d597d64545688dfa6cc67ed6bbf7520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo622905256ee4d597d64545688dfa6cc676304BFDA	\N	Q2hhcmdlOjY4ZjI4Njg3NjUxMTQ0YTYyNjM1ZGFmMA==	2025-10-17 18:10:15.640645+00	2025-10-17 18:10:15.640645+00	\N	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjI4Njg3NjUxMTQ0YTYyNjM1ZGFmMA==	\N
c959e22f-98be-499b-abe9-2e90419c2cbd	4915158832107	pix	2990	pending	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/ed83114e8fb24e5ca6ea5e6f8712f55b520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo62290525ed83114e8fb24e5ca6ea5e6f8630441CF	\N	Q2hhcmdlOjY4ZjJkMDI4NjUxMTQ0YTYyNjM2NmQxNw==	2025-10-17 23:24:24.768406+00	2025-10-17 23:24:24.768406+00	\N	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjJkMDI4NjUxMTQ0YTYyNjM2NmQxNw==	d312fd6c-c450-47bf-a4e3-5b2c0e56a6ce
1b2ec204-f1c9-40d6-a194-df7e4e96b170	4915158832107	pix	2990	pending	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/f172862cf9784418a5fba2afa57bc597520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo62290525f172862cf9784418a5fba2afa63047506	\N	Q2hhcmdlOjY4ZjJkMTlmNjUxMTQ0YTYyNjM2NmY5NQ==	2025-10-17 23:30:39.190239+00	2025-10-17 23:30:39.190239+00	\N	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjJkMTlmNjUxMTQ0YTYyNjM2NmY5NQ==	d4480946-6a17-4ade-a394-26c5d4e1f968
2dedcd4b-f258-487b-a5e8-41a5b0a08e7c	4915158832107	pix	2990	pending	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/37e1db96c926451fa3e9adbc52ab46f3520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo6229052537e1db96c926451fa3e9adbc56304F2E6	\N	Q2hhcmdlOjY4ZjJkMjhhNjUxMTQ0YTYyNjM2NzJkMg==	2025-10-17 23:34:34.593117+00	2025-10-17 23:34:34.593117+00	\N	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjJkMjhhNjUxMTQ0YTYyNjM2NzJkMg==	374166ad-f6f8-4063-b45f-ea570f51f051
c01c2eda-3bc1-410c-95fb-e65129fc5ab4	4915158832107	pix	2990	confirmed	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/3c1f309f454b4640b6760ad1ec75e08f520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo622905253c1f309f454b4640b6760ad1e63041CBF	\N	3c1f309f454b4640b6760ad1ec75e08f	2025-10-17 18:22:06.955543+00	2025-10-18 11:10:45.177671+00	2025-10-18 11:10:45.177671+00	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjI4OTRlNjUxMTQ0YTYyNjM1ZGZlZg==	\N
aff1b1dc-79be-473b-a8e5-5334e0ee2e45	4915158832107	pix	2990	confirmed	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/28ecc257c2f24c5e89fea740cb9faf33520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo6229052528ecc257c2f24c5e89fea740c630480D0	\N	28ecc257c2f24c5e89fea740cb9faf33	2025-10-18 11:25:48.449391+00	2025-10-18 11:36:45.724897+00	2025-10-18 11:36:45.724897+00	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjM3OTNjNjUxMTQ0YTYyNjM2YTMxOQ==	3e2f7584-3be0-4d8c-929b-69ed6392364b
e298ab10-47c4-4f3a-a06e-497754402957	4915158832107	pix	2990	confirmed	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/2332f0cb1ecc4e6eaf36e601eecd6627520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo622905252332f0cb1ecc4e6eaf36e601e63043051	\N	2332f0cb1ecc4e6eaf36e601eecd6627	2025-10-18 11:45:27.904731+00	2025-10-18 12:04:24.144958+00	2025-10-18 12:04:24.144958+00	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjM3ZGQ3NjUxMTQ0YTYyNjM2YTU4Ng==	57850979-268b-49e4-92fc-014000339589
dfbc91f8-6a9c-4d64-82b2-380eccc5c244	4915158832107	pix	2990	confirmed	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/6f1b5521b0b14ede9eb6376271f8ff8a520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo622905256f1b5521b0b14ede9eb63762763044F57	\N	6f1b5521b0b14ede9eb6376271f8ff8a	2025-10-18 12:11:58.00401+00	2025-10-18 12:12:14.52522+00	2025-10-18 12:12:14.52522+00	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjM4NDBkNjUxMTQ0YTYyNjM2YTdmOA==	25e5c02c-58ee-4654-88bb-8f93bcabd8d2
26dbf9c5-c223-48ef-8193-4b02bb1f7d8a	4915158832107	pix	2990	confirmed	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/0c32164e51a444c8b70ad115d464f85d520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo622905250c32164e51a444c8b70ad115d630451E3	\N	0c32164e51a444c8b70ad115d464f85d	2025-10-18 12:18:56.387753+00	2025-10-18 12:19:33.93147+00	2025-10-18 12:19:33.93147+00	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjM4NWIwNjUxMTQ0YTYyNjM2YTkyOQ==	991df932-0fc9-4a7b-898d-c7334bf368d8
11839da8-ea56-4dca-b643-89cf0b70054c	4915158832107	pix	2990	confirmed	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/73ecd9e831be43fd9e10ac8c41e57a03520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo6229052573ecd9e831be43fd9e10ac8c46304DA82	\N	73ecd9e831be43fd9e10ac8c41e57a03	2025-10-18 17:55:27.640818+00	2025-10-18 17:56:21.406428+00	2025-10-18 17:56:21.406428+00	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjNkNDhmNjUxMTQ0YTYyNjM2YzA0Nw==	6f5dab3c-a4bb-48d8-b15c-b724e217d778
f1f7894a-c7da-4bfb-b51b-1e7412572d03	4915158832107	pix	2990	expired	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/50d9de4ff90145499b844df9f5210d2a520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo6229052550d9de4ff90145499b844df9f63040543	\N	Q2hhcmdlOjY4ZjQ4YThiNjUxMTQ0YTYyNjM3MTFiZA==	2025-10-19 06:51:56.025339+00	2025-10-19 07:52:00.508459+00	\N	2025-10-19 07:52:00.508459+00	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjQ4YThiNjUxMTQ0YTYyNjM3MTFiZA==	3f76a55d-47e1-4f12-b831-f07ac39a69f0
42c03b95-9643-4136-b570-1560599593b9	4915158832107	pix	2990	confirmed	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/efca19cc10fa43e990e4df724ee57a60520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo62290525efca19cc10fa43e990e4df72463046770	\N	efca19cc10fa43e990e4df724ee57a60	2025-10-19 07:52:52.491518+00	2025-10-19 07:53:31.087043+00	2025-10-19 07:53:31.087043+00	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjQ5OGQ0NjUxMTQ0YTYyNjM3MWE5Yw==	be34c1fd-352a-45e3-aa52-2f503a9fc805
19b7979b-976f-4a36-b1ad-8eec9d1bc61b	4915158832107	pix	2990	confirmed	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/696928f3e7014ae2af86ccdc69815862520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo62290525696928f3e7014ae2af86ccdc66304A599	\N	696928f3e7014ae2af86ccdc69815862	2025-10-19 11:14:02.164+00	2025-10-19 11:16:28.956871+00	2025-10-19 11:16:28.956871+00	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjRjN2Y5NjUxMTQ0YTYyNjM3Mjc5Zg==	681f44c5-d60a-401e-8dba-aafca662b7f6
3bc54144-eed1-4d3e-8ede-b2f5af5ecbc8	4915158832107	pix	2990	expired	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/0f2ca53b66ff49c8a569f87d08b2bef6520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo622905250f2ca53b66ff49c8a569f87d063046BB0	\N	Q2hhcmdlOjY4ZjJlMDE0NjUxMTQ0YTYyNjM2N2RhZQ==	2025-10-18 00:32:20.839239+00	2025-10-19 22:11:26.187031+00	\N	2025-10-19 22:11:26.187031+00	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjJlMDE0NjUxMTQ0YTYyNjM2N2RhZQ==	020dffbd-7dfc-42bb-a403-b9808cd2e330
1d549066-ab3d-47ef-89cb-a9b86b184a44	5511982033817	pix	2990	confirmed	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/2b222af43e7b4e1bb329633c94da42f6520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo622905252b222af43e7b4e1bb329633c96304FE84	\N	2b222af43e7b4e1bb329633c94da42f6	2025-10-19 15:03:20.91178+00	2025-10-19 15:12:26.708391+00	2025-10-19 15:12:26.708391+00	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjRmZGI4NjUxMTQ0YTYyNjM3MzNlNw==	04af6c1e-d6d7-43de-9b78-5d711a4127c7
9abd1ef1-a567-4d9e-83c6-1a79c302302b	4915158832107	pix	2990	expired	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/5083361a7835473e960d6fb5e4beb7c8520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo622905255083361a7835473e960d6fb5e63043133	\N	Q2hhcmdlOjY4ZjZjMDIzMjEwZGY2MjIzYWMyN2NhOQ==	2025-10-20 23:05:07.240569+00	2025-10-21 00:06:00.823602+00	\N	2025-10-21 00:06:00.823602+00	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4ZjZjMDIzMjEwZGY2MjIzYWMyN2NhOQ==	9217ba7f-e064-4eb4-9919-679fb4e3a951
6135ab1a-8c0a-4af2-8f48-da1afbc64144	4915158832107	pix	2990	expired	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/a801fdd79b0444549652f0e73248014c520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo62290525a801fdd79b0444549652f0e736304C643	\N	Q2hhcmdlOjY4Zjc2ODc2MjEwZGY2MjIzYWMzMWE2Yg==	2025-10-21 11:03:18.901844+00	2025-10-21 12:04:00.807872+00	\N	2025-10-21 12:04:00.807872+00	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4Zjc2ODc2MjEwZGY2MjIzYWMzMWE2Yg==	311ed125-5fd9-4c1c-b769-fb5ff0c8cba0
8947e60c-eb24-45ad-83c0-91a22c9757b8	5511982033818	pix	2990	confirmed	00020101021226980014br.gov.bcb.pix2576api.woovi-sandbox.com/api/testaccount/qr/v1/159e546cd5ff4b56a450a82ba54e21f3520400005303986540529.905802BR5925Clique_Tecnologia_em_Saud6009Sao_Paulo62290525159e546cd5ff4b56a450a82ba6304FA5E	\N	159e546cd5ff4b56a450a82ba54e21f3	2025-10-21 12:22:49.290059+00	2025-10-21 12:23:01.703535+00	2025-10-21 12:23:01.703535+00	\N	\N	https://openpix.com.br/pay/Q2hhcmdlOjY4Zjc3YjE5MjEwZGY2MjIzYWMzNGIzNw==	48b2f584-e6d7-4b34-a642-8b3ac85ee3de
\.


--
-- TOC entry 5144 (class 0 OID 25195)
-- Dependencies: 239
-- Data for Name: prescription_queue; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.prescription_queue (renewal_id, priority, assigned_doctor_id, assigned_at, expires_at, created_at) FROM stdin;
dba64f9e-b837-44b2-ad40-ba4bba0d91f2	1	86001d90-f0a0-4a2e-98db-b996a445052e	2025-10-17 23:08:15.054813+00	\N	2025-10-17 23:08:15.049153+00
ff14a752-4b62-478f-945a-284b77f72eff	1	86001d90-f0a0-4a2e-98db-b996a445052e	2025-10-17 23:19:07.965282+00	\N	2025-10-17 23:19:07.96001+00
d312fd6c-c450-47bf-a4e3-5b2c0e56a6ce	1	86001d90-f0a0-4a2e-98db-b996a445052e	2025-10-17 23:23:50.76371+00	\N	2025-10-17 23:23:50.758723+00
d4480946-6a17-4ade-a394-26c5d4e1f968	1	86001d90-f0a0-4a2e-98db-b996a445052e	2025-10-17 23:28:56.831999+00	\N	2025-10-17 23:28:56.826614+00
374166ad-f6f8-4063-b45f-ea570f51f051	1	86001d90-f0a0-4a2e-98db-b996a445052e	2025-10-17 23:33:57.333797+00	\N	2025-10-17 23:33:57.32817+00
020dffbd-7dfc-42bb-a403-b9808cd2e330	1	86001d90-f0a0-4a2e-98db-b996a445052e	2025-10-18 00:29:57.640745+00	\N	2025-10-18 00:29:57.635422+00
3e2f7584-3be0-4d8c-929b-69ed6392364b	1	a542b6ef-ab24-49cc-80cd-396ed5a6171a	2025-10-18 11:23:26.373327+00	\N	2025-10-18 11:23:26.36749+00
3f76a55d-47e1-4f12-b831-f07ac39a69f0	1	a542b6ef-ab24-49cc-80cd-396ed5a6171a	2025-10-19 06:43:53.301567+00	\N	2025-10-19 06:43:53.297288+00
9217ba7f-e064-4eb4-9919-679fb4e3a951	1	a542b6ef-ab24-49cc-80cd-396ed5a6171a	2025-10-20 23:03:44.13688+00	\N	2025-10-20 23:03:44.133144+00
925fa162-374d-4176-a085-74228abe40e4	1	a542b6ef-ab24-49cc-80cd-396ed5a6171a	2025-10-21 10:46:12.454202+00	\N	2025-10-21 10:46:12.448659+00
311ed125-5fd9-4c1c-b769-fb5ff0c8cba0	1	a542b6ef-ab24-49cc-80cd-396ed5a6171a	2025-10-21 11:00:50.777263+00	\N	2025-10-21 11:00:50.772649+00
8dfb303c-c642-46ae-9970-14616ea72ac4	1	a542b6ef-ab24-49cc-80cd-396ed5a6171a	2025-10-21 12:12:59.4969+00	\N	2025-10-21 12:12:59.491643+00
c67e14f6-fb1f-4e56-ba62-e34ae783d120	1	a542b6ef-ab24-49cc-80cd-396ed5a6171a	2025-10-21 14:39:59.990734+00	\N	2025-10-21 14:39:59.985561+00
d01f397a-40ef-467e-8d2f-8ae40ae4563b	1	86001d90-f0a0-4a2e-98db-b996a445052e	2025-10-22 09:53:50.127713+00	\N	2025-10-22 09:53:50.1226+00
55f1c3cd-23be-4c73-bc2f-8218827f1553	1	86001d90-f0a0-4a2e-98db-b996a445052e	2025-10-26 11:18:49.995942+00	\N	2025-10-26 11:18:49.989242+00
39507116-4a58-4600-8726-79afd9aa0494	1	86001d90-f0a0-4a2e-98db-b996a445052e	2025-10-31 12:35:12.15374+00	\N	2025-10-31 12:35:11.863087+00
\.


--
-- TOC entry 5136 (class 0 OID 25095)
-- Dependencies: 230
-- Data for Name: prescription_renewals; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.prescription_renewals (id, patient_id, doctor_id, status, risk_level, rejection_reason, approved_at, created_at, updated_at, prescription_id, medical_history_id, temporary_files, row_version, rejection_count, is_permanently_rejected) FROM stdin;
57850979-268b-49e4-92fc-014000339589	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	approved	yellow	\N	2025-10-18 12:04:31.047981+00	2025-10-18 11:44:38.041319+00	2025-10-18 12:04:31.047981+00	8762e84a-8521-498f-b184-3db0c31b757b	1297a487-e0f3-44c1-bee8-db989664376b	[]	0	0	f
ff14a752-4b62-478f-945a-284b77f72eff	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	documents_signed	yellow	\N	\N	2025-10-17 23:19:07.956906+00	2025-10-17 23:20:18.286322+00	60307ee9-bf32-451c-ae8f-4e80a5eadd62	d8584ddb-8880-4f4c-8612-f915649ca2df	[]	0	0	f
dba64f9e-b837-44b2-ad40-ba4bba0d91f2	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	documents_signed	red	\N	\N	2025-10-17 23:08:15.046021+00	2025-10-17 23:12:21.371443+00	f36d497c-a5df-46fd-bb64-e3253dfd8092	356f3094-0c62-462a-81d4-1302d902e54a	[]	0	0	f
04af6c1e-d6d7-43de-9b78-5d711a4127c7	3db328c8-da70-418c-a245-d01175590664	a542b6ef-ab24-49cc-80cd-396ed5a6171a	approved	green	\N	2025-10-19 15:12:34.082659+00	2025-10-19 14:48:45.875454+00	2025-10-19 15:12:34.082659+00	b665e184-53ae-4163-89de-87dc47698c77	b154bd52-f040-4ca0-a44f-3710152b68ec	[]	0	0	f
d312fd6c-c450-47bf-a4e3-5b2c0e56a6ce	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	documents_signed	red	\N	\N	2025-10-17 23:23:50.755815+00	2025-10-17 23:24:23.731732+00	a6f8e964-e1fa-455b-a65a-e688d4354f92	2627240b-22d8-4d15-a72f-6c47fce38886	[]	0	0	f
25e5c02c-58ee-4654-88bb-8f93bcabd8d2	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	approved	green	\N	2025-10-18 12:12:23.213151+00	2025-10-18 12:10:44.5219+00	2025-10-18 12:12:23.213151+00	e3162d99-1a38-4f67-9f90-759759973caf	e7d32029-be94-4e0f-98e8-c7781ecb247d	[]	0	0	f
958b0af9-7ab0-4317-bcf6-02a06a4c1e18	a6fe8ce5-c9a9-4f1e-a698-c7d834256762	86001d90-f0a0-4a2e-98db-b996a445052e	approved	green	\N	2025-10-21 01:12:48.281424+00	2025-10-21 01:09:37.241677+00	2025-10-21 01:12:48.281424+00	0200c690-5170-4a3b-b24a-baec7a46c7a4	4c0e7986-b897-4236-bf4f-76218c82383f	[]	0	0	f
fbf39f31-647a-46a1-9845-6e8f85c04ed3	a6fe8ce5-c9a9-4f1e-a698-c7d834256762	86001d90-f0a0-4a2e-98db-b996a445052e	documents_signed	green	\N	\N	2025-10-21 01:21:56.031819+00	2025-10-21 01:21:58.755196+00	602a0c46-e90f-4489-8fb5-a4afdeb86c25	\N	\N	0	0	f
991df932-0fc9-4a7b-898d-c7334bf368d8	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	approved	yellow	\N	2025-10-18 12:19:40.036538+00	2025-10-18 12:18:01.553838+00	2025-10-18 12:19:40.036538+00	5ec39726-0b2b-4af7-afcb-1c5fc040e512	dd61dd98-734c-4096-b5d4-d908848c0b9c	[]	0	0	f
9a88289a-547f-4384-a6e8-0b4f51811142	8e31833e-effe-4867-9965-9a346c850b72	a542b6ef-ab24-49cc-80cd-396ed5a6171a	approved	green	\N	2025-10-19 22:47:37.602727+00	2025-10-19 22:32:38.93108+00	2025-10-19 22:47:37.602727+00	9c832368-36e5-4b76-bbd0-6c8aca0787e0	316005b0-6bd1-4c26-a46f-c0bd13c6b32d	[]	0	0	f
d4480946-6a17-4ade-a394-26c5d4e1f968	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	documents_signed	green	\N	\N	2025-10-17 23:28:56.823655+00	2025-10-17 23:30:38.207116+00	aea3e920-33f8-47c2-9be6-3283570f231a	052d8794-9fd4-4b12-aee4-d33c48553b51	[]	0	0	f
925fa162-374d-4176-a085-74228abe40e4	2b635923-f6c4-435a-9054-156c2113888f	a542b6ef-ab24-49cc-80cd-396ed5a6171a	documents_signed	red	\N	\N	2025-10-21 10:46:12.44624+00	2025-10-21 10:48:38.388603+00	7477954b-0447-4b37-8f14-2d263bb7f9c5	50aa6b31-ecc5-4955-9a1b-8ef2248a8e81	[]	0	0	f
8dfb303c-c642-46ae-9970-14616ea72ac4	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	documents_signed	green	\N	\N	2025-10-21 12:12:59.48902+00	2025-10-21 12:15:09.521669+00	39473013-4410-4d7d-9b3a-ecb5dd1cd1dc	99906368-963d-4595-a942-dcbebfb16f3d	[]	0	0	f
374166ad-f6f8-4063-b45f-ea570f51f051	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	documents_signed	red	\N	\N	2025-10-17 23:33:57.324761+00	2025-10-17 23:34:32.685675+00	80fb920f-5180-4df3-94c2-6792b961ed6a	4be2fd18-2db1-4f47-861f-cb64be199162	[]	0	0	f
f27914de-5d3a-4de1-922c-4a547f9028fe	5e113a13-25ab-4812-acc2-0c675ac8b791	aa13cd03-5ea1-4264-95e2-cc4a8b2fdafb	rejected	green	Histórico médico apresenta incompatibilidades.	\N	2025-10-18 16:47:17.847149+00	2025-10-26 11:08:29.811383+00	814ce2d9-3645-4244-8045-c4f3acc8bafc	063edfb7-f1e4-47c4-a5a0-368ba540dff9	[]	0	1	t
40c941cc-e135-4acf-ab4a-5b050228a258	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	approved	yellow	\N	2025-10-20 11:22:17.10564+00	2025-10-20 11:05:50.638967+00	2025-10-20 11:22:17.10564+00	124505ca-d8a9-496c-a5b8-eb4fb9765d8d	0f1f1ac3-49e5-4e20-8b3b-c2a726f72483	[]	0	0	f
48b2f584-e6d7-4b34-a642-8b3ac85ee3de	f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0	a542b6ef-ab24-49cc-80cd-396ed5a6171a	approved	yellow	\N	2025-10-21 12:23:05.824307+00	2025-10-21 11:25:23.119443+00	2025-10-21 12:23:05.824307+00	d3985962-f30c-4cd5-a85d-de51f567602c	b56b5ad1-4cae-41fd-89ce-a1dfa8535e7a	[]	0	0	f
020dffbd-7dfc-42bb-a403-b9808cd2e330	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	documents_signed	yellow	\N	\N	2025-10-18 00:29:57.632424+00	2025-10-18 00:32:19.880837+00	bbe28f75-5256-4117-b569-44002a3d6a0f	61f04e64-6a36-4c90-a5e9-4e3ca74e2679	[]	0	0	f
6f5dab3c-a4bb-48d8-b15c-b724e217d778	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	approved	yellow	\N	2025-10-18 17:56:31.233699+00	2025-10-18 17:30:18.405017+00	2025-10-18 17:56:31.233699+00	443cea4c-c7b5-4377-a790-574c321fa102	92ff8ad6-288c-40b0-b5d6-5a4e2758ad04	[]	0	0	f
247ede61-5b83-4c09-89a3-54db99807db5	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	documents_signed	red	\N	\N	2025-10-17 22:10:49.433766+00	2025-10-20 19:38:04.329821+00	1a0e6058-0f04-412d-ba26-410cc3e19497	18dcda57-8888-41ad-97a5-5367e4eaf87b	[]	0	0	f
3e2f7584-3be0-4d8c-929b-69ed6392364b	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	documents_signed	red	\N	\N	2025-10-18 11:23:26.364735+00	2025-10-18 11:25:47.226346+00	1b86e36d-ccd6-46b7-89de-40e8e0c933a6	d7fd19ca-966c-4b73-a6f4-b9f9f9c52382	[]	0	0	f
3f76a55d-47e1-4f12-b831-f07ac39a69f0	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	documents_signed	green	\N	\N	2025-10-19 06:43:53.294633+00	2025-10-19 06:51:55.067726+00	560dd7fc-49db-4228-8396-3e105425f3d3	e5ab776f-b6a6-4ceb-affa-3cbffb99d62d	[]	0	0	f
311ed125-5fd9-4c1c-b769-fb5ff0c8cba0	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	documents_signed	red	\N	\N	2025-10-21 11:00:50.769217+00	2025-10-21 11:03:18.108174+00	bd484500-e50a-4497-9604-249f4f582e00	03b2ad09-79ed-413b-ba5e-07e8bd8f838b	[]	0	0	f
65c3d4c0-b719-49f8-bd47-bac334142b26	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	documents_signed	red	\N	\N	2025-10-19 12:50:39.824652+00	2025-10-20 22:47:06.049245+00	1bf43581-1df3-41fb-b9f6-c803b60096a5	24d3c1ec-9878-48e9-bd0c-51ce72bda145	[]	0	0	f
badb42d5-27a3-4ddf-bfcd-1bb49b06665d	2b635923-f6c4-435a-9054-156c2113888f	a542b6ef-ab24-49cc-80cd-396ed5a6171a	approved	yellow	\N	2025-10-21 11:14:35.687893+00	2025-10-21 11:01:58.726023+00	2025-10-21 11:14:35.687893+00	70697166-4d66-45fb-8d6b-44dd169e6c2a	2120281b-1973-40cc-8ac5-3a69978c44dd	[]	0	0	f
30af3ecd-1eba-4b01-8564-c48bab73a739	5e113a13-25ab-4812-acc2-0c675ac8b791	\N	rejected	red	Histórico médico insuficiente para renovação segura. Por favor, complete as informações solicitadas ou agende uma consulta.	\N	2025-10-21 11:57:10.663078+00	2025-10-22 12:39:19.68813+00	a98b2d8f-7538-469c-bf13-60f3f364ffc7	c7ff2e37-8d60-48e3-876a-8c689a3e6655	[]	0	0	f
be34c1fd-352a-45e3-aa52-2f503a9fc805	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	approved	yellow	\N	2025-10-19 07:53:36.527665+00	2025-10-19 07:51:43.915332+00	2025-10-19 07:53:36.527665+00	a537502f-b838-4031-83de-d9362737787a	a55aa716-f36f-4da2-b06b-60e651fe6e01	[]	0	0	f
d01f397a-40ef-467e-8d2f-8ae40ae4563b	5e113a13-25ab-4812-acc2-0c675ac8b791	2f6c46a2-bd56-4aab-90b4-439b55b526aa	rejected	red	Histórico médico apresenta incompatibilidades.	\N	2025-10-22 09:53:50.1193+00	2025-10-26 11:09:04.428123+00	\N	40f07747-c61a-4a60-8572-f828ed2a85b5	[]	0	1	t
c3425194-c029-4588-8b56-85661d72b7a1	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	rejected	yellow	Contraindicação médica grave identificada que impede renovação segura.	\N	2025-10-18 17:02:10.116092+00	2025-10-26 11:13:55.771219+00	\N	996d3227-7e1b-49b4-9a31-c201487fc971	[]	0	1	t
681f44c5-d60a-401e-8dba-aafca662b7f6	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	approved	green	\N	2025-10-19 11:16:37.110533+00	2025-10-19 11:10:00.610968+00	2025-10-19 11:16:37.110533+00	a2ccbba3-26b5-4148-ab0b-34dabc536eea	08c27ba4-76b6-4a33-9d8c-0a05328d479a	[]	0	0	f
c67e14f6-fb1f-4e56-ba62-e34ae783d120	584648e5-0c1d-44f9-aa12-8cde21c2e4d2	2f6c46a2-bd56-4aab-90b4-439b55b526aa	rejected	green	Paciente requer avaliação médica presencial urgente.	\N	2025-10-21 14:39:59.983083+00	2025-10-23 13:27:33.141974+00	\N	779162bd-cd20-4977-87df-dbb33f58ab91	[]	0	1	t
9e9f34af-401f-486c-aaaa-4e34c2da0783	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	rejected	yellow	Histórico médico apresenta incompatibilidades.	\N	2025-10-21 00:09:00.865046+00	2025-10-23 13:33:50.374526+00	\N	b1f8c970-9fa7-45ec-a416-54b551bc748e	[]	0	1	t
9217ba7f-e064-4eb4-9919-679fb4e3a951	75ffc611-f82c-43cf-bf3e-bbf75123b7aa	86001d90-f0a0-4a2e-98db-b996a445052e	documents_signed	yellow	\N	\N	2025-10-20 23:03:44.131001+00	2025-10-20 23:05:06.332736+00	c1f7a8c5-2ed8-4de9-9ace-d2694f155384	e22ac097-d2d6-43af-9306-acab43d542bd	[]	0	0	f
c58c9f04-997f-4fde-9afb-18bfe93a8c22	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	rejected	green	Histórico médico apresenta incompatibilidades.	\N	2025-10-18 17:31:33.16667+00	2025-10-23 13:35:04.99563+00	bb18a144-0354-486a-8c97-c9a25de11dc1	\N	[]	0	1	t
5fcdf7d1-8261-4067-b31c-664f2d2ae00f	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	rejected	yellow	Histórico médico apresenta incompatibilidades.	\N	2025-10-20 23:49:59.767127+00	2025-10-23 13:36:52.269285+00	\N	0a774fde-8e33-4a4b-8131-917495427eab	[]	0	1	t
ccf2612b-fd87-47ad-833e-321a6277ae74	5e113a13-25ab-4812-acc2-0c675ac8b791	2f6c46a2-bd56-4aab-90b4-439b55b526aa	rejected	yellow	Contraindicação médica grave identificada que impede renovação segura.	\N	2025-10-21 11:51:30.633922+00	2025-10-26 11:14:13.462792+00	\N	bc2721b7-511d-4079-9e48-8df88dc44751	[]	0	1	t
55f1c3cd-23be-4c73-bc2f-8218827f1553	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	rejected	yellow	Histórico médico apresenta incompatibilidades.	\N	2025-10-26 11:18:49.984709+00	2025-10-26 13:42:54.853916+00	\N	e2d8b3ab-d167-4bae-9980-fde5f578fc84	[]	0	1	t
58402953-4ccb-4685-81c1-e20b23083dd9	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	rejected	yellow	Histórico médico apresenta incompatibilidades.	\N	2025-10-28 06:23:59.657424+00	2025-10-31 12:11:21.53436+00	7748588f-5484-4c3b-9ff6-a3b15a9a748e	f43f799e-99d4-440f-ad59-cd86ba2e263d	[]	0	1	t
39507116-4a58-4600-8726-79afd9aa0494	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	rejected	yellow	Histórico médico apresenta incompatibilidades.	\N	2025-10-31 12:35:11.778269+00	2025-11-02 22:35:30.732096+00	\N	40fedb98-63b3-4c91-9088-39ee29aab896	[]	0	1	t
\.


--
-- TOC entry 5145 (class 0 OID 25200)
-- Dependencies: 240
-- Data for Name: prescriptions; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.prescriptions (id, patient_id, doctor_id, medications, issued_date, valid_until, medical_notes, created_at, updated_at, file_paths) FROM stdin;
80fb920f-5180-4df3-94c2-6792b961ed6a	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-17	2025-12-16	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	2025-10-17 23:34:24.960404+00	2025-10-17 23:34:24.960574+00	{}
732cbdc3-2349-4c60-bea1-bf099cafca9c	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-18	2025-12-17	1. asdfasdfasdf	2025-10-18 00:30:46.238142+00	2025-10-18 00:30:46.238293+00	{}
8762e84a-8521-498f-b184-3db0c31b757b	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-18	2025-12-17	1. DIAZEPAM 10 mg - Tomar 1 comprimido à noite	2025-10-18 11:44:49.469+00	2025-10-18 11:45:21.036427+00	{}
5ec39726-0b2b-4af7-afcb-1c5fc040e512	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-18	2025-12-17	1. Diazepam 10 mg - Tomar 1 comprimido à noite\nA receita q deveria chegar.	2025-10-18 12:18:50.468538+00	2025-10-18 12:18:50.468714+00	{}
560dd7fc-49db-4228-8396-3e105425f3d3	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-19	2025-12-18	1. Amitriptilina 25 mg - Tomar 1 comprimido à noite antes de dormir.	2025-10-19 06:51:51.031602+00	2025-10-19 06:51:51.031772+00	{}
8cc83b89-ff28-4f98-96af-1576e0ee2e1e	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-19	2025-12-18	essa é a receita que deve chegar.	2025-10-19 11:12:01.305104+00	2025-10-19 11:12:01.305356+00	{}
a2ccbba3-26b5-4148-ab0b-34dabc536eea	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-19	2025-12-18	essa é a receita q deve chegar	2025-10-19 11:13:56.669024+00	2025-10-19 11:13:56.669227+00	{}
b665e184-53ae-4163-89de-87dc47698c77	3db328c8-da70-418c-a245-d01175590664	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-19	2025-12-18	1. ATENTAH (ATOMOXETINA) 18 mg/cp - Dar 1 comprimido por dia, no café da manhã, todos os dias, a partir do segundo mês do fármaco. USO CONTÍNUO	2025-10-19 15:03:14.544732+00	2025-10-19 15:03:14.544876+00	{}
124505ca-d8a9-496c-a5b8-eb4fb9765d8d	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-20	2025-12-19	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	2025-10-20 11:08:58.882742+00	2025-10-20 11:08:58.882884+00	{}
1bf43581-1df3-41fb-b9f6-c803b60096a5	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	[]	2025-10-20	2025-12-19	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	2025-10-20 22:47:02.714173+00	2025-10-20 22:47:02.714322+00	{}
c1f7a8c5-2ed8-4de9-9ace-d2694f155384	75ffc611-f82c-43cf-bf3e-bbf75123b7aa	86001d90-f0a0-4a2e-98db-b996a445052e	[]	2025-10-20	2025-12-19	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	2025-10-20 23:05:03.34201+00	2025-10-20 23:05:03.342153+00	{}
602a0c46-e90f-4489-8fb5-a4afdeb86c25	a6fe8ce5-c9a9-4f1e-a698-c7d834256762	86001d90-f0a0-4a2e-98db-b996a445052e	[]	2025-10-21	2025-12-20	Depois conta pra patrícia como foi a experiência renovando sua receita...	2025-10-21 01:21:56.031838+00	2025-10-21 01:21:56.032033+00	{}
7477954b-0447-4b37-8f14-2d263bb7f9c5	2b635923-f6c4-435a-9054-156c2113888f	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-21	2025-12-20	1. ATENTAH (ATOMOXETINA) 18 mg/cp - Dar 1 comprimido por dia, no café da manhã, todos os dias, a partir do segundo mês do fármaco. USO CONTÍNUO	2025-10-21 10:48:35.21208+00	2025-10-21 10:48:35.212218+00	{}
bd484500-e50a-4497-9604-249f4f582e00	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	[]	2025-10-21	2025-12-20	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	2025-10-21 11:03:15.806299+00	2025-10-21 11:03:15.806428+00	{}
7a1a68a9-91e6-4397-b0e5-e71842ce7b9b	f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0	86001d90-f0a0-4a2e-98db-b996a445052e	[]	2025-10-21	2025-12-20	1. Ciprofloxacino 500 mg - Tomar 1 comprimido, via oral, duas vezes ao dia	2025-10-21 11:26:57.998+00	2025-10-21 11:30:40.168999+00	{}
3b4f7785-6926-4e30-a453-709aab4a0c25	f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-21	2025-12-20	1. Ciprofloxacino 500 mg - Tomar 1 comprimido, via oral, duas vezes ao dia	2025-10-21 12:00:46.652+00	2025-10-21 12:21:40.234778+00	{}
d3985962-f30c-4cd5-a85d-de51f567602c	f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-21	2025-12-20	1. Ciprofloxacino 500 mg - Tomar 1 comprimido, via oral, duas vezes ao dia	2025-10-21 12:22:44.837727+00	2025-10-21 12:22:44.837859+00	{}
a98b2d8f-7538-469c-bf13-60f3f364ffc7	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	[]	2025-10-21	2025-12-20	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	2025-10-21 11:58:41.986+00	2025-10-22 12:39:19.68813+00	{}
bb18a144-0354-486a-8c97-c9a25de11dc1	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-18	2025-12-17	456	2025-10-18 17:31:33.166+00	2025-10-23 13:35:04.99563+00	{}
814ce2d9-3645-4244-8045-c4f3acc8bafc	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	[]	2025-10-22	2025-12-21	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mg - Tomar 1 comprimido em jejum	2025-10-22 08:45:46.396+00	2025-10-26 11:08:29.811383+00	{}
ecb2ee41-adcf-49c4-bf66-b21f61e4991b	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-18	2025-12-17	1. asdfasdfasdf	2025-10-18 00:30:39.399546+00	2025-10-18 00:30:39.399694+00	{}
bbe28f75-5256-4117-b569-44002a3d6a0f	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-18	2025-12-17	1. asdfasdfasdf	2025-10-18 00:32:15.042476+00	2025-10-18 00:32:15.042648+00	{}
1b86e36d-ccd6-46b7-89de-40e8e0c933a6	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-18	2025-12-17	1. Amitriptilina 25 mg - Tomar 1 comprimido à noite antes de dormir.	2025-10-18 11:25:43.18113+00	2025-10-18 11:25:43.181274+00	{}
db7026c8-37be-4866-a43b-8e77d6430d4d	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-18	2025-12-17	essa é uma receita	2025-10-18 12:11:03.36556+00	2025-10-18 12:11:03.365688+00	{}
e3162d99-1a38-4f67-9f90-759759973caf	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-18	2025-12-17	456465	2025-10-18 12:11:51.469469+00	2025-10-18 12:11:51.469597+00	{}
465cb8af-15c9-476c-9d88-bff0329394d1	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-18	2025-12-17	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	2025-10-18 17:31:08.898+00	2025-10-18 17:54:57.870695+00	{}
443cea4c-c7b5-4377-a790-574c321fa102	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-18	2025-12-17	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	2025-10-18 17:55:21.119567+00	2025-10-18 17:55:21.119702+00	{}
a537502f-b838-4031-83de-d9362737787a	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-19	2025-12-18	1. DIAZEPAM 10 mg - Tomar 1 comprimido à noite\n\nessa é a receita q deve chegar.	2025-10-19 07:52:46.658132+00	2025-10-19 07:52:46.6583+00	{}
1b76b9c4-4678-4756-9333-3f8da5c9e578	3db328c8-da70-418c-a245-d01175590664	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-19	2025-12-18	1. ATENTAH (ATOMOXETINA) 18 mg/cp - Dar 1 comprimido por dia, no café da manhã, todos os dias, a partir do segundo mês do fármaco. USO CONTÍNUO	2025-10-19 14:59:16.665+00	2025-10-19 15:01:28.586685+00	{}
7d8923e6-db79-44b5-abf1-1c6b351e4264	8e31833e-effe-4867-9965-9a346c850b72	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-19	2025-12-18	NA PRÁTICA SUA RECEITA SERIA REJEITADA, PORQUE O NOME ESTÁ NÃO INFORMADO.\n\n\nPODE TESTAR ESSE PDF NO VALIDADOR DO IT, É UM PDF VÁLIDO  E ASSINADO DIGITALMENTE.\n\nJÁ ESTÁ INTEGRADO COM PLATAFORMA DE PAGAMENTOS, NO MEOMENTO EM MODO SANDBOX.	2025-10-19 22:45:19.728418+00	2025-10-19 22:45:19.728556+00	{}
9c832368-36e5-4b76-bbd0-6c8aca0787e0	8e31833e-effe-4867-9965-9a346c850b72	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-19	2025-12-18	na pratica seria rejeitada por nome nao informado\n\n\njá está integrado com plataforma de pagamentos, atualmente em modo sandbox.\n\n\nreceita válida, pode testar assinatura digital no iti	2025-10-19 22:46:47.40495+00	2025-10-19 22:46:47.405101+00	{}
1a0e6058-0f04-412d-ba26-410cc3e19497	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-20	2025-12-19	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	2025-10-20 19:38:01.089225+00	2025-10-20 19:38:01.089375+00	{}
f36d497c-a5df-46fd-bb64-e3253dfd8092	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-17	2025-12-16	1. DIAZEPAM 10 mg - Tomar 1 comprimido noite	2025-10-17 23:12:15.988832+00	2025-10-17 23:12:15.988995+00	{}
60307ee9-bf32-451c-ae8f-4e80a5eadd62	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-17	2025-12-16	asdfasdf	2025-10-17 23:20:10.788465+00	2025-10-17 23:20:10.788596+00	{}
a6f8e964-e1fa-455b-a65a-e688d4354f92	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-17	2025-12-16	adsfasdf	2025-10-17 23:24:18.976323+00	2025-10-17 23:24:18.976483+00	{}
9f48e3a1-39bf-4b50-91c8-2403886c0e6e	75ffc611-f82c-43cf-bf3e-bbf75123b7aa	86001d90-f0a0-4a2e-98db-b996a445052e	[]	2025-10-20	2025-12-19	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	2025-10-20 23:04:30.162956+00	2025-10-20 23:04:30.163125+00	{}
0a7142d3-895e-41c6-98c1-72e71bdd0c26	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-17	2025-12-16	asdfasdf	2025-10-17 23:29:36.694+00	2025-10-17 23:30:19.444556+00	{}
aea3e920-33f8-47c2-9be6-3283570f231a	5e113a13-25ab-4812-acc2-0c675ac8b791	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-17	2025-12-16	asdfasdf	2025-10-17 23:30:31.04017+00	2025-10-17 23:30:31.040307+00	{}
0200c690-5170-4a3b-b24a-baec7a46c7a4	a6fe8ce5-c9a9-4f1e-a698-c7d834256762	86001d90-f0a0-4a2e-98db-b996a445052e	[]	2025-10-21	2025-12-20	Uso inalatório:\n1. SALBUTAMOL 100 mcg ----------------------------- 1 frasco \nInalar 2 jatos a cada 6 horas se falta de ar ou “chiado” no peito.\n\n2. BECLOMETASONA 200 mcg -------------------------- 1 frasco \nInalar 1 jato de 12/12h, lavar a boca após.\n\n\n\nUso nasal:\n3. BUDESONIDA SPRAY NASAL 50 mcg/jato -------------- contínuo. \nAplicar um jato em cada narina de 12/12h	2025-10-21 01:12:08.106008+00	2025-10-21 01:12:08.106129+00	{}
70697166-4d66-45fb-8d6b-44dd169e6c2a	2b635923-f6c4-435a-9054-156c2113888f	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-21	2025-12-20	1. Ciprofloxacino 500 mg - Tomar 1 comprimido, via oral, duas vezes ao dia	2025-10-21 11:02:32.39047+00	2025-10-21 11:02:32.390597+00	{}
4f0dac43-3911-4322-849e-4bdf810351aa	f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-21	2025-12-20	1. Ciprofloxacino 500 mg - Tomar 1 comprimido, via oral, duas vezes ao dia	2025-10-21 11:26:03.973+00	2025-10-21 11:26:16.644107+00	{}
654da6f1-ab88-4087-ab34-e81318de2c7b	f1d6ed0b-92b4-40ed-9e23-0b65f891a2d0	a542b6ef-ab24-49cc-80cd-396ed5a6171a	[]	2025-10-21	2025-12-20	1. Ciprofloxacino 500 mg - Tomar 1 comprimido, via oral, duas vezes ao dia	2025-10-21 11:32:12.169+00	2025-10-21 12:00:16.342131+00	{}
39473013-4410-4d7d-9b3a-ecb5dd1cd1dc	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	[]	2025-10-21	2025-12-20	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mg - Tomar 1 comprimido em jejum	2025-10-21 12:15:06.482861+00	2025-10-21 12:15:06.482996+00	{}
7748588f-5484-4c3b-9ff6-a3b15a9a748e	5e113a13-25ab-4812-acc2-0c675ac8b791	86001d90-f0a0-4a2e-98db-b996a445052e	[]	2025-10-28	2025-12-27	1. Aripiprazol 10 mg - Tomar 1 comprimido pela manhã\n2. Levotiroxina 75 mcg - Tomar 1 comprimido em jejum	2025-10-28 06:26:25.37+00	2025-10-31 12:11:21.53436+00	{}
\.


--
-- TOC entry 5146 (class 0 OID 25211)
-- Dependencies: 241
-- Data for Name: processed_events; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.processed_events (event_type, entity_id, occurred_at, processed_at) FROM stdin;
ApprovalInitiated	ca39c4cd-2ffd-473f-958e-48977b10dd48	2025-09-28 23:57:31.696615+00	2025-09-28 23:57:31.699558+00
ApprovalInitiated	ca39c4cd-2ffd-473f-958e-48977b10dd48	2025-09-28 23:57:38.573672+00	2025-09-28 23:57:38.584583+00
ApprovalInitiated	b2cee605-bafa-470d-9f98-623311a992c7	2025-09-29 00:08:22.301864+00	2025-09-29 00:08:22.306301+00
ApprovalInitiated	ca39c4cd-2ffd-473f-958e-48977b10dd48	2025-09-29 00:08:23.588925+00	2025-09-29 00:08:23.600138+00
ApprovalInitiated	e639a0a1-2b87-4055-9a06-4ef1e60ec776	2025-09-29 00:12:24.489958+00	2025-09-29 00:12:24.501893+00
ApprovalInitiated	e639a0a1-2b87-4055-9a06-4ef1e60ec776	2025-09-29 00:25:17.13547+00	2025-09-29 00:25:17.140509+00
ApprovalInitiated	e639a0a1-2b87-4055-9a06-4ef1e60ec776	2025-09-29 00:25:23.590713+00	2025-09-29 00:25:23.593162+00
ApprovalInitiated	eb5f6492-7267-4f61-8084-601497820ab7	2025-09-29 00:27:34.358311+00	2025-09-29 00:27:34.371527+00
ApprovalInitiated	eb5f6492-7267-4f61-8084-601497820ab7	2025-09-29 00:27:39.620904+00	2025-09-29 00:27:39.623949+00
ApprovalInitiated	c360d2f4-ecff-4003-a656-0f54ca7685cd	2025-09-29 00:29:16.471264+00	2025-09-29 00:29:16.483793+00
ApprovalInitiated	c360d2f4-ecff-4003-a656-0f54ca7685cd	2025-09-29 00:29:33.501137+00	2025-09-29 00:29:33.513925+00
ApprovalInitiated	c360d2f4-ecff-4003-a656-0f54ca7685cd	2025-09-29 00:29:42.634711+00	2025-09-29 00:29:42.645829+00
ApprovalInitiated	c360d2f4-ecff-4003-a656-0f54ca7685cd	2025-09-29 00:29:49.677406+00	2025-09-29 00:29:49.679978+00
ApprovalInitiated	afd8c628-4807-4d46-b5d2-98716e4c5338	2025-09-29 00:31:43.01282+00	2025-09-29 00:31:43.025577+00
ApprovalInitiated	48f75bc0-6ac1-4d4e-ae1d-72242e9ec72f	2025-09-29 00:37:53.35596+00	2025-09-29 00:37:53.368803+00
ApprovalInitiated	48f75bc0-6ac1-4d4e-ae1d-72242e9ec72f	2025-09-29 00:37:58.702852+00	2025-09-29 00:37:58.706733+00
ApprovalInitiated	f0fb7f4c-a694-490b-9bb1-5248d4bdb988	2025-09-29 00:41:16.267726+00	2025-09-29 00:41:16.279808+00
ApprovalInitiated	f0fb7f4c-a694-490b-9bb1-5248d4bdb988	2025-09-29 00:41:26.928188+00	2025-09-29 00:41:26.939198+00
ApprovalInitiated	f0fb7f4c-a694-490b-9bb1-5248d4bdb988	2025-09-29 00:42:16.28061+00	2025-09-29 00:42:16.316474+00
ApprovalInitiated	f0fb7f4c-a694-490b-9bb1-5248d4bdb988	2025-09-29 00:42:21.431678+00	2025-09-29 00:42:21.43486+00
ApprovalInitiated	01eb4705-c7ba-4728-8706-e82be7e34abc	2025-09-29 00:48:09.645067+00	2025-09-29 00:48:09.657677+00
ApprovalInitiated	cc9db502-db6a-4ade-b4c9-00d0081c200f	2025-09-29 01:24:54.138686+00	2025-09-29 01:24:54.151351+00
ApprovalInitiated	21356d94-a6f7-4734-afc1-e5cc207b3570	2025-09-29 08:15:41.682773+00	2025-09-29 08:15:41.695511+00
ApprovalInitiated	21356d94-a6f7-4734-afc1-e5cc207b3570	2025-09-29 08:16:26.203546+00	2025-09-29 08:16:26.214699+00
ApprovalInitiated	21356d94-a6f7-4734-afc1-e5cc207b3570	2025-09-29 08:19:01.089184+00	2025-09-29 08:19:01.101416+00
ApprovalInitiated	1babc490-6470-4bb2-81f1-ef44a6c3a3c9	2025-09-29 08:19:33.180981+00	2025-09-29 08:19:33.185562+00
ApprovalInitiated	1babc490-6470-4bb2-81f1-ef44a6c3a3c9	2025-09-29 08:20:12.478794+00	2025-09-29 08:20:12.489986+00
ApprovalInitiated	eb4c510f-3718-4117-98f8-852ff6cc9fd5	2025-09-29 08:37:28.845007+00	2025-09-29 08:37:28.850806+00
ApprovalInitiated	eb4c510f-3718-4117-98f8-852ff6cc9fd5	2025-09-29 08:42:13.568751+00	2025-09-29 08:42:13.583552+00
ApprovalInitiated	eb4c510f-3718-4117-98f8-852ff6cc9fd5	2025-09-29 08:42:55.703145+00	2025-09-29 08:42:55.71665+00
ApprovalInitiated	eb4c510f-3718-4117-98f8-852ff6cc9fd5	2025-09-29 08:49:54.045247+00	2025-09-29 08:49:54.060816+00
ApprovalInitiated	eb4c510f-3718-4117-98f8-852ff6cc9fd5	2025-09-29 08:51:12.147992+00	2025-09-29 08:51:12.159008+00
ApprovalInitiated	1fb2a721-8302-475f-a4c4-f8d235d7afe6	2025-09-29 08:53:25.07707+00	2025-09-29 08:53:25.088755+00
ApprovalInitiated	752f619c-06ce-4df3-855d-559d6a6c154d	2025-09-29 08:53:29.179851+00	2025-09-29 08:53:29.191432+00
ApprovalInitiated	f87277a0-7d1b-4528-9fc3-bd5d2420b33f	2025-09-29 08:53:34.376877+00	2025-09-29 08:53:34.388225+00
ApprovalInitiated	c4502f3e-d905-4d4d-b2af-1a05650444a3	2025-09-29 08:53:38.307227+00	2025-09-29 08:53:38.318766+00
ApprovalInitiated	c8c881f9-8dc0-4e7a-8a7a-ecbf92e54593	2025-09-29 08:53:43.189832+00	2025-09-29 08:53:43.1949+00
ApprovalInitiated	ca7f4cff-f529-4b2e-a0d0-8cdc80bd5c46	2025-09-29 09:08:05.318555+00	2025-09-29 09:08:05.332202+00
ApprovalInitiated	ca7f4cff-f529-4b2e-a0d0-8cdc80bd5c46	2025-09-29 09:08:48.45661+00	2025-09-29 09:08:48.469597+00
ApprovalInitiated	1ea3d01b-7fe0-419c-8402-d4a93d723046	2025-09-29 09:16:45.96747+00	2025-09-29 09:16:45.979036+00
ApprovalInitiated	67cfd18a-e0a6-491a-b25c-9712e23de3b8	2025-09-29 09:21:06.838193+00	2025-09-29 09:21:06.850641+00
ApprovalInitiated	431dab7c-33ab-4b96-98db-fac9728723b5	2025-09-29 09:23:24.943047+00	2025-09-29 09:23:24.954799+00
ApprovalInitiated	431dab7c-33ab-4b96-98db-fac9728723b5	2025-09-29 09:23:34.078878+00	2025-09-29 09:23:34.082418+00
ApprovalInitiated	620ce7fb-ab95-439b-a814-cac66444fb08	2025-09-29 09:24:16.146293+00	2025-09-29 09:24:16.159213+00
ApprovalInitiated	c6b96e12-abf5-4df8-851c-072b6c4c2829	2025-09-29 09:40:25.858676+00	2025-09-29 09:40:25.887247+00
ApprovalInitiated	d83ed9af-5ace-4d69-bc4d-2792eb7934f9	2025-09-29 09:42:54.525436+00	2025-09-29 09:42:54.538321+00
ApprovalInitiated	28b0c8a3-aae5-4bb9-86fc-14c905d03b85	2025-09-29 09:53:49.78081+00	2025-09-29 09:53:49.792996+00
ApprovalInitiated	28b0c8a3-aae5-4bb9-86fc-14c905d03b85	2025-09-29 13:18:50.672493+00	2025-09-29 13:18:50.684379+00
ApprovalInitiated	01cf1cc3-866d-4c61-b0ec-92e624e4bb8e	2025-09-29 13:18:59.530274+00	2025-09-29 13:18:59.542283+00
ApprovalInitiated	09f62337-44e1-4881-9485-eb5f5bd88e8c	2025-09-29 13:19:04.387254+00	2025-09-29 13:19:04.390575+00
ApprovalInitiated	cce80a81-c399-4e7e-bb1e-0e0b76916daa	2025-09-29 13:41:41.826476+00	2025-09-29 13:41:41.840211+00
ApprovalInitiated	cce80a81-c399-4e7e-bb1e-0e0b76916daa	2025-09-29 13:42:15.559715+00	2025-09-29 13:42:15.57271+00
ApprovalInitiated	c830b563-4baf-414d-9f7b-dd35079a3acd	2025-09-29 13:44:25.31379+00	2025-09-29 13:44:25.325297+00
ApprovalInitiated	e7871b7e-952d-4be2-91ac-2641cd12a423	2025-09-29 13:44:29.940002+00	2025-09-29 13:44:29.952408+00
ApprovalInitiated	bbf3a03e-6d9a-45fb-b186-27b82ae5a855	2025-09-29 13:50:42.395443+00	2025-09-29 13:50:42.408213+00
ApprovalInitiated	c9b9cf52-55f2-4bb3-af6d-87eeb0fb6837	2025-09-28 23:46:55.782942+00	2025-09-28 23:46:55.796923+00
ApprovalInitiated	c9b9cf52-55f2-4bb3-af6d-87eeb0fb6837	2025-09-28 23:47:42.253034+00	2025-09-28 23:47:42.258467+00
ApprovalInitiated	c9b9cf52-55f2-4bb3-af6d-87eeb0fb6837	2025-09-28 23:47:56.677343+00	2025-09-28 23:47:56.683906+00
ApprovalInitiated	b2cee605-bafa-470d-9f98-623311a992c7	2025-09-28 23:50:21.595143+00	2025-09-28 23:50:21.60672+00
ApprovalInitiated	b2cee605-bafa-470d-9f98-623311a992c7	2025-09-28 23:50:47.939521+00	2025-09-28 23:50:47.950936+00
ApprovalInitiated	b2cee605-bafa-470d-9f98-623311a992c7	2025-09-28 23:50:57.97588+00	2025-09-28 23:50:57.978375+00
ApprovalInitiated	b2cee605-bafa-470d-9f98-623311a992c7	2025-09-28 23:51:03.022892+00	2025-09-28 23:51:03.026261+00
ApprovalInitiated	8c155cbe-ac39-4cc7-b43b-2b138df9c0c7	2025-09-29 13:50:55.105938+00	2025-09-29 13:50:55.120023+00
ApprovalInitiated	53479867-e5ff-4ada-9e60-9724f0dc3039	2025-09-29 14:54:27.566423+00	2025-09-29 14:54:27.579377+00
ApprovalInitiated	53479867-e5ff-4ada-9e60-9724f0dc3039	2025-09-29 14:55:04.960318+00	2025-09-29 14:55:04.972517+00
ApprovalInitiated	53479867-e5ff-4ada-9e60-9724f0dc3039	2025-09-29 14:55:29.273795+00	2025-09-29 14:55:29.277241+00
ApprovalInitiated	7faedf5d-be00-4332-89d2-577594e14087	2025-09-29 14:56:32.402213+00	2025-09-29 14:56:32.414125+00
ApprovalInitiated	7faedf5d-be00-4332-89d2-577594e14087	2025-09-29 14:56:46.847825+00	2025-09-29 14:56:46.858865+00
ApprovalInitiated	ca5a6855-0b5c-434a-beea-08d5afdcb69d	2025-09-29 15:11:00.416591+00	2025-09-29 15:11:00.427771+00
ApprovalInitiated	ca5a6855-0b5c-434a-beea-08d5afdcb69d	2025-09-29 15:12:05.238816+00	2025-09-29 15:12:05.252399+00
ApprovalInitiated	ca5a6855-0b5c-434a-beea-08d5afdcb69d	2025-09-29 15:12:18.860099+00	2025-09-29 15:12:18.863026+00
ApprovalInitiated	16be3cf5-959f-46ad-a6cb-45c7374f13b7	2025-09-29 15:35:42.252057+00	2025-09-29 15:35:42.26847+00
ApprovalInitiated	50ef3668-0327-436e-942b-9186d25a8d1c	2025-09-29 15:37:04.637036+00	2025-09-29 15:37:04.653154+00
ApprovalInitiated	16be3cf5-959f-46ad-a6cb-45c7374f13b7	2025-09-29 15:38:28.988011+00	2025-09-29 15:38:29.004587+00
ApprovalInitiated	16be3cf5-959f-46ad-a6cb-45c7374f13b7	2025-09-29 15:38:56.514397+00	2025-09-29 15:38:56.528896+00
ApprovalInitiated	50ef3668-0327-436e-942b-9186d25a8d1c	2025-09-29 15:40:33.820032+00	2025-09-29 15:40:33.833087+00
ApprovalInitiated	50ef3668-0327-436e-942b-9186d25a8d1c	2025-09-29 15:44:48.897313+00	2025-09-29 15:44:48.912196+00
ApprovalInitiated	51834db8-a35e-49f3-ab48-98665450a32a	2025-09-29 15:45:40.578137+00	2025-09-29 15:45:40.581958+00
ApprovalInitiated	5fd6b1fb-8cd7-4609-bcf7-3dff9fdad7fc	2025-10-03 09:04:39.982779+00	2025-10-03 09:04:39.993163+00
ApprovalInitiated	5fd6b1fb-8cd7-4609-bcf7-3dff9fdad7fc	2025-10-03 09:05:10.463953+00	2025-10-03 09:05:10.469024+00
ApprovalInitiated	5fd6b1fb-8cd7-4609-bcf7-3dff9fdad7fc	2025-10-03 09:05:41.45947+00	2025-10-03 09:05:41.472596+00
ApprovalInitiated	e0f44ed3-6b2c-4d26-bbb2-a51d789dbe62	2025-10-03 09:19:28.059084+00	2025-10-03 09:19:28.072592+00
ApprovalInitiated	c3b2a16d-3042-42d7-81f9-0a3ab895efd2	2025-10-03 09:51:54.253787+00	2025-10-03 09:51:54.25921+00
ApprovalInitiated	751043ed-e837-4e3f-a7c6-d3d15ff69f8f	2025-10-03 09:54:07.18926+00	2025-10-03 09:54:07.195811+00
ApprovalInitiated	2008430e-df45-46ab-82b4-dfb31540cc6d	2025-10-03 10:15:27.455873+00	2025-10-03 10:15:27.470415+00
ApprovalInitiated	5196fc85-5093-4473-9b87-82c20706cfbd	2025-10-03 10:42:00.865929+00	2025-10-03 10:42:00.871503+00
ApprovalInitiated	5196fc85-5093-4473-9b87-82c20706cfbd	2025-10-03 10:43:20.139235+00	2025-10-03 10:43:20.151257+00
ApprovalInitiated	69f78665-92e8-4b01-84f9-f593d6668930	2025-10-03 11:02:13.459368+00	2025-10-03 11:02:13.472631+00
ApprovalInitiated	86ff1626-1ebb-4a1d-b74e-e37df2c5ab53	2025-10-03 15:15:06.784994+00	2025-10-03 15:15:06.798069+00
ApprovalInitiated	1e0dee80-4cda-4250-8e7b-3d4b600f8af2	2025-10-03 16:19:59.766157+00	2025-10-03 16:19:59.778288+00
ApprovalInitiated	21172e4c-cc59-4ebb-b60b-2aea087e7eea	2025-10-03 19:04:44.165379+00	2025-10-03 19:04:44.179064+00
ApprovalInitiated	605020a1-56ac-4388-b2e6-95c77c16a6c6	2025-10-03 19:19:44.761264+00	2025-10-03 19:19:44.775661+00
ApprovalInitiated	84cd7a49-8f09-4983-a6d7-245625a30214	2025-10-03 19:55:49.18358+00	2025-10-03 19:55:49.20155+00
\.


--
-- TOC entry 5147 (class 0 OID 25217)
-- Dependencies: 242
-- Data for Name: sessions; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.sessions (id, user_id, token, expires_at, created_at) FROM stdin;
\.


--
-- TOC entry 5148 (class 0 OID 25222)
-- Dependencies: 243
-- Data for Name: user_sessions; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.user_sessions (id, user_id, phone, cpf, session_data, expires_at, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5149 (class 0 OID 25231)
-- Dependencies: 244
-- Data for Name: users; Type: TABLE DATA; Schema: core; Owner: doadmin
--

COPY core.users (id, phone, cpf, full_name, email, password_hash, birth_date, created_at, updated_at, user_type, is_active) FROM stdin;
7455f35f-3853-4c16-93ff-402264d96822	\N	\N	\N	russell.waters@gmail.com	$2b$12$kpE9j.Zn0I1.xY8AH1l4M.OQ22icQYb285I6OpXt98Csn0ZRdTZxm	\N	2025-08-04 21:17:37.030519+00	2025-08-04 21:17:37.030519+00	doctor	t
f846cd4c-6261-4048-8f82-33e2bb306fb8	\N	\N	\N	delphine_skiles13@gmail.com	$2b$12$mGTqo0OrL2fmb1Uvc/MHQerpD4DAt7wYWxk1XaF74EADA0f96Yi1G	\N	2025-08-04 22:19:05.731262+00	2025-08-04 22:19:05.731262+00	doctor	t
6dd1fd80-a17c-4d7c-9ce2-41fa5eda4487	\N	\N	\N	127.0.0.1.retract121@passinbox.com	$2b$12$PIAnP0YlEbas2jB..vgz8uFRv8e8DPb2wAxq/zUQRGF7c30XsTG0m	\N	2025-08-07 11:52:27.178267+00	2025-08-07 11:52:27.178267+00	doctor	t
192c5307-1d94-44f2-a6e4-aa831ca1d73e	\N	\N	\N	127.0.0.1.profusely220@passinbox.com	$2b$12$WKdOlFNkVw3A4SfD3Z/ohe1CnIssNSJp2fbVQKw2gYmT2FsA5TyXO	\N	2025-08-07 15:58:56.922125+00	2025-08-07 15:58:56.92213+00	doctor	t
6a32a357-daf5-4459-b82c-645299b23bc0	\N	\N	\N	lcsavb@gmail.com	$2b$12$eRXVehJ2GST2FovNh1yrhuavddoJZjQpJm.FrDnaZgaLvD/eJkwHG	\N	2025-08-04 21:16:58.544668+00	2025-08-07 15:59:45.826936+00	doctor	t
4ca24570-00df-491e-96c8-eb8462dc9941	\N	\N	\N	127.0.0.1.trickster943@passinbox.com	$2b$12$4USRwok/tTnEDx0HjBaJuO3AHfFIRppAPH6NT.2Uy.00Zm/sc42Vm	\N	2025-08-07 16:10:17.943333+00	2025-08-20 21:04:16.59704+00	doctor	t
fee86384-f421-44af-954e-37c2e8db8087	\N	\N	\N	admin@cliquereceita.com	$2b$12$diqU0BQGC4DR10/35VxrnuNMtP86w2zlody35YD/NZJy9U.91hrtu	\N	2025-08-23 12:52:35.12109+00	2025-08-23 12:54:51.708316+00	admin	t
f12a8a07-8ac4-4c85-9883-4775418876a2	\N	\N	\N	admin@cliquereceita.local	$2a$06$eSyFANA/09DvIfjfQPIQqeEIHiegLbw4iLRymiN0YtcyLqtFz5Ahu	\N	2025-09-24 16:47:28.422359+00	2025-09-24 16:47:28.422359+00	admin	t
74584d8a-54f7-467b-9864-582e94bb7452	\N	456	\N	laron.feeney19@yahoo.com	$2b$12$BVVl50HJQ9vd9GOjY.3.bervGUGkACeQJV4TmytbydUgkOnO7BuOW	\N	2025-08-04 21:15:47.335757+00	2025-10-19 12:16:31.600814+00	doctor	t
a8a3c6c8-82fd-4912-871a-6f8791f73d39	\N	\N	\N	lucas@cliquereceitasdfa.com.br	$2b$12$j6cktR/Px6zHdKDRUMp4ueDxPQ0YlVaGmSaqDB8Qk3Rx4UqKNFOxK	\N	2025-10-19 12:53:29.30569+00	2025-10-20 22:45:22.363765+00	doctor	t
ec650cd5-7ea6-4066-85a3-37d3a6f17270	+4915158832107	33377415840	\N	lucas@cliquereceita.com.br	$2b$12$43v.mqA1WYFPBSiKgQlmHegtvjaCHwt1UZw1v3vTEXiMI3D7aEZJ2	\N	2025-08-23 13:03:20.14444+00	2025-10-21 00:35:27.109689+00	admin,doctor	t
a0e6d250-2365-489d-85f7-96c9b5d934ec	\N	\N	\N	lcsa@ak.com	$2b$12$qp6DrgLyZFm9mCkg.tib4OIRPTVreBO.nyO8FbKZooSBBlMTCqsa6	\N	2025-10-26 14:08:41.903144+00	2025-10-26 14:08:41.903144+00	doctor	t
d04d8ef9-394b-4077-8acc-4ec48ac89937	\N	\N	\N	231@gmail.com	$2b$12$XqkQKAPY1yPrSYI1SIEbn.TObdCEIFtZrSuMG/UnzB9EWXVY0MWa6	\N	2025-10-26 14:32:49.094167+00	2025-10-26 14:32:49.094167+00	doctor	t
917b5903-544c-4d2b-802a-d8724b2f1d3c	\N	\N	\N	lcsavb@mgil.com	$2b$12$VaDJJUK12HPrpXhYHCTTou/27JqRIdvQ/.Kw3Y/KtjJkqXHuBKdBS	\N	2025-10-26 14:54:50.15712+00	2025-10-26 14:54:50.15712+00	doctor	t
d5bf74ee-1147-4ff5-a2c8-17b9fd2a958c	\N	\N	\N	vamos@gmail.com	$2b$12$6wDZQNox5/tlBEWgpuD/b.DEDE2CnUbnxItjRrJ.GDi1g/lcqPLd2	\N	2025-10-26 21:57:02.959144+00	2025-10-26 21:57:02.959144+00	doctor	t
84704d75-9e37-4bbb-ba87-778679f538a1	\N	\N	\N	lcs@lg.com	$2b$12$jwCkL48XyhOIuNQI./.UhejTR2AF/5Za916an7VydfMwr8/esmV12	\N	2025-10-27 10:15:33.753371+00	2025-10-27 10:15:33.753371+00	doctor	t
81c591f5-2bbc-4cdf-9363-43e4ba222648	\N	\N	\N	lcs@lcs.com	$2b$12$ml8Hes.0RT77Lc8DMGUePOPL6EJhQNXi9FMn.LZDCPQj9Myx0MlF2	\N	2025-10-27 10:21:50.023675+00	2025-10-27 10:21:50.023675+00	doctor	t
82183e88-b149-4abf-81a1-03605a0ad465	\N	\N	\N	lcs@lcasdfasdfs.com	$2b$12$t0pNCDIuFO5T5itBlburcuDRVAyS4piNfEavMoxehn8S/Xog3ut/K	\N	2025-10-27 10:27:03.565725+00	2025-10-27 10:27:03.565725+00	doctor	t
e8c04bc5-b237-484d-be31-0369c3ad1a40	+5511992548	58748	NOMECOMPLETO	kadk@ksks.com	$2b$12$QunNHJjKzBoCb.LiN9m2z.b/mjrjnZZo5vW3Pb5S.NN.aWpjTpbhq	\N	2025-10-27 10:32:41.503742+00	2025-10-27 10:32:41.503742+00	doctor	t
6362c867-8ef6-4bc4-ba4b-fc7d17bd7f71	+5546546	33355487450	NOMECOMPLETO	lkasjdflkajsdfklasjdkl2jkalsdfjkl@lkajsdf.com	$2b$12$Isb76ChGSCbkTRcUtfqNYOQe0S5a6R7BfyVxYHJXEdgSXLscSwkBu	\N	2025-10-27 10:38:41.427331+00	2025-10-27 10:38:41.427331+00	doctor	t
4f8929c1-d6b1-4e41-a940-981f6a589ece	+5511982033818	35017532846	\N	heitorettori@gmail.com	$2b$12$yhpouU1F5MTGNOLC14ekaeyFaukej4z/IMGONOZ1UwYzYIqEBZdZe	\N	2025-10-15 13:31:55.377565+00	2025-10-28 12:16:17.940986+00	admin,doctor	t
\.


--
-- TOC entry 5150 (class 0 OID 25242)
-- Dependencies: 245
-- Data for Name: _sqlx_migrations; Type: TABLE DATA; Schema: public; Owner: doadmin
--

COPY public._sqlx_migrations (version, description, installed_on, success, checksum, execution_time) FROM stdin;
1	initial	2025-08-04 15:14:42.949609+00	t	\\x28f7eeff52d4259c0459db0f06b73bf40209c28ad8e37fb1a00eeb378049e2358f0e3d178f8130797f5cdfccb220e4ad	9815996
2	add password hash	2025-08-04 15:14:42.961282+00	t	\\x7da005fb6c246fd6a56a333d62abe4af2667418fe6f770c8e105cd7e3e25122acc3ecbb5a5ec0fcbba5a4a46acfca123	2105149
\.


--
-- TOC entry 4797 (class 2606 OID 25250)
-- Name: _sqlx_migrations _sqlx_migrations_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core._sqlx_migrations
    ADD CONSTRAINT _sqlx_migrations_pkey PRIMARY KEY (version);


--
-- TOC entry 4799 (class 2606 OID 25252)
-- Name: clinics clinics_cnpj_key; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.clinics
    ADD CONSTRAINT clinics_cnpj_key UNIQUE (cnpj);


--
-- TOC entry 4801 (class 2606 OID 25254)
-- Name: clinics clinics_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.clinics
    ADD CONSTRAINT clinics_pkey PRIMARY KEY (id);


--
-- TOC entry 4806 (class 2606 OID 25256)
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (id);


--
-- TOC entry 4817 (class 2606 OID 25258)
-- Name: doctor_blackouts doctor_blackouts_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.doctor_blackouts
    ADD CONSTRAINT doctor_blackouts_pkey PRIMARY KEY (id);


--
-- TOC entry 4820 (class 2606 OID 25260)
-- Name: doctor_certificates doctor_certificates_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.doctor_certificates
    ADD CONSTRAINT doctor_certificates_pkey PRIMARY KEY (doctor_id);


--
-- TOC entry 4822 (class 2606 OID 25262)
-- Name: doctor_extra_windows doctor_extra_windows_no_overlap; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.doctor_extra_windows
    ADD CONSTRAINT doctor_extra_windows_no_overlap EXCLUDE USING gist (doctor_id WITH =, win WITH &&);


--
-- TOC entry 4824 (class 2606 OID 25264)
-- Name: doctor_extra_windows doctor_extra_windows_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.doctor_extra_windows
    ADD CONSTRAINT doctor_extra_windows_pkey PRIMARY KEY (id);


--
-- TOC entry 4827 (class 2606 OID 25266)
-- Name: doctor_schedules doctor_schedules_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.doctor_schedules
    ADD CONSTRAINT doctor_schedules_pkey PRIMARY KEY (id);


--
-- TOC entry 4833 (class 2606 OID 25268)
-- Name: doctors doctors_crm_crm_state_key; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.doctors
    ADD CONSTRAINT doctors_crm_crm_state_key UNIQUE (crm, crm_state);


--
-- TOC entry 4835 (class 2606 OID 25270)
-- Name: doctors doctors_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.doctors
    ADD CONSTRAINT doctors_pkey PRIMARY KEY (id);


--
-- TOC entry 4858 (class 2606 OID 25272)
-- Name: files files_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);


--
-- TOC entry 4867 (class 2606 OID 25274)
-- Name: medical_history medical_history_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.medical_history
    ADD CONSTRAINT medical_history_pkey PRIMARY KEY (id);


--
-- TOC entry 4872 (class 2606 OID 25276)
-- Name: ocr_jobs ocr_jobs_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.ocr_jobs
    ADD CONSTRAINT ocr_jobs_pkey PRIMARY KEY (job_id);


--
-- TOC entry 4877 (class 2606 OID 25278)
-- Name: password_recovery_tokens password_recovery_tokens_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.password_recovery_tokens
    ADD CONSTRAINT password_recovery_tokens_pkey PRIMARY KEY (id);


--
-- TOC entry 4879 (class 2606 OID 25280)
-- Name: password_recovery_tokens password_recovery_tokens_token_key; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.password_recovery_tokens
    ADD CONSTRAINT password_recovery_tokens_token_key UNIQUE (token);


--
-- TOC entry 4885 (class 2606 OID 25282)
-- Name: patient_phones patient_phones_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.patient_phones
    ADD CONSTRAINT patient_phones_pkey PRIMARY KEY (id);


--
-- TOC entry 4887 (class 2606 OID 25284)
-- Name: patient_phones patient_phones_unique; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.patient_phones
    ADD CONSTRAINT patient_phones_unique UNIQUE (patient_id, phone);


--
-- TOC entry 4839 (class 2606 OID 25286)
-- Name: patients patients_cpf_key; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.patients
    ADD CONSTRAINT patients_cpf_key UNIQUE (cpf);


--
-- TOC entry 4841 (class 2606 OID 25288)
-- Name: patients patients_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.patients
    ADD CONSTRAINT patients_pkey PRIMARY KEY (id);


--
-- TOC entry 4843 (class 2606 OID 25290)
-- Name: patients patients_user_id_key; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.patients
    ADD CONSTRAINT patients_user_id_key UNIQUE (user_id);


--
-- TOC entry 4892 (class 2606 OID 25292)
-- Name: payment_splits payment_splits_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.payment_splits
    ADD CONSTRAINT payment_splits_pkey PRIMARY KEY (id);


--
-- TOC entry 4901 (class 2606 OID 25294)
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- TOC entry 4905 (class 2606 OID 25296)
-- Name: prescription_queue prescription_queue_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.prescription_queue
    ADD CONSTRAINT prescription_queue_pkey PRIMARY KEY (renewal_id);


--
-- TOC entry 4856 (class 2606 OID 25298)
-- Name: prescription_renewals prescriptions_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.prescription_renewals
    ADD CONSTRAINT prescriptions_pkey PRIMARY KEY (id);


--
-- TOC entry 4911 (class 2606 OID 25300)
-- Name: prescriptions prescriptions_pkey1; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.prescriptions
    ADD CONSTRAINT prescriptions_pkey1 PRIMARY KEY (id);


--
-- TOC entry 4914 (class 2606 OID 25302)
-- Name: processed_events processed_events_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.processed_events
    ADD CONSTRAINT processed_events_pkey PRIMARY KEY (event_type, entity_id, occurred_at);


--
-- TOC entry 4918 (class 2606 OID 25304)
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- TOC entry 4920 (class 2606 OID 25306)
-- Name: sessions sessions_token_key; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.sessions
    ADD CONSTRAINT sessions_token_key UNIQUE (token);


--
-- TOC entry 4881 (class 2606 OID 25308)
-- Name: password_recovery_tokens unique_active_token_per_user; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.password_recovery_tokens
    ADD CONSTRAINT unique_active_token_per_user UNIQUE (user_id);


--
-- TOC entry 4804 (class 2606 OID 25310)
-- Name: clinics uq_clinics_doctor_id; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.clinics
    ADD CONSTRAINT uq_clinics_doctor_id UNIQUE (doctor_id);


--
-- TOC entry 4925 (class 2606 OID 25312)
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (id);


--
-- TOC entry 4930 (class 2606 OID 25314)
-- Name: users users_cpf_key; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.users
    ADD CONSTRAINT users_cpf_key UNIQUE (cpf);


--
-- TOC entry 4932 (class 2606 OID 25316)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 4934 (class 2606 OID 25318)
-- Name: users users_phone_key; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.users
    ADD CONSTRAINT users_phone_key UNIQUE (phone);


--
-- TOC entry 4936 (class 2606 OID 25320)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4938 (class 2606 OID 25322)
-- Name: _sqlx_migrations _sqlx_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: doadmin
--

ALTER TABLE ONLY public._sqlx_migrations
    ADD CONSTRAINT _sqlx_migrations_pkey PRIMARY KEY (version);


--
-- TOC entry 4802 (class 1259 OID 25323)
-- Name: idx_clinics_cnpj; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_clinics_cnpj ON core.clinics USING btree (cnpj);


--
-- TOC entry 4807 (class 1259 OID 25324)
-- Name: idx_conversations_curated_data; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_conversations_curated_data ON core.conversations USING gin (curated_data);


--
-- TOC entry 4808 (class 1259 OID 25325)
-- Name: idx_conversations_ocr_request_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_conversations_ocr_request_id ON core.conversations USING btree (ocr_request_id) WHERE (ocr_request_id IS NOT NULL);


--
-- TOC entry 4809 (class 1259 OID 25326)
-- Name: idx_conversations_ocr_status; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_conversations_ocr_status ON core.conversations USING btree (ocr_status) WHERE (ocr_status IS NOT NULL);


--
-- TOC entry 4810 (class 1259 OID 25327)
-- Name: idx_conversations_patient_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_conversations_patient_id ON core.conversations USING btree (patient_id);


--
-- TOC entry 4811 (class 1259 OID 25328)
-- Name: idx_conversations_patient_phone_active; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE UNIQUE INDEX idx_conversations_patient_phone_active ON core.conversations USING btree (patient_id, phone_number) WHERE (is_active = true);


--
-- TOC entry 5242 (class 0 OID 0)
-- Dependencies: 4811
-- Name: INDEX idx_conversations_patient_phone_active; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON INDEX core.idx_conversations_patient_phone_active IS 'Enforces business rule: One active conversation per (patient, phone) pair.
   Allows family phone sharing where multiple patients use the same phone number.
   Each patient gets their own conversation with isolated SessionData.
   See Issue #17 for rationale.';


--
-- TOC entry 4812 (class 1259 OID 25329)
-- Name: idx_conversations_payment_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_conversations_payment_id ON core.conversations USING btree (payment_id) WHERE (payment_id IS NOT NULL);


--
-- TOC entry 4813 (class 1259 OID 25330)
-- Name: idx_conversations_phone_number; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_conversations_phone_number ON core.conversations USING btree (phone_number);


--
-- TOC entry 4814 (class 1259 OID 25331)
-- Name: idx_conversations_renewal_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_conversations_renewal_id ON core.conversations USING btree (prescription_renewal_id);


--
-- TOC entry 4815 (class 1259 OID 25332)
-- Name: idx_conversations_session_data; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_conversations_session_data ON core.conversations USING gin (session_data);


--
-- TOC entry 4818 (class 1259 OID 25333)
-- Name: idx_doctor_blackouts_lower; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_doctor_blackouts_lower ON core.doctor_blackouts USING btree (doctor_id, lower(win));


--
-- TOC entry 4825 (class 1259 OID 25334)
-- Name: idx_doctor_extra_windows_lower; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_doctor_extra_windows_lower ON core.doctor_extra_windows USING btree (doctor_id, lower(win));


--
-- TOC entry 4828 (class 1259 OID 25335)
-- Name: idx_doctor_schedules_active; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_doctor_schedules_active ON core.doctor_schedules USING btree (active);


--
-- TOC entry 4829 (class 1259 OID 25336)
-- Name: idx_doctor_schedules_availability; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_doctor_schedules_availability ON core.doctor_schedules USING btree (day_of_week, start_time, end_time) WHERE (active = true);


--
-- TOC entry 4830 (class 1259 OID 25337)
-- Name: idx_doctor_schedules_doctor_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_doctor_schedules_doctor_id ON core.doctor_schedules USING btree (doctor_id);


--
-- TOC entry 4831 (class 1259 OID 25338)
-- Name: idx_doctor_schedules_no_overlap; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE UNIQUE INDEX idx_doctor_schedules_no_overlap ON core.doctor_schedules USING btree (doctor_id, day_of_week, start_time, end_time) WHERE (active = true);


--
-- TOC entry 4859 (class 1259 OID 25339)
-- Name: idx_files_medical_history_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_files_medical_history_id ON core.files USING btree (medical_history_id);


--
-- TOC entry 4860 (class 1259 OID 25340)
-- Name: idx_files_patient_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_files_patient_id ON core.files USING btree (patient_id) WHERE (patient_id IS NOT NULL);


--
-- TOC entry 4861 (class 1259 OID 25341)
-- Name: idx_files_renewal_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_files_renewal_id ON core.files USING btree (prescription_renewal_id) WHERE (prescription_renewal_id IS NOT NULL);


--
-- TOC entry 4862 (class 1259 OID 25342)
-- Name: idx_medical_history_not_draft; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_medical_history_not_draft ON core.medical_history USING btree (patient_id, created_at DESC) WHERE (is_draft = false);


--
-- TOC entry 5243 (class 0 OID 0)
-- Dependencies: 4862
-- Name: INDEX idx_medical_history_not_draft; Type: COMMENT; Schema: core; Owner: doadmin
--

COMMENT ON INDEX core.idx_medical_history_not_draft IS 'Optimized index for fetching official (non-draft) medical history versions by patient.';


--
-- TOC entry 4863 (class 1259 OID 25343)
-- Name: idx_medical_history_patient_date; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_medical_history_patient_date ON core.medical_history USING btree (patient_id, created_at DESC);


--
-- TOC entry 4864 (class 1259 OID 25344)
-- Name: idx_medical_history_patient_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_medical_history_patient_id ON core.medical_history USING btree (patient_id);


--
-- TOC entry 4865 (class 1259 OID 25345)
-- Name: idx_medical_history_version; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_medical_history_version ON core.medical_history USING btree (patient_id, version DESC);


--
-- TOC entry 4868 (class 1259 OID 25346)
-- Name: idx_ocr_jobs_conversation; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_ocr_jobs_conversation ON core.ocr_jobs USING btree (conversation_id);


--
-- TOC entry 4869 (class 1259 OID 25347)
-- Name: idx_ocr_jobs_photo_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE UNIQUE INDEX idx_ocr_jobs_photo_id ON core.ocr_jobs USING btree (photo_id);


--
-- TOC entry 4870 (class 1259 OID 25348)
-- Name: idx_ocr_jobs_status; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_ocr_jobs_status ON core.ocr_jobs USING btree (status, created_at);


--
-- TOC entry 4873 (class 1259 OID 25349)
-- Name: idx_password_recovery_tokens_expires_at; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_password_recovery_tokens_expires_at ON core.password_recovery_tokens USING btree (expires_at);


--
-- TOC entry 4874 (class 1259 OID 25350)
-- Name: idx_password_recovery_tokens_token; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_password_recovery_tokens_token ON core.password_recovery_tokens USING btree (token);


--
-- TOC entry 4875 (class 1259 OID 25351)
-- Name: idx_password_recovery_tokens_user_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_password_recovery_tokens_user_id ON core.password_recovery_tokens USING btree (user_id);


--
-- TOC entry 4882 (class 1259 OID 25352)
-- Name: idx_patient_phones_one_primary; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE UNIQUE INDEX idx_patient_phones_one_primary ON core.patient_phones USING btree (patient_id) WHERE (is_primary = true);


--
-- TOC entry 4883 (class 1259 OID 25353)
-- Name: idx_patient_phones_patient_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_patient_phones_patient_id ON core.patient_phones USING btree (patient_id);


--
-- TOC entry 4836 (class 1259 OID 25354)
-- Name: idx_patients_cpf; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_patients_cpf ON core.patients USING btree (cpf);


--
-- TOC entry 4837 (class 1259 OID 25355)
-- Name: idx_patients_email; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_patients_email ON core.patients USING btree (email);


--
-- TOC entry 4888 (class 1259 OID 25356)
-- Name: idx_payment_splits_payment_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_payment_splits_payment_id ON core.payment_splits USING btree (payment_id);


--
-- TOC entry 4889 (class 1259 OID 25357)
-- Name: idx_payment_splits_recipient; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_payment_splits_recipient ON core.payment_splits USING btree (recipient_type, recipient_id);


--
-- TOC entry 4890 (class 1259 OID 25358)
-- Name: idx_payment_splits_status; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_payment_splits_status ON core.payment_splits USING btree (status);


--
-- TOC entry 4893 (class 1259 OID 25359)
-- Name: idx_payments_created_at; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_payments_created_at ON core.payments USING btree (created_at DESC);


--
-- TOC entry 4894 (class 1259 OID 25360)
-- Name: idx_payments_payment_link; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_payments_payment_link ON core.payments USING btree (payment_link) WHERE (payment_link IS NOT NULL);


--
-- TOC entry 4895 (class 1259 OID 25361)
-- Name: idx_payments_pending_expiry; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_payments_pending_expiry ON core.payments USING btree (created_at) WHERE ((status)::text = 'pending'::text);


--
-- TOC entry 4896 (class 1259 OID 25362)
-- Name: idx_payments_phone_number; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_payments_phone_number ON core.payments USING btree (phone_number);


--
-- TOC entry 4897 (class 1259 OID 25363)
-- Name: idx_payments_phone_status; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_payments_phone_status ON core.payments USING btree (phone_number, status) WHERE ((status)::text = 'confirmed'::text);


--
-- TOC entry 4898 (class 1259 OID 25364)
-- Name: idx_payments_renewal_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_payments_renewal_id ON core.payments USING btree (prescription_renewal_id);


--
-- TOC entry 4899 (class 1259 OID 25365)
-- Name: idx_payments_status; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_payments_status ON core.payments USING btree (status);


--
-- TOC entry 4902 (class 1259 OID 25366)
-- Name: idx_prescription_queue_assigned_doctor; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_prescription_queue_assigned_doctor ON core.prescription_queue USING btree (assigned_doctor_id);


--
-- TOC entry 4903 (class 1259 OID 25367)
-- Name: idx_prescription_queue_priority; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_prescription_queue_priority ON core.prescription_queue USING btree (priority, created_at);


--
-- TOC entry 4844 (class 1259 OID 25368)
-- Name: idx_prescription_renewals_approval_failed; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_prescription_renewals_approval_failed ON core.prescription_renewals USING btree (doctor_id) WHERE ((status)::text = 'approval_failed'::text);


--
-- TOC entry 4845 (class 1259 OID 25369)
-- Name: idx_prescription_renewals_medical_history_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_prescription_renewals_medical_history_id ON core.prescription_renewals USING btree (medical_history_id);


--
-- TOC entry 4846 (class 1259 OID 25370)
-- Name: idx_prescription_renewals_queue_priority; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_prescription_renewals_queue_priority ON core.prescription_renewals USING btree (doctor_id, (
CASE
    WHEN ((status)::text = 'approval_failed'::text) THEN 0
    ELSE 1
END), risk_level, created_at) WHERE ((status)::text = ANY (ARRAY[('pending'::character varying)::text, ('under_review'::character varying)::text, ('approval_failed'::character varying)::text]));


--
-- TOC entry 4847 (class 1259 OID 25371)
-- Name: idx_prescription_renewals_row_version; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_prescription_renewals_row_version ON core.prescription_renewals USING btree (row_version);


--
-- TOC entry 4848 (class 1259 OID 25372)
-- Name: idx_prescription_renewals_temporary_files; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_prescription_renewals_temporary_files ON core.prescription_renewals USING gin (temporary_files);


--
-- TOC entry 4906 (class 1259 OID 25373)
-- Name: idx_prescriptions_doctor_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_prescriptions_doctor_id ON core.prescriptions USING btree (doctor_id);


--
-- TOC entry 4907 (class 1259 OID 25374)
-- Name: idx_prescriptions_issued_date; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_prescriptions_issued_date ON core.prescriptions USING btree (issued_date);


--
-- TOC entry 4908 (class 1259 OID 25375)
-- Name: idx_prescriptions_patient_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_prescriptions_patient_id ON core.prescriptions USING btree (patient_id);


--
-- TOC entry 4909 (class 1259 OID 25376)
-- Name: idx_prescriptions_valid_until; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_prescriptions_valid_until ON core.prescriptions USING btree (valid_until);


--
-- TOC entry 4912 (class 1259 OID 25377)
-- Name: idx_processed_events_entity; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_processed_events_entity ON core.processed_events USING btree (entity_id);


--
-- TOC entry 4849 (class 1259 OID 25378)
-- Name: idx_renewals_created_at; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_renewals_created_at ON core.prescription_renewals USING btree (created_at DESC);


--
-- TOC entry 4850 (class 1259 OID 25379)
-- Name: idx_renewals_doctor_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_renewals_doctor_id ON core.prescription_renewals USING btree (doctor_id);


--
-- TOC entry 4851 (class 1259 OID 25380)
-- Name: idx_renewals_patient_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_renewals_patient_id ON core.prescription_renewals USING btree (patient_id);


--
-- TOC entry 4852 (class 1259 OID 25381)
-- Name: idx_renewals_permanently_rejected; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_renewals_permanently_rejected ON core.prescription_renewals USING btree (is_permanently_rejected) WHERE (is_permanently_rejected = true);


--
-- TOC entry 4853 (class 1259 OID 25382)
-- Name: idx_renewals_prescription_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_renewals_prescription_id ON core.prescription_renewals USING btree (prescription_id);


--
-- TOC entry 4854 (class 1259 OID 25383)
-- Name: idx_renewals_status; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_renewals_status ON core.prescription_renewals USING btree (status);


--
-- TOC entry 4915 (class 1259 OID 25384)
-- Name: idx_sessions_expires_at; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_sessions_expires_at ON core.sessions USING btree (expires_at);


--
-- TOC entry 4916 (class 1259 OID 25385)
-- Name: idx_sessions_token; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_sessions_token ON core.sessions USING btree (token);


--
-- TOC entry 4921 (class 1259 OID 25386)
-- Name: idx_user_sessions_expires_at; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_user_sessions_expires_at ON core.user_sessions USING btree (expires_at);


--
-- TOC entry 4922 (class 1259 OID 25387)
-- Name: idx_user_sessions_phone; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_user_sessions_phone ON core.user_sessions USING btree (phone);


--
-- TOC entry 4923 (class 1259 OID 25388)
-- Name: idx_user_sessions_user_id; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_user_sessions_user_id ON core.user_sessions USING btree (user_id);


--
-- TOC entry 4926 (class 1259 OID 25389)
-- Name: idx_users_cpf; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_users_cpf ON core.users USING btree (cpf);


--
-- TOC entry 4927 (class 1259 OID 25390)
-- Name: idx_users_email; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_users_email ON core.users USING btree (email);


--
-- TOC entry 4928 (class 1259 OID 25391)
-- Name: idx_users_type; Type: INDEX; Schema: core; Owner: doadmin
--

CREATE INDEX idx_users_type ON core.users USING btree (user_type);


--
-- TOC entry 4968 (class 2620 OID 25392)
-- Name: clinics update_clinics_updated_at; Type: TRIGGER; Schema: core; Owner: doadmin
--

CREATE TRIGGER update_clinics_updated_at BEFORE UPDATE ON core.clinics FOR EACH ROW EXECUTE FUNCTION core.update_updated_at_column();


--
-- TOC entry 4969 (class 2620 OID 25393)
-- Name: doctor_blackouts update_doctor_blackouts_updated_at; Type: TRIGGER; Schema: core; Owner: doadmin
--

CREATE TRIGGER update_doctor_blackouts_updated_at BEFORE UPDATE ON core.doctor_blackouts FOR EACH ROW EXECUTE FUNCTION core.update_updated_at_column();


--
-- TOC entry 4970 (class 2620 OID 25394)
-- Name: doctor_extra_windows update_doctor_extra_windows_updated_at; Type: TRIGGER; Schema: core; Owner: doadmin
--

CREATE TRIGGER update_doctor_extra_windows_updated_at BEFORE UPDATE ON core.doctor_extra_windows FOR EACH ROW EXECUTE FUNCTION core.update_updated_at_column();


--
-- TOC entry 4971 (class 2620 OID 25395)
-- Name: doctor_schedules update_doctor_schedules_updated_at; Type: TRIGGER; Schema: core; Owner: doadmin
--

CREATE TRIGGER update_doctor_schedules_updated_at BEFORE UPDATE ON core.doctor_schedules FOR EACH ROW EXECUTE FUNCTION core.update_updated_at_column();


--
-- TOC entry 4972 (class 2620 OID 25396)
-- Name: doctors update_doctors_updated_at; Type: TRIGGER; Schema: core; Owner: doadmin
--

CREATE TRIGGER update_doctors_updated_at BEFORE UPDATE ON core.doctors FOR EACH ROW EXECUTE FUNCTION core.update_updated_at_column();


--
-- TOC entry 4975 (class 2620 OID 25397)
-- Name: files update_files_updated_at; Type: TRIGGER; Schema: core; Owner: doadmin
--

CREATE TRIGGER update_files_updated_at BEFORE UPDATE ON core.files FOR EACH ROW EXECUTE FUNCTION core.update_updated_at_column();


--
-- TOC entry 4976 (class 2620 OID 25398)
-- Name: medical_history update_medical_history_updated_at; Type: TRIGGER; Schema: core; Owner: doadmin
--

CREATE TRIGGER update_medical_history_updated_at BEFORE UPDATE ON core.medical_history FOR EACH ROW EXECUTE FUNCTION core.update_updated_at_column();


--
-- TOC entry 4977 (class 2620 OID 25399)
-- Name: patient_phones update_patient_phones_updated_at; Type: TRIGGER; Schema: core; Owner: doadmin
--

CREATE TRIGGER update_patient_phones_updated_at BEFORE UPDATE ON core.patient_phones FOR EACH ROW EXECUTE FUNCTION core.update_updated_at_column();


--
-- TOC entry 4973 (class 2620 OID 25400)
-- Name: patients update_patients_updated_at; Type: TRIGGER; Schema: core; Owner: doadmin
--

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON core.patients FOR EACH ROW EXECUTE FUNCTION core.update_updated_at_column();


--
-- TOC entry 4978 (class 2620 OID 25401)
-- Name: prescriptions update_prescriptions_updated_at; Type: TRIGGER; Schema: core; Owner: doadmin
--

CREATE TRIGGER update_prescriptions_updated_at BEFORE UPDATE ON core.prescriptions FOR EACH ROW EXECUTE FUNCTION core.update_updated_at_column();


--
-- TOC entry 4974 (class 2620 OID 25402)
-- Name: prescription_renewals update_renewals_updated_at; Type: TRIGGER; Schema: core; Owner: doadmin
--

CREATE TRIGGER update_renewals_updated_at BEFORE UPDATE ON core.prescription_renewals FOR EACH ROW EXECUTE FUNCTION core.update_updated_at_column();


--
-- TOC entry 4979 (class 2620 OID 25403)
-- Name: user_sessions update_user_sessions_updated_at; Type: TRIGGER; Schema: core; Owner: doadmin
--

CREATE TRIGGER update_user_sessions_updated_at BEFORE UPDATE ON core.user_sessions FOR EACH ROW EXECUTE FUNCTION core.update_updated_at_column();


--
-- TOC entry 4980 (class 2620 OID 25404)
-- Name: users update_users_updated_at; Type: TRIGGER; Schema: core; Owner: doadmin
--

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON core.users FOR EACH ROW EXECUTE FUNCTION core.update_updated_at_column();


--
-- TOC entry 4940 (class 2606 OID 25405)
-- Name: conversations conversations_patient_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.conversations
    ADD CONSTRAINT conversations_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES core.patients(id) ON DELETE CASCADE;


--
-- TOC entry 4941 (class 2606 OID 25410)
-- Name: conversations conversations_payment_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.conversations
    ADD CONSTRAINT conversations_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES core.payments(id) ON DELETE SET NULL;


--
-- TOC entry 4943 (class 2606 OID 25415)
-- Name: doctor_blackouts doctor_blackouts_doctor_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.doctor_blackouts
    ADD CONSTRAINT doctor_blackouts_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES core.doctors(id) ON DELETE CASCADE;


--
-- TOC entry 4945 (class 2606 OID 25420)
-- Name: doctor_extra_windows doctor_extra_windows_doctor_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.doctor_extra_windows
    ADD CONSTRAINT doctor_extra_windows_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES core.doctors(id) ON DELETE CASCADE;


--
-- TOC entry 4946 (class 2606 OID 25425)
-- Name: doctor_schedules doctor_schedules_doctor_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.doctor_schedules
    ADD CONSTRAINT doctor_schedules_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES core.doctors(id) ON DELETE CASCADE;


--
-- TOC entry 4947 (class 2606 OID 25430)
-- Name: doctors doctors_user_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.doctors
    ADD CONSTRAINT doctors_user_id_fkey FOREIGN KEY (user_id) REFERENCES core.users(id);


--
-- TOC entry 4953 (class 2606 OID 25435)
-- Name: files files_medical_history_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.files
    ADD CONSTRAINT files_medical_history_id_fkey FOREIGN KEY (medical_history_id) REFERENCES core.medical_history(id) ON DELETE CASCADE;


--
-- TOC entry 4939 (class 2606 OID 25440)
-- Name: clinics fk_clinics_doctor; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.clinics
    ADD CONSTRAINT fk_clinics_doctor FOREIGN KEY (doctor_id) REFERENCES core.doctors(id) ON DELETE CASCADE;


--
-- TOC entry 4942 (class 2606 OID 25445)
-- Name: conversations fk_conversations_prescription_renewal; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.conversations
    ADD CONSTRAINT fk_conversations_prescription_renewal FOREIGN KEY (prescription_renewal_id) REFERENCES core.prescription_renewals(id) ON DELETE CASCADE;


--
-- TOC entry 4944 (class 2606 OID 25450)
-- Name: doctor_certificates fk_doctor_certificates_doctor_id; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.doctor_certificates
    ADD CONSTRAINT fk_doctor_certificates_doctor_id FOREIGN KEY (doctor_id) REFERENCES core.doctors(id) ON DELETE CASCADE;


--
-- TOC entry 4954 (class 2606 OID 25455)
-- Name: files fk_files_conversation; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.files
    ADD CONSTRAINT fk_files_conversation FOREIGN KEY (conversation_id) REFERENCES core.conversations(id) ON DELETE SET NULL;


--
-- TOC entry 4955 (class 2606 OID 25460)
-- Name: files fk_files_patient; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.files
    ADD CONSTRAINT fk_files_patient FOREIGN KEY (patient_id) REFERENCES core.patients(id) ON DELETE CASCADE;


--
-- TOC entry 4956 (class 2606 OID 25465)
-- Name: files fk_files_renewal; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.files
    ADD CONSTRAINT fk_files_renewal FOREIGN KEY (prescription_renewal_id) REFERENCES core.prescription_renewals(id) ON DELETE SET NULL;


--
-- TOC entry 4961 (class 2606 OID 25470)
-- Name: payments fk_payments_prescription_renewal; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.payments
    ADD CONSTRAINT fk_payments_prescription_renewal FOREIGN KEY (prescription_renewal_id) REFERENCES core.prescription_renewals(id) ON DELETE CASCADE;


--
-- TOC entry 4949 (class 2606 OID 25475)
-- Name: prescription_renewals fk_prescriptionrenewals_prescriptions; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.prescription_renewals
    ADD CONSTRAINT fk_prescriptionrenewals_prescriptions FOREIGN KEY (prescription_id) REFERENCES core.prescriptions(id) ON DELETE CASCADE;


--
-- TOC entry 4957 (class 2606 OID 25480)
-- Name: medical_history medical_history_patient_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.medical_history
    ADD CONSTRAINT medical_history_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES core.patients(id) ON DELETE CASCADE;


--
-- TOC entry 4958 (class 2606 OID 25485)
-- Name: password_recovery_tokens password_recovery_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.password_recovery_tokens
    ADD CONSTRAINT password_recovery_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES core.users(id) ON DELETE CASCADE;


--
-- TOC entry 4959 (class 2606 OID 25490)
-- Name: patient_phones patient_phones_patient_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.patient_phones
    ADD CONSTRAINT patient_phones_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES core.patients(id) ON DELETE CASCADE;


--
-- TOC entry 4948 (class 2606 OID 25495)
-- Name: patients patients_user_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.patients
    ADD CONSTRAINT patients_user_id_fkey FOREIGN KEY (user_id) REFERENCES core.users(id) ON DELETE CASCADE;


--
-- TOC entry 4960 (class 2606 OID 25500)
-- Name: payment_splits payment_splits_payment_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.payment_splits
    ADD CONSTRAINT payment_splits_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES core.payments(id) ON DELETE CASCADE;


--
-- TOC entry 4962 (class 2606 OID 25505)
-- Name: prescription_queue prescription_queue_assigned_doctor_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.prescription_queue
    ADD CONSTRAINT prescription_queue_assigned_doctor_id_fkey FOREIGN KEY (assigned_doctor_id) REFERENCES core.doctors(id);


--
-- TOC entry 4963 (class 2606 OID 25510)
-- Name: prescription_queue prescription_queue_renewal_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.prescription_queue
    ADD CONSTRAINT prescription_queue_renewal_id_fkey FOREIGN KEY (renewal_id) REFERENCES core.prescription_renewals(id) ON DELETE CASCADE;


--
-- TOC entry 4950 (class 2606 OID 25515)
-- Name: prescription_renewals prescription_renewals_medical_history_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.prescription_renewals
    ADD CONSTRAINT prescription_renewals_medical_history_id_fkey FOREIGN KEY (medical_history_id) REFERENCES core.medical_history(id) ON DELETE SET NULL;


--
-- TOC entry 4951 (class 2606 OID 25520)
-- Name: prescription_renewals prescriptions_doctor_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.prescription_renewals
    ADD CONSTRAINT prescriptions_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES core.doctors(id);


--
-- TOC entry 4964 (class 2606 OID 25525)
-- Name: prescriptions prescriptions_doctor_id_fkey1; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.prescriptions
    ADD CONSTRAINT prescriptions_doctor_id_fkey1 FOREIGN KEY (doctor_id) REFERENCES core.doctors(id);


--
-- TOC entry 4952 (class 2606 OID 25530)
-- Name: prescription_renewals prescriptions_patient_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.prescription_renewals
    ADD CONSTRAINT prescriptions_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES core.patients(id) ON DELETE CASCADE;


--
-- TOC entry 4965 (class 2606 OID 25535)
-- Name: prescriptions prescriptions_patient_id_fkey1; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.prescriptions
    ADD CONSTRAINT prescriptions_patient_id_fkey1 FOREIGN KEY (patient_id) REFERENCES core.patients(id);


--
-- TOC entry 4966 (class 2606 OID 25540)
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES core.users(id);


--
-- TOC entry 4967 (class 2606 OID 25545)
-- Name: user_sessions user_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: doadmin
--

ALTER TABLE ONLY core.user_sessions
    ADD CONSTRAINT user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES core.users(id) ON DELETE CASCADE;


-- Completed on 2025-11-03 00:50:12 CET

--
-- PostgreSQL database dump complete
--

\unrestrict hksdDt5C7qP4gl1vmdM2ZULjD9joIYS56H2xZeQ48uOUXWQVy6qyfwBSgaOvYua


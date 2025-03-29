--
-- PostgreSQL database dump
--

-- Dumped from database version 11.22
-- Dumped by pg_dump version 11.22

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO lucas;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO lucas;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO lucas;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.auth_group_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO lucas;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO lucas;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO lucas;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;


--
-- Name: clinicas_clinica; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.clinicas_clinica (
    id integer NOT NULL,
    nome_clinica character varying(200) NOT NULL,
    cns_clinica character varying(7) NOT NULL,
    logradouro character varying(200) NOT NULL,
    logradouro_num character varying(6) NOT NULL,
    cidade character varying(30) NOT NULL,
    bairro character varying(30) NOT NULL,
    cep character varying(9) NOT NULL,
    telefone_clinica character varying(13) NOT NULL
);


ALTER TABLE public.clinicas_clinica OWNER TO lucas;

--
-- Name: clinicas_clinica_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.clinicas_clinica_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.clinicas_clinica_id_seq OWNER TO lucas;

--
-- Name: clinicas_clinica_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.clinicas_clinica_id_seq OWNED BY public.clinicas_clinica.id;


--
-- Name: clinicas_clinicausuario; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.clinicas_clinicausuario (
    id integer NOT NULL,
    clinica_id integer,
    usuario_id integer
);


ALTER TABLE public.clinicas_clinicausuario OWNER TO lucas;

--
-- Name: clinicas_clinicausuario_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.clinicas_clinicausuario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.clinicas_clinicausuario_id_seq OWNER TO lucas;

--
-- Name: clinicas_clinicausuario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.clinicas_clinicausuario_id_seq OWNED BY public.clinicas_clinicausuario.id;


--
-- Name: clinicas_emissor; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.clinicas_emissor (
    id integer NOT NULL,
    clinica_id integer NOT NULL,
    medico_id integer NOT NULL
);


ALTER TABLE public.clinicas_emissor OWNER TO lucas;

--
-- Name: clinicas_emissor_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.clinicas_emissor_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.clinicas_emissor_id_seq OWNER TO lucas;

--
-- Name: clinicas_emissor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.clinicas_emissor_id_seq OWNED BY public.clinicas_emissor.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO lucas;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO lucas;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO lucas;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO lucas;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO lucas;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.django_migrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO lucas;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO lucas;

--
-- Name: medicos_medico; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.medicos_medico (
    id integer NOT NULL,
    nome_medico character varying(200) NOT NULL,
    crm_medico character varying(10) NOT NULL,
    cns_medico character varying(15) NOT NULL
);


ALTER TABLE public.medicos_medico OWNER TO lucas;

--
-- Name: medicos_medico_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.medicos_medico_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.medicos_medico_id_seq OWNER TO lucas;

--
-- Name: medicos_medico_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.medicos_medico_id_seq OWNED BY public.medicos_medico.id;


--
-- Name: medicos_medicousuario; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.medicos_medicousuario (
    id integer NOT NULL,
    medico_id integer,
    usuario_id integer
);


ALTER TABLE public.medicos_medicousuario OWNER TO lucas;

--
-- Name: medicos_medicousuario_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.medicos_medicousuario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.medicos_medicousuario_id_seq OWNER TO lucas;

--
-- Name: medicos_medicousuario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.medicos_medicousuario_id_seq OWNED BY public.medicos_medicousuario.id;


--
-- Name: pacientes_paciente; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.pacientes_paciente (
    id integer NOT NULL,
    nome_paciente character varying(100) NOT NULL,
    idade character varying(100) NOT NULL,
    sexo character varying(100) NOT NULL,
    nome_mae character varying(100) NOT NULL,
    incapaz boolean NOT NULL,
    nome_responsavel character varying(100) NOT NULL,
    rg character varying(100) NOT NULL,
    peso character varying(100) NOT NULL,
    altura character varying(100) NOT NULL,
    escolha_etnia character varying(100) NOT NULL,
    cpf_paciente character varying(14) NOT NULL,
    cns_paciente character varying(100) NOT NULL,
    email_paciente character varying(254),
    cidade_paciente character varying(100) NOT NULL,
    end_paciente character varying(100) NOT NULL,
    cep_paciente character varying(100) NOT NULL,
    telefone1_paciente character varying(100) NOT NULL,
    telefone2_paciente character varying(100) NOT NULL,
    etnia character varying(100) NOT NULL
);


ALTER TABLE public.pacientes_paciente OWNER TO lucas;

--
-- Name: pacientes_paciente_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.pacientes_paciente_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pacientes_paciente_id_seq OWNER TO lucas;

--
-- Name: pacientes_paciente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.pacientes_paciente_id_seq OWNED BY public.pacientes_paciente.id;


--
-- Name: pacientes_paciente_usuarios; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.pacientes_paciente_usuarios (
    id integer NOT NULL,
    paciente_id integer NOT NULL,
    usuario_id integer NOT NULL
);


ALTER TABLE public.pacientes_paciente_usuarios OWNER TO lucas;

--
-- Name: pacientes_paciente_usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.pacientes_paciente_usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pacientes_paciente_usuarios_id_seq OWNER TO lucas;

--
-- Name: pacientes_paciente_usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.pacientes_paciente_usuarios_id_seq OWNED BY public.pacientes_paciente_usuarios.id;


--
-- Name: processos_doenca; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.processos_doenca (
    id integer NOT NULL,
    cid character varying(6) NOT NULL,
    nome character varying(500) NOT NULL,
    protocolo_id integer
);


ALTER TABLE public.processos_doenca OWNER TO lucas;

--
-- Name: processos_doenca_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.processos_doenca_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.processos_doenca_id_seq OWNER TO lucas;

--
-- Name: processos_doenca_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.processos_doenca_id_seq OWNED BY public.processos_doenca.id;


--
-- Name: processos_medicamento; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.processos_medicamento (
    id integer NOT NULL,
    nome character varying(600) NOT NULL,
    dosagem character varying(100) NOT NULL,
    apres character varying(600) NOT NULL
);


ALTER TABLE public.processos_medicamento OWNER TO lucas;

--
-- Name: processos_medicamento_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.processos_medicamento_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.processos_medicamento_id_seq OWNER TO lucas;

--
-- Name: processos_medicamento_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.processos_medicamento_id_seq OWNED BY public.processos_medicamento.id;


--
-- Name: processos_processo; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.processos_processo (
    id integer NOT NULL,
    anamnese text NOT NULL,
    prescricao jsonb NOT NULL,
    tratou boolean NOT NULL,
    tratamentos_previos text NOT NULL,
    data1 date,
    preenchido_por character varying(128) NOT NULL,
    dados_condicionais jsonb NOT NULL,
    clinica_id integer NOT NULL,
    doenca_id integer,
    emissor_id integer NOT NULL,
    medico_id integer NOT NULL,
    paciente_id integer NOT NULL,
    usuario_id integer NOT NULL
);


ALTER TABLE public.processos_processo OWNER TO lucas;

--
-- Name: processos_processo_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.processos_processo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.processos_processo_id_seq OWNER TO lucas;

--
-- Name: processos_processo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.processos_processo_id_seq OWNED BY public.processos_processo.id;


--
-- Name: processos_processo_medicamentos; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.processos_processo_medicamentos (
    id integer NOT NULL,
    processo_id integer NOT NULL,
    medicamento_id integer NOT NULL
);


ALTER TABLE public.processos_processo_medicamentos OWNER TO lucas;

--
-- Name: processos_processo_medicamentos_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.processos_processo_medicamentos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.processos_processo_medicamentos_id_seq OWNER TO lucas;

--
-- Name: processos_processo_medicamentos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.processos_processo_medicamentos_id_seq OWNED BY public.processos_processo_medicamentos.id;


--
-- Name: processos_protocolo; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.processos_protocolo (
    id integer NOT NULL,
    nome character varying(600) NOT NULL,
    arquivo character varying(600) NOT NULL,
    dados_condicionais jsonb
);


ALTER TABLE public.processos_protocolo OWNER TO lucas;

--
-- Name: processos_protocolo_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.processos_protocolo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.processos_protocolo_id_seq OWNER TO lucas;

--
-- Name: processos_protocolo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.processos_protocolo_id_seq OWNED BY public.processos_protocolo.id;


--
-- Name: processos_protocolo_medicamentos; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.processos_protocolo_medicamentos (
    id integer NOT NULL,
    protocolo_id integer NOT NULL,
    medicamento_id integer NOT NULL
);


ALTER TABLE public.processos_protocolo_medicamentos OWNER TO lucas;

--
-- Name: processos_protocolo_medicamentos_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.processos_protocolo_medicamentos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.processos_protocolo_medicamentos_id_seq OWNER TO lucas;

--
-- Name: processos_protocolo_medicamentos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.processos_protocolo_medicamentos_id_seq OWNED BY public.processos_protocolo_medicamentos.id;


--
-- Name: usuarios_usuario; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.usuarios_usuario (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    is_medico boolean NOT NULL,
    is_clinica boolean NOT NULL
);


ALTER TABLE public.usuarios_usuario OWNER TO lucas;

--
-- Name: usuarios_usuario_groups; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.usuarios_usuario_groups (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.usuarios_usuario_groups OWNER TO lucas;

--
-- Name: usuarios_usuario_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.usuarios_usuario_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.usuarios_usuario_groups_id_seq OWNER TO lucas;

--
-- Name: usuarios_usuario_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.usuarios_usuario_groups_id_seq OWNED BY public.usuarios_usuario_groups.id;


--
-- Name: usuarios_usuario_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.usuarios_usuario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.usuarios_usuario_id_seq OWNER TO lucas;

--
-- Name: usuarios_usuario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.usuarios_usuario_id_seq OWNED BY public.usuarios_usuario.id;


--
-- Name: usuarios_usuario_user_permissions; Type: TABLE; Schema: public; Owner: lucas
--

CREATE TABLE public.usuarios_usuario_user_permissions (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.usuarios_usuario_user_permissions OWNER TO lucas;

--
-- Name: usuarios_usuario_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: lucas
--

CREATE SEQUENCE public.usuarios_usuario_user_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.usuarios_usuario_user_permissions_id_seq OWNER TO lucas;

--
-- Name: usuarios_usuario_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: lucas
--

ALTER SEQUENCE public.usuarios_usuario_user_permissions_id_seq OWNED BY public.usuarios_usuario_user_permissions.id;


--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);


--
-- Name: clinicas_clinica id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.clinicas_clinica ALTER COLUMN id SET DEFAULT nextval('public.clinicas_clinica_id_seq'::regclass);


--
-- Name: clinicas_clinicausuario id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.clinicas_clinicausuario ALTER COLUMN id SET DEFAULT nextval('public.clinicas_clinicausuario_id_seq'::regclass);


--
-- Name: clinicas_emissor id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.clinicas_emissor ALTER COLUMN id SET DEFAULT nextval('public.clinicas_emissor_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- Name: medicos_medico id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.medicos_medico ALTER COLUMN id SET DEFAULT nextval('public.medicos_medico_id_seq'::regclass);


--
-- Name: medicos_medicousuario id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.medicos_medicousuario ALTER COLUMN id SET DEFAULT nextval('public.medicos_medicousuario_id_seq'::regclass);


--
-- Name: pacientes_paciente id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.pacientes_paciente ALTER COLUMN id SET DEFAULT nextval('public.pacientes_paciente_id_seq'::regclass);


--
-- Name: pacientes_paciente_usuarios id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.pacientes_paciente_usuarios ALTER COLUMN id SET DEFAULT nextval('public.pacientes_paciente_usuarios_id_seq'::regclass);


--
-- Name: processos_doenca id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_doenca ALTER COLUMN id SET DEFAULT nextval('public.processos_doenca_id_seq'::regclass);


--
-- Name: processos_medicamento id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_medicamento ALTER COLUMN id SET DEFAULT nextval('public.processos_medicamento_id_seq'::regclass);


--
-- Name: processos_processo id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_processo ALTER COLUMN id SET DEFAULT nextval('public.processos_processo_id_seq'::regclass);


--
-- Name: processos_processo_medicamentos id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_processo_medicamentos ALTER COLUMN id SET DEFAULT nextval('public.processos_processo_medicamentos_id_seq'::regclass);


--
-- Name: processos_protocolo id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_protocolo ALTER COLUMN id SET DEFAULT nextval('public.processos_protocolo_id_seq'::regclass);


--
-- Name: processos_protocolo_medicamentos id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_protocolo_medicamentos ALTER COLUMN id SET DEFAULT nextval('public.processos_protocolo_medicamentos_id_seq'::regclass);


--
-- Name: usuarios_usuario id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.usuarios_usuario ALTER COLUMN id SET DEFAULT nextval('public.usuarios_usuario_id_seq'::regclass);


--
-- Name: usuarios_usuario_groups id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.usuarios_usuario_groups ALTER COLUMN id SET DEFAULT nextval('public.usuarios_usuario_groups_id_seq'::regclass);


--
-- Name: usuarios_usuario_user_permissions id; Type: DEFAULT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.usuarios_usuario_user_permissions ALTER COLUMN id SET DEFAULT nextval('public.usuarios_usuario_user_permissions_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add doenca	1	add_doenca
2	Can change doenca	1	change_doenca
3	Can delete doenca	1	delete_doenca
4	Can view doenca	1	view_doenca
5	Can add medicamento	2	add_medicamento
6	Can change medicamento	2	change_medicamento
7	Can delete medicamento	2	delete_medicamento
8	Can view medicamento	2	view_medicamento
9	Can add protocolo	3	add_protocolo
10	Can change protocolo	3	change_protocolo
11	Can delete protocolo	3	delete_protocolo
12	Can view protocolo	3	view_protocolo
13	Can add processo	4	add_processo
14	Can change processo	4	change_processo
15	Can delete processo	4	delete_processo
16	Can view processo	4	view_processo
17	Can add medico	5	add_medico
18	Can change medico	5	change_medico
19	Can delete medico	5	delete_medico
20	Can view medico	5	view_medico
21	Can add medico usuario	6	add_medicousuario
22	Can change medico usuario	6	change_medicousuario
23	Can delete medico usuario	6	delete_medicousuario
24	Can view medico usuario	6	view_medicousuario
25	Can add clinica	7	add_clinica
26	Can change clinica	7	change_clinica
27	Can delete clinica	7	delete_clinica
28	Can view clinica	7	view_clinica
29	Can add clinica usuario	8	add_clinicausuario
30	Can change clinica usuario	8	change_clinicausuario
31	Can delete clinica usuario	8	delete_clinicausuario
32	Can view clinica usuario	8	view_clinicausuario
33	Can add emissor	9	add_emissor
34	Can change emissor	9	change_emissor
35	Can delete emissor	9	delete_emissor
36	Can view emissor	9	view_emissor
37	Can add paciente	10	add_paciente
38	Can change paciente	10	change_paciente
39	Can delete paciente	10	delete_paciente
40	Can view paciente	10	view_paciente
41	Can add usuario	11	add_usuario
42	Can change usuario	11	change_usuario
43	Can delete usuario	11	delete_usuario
44	Can view usuario	11	view_usuario
45	Can add log entry	12	add_logentry
46	Can change log entry	12	change_logentry
47	Can delete log entry	12	delete_logentry
48	Can view log entry	12	view_logentry
49	Can add permission	13	add_permission
50	Can change permission	13	change_permission
51	Can delete permission	13	delete_permission
52	Can view permission	13	view_permission
53	Can add group	14	add_group
54	Can change group	14	change_group
55	Can delete group	14	delete_group
56	Can view group	14	view_group
57	Can add content type	15	add_contenttype
58	Can change content type	15	change_contenttype
59	Can delete content type	15	delete_contenttype
60	Can view content type	15	view_contenttype
61	Can add session	16	add_session
62	Can change session	16	change_session
63	Can delete session	16	delete_session
64	Can view session	16	view_session
\.


--
-- Data for Name: clinicas_clinica; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.clinicas_clinica (id, nome_clinica, cns_clinica, logradouro, logradouro_num, cidade, bairro, cep, telefone_clinica) FROM stdin;
1	Dr. Oline	6832548	Rua Sena Madureira	300	São Paulo	Vila Mariana	06403-300	(11) 5484.548
\.


--
-- Data for Name: clinicas_clinicausuario; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.clinicas_clinicausuario (id, clinica_id, usuario_id) FROM stdin;
1	1	1
\.


--
-- Data for Name: clinicas_emissor; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.clinicas_emissor (id, clinica_id, medico_id) FROM stdin;
1	1	1
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	processos	doenca
2	processos	medicamento
3	processos	protocolo
4	processos	processo
5	medicos	medico
6	medicos	medicousuario
7	clinicas	clinica
8	clinicas	clinicausuario
9	clinicas	emissor
10	pacientes	paciente
11	usuarios	usuario
12	admin	logentry
13	auth	permission
14	auth	group
15	contenttypes	contenttype
16	sessions	session
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2025-03-26 12:28:01.404068+00
2	contenttypes	0002_remove_content_type_name	2025-03-26 12:28:01.40943+00
3	auth	0001_initial	2025-03-26 12:28:01.437973+00
4	auth	0002_alter_permission_name_max_length	2025-03-26 12:28:01.48319+00
5	auth	0003_alter_user_email_max_length	2025-03-26 12:28:01.486695+00
6	auth	0004_alter_user_username_opts	2025-03-26 12:28:01.490839+00
7	auth	0005_alter_user_last_login_null	2025-03-26 12:28:01.494374+00
8	auth	0006_require_contenttypes_0002	2025-03-26 12:28:01.497064+00
9	auth	0007_alter_validators_add_error_messages	2025-03-26 12:28:01.501001+00
10	auth	0008_alter_user_username_max_length	2025-03-26 12:28:01.504968+00
11	auth	0009_alter_user_last_name_max_length	2025-03-26 12:28:01.50803+00
12	auth	0010_alter_group_name_max_length	2025-03-26 12:28:01.513253+00
13	auth	0011_update_proxy_permissions	2025-03-26 12:28:01.516066+00
14	usuarios	0001_initial	2025-03-26 12:28:01.544251+00
15	admin	0001_initial	2025-03-26 12:28:01.606851+00
16	admin	0002_logentry_remove_auto_add	2025-03-26 12:28:01.622649+00
17	admin	0003_logentry_add_action_flag_choices	2025-03-26 12:28:01.627729+00
18	medicos	0001_initial	2025-03-26 12:28:01.656759+00
19	pacientes	0001_initial	2025-03-26 12:28:01.699327+00
20	clinicas	0001_initial	2025-03-26 12:28:01.733279+00
21	clinicas	0002_emissor_medico	2025-03-26 12:28:01.743211+00
22	processos	0001_initial	2025-03-26 12:28:01.827825+00
23	clinicas	0003_auto_20200228_1704	2025-03-26 12:28:01.917281+00
24	clinicas	0004_auto_20200228_1704	2025-03-26 12:28:01.939531+00
25	medicos	0002_auto_20200228_1704	2025-03-26 12:28:01.957454+00
26	pacientes	0002_paciente_usuarios	2025-03-26 12:28:01.977469+00
27	processos	0002_auto_20200228_1704	2025-03-26 12:28:02.012089+00
28	sessions	0001_initial	2025-03-26 12:28:02.066687+00
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
3dfea76see12wayw11cuymkg9rtn2yxj	N2QxODZkY2QyY2I4MDUzNDAzMzMxOThiZDU4MzY3ZjMxNTQ4NWRlMDp7ImNvbnZpdGVfYWNlaXRvIjp0cnVlLCJfYXV0aF91c2VyX2lkIjoiMSIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZmE4NGViMzc1MWQzMzgxODE5NWNiM2QyNGQzZmYyMmQ3YTlhOGExYiIsInBhY2llbnRlX2V4aXN0ZSI6ZmFsc2UsImNpZCI6Ikc0MC4wIiwiY3BmX3BhY2llbnRlIjoiMzMzLjc3NC4xNTgtNDAiLCJwYXRoX3BkZl9maW5hbCI6Ii9zdGF0aWMvdG1wL3BkZl9maW5hbF8zMzMuNzc0LjE1OC00MF9HNDAuMC5wZGYiLCJwcm9jZXNzb19pZCI6M30=	2025-04-09 12:42:29.977207+00
\.


--
-- Data for Name: medicos_medico; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.medicos_medico (id, nome_medico, crm_medico, cns_medico) FROM stdin;
1	Lucas Amorim Vieira de Barros	150494	980016283604585
\.


--
-- Data for Name: medicos_medicousuario; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.medicos_medicousuario (id, medico_id, usuario_id) FROM stdin;
1	1	1
\.


--
-- Data for Name: pacientes_paciente; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.pacientes_paciente (id, nome_paciente, idade, sexo, nome_mae, incapaz, nome_responsavel, rg, peso, altura, escolha_etnia, cpf_paciente, cns_paciente, email_paciente, cidade_paciente, end_paciente, cep_paciente, telefone1_paciente, telefone2_paciente, etnia) FROM stdin;
1	Lucas Amorim Vieira de Barros			Marlene	f			80	160		333.774.158-40				Rua das Flores, 40				etnia_branca
\.


--
-- Data for Name: pacientes_paciente_usuarios; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.pacientes_paciente_usuarios (id, paciente_id, usuario_id) FROM stdin;
1	1	1
\.


--
-- Data for Name: processos_doenca; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.processos_doenca (id, cid, nome, protocolo_id) FROM stdin;
20	Q82.8	Outras Malformações Congênitas Especificadas da Pele	\N
30	L73.2	Hidradenite Supurativa	\N
58	E22.0	Acromegalia e Gigantismo Hipofisário	2
148	D70	Agranulocitose	\N
157	D56.1	Talassemia Beta	\N
158	D56.8	Outras Talassemias	\N
190	Z94.1	Coração Transplantado	\N
176	L70.0	Acne Vulgar	1
177	L70.1	Acne Conglobata	1
178	L70.8	Outras Formas de Acne	1
141	D46.0	Anemia Refratária Sem Sideroblastos	3
142	D46.1	Anemia Refratária Com Sideroblastos	3
143	D46.7	Outras Síndromes Mielodisplásicas	3
149	Z94.8	Outros Órgãos e Tecidos Transplantados	3
53	D61.0	Anemia Aplástica Constitucional	4
144	D61.1	Anemia Aplástica Induzida Por Drogas	4
145	D61.2	Anemia Aplástica Devida a Outros Agentes Externos	4
146	D61.3	Anemia Aplástica Idiopática	4
147	D61.8	Outras Anemias Aplásticas Especificadas	4
69	D59.0	Anemia Hemolítica Auto-imune Induzida Por Droga	5
70	D59.1	Outras Anemias Hemolíticas Auto-imunes	5
43	N18.8	Outra Insuficiência Renal Crônica	7
120	D84.1	Defeitos no Sistema Complemento	8
131	M07.0	Artropatia Psoriásica Interfalangiana Distal	10
132	M07.2	Espondilite Psoriásica	10
133	M07.3	Outras Artropatias Psoriásicas	10
21	M08.1	Espondilite Ancilosante Juvenil	12
22	M08.2	Artrite Juvenil Com Início Sistêmico	12
23	M08.3	Poliartrite Juvenil (soro-negativa)	12
24	M08.4	Artrite Juvenil Pauciarticular	12
25	M08.8	Outras Artrites Juvenis	12
26	M08.9	Artrite Juvenil Não Especificada	12
6	M08.0	Artrite Reumatóide Juvenil	12
1	M05.0	Síndrome de Felty	12
2	M05.3	Artrite Reumatóide Com Comprometimento de Outros Órgãos e Sistemas	12
3	M05.8	Outras Artrites Reumatóides Soro-positivas	12
4	M06.0	Artrite Reumatóide Soro-negativa	12
5	M06.8	Outras Artrites Reumatóides Especificadas	12
55	J45.0	Asma Predominantemente Alérgica	13
56	J45.1	Asma Não-alérgica	13
57	J45.8	Asma Mista	13
213	F84.0	Autismo Infantil	14
214	F84.1	Autismo Atípico	14
215	F84.3	Outro Transtorno Desintegrativo da Infância	14
216	F84.5	Síndrome de Asperger	14
217	F84.8	Outros Transtornos Globais do Desenvolvimento	14
218	E23.0	Hipopituitarismo	15
123	E23.2	Diabetes Insípido	18
166	E10.0	Diabetes Mellitus Insulino-dependente - Com Coma	19
167	E10.1	Diabetes Mellitus Insulino-dependente - Com Cetoacidose	19
168	E10.2	Diabetes Mellitus Insulino-dependente - Com Complicações Renais	19
169	E10.3	Diabetes Mellitus Insulino-dependente - Com Complicações Oftálmicas	19
170	E10.4	Diabetes Mellitus Insulino-dependente - Com Complicações Neurológicas	19
171	E10.5	Diabetes Mellitus Insulino-dependente - Com Complicações Circulatórias Periféricas	19
172	E10.6	Diabetes Mellitus Insulino-dependente - Com Outras Complicações Especificadas	19
173	E10.7	Diabetes Mellitus Insulino-dependente - Com Complicações Múltiplas	19
174	E10.8	Diabetes Mellitus Insulino-dependente - Com Complicações Não Especificadas	19
175	E10.9	Diabetes Mellitus Insulino-dependente - Sem Complicações	19
7	E78.0	Hipercolesterolemia Pura	20
8	E78.1	Hipergliceridemia Pura	20
9	E78.2	Hiperlipidemia Mista	20
10	E78.3	Hiperquilomicronemia	20
11	E78.4	Outras Hiperlipidemias	20
12	E78.5	Hiperlipidemia Não Especificada	20
13	E78.6	Deficiências de Lipoproteínas	20
14	E78.8	Outros Distúrbios do Metabolismo de Lipoproteínas	20
229	G24.3	Torcicolo Espasmódico	21
230	G24.4	Distonia Orofacial Idiopática	21
231	G24.5	Blefaroespasmo	21
232	G24.8	Outras Distonias	21
233	G51.3	Espasmo Hemifacial Clônico	21
234	G51.8	Outros Transtornos do Nervo Facial	21
42	N18.0	Doença Renal em Estádio Final	22
62	N25.0	Osteodistrofia Renal	22
124	G30.0	Doença de Alzheimer de Início Precoce	23
125	G30.1	Doença de Alzheimer de Início Tardio	23
126	G30.8	Outras Formas de Doença de Alzheimer	23
127	F00.0	Demência na Doença de Alzheimer de Início Precoce	23
128	F00.1	Demência na Doença de Alzheimer de Início Tardio	23
129	F00.2	Demência na Doença de Alzheimer, Forma Atípica ou Mista	23
27	K50.0	Doença de Crohn do Intestino Delgado	24
28	K50.1	Doença de Crohn do Intestino Grosso	24
29	K50.8	Outra Forma de Doença de Crohn	24
163	E75.2	Outras Esfingolipidoses	25
159	D57.0	Anemia Falciforme Com Crise	26
160	D57.1	Anemia Falciforme Sem Crise	26
161	D57.2	Transtornos Falciformes Heterozigóticos Duplos	26
59	M88.0	Doença de Paget do Crânio	27
60	M88.8	Doença de Paget de Outros Ossos	27
49	G20	Doença de Parkinson	28
210	E83.0	Distúrbios do Metabolismo do Cobre	29
116	R52.1	Dor Crônica Intratável	30
117	R52.2	Outra Dor Crônica	30
138	J44.0	Doença Pulmonar Obstrutiva Crônica Com Infecção Respiratória Aguda do Trato Respiratório Inferior	31
139	J44.1	Doença Pulmonar Obstrutiva Crônica Com Exacerbação Aguda Não Especificada	31
140	J44.8	Outras Formas Especificadas de Doença Pulmonar Obstrutiva Crônica	31
150	N80.0	Endometriose do Útero	32
151	N80.1	Endometriose do Ovário	32
152	N80.2	Endometriose da Trompa de Falópio	32
153	N80.3	Endometriose do Peritônio Pélvico	32
154	N80.4	Endometriose do Septo Retovaginal e da Vagina	32
155	N80.5	Endometriose do Intestino	32
156	N80.8	Outra Endometriose	32
72	G40.0	Epilepsia e Síndromes Epilépticas Idiopáticas Definidas Por Sua Localização (focal) (parcial) Com Crises de Início Focal	33
73	G40.1	Epilepsia e Síndromes Epilépticas Sintomáticas Definidas Por Sua Localização (focal) (parcial) Com Crises Parciais Simples	33
74	G40.2	Epilepsia e Síndromes Epilépticas Sintomáticas Definidas Por Sua Localização (focal) (parcial) Com Crises Parciais Complexas	33
75	G40.3	Epilepsia e Síndromes Epilépticas Generalizadas Idiopáticas	33
76	G40.4	Outras Epilepsias e Síndromes Epilépticas Generalizadas	33
77	G40.5	Síndromes Epilépticas Especiais	33
78	G40.6	Crise de Grande Mal, Não Especificada (com ou Sem Pequeno Mal)	33
79	G40.7	Pequeno Mal Não Especificado, Sem Crises de Grande Mal	33
80	G40.8	Outras Epilepsias	33
212	G12.2	Doença do Neurônio Motor	34
54	G35	Esclerose Múltipla	35
67	M45	Espondilite Ancilosante	38
68	M46.8	Outras Espondilopatias Inflamatórias Especificadas	38
108	F20.0	Esquizofrenia Paranóide	39
109	F20.1	Esquizofrenia Hebefrênica	39
110	F20.2	Esquizofrenia Catatônica	39
111	F20.3	Esquizofrenia Indiferenciada	39
112	F20.4	Depressão Pós-esquizofrênica	39
113	F20.5	Esquizofrenia Residual	39
114	F20.6	Esquizofrenia Simples	39
115	F20.8	Outras Esquizofrenias	39
118	E70.0	Fenilcetonúria Clássica	40
119	E70.1	Outras Hiperfenilalaninemias	40
209	E84.1	Fibrose Cística Com Manifestações Intestinais	41
40	E84.0	Fibrose Cística Com Manifestações Pulmonares	42
41	E84.8	Fibrose Cística Com Outras Manifestações	42
44	D18.0	Hemangioma de Qualquer Localização	43
47	B17.1	Hepatite Aguda C	45
48	B18.2	Hepatite Viral Crônica C	45
71	E25.0	Transtornos Adrenogenitais Congênitos Associados à Deficiência Enzimática	47
50	I27.0	Hipertensão Pulmonar Primária	49
51	I27.2	Outra Hipertensão Pulmonar Secundária	49
52	I27.8	Outras Doenças Pulmonares do Coração Especificadas	49
63	E20.0	Hipoparatireoidismo Idiopático	50
64	E20.1	Pseudohipoparatireoidismo	50
65	E20.8	Outro Hipoparatireoidismo	50
66	E89.2	Hipoparatireoidismo Pós-procedimento	50
15	Q80.0	Ictiose Vulgar	51
16	Q80.1	Ictiose Ligada ao Cromossomo X	51
17	Q80.2	Ictiose Lamelar	51
18	Q80.3	Eritrodermia Ictiosiforme Bulhosa Congênita	51
19	Q80.8	Outras Ictioses Congênitas	51
134	T86.1	Falência ou Rejeição de Transplante de Rim	54
135	Z94.0	Rim Transplantado	54
180	D25.0	Leiomioma Submucoso do Útero	57
181	D25.1	Leiomioma Intramural do Útero	57
182	D25.2	Leiomioma Subseroso do Útero	57
104	L93.0	Lúpus Eritematoso Discóide	58
105	L93.1	Lúpus Eritematoso Cutâneo Subagudo	58
106	M32.1	Lúpus Eritematoso Disseminado (sistêmico) Com Comprometimento de Outros Órgãos e Sistemas	58
107	M32.8	Outras Formas de Lúpus Eritematoso Disseminado (sistêmico)	58
211	G70.0	Miastenia Gravis	59
179	E76.0	Mucopolissacaridose do Tipo I	60
162	E76.1	Mucopolissacaridose do Tipo II	61
191	M80.0	Osteoporose Pós-menopáusica Com Fratura Patológica	63
192	M80.1	Osteoporose Pós-ooforectomia Com Fratura Patológica	63
193	M80.2	Osteoporose de Desuso Com Fratura Patológica	63
194	M80.3	Osteoporose Por Má-absorção Pós-cirúrgica Com Fratura Patológica	63
195	M80.4	Osteoporose Induzida Por Drogas Com Fratura Patológica	63
196	M80.5	Osteoporose Idiopática Com Fratura Patológica	63
197	M80.8	Outras Osteoporoses Com Fratura Patológica	63
198	M81.0	Osteoporose Pós-menopáusica	63
199	M81.1	Osteoporose Pós-ooforectomia	63
200	M81.2	Osteoporose de Desuso	63
201	M81.3	Osteoporose Devida à Má-absorção Pós-cirúrgica	63
202	M81.4	Osteoporose Induzida Por Drogas	63
203	M81.5	Osteoporose Idiopática	63
204	M81.6	Osteoporose Localizada (Lequesne)	63
205	M81.8	Outras Osteoporoses	63
206	M82.0	Osteoporose na Mielomatose Múltipla	63
207	M82.1	Osteoporose em Distúrbios Endócrinos	63
208	M82.8	Osteoporose em Outras Doenças Classificadas em Outra Parte	63
219	E85.1	Amiloidose Heredofamiliar Neuropática	64
164	B16.0	Hepatite Aguda B Com Agente Delta (co-infecção), Com Coma Hepático	65
165	B16.2	Hepatite Aguda B Sem Agente Delta, Com Coma Hepático	65
45	B18.0	Hepatite Viral Crônica B Com Agente Delta	65
46	B18.1	Hepatite Crônica Viral B Sem Agente Delta	65
31	L40.0	Psoríase Vulgar	66
32	L40.1	Psoríase Pustulosa Generalizada	66
33	L40.4	Psoríase Gutata	66
34	L40.8	Outras Formas de Psoríase	66
235	E22.8	Outras Hiperfunções da Hipófise	67
130	D69.3	Púrpura Trombocitopênica Idiopática	68
61	E83.3	Distúrbios do Metabolismo do Fósforo	69
183	K51.0	Enterocolite Ulcerativa (crônica)	70
184	K51.1	Ileocolite Ulcerativa (crônica)	70
185	K51.2	Proctite Ulcerativa (crônica)	70
186	K51.3	Retossigmoidite Ulcerativa (crônica)	70
187	K51.4	Pseudopolipose do Cólon	70
188	K51.5	Proctocolite Mucosa	70
189	K51.8	Outras Colites Ulcerativas	70
81	I20.0	Angina Instável	71
82	I20.1	Angina Pectoris Com Espasmo Documentado	71
83	I21.0	Infarto Agudo Transmural da Parede Anterior do Miocárdio	71
84	I21.1	Infarto Agudo Transmural da Parede Inferior do Miocárdio	71
85	I21.2	Infarto Agudo Transmural do Miocárdio de Outras Localizações	71
86	I21.3	Infarto Agudo Transmural do Miocárdio, de Localização Não Especificada	71
87	I21.4	Infarto Agudo Subendocárdico do Miocárdio	71
88	I21.9	Infarto Agudo do Miocárdio Não Especificado	71
89	I22.0	Infarto do Miocárdio Recorrente da Parede Anterior	71
90	I22.1	Infarto do Miocárdio Recorrente da Parede Inferior	71
91	I22.8	Infarto do Miocárdio Recorrente de Outras Localizações	71
92	I22.9	Infarto do Miocárdio Recorrente de Localização Não Especificada	71
93	I23.0	Hemopericárdio Como Complicação Atual Subseqüente ao Infarto Agudo do Miocárdio	71
94	I23.1	Comunicação Interatrial Como Complicação Atual Subseqüente ao Infarto Agudo do Miocárdio	71
95	I23.2	Comunicação Interventricular Como Complicação Atual Subseqüente ao Infarto Agudo do Miocárdio	71
96	I23.3	Ruptura da Parede do Coração Sem Ocorrência de Hemopericárdio Como Complicação Atual Subseqüente ao Infarto Agudo do Miocárdio	71
97	I23.4	Ruptura de Cordoalhas Tendíneas Como Complicação Atual Subseqüente ao Infarto Agudo do Miocárdio	71
98	I23.5	Ruptura de Músculos Papilares Como Complicação Atual Subseqüente ao Infarto Agudo do Miocárdio	71
99	I23.6	Trombose de Átrio, Aurícula e Ventrículo Como Complicação Atual Subseqüente ao Infarto Agudo do Miocárdio	71
100	I23.8	Outras Complicações Atuais Subseqüentes ao Infarto Agudo do Miocárdio	71
101	I24.0	Trombose Coronária Que Não Resulta em Infarto do Miocárdio	71
102	I24.8	Outras Formas de Doença Isquêmica Aguda do Coração	71
103	I24.9	Doença Isquêmica Aguda do Coração Não Especificada	71
220	N04.0	Síndrome Nefrótica - Anormalidade Glomerular Minor	73
221	N04.1	Síndrome Nefrótica - Lesões Glomerulares Focais e Segmentares	73
222	N04.2	Síndrome Nefrótica - Glomerulonefrite Membranosa Difusa	73
223	N04.3	Síndrome Nefrótica - Glomerulonefrite Proliferativa Mesangial Difusa	73
224	N04.4	Síndrome Nefrótica - Glomerulonefrite Proliferativa Endocapilar Difusa	73
225	N04.5	Síndrome Nefrótica - Glomerulonefrite Mesangiocapilar Difusa	73
226	N04.6	Síndrome Nefrótica - Doença de Depósito Denso	73
227	N04.7	Síndrome Nefrótica - Glomerulonefrite Difusa em Crescente	73
228	N04.8	Síndrome Nefrótica - Outras	73
121	E83.1	Doença do Metabolismo do Ferro	77
122	T45.4	Intoxicação Por Ferro e Seus Compostos	77
137	Z94.4	Fígado Transplantado	78
136	T86.4	Falência ou Rejeição de Transplante de Fígado	78
35	H30.1	Inflamação Corrorretiniana Disseminada	81
36	H30.2	Ciclite Posterior	81
37	H30.8	Outras Inflamações Coriorretinianas	81
38	H20.1	Iridociclite Crônica	81
39	H15.0	Esclerite	81
\.


--
-- Data for Name: processos_medicamento; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.processos_medicamento (id, nome, dosagem, apres) FROM stdin;
1	abatacepte	250 mg	pó para solução injetável
2	abatacepte	125 mg/mL	solução injetável
3	acetato de ciproterona	50 mg	comprimido
4	acetato de desmopressina	0,1 mg/mL	solução nasal (frasco com 2,5 mL)
5	acetato de desmopressina	0,1 mg	comprimido
6	acetato de desmopressina	0,2 mg	comprimido
7	acetato de fludrocortisona	0,1 mg	comprimido
8	acetato de glatirâmer	20 mg	solução injetável
9	acetato de glatirâmer	40 mg	solução injetável
10	acetato de gosserrelina	3,6 mg	implante subcutâneo
11	acetato de gosserrelina	10,8 mg	implante subcutâneo
12	acetato de lanreotida	60 mg	solução injetável
13	acetato de lanreotida	90 mg	solução injetável
14	acetato de lanreotida	120 mg	solução injetável
15	acetato de leuprorrelina	3,75 mg	pó para suspensão injetável
16	acetato de leuprorrelina	11,25 mg	pó para suspensão injetável
17	acetato de ciproterona	50 mg	comprimido
18	acetato de fludrocortisona	0,1 mg	comprimido
19	acetato de octreotida	10 mg	pó para suspensão injetável
20	acetato de octreotida	20 mg	pó para suspensão injetável
21	acetato de octreotida	30 mg	pó para suspensão injetável
22	acetazolamida	250 mg	comprimido
23	ácido nicotínico	250 mg	comprimido de liberação prolongada
24	ácido nicotínico	500 mg	comprimido de liberação prolongada
25	ácido nicotínico	750 mg	comprimido de liberação prolongada
26	ácido ursodesoxicólico	50 mg	comprimido
27	ácido ursodesoxicólico	150 mg	comprimido
28	ácido ursodesoxicólico	300 mg	comprimido
29	acitretina	10 mg	cápsula
30	acitretina	25 mg	cápsula
31	adalimumabe	40 mg	solução injetável
32	alfacalcidol	0,25 mcg	cápsula mole
33	alfacalcidol	1 mcg	cápsula mole
34	alfadornase	1 mg/mL	solução para inalação (ampola com 2,5 mL)
35	alfaelosulfase	5 mg	solução injetável
36	alfaepoetina	1.000 UI	solução injetável
37	alfaepoetina	2.000 UI	solução injetável
38	alfaepoetina	3.000 UI	pó para solução injetável
39	alfaepoetina	3.000 UI	solução injetável
40	alfaepoetina	4.000 UI	pó para solução injetável
41	alfaepoetina	4.000 UI	solução injetável
42	alfaepoetina	10.000 UI	pó para solução injetável
43	alfaepoetina	10.000 UI	solução injetável
44	alfainterferona 2b	3.000.000 UI	pó para solução injetável
45	alfainterferona 2b	5.000.000 UI	pó para solução injetável
46	alfainterferona 2b	10.000.000 UI	pó para solução injetável
47	alfapeginterferona 2a	180 mcg	solução injetável
48	alfapeginterferona 2b	118,4 mcg (80 mcg/0,5 mL após reconstituição)	pó para solução injetável
49	alfapeginterferona 2b	148 mcg (100 mcg/0,5 mL após reconstituição)	pó para solução injetável
50	alfapeginterferona 2b	177,6 mcg (120 mcg/0,5 mL após reconstituição)	pó para solução injetável
51	alfataliglicerase	200 U	pó para solução injetável
52	alfavelaglicerase	200 U	pó para solução injetável
53	alfavelaglicerase	400 U	pó para solução injetável
54	ambrisentana	5 mg	comprimido
55	ambrisentana	10 mg	comprimido
56	atorvastatina cálcica	10 mg	comprimido
57	atorvastatina cálcica	20 mg	comprimido
58	atorvastatina cálcica	40 mg	comprimido
59	atorvastatina cálcica	80 mg	comprimido
60	azatioprina	50 mg	comprimido
61	betainterferona 1a	22 mcg (6.000.000 UI)	comprimido
62	betainterferona 1a	30 mcg (6.000.000 UI)	solução injetável
63	betainterferona 1a	44 mcg (12.000.000 UI)	solução injetável
64	betainterferona 1b	300 mcg (9.600.000 UI)	pó para solução injetável
65	bezafibrato	200 mg	comprimido
66	bezafibrato	400 mg	comprimido de liberação prolongada
67	bimatoprosta	0,3 mg/mL (0,03%)	solução oftálmica (frasco com 3 mL)
68	biotina	2,5 mg	cápsula
69	bosentana	62,5 mg	comprimido
70	bosentana	125 mg	comprimido
71	brinzolamida	10 mg/mL	suspensão oftálmica (frasco com 5 mL)
72	brometo de piridostigmina	60 mg	comprimido
73	bromidrato de fenoterol	100 mcg/dose	solução aerossol (frasco com 200 doses)
74	bromidrato de galantamina	8 mg	cápsula de liberação prolongada
75	bromidrato de galantamina	16 mg	cápsula de liberação prolongada
76	bromidrato de galantamina	24 mg	cápsula de liberação prolongada
77	budesonida	200 mcg	aerossol bucal
78	budesonida	200 mcg	cápsula para inalação
79	budesonida	200 mcg	pó para inalação
80	budesonida	400 mcg	cápsula para inalação
81	cabergolina	0,5 mg	comprimido
82	calcipotriol	50 mcg/g (0,005%)	pomada (bisnaga com 30 g)
83	calcitonina	50 UI	solução injetável
84	calcitonina	100 UI	solução injetável
85	calcitonina	200 UI/dose	solução spray nasal (frasco com 2 mL)
86	calcitriol	1 mcg/mL	solução injetável (ampola com 1 mL)
87	calcitriol	0,25 mcg	cápsula mole
88	certolizumabe pegol	200 mg	solução injetável
89	ciclofosfamida	50 mg	comprimido
90	ciclosporina	10 mg	cápsula mole
91	ciclosporina	25 mg	cápsula mole
92	ciclosporina	50 mg	cápsula mole
93	ciclosporina	100 mg	cápsula mole
94	ciclosporina	50 mg	solução injetável
95	ciclosporina	100 mg/mL	solução oral (frasco com 50 mL)
96	ciprofibrato	100 mg	comprimido
97	citrato de sildenafila	20 mg	comprimido
98	citrato de sildenafila	25 mg	comprimido
99	citrato de sildenafila	50 mg	comprimido
100	clobazam	10 mg	comprimido
101	clobazam	20 mg	comprimido
102	clopidogrel	75 mg	comprimido
103	cloridrato de amantadina	100 mg	comprimido
104	cloridrato de cinacalcete	30 mg	comprimido
105	cloridrato de cinacalcete	60 mg	comprimido
106	cloridrato de donepezila	5 mg	comprimido
107	cloridrato de donepezila	10 mg	comprimido
108	cloridrato de dorzolamida	20 mg/mL	solução oftálmica (frasco com 5 mL)
109	cloridrato de metadona	5 mg	comprimido
110	cloridrato de metadona	10 mg	comprimido
111	cloridrato de metadona	10 mg/mL	solução injetável (ampola com 1 mL)
112	cloridrato de pilocarpina	20 mg/mL (2%)	solução oftálmica (frasco com 10 mL)
113	cloridrato de raloxifeno	60 mg	comprimido
114	cloridrato de selegilina	5 mg	comprimido
115	cloridrato de selegilina	10 mg	comprimido
116	cloridrato de sevelâmer	800 mg	comprimido
117	cloridrato de triexifenidil	5 mg	comprimido
118	cloridrato de ziprasidona	40 mg	cápsula
119	cloridrato de ziprasidona	80 mg	cápsula
120	clozapina	25 mg	comprimido
121	clozapina	100 mg	comprimido
122	complemento alimentar para paciente fenilcetonúrico maior de 1 ano (fórmula de aminoácidos isenta de fenilalanina)	N/A	N/A
123	daclatasvir	30 mg	comprimido
124	daclatasvir	60 mg	comprimido
125	danazol	100 mg	cápsula
126	danazol	200 mg	cápsula
127	deferasirox	125 mg	comprimido para suspensão
128	deferasirox	250 mg	comprimido para suspensão
129	deferasirox	500 mg	comprimido para suspensão
130	deferiprona	500 mg	comprimido
131	dextrotartarato de brimonidina	2 mg/mL	solução oftálmica (frasco com 5 mL)
132	dicloridrato de pramipexol	0,125 mg	comprimido
133	dicloridrato de pramipexol	0,25 mg	comprimido
134	dicloridrato de pramipexol	1 mg	comprimido
135	difosfato de cloroquina	150 mg	comprimido
136	dicloridrato de sapropterina	100 mg	comprimido
137	eculizumabe	10 mg/ml	solução para diluição para infusão
138	eltrombopague olamina	25 mg	comprimido
139	eltrombopague olamina	50 mg	comprimido
140	enoxaparina sódica	40 mg/0,4 ml	solução injetável
141	entacapona	200 mg	comprimido
142	entecavir	0,5 mg	comprimido
143	entecavir	1 mg	comprimido
144	etanercepte	25 mg	solução injetável
145	etanercepte	50 mg	solução injetável
146	etofibrato	500 mg	cápsula
147	etossuximida	50 mg/mL	xarope (frasco com 120 mL)
148	everolimo	0,5 mg	comprimido
149	everolimo	0,75 mg	comprimido
150	everolimo	1 mg	comprimido
151	fenofibrato	200 mg	cápsula
152	fenofibrato	250 mg	cápsula de liberação retardada
153	filgrastim	300 mcg	solução injetável
154	fingolimode	0,5 mg	cápsula
155	fluvastatina	20 mg	cápsula
156	fluvastatina	40 mg	cápsula
157	fosfato de codeína	3 mg/mL	solução oral (frasco com 120 mL)
158	fosfato de codeína	30 mg	comprimido
159	fosfato de codeína	60 mg	comprimido
160	fosfato de codeína	30 mg/mL	solução injetável (ampola com 2 mL)
161	fumarato de dimetila	120 mg	cápsula
162	fumarato de dimetila	240 mg	cápsula
163	fumarato de formoterol	12 mcg	cápsula para inalação
164	fumarato de formoterol	12 mcg	pó para inalação
165	fumarato de formoterol + budesonida	6 mcg + 200 mcg	cápsula para inalação
166	fumarato de formoterol + budesonida	6 mcg + 200 mcg	pó para inalação
167	fumarato de formoterol + budesonida	12 mcg + 400 mcg	cápsula para inalação
168	fumarato de formoterol + budesonida	12 mcg + 400 mcg	pó para inalação
169	fumarato de tenofovir desoproxila	300 mg	comprimido
170	gabapentina	300 mg	cápsula
171	gabapentina	400 mg	cápsula
172	galsulfase	5 mg	solução injetável
173	genfibrozila	600 mg	comprimido
174	genfibrozila	900 mg	comprimido
175	golimumabe	50 mg	solução injetável
176	hemifumarato de quetiapina	25 mg	comprimido
177	hemifumarato de quetiapina	100 mg	comprimido
178	hemifumarato de quetiapina	200 mg	comprimido
179	hemifumarato de quetiapina	300 mg	comprimido
180	hidróxido de alumínio	230 mg	comprimido
181	hidróxido de alumínio	300 mg	comprimido
182	hidróxido de alumínio	61,5 mg/mL	suspensão oral (frasco com 100 mL, 150 mL ou 240 mL)
183	hidroxiureia	500 mg	cápsula
184	idursulfase	2 mg/mL	solução injetável
185	iloprosta	10 mcg/mL	solução para nebulização
186	imiglucerase	200 U	pó para solução injetável
187	imiglucerase	400 U	pó para solução injetável
188	imunoglobulina humana	0,5 g	pó para solução injetável
189	imunoglobulina humana	0,5 g	solução injetável
190	imunoglobulina humana	1 g	pó para solução injetável
191	imunoglobulina humana	1 g	solução injetável
192	imunoglobulina humana	2,5 g	pó para solução injetável
193	imunoglobulina humana	2,5 g	solução injetável
194	imunoglobulina humana	3 g	pó para solução injetável
195	imunoglobulina humana	3 g	solução injetável
196	imunoglobulina humana	5 g	pó para solução injetável
197	imunoglobulina humana	5 g	solução injetável
198	imunoglobulina humana	6 g	pó para solução injetável
199	imunoglobulina humana anti-hepatite B	100 UI	solução injetável
200	imunoglobulina humana anti-hepatite B	500 UI	solução injetável
201	imunoglobulina humana anti-hepatite B	600 UI	solução injetável
202	infliximabe	100 mg	pó para solução injetável
203	insulina análoga de ação prolongada	100 UI/ml	(frasco com 10 mL) solução injetável com sistema de aplicação
204	insulina análoga de ação rápida	100 UI/ml	solução injetável com sistema de aplicação
205	isotretinoína	10 mg	cápsula mole
206	isotretinoína	20 mg	cápsula mole
207	lamivudina	10 mg/mL	solução oral (frasco de 240 mL)
208	lamivudina	150 mg	comprimido
209	lamotrigina	25 mg	comprimido
210	lamotrigina	50 mg	comprimido
211	lamotrigina	100 mg	comprimido
212	laronidase	0,58 mg/mL	solução injetável
213	latanoprosta	0,05 mg/mL	solução oftálmica (frasco com 2,5 mL)
214	leflunomida	20 mg	comprimido
215	levetiracetam	250 mg	comprimido
216	levetiracetam	750 mg	comprimido
217	levetiracetam	100 mg/ml	solução oral
218	lovastatina	10 mg	comprimido
219	lovastatina	20 mg	comprimido
220	lovastatina	40 mg	comprimido
221	maleato de timolol	5 mg/mL (0,5%)	solução oftálmica (frasco com 5 mL)
222	memantina	10 mg	comprimido
223	mesalazina	400 mg	comprimido
224	mesalazina	500 mg	comprimido de liberação prolongada
225	mesalazina	800 mg	comprimido
226	mesalazina	250 mg	supositório retal
227	mesalazina	500 mg	supositório retal
228	mesalazina	1.000 mg	supositório retal
229	mesalazina	10 mg/mL	enema retal (frasco com 100 mL) 
230	mesalazina	30 mg/mL	enema retal (frasco com 100 mL)
231	mesilato de bromocriptina	2,5 mg	comprimido
232	mesilato de desferroxamina	500 mg	pó para solução injetável
233	mesilato de rasagilina	1 mg	comprimido
234	metilprednisolona	500 mg	pó para solução injetável
235	metotrexato	25 mg/mL	solução injetável (frasco com 2 mL)
236	metotrexato	2,5 mg	comprimido
237	micofenolato de mofetila	500 mg	comprimido
238	micofenolato de sódio	180 mg	comprimido
239	micofenolato de sódio	360 mg	comprimido
240	miglustate	100 mg	cápsula
241	naproxeno	250 mg	comprimido
242	naproxeno	500 mg	comprimido
243	natalizumabe	20 mg/mL	solução injetável
244	nusinersena	2,4 mg/ml	solução injetável
245	octreotida	0,1 mg/mL	solução injetável
246	olanzapina	5 mg	comprimido
247	olanzapina	10 mg	comprimido
248	olanzapina	30 mg	solução injetável
249	pamidronato dissódico	60 mg	solução injetável
250	pancreatina	10.000 UI	cápsula
251	pancreatina	25.000 UI	cápsula
252	paricalcitol	5 mcg/mL	solução injetável (ampola com 1 mL)
253	penicilamina	250 mg	cápsula
254	pravastatina sódica	10 mg	comprimido
255	pravastatina sódica	20 mg	comprimido
256	pravastatina sódica	40 mg	comprimido
257	primidona	100 mg	comprimido
258	primidona	250 mg	comprimido
259	propionato de clobetasol	0,5 mg/g	creme (bisnaga com 30 g)
260	propionato de clobetasol	0,5 mg/g	solução capilar (frasco com 50 g)
261	ribavirina	250 mg	cápsula
262	riluzol	50 mg	comprimido
263	risedronato sódico	5 mg	comprimido
264	risedronato sódico	35 mg	comprimido
265	risperidona	1 mg/mL	solução oral (frasco com 30 mL)
266	risperidona	1 mg	comprimido
267	risperidona	2 mg	comprimido
268	risperidona	3 mg	comprimido
269	rituximabe	10 mg/mL	solução injetável (frasco com 50 mL)
270	rivastigmina	1,5 mg	cápsula
271	rivastigmina	3 mg	cápsula
272	rivastigmina	4,5 mg	cápsula
273	rivastigmina	6 mg	cápsula
274	rivastigmina	2 mg/mL	solução oral (frasco com 120 mL)
275	rivastigmina	9 mg	adesivo transdérmico
276	rivastigmina	18 mg	adesivo transdérmico
277	sacarato de hidróxido férrico	20 mg/mL	solução injetável (frasco com 5 mL)
278	secuquinumabe	150 mg/mL	pó para solução injetável
279	sirolimo	1 mg	comprimido
280	sirolimo	2 mg	comprimido
281	sofosbuvir	400 mg	comprimido
282	somatropina	4 UI	pó para solução injetável (frasco-ampola)
283	somatropina	12 UI	pó para solução injetável (frasco-ampola)
284	somatropina	15 UI	pó para solução injetável (frasco-ampola)
285	somatropina	16 UI	pó para solução injetável (frasco-ampola)
286	somatropina	18 UI	pó para solução injetável (frasco-ampola)
287	somatropina	24 UI	pó para solução injetável (frasco-ampola)
288	somatropina	30 UI	pó para solução injetável (frasco-ampola)
289	sulfassalazina	500 mg	comprimido
290	sulfato de hidroxicloroquina	400 mg	comprimido
291	sulfato de morfina	10 mg/mL	solução injetável (ampola com 1 mL)
292	sulfato de morfina	10 mg/mL	solução oral (frasco com 60 mL)
293	sulfato de morfina	10 mg	comprimido
294	sulfato de morfina	30 mg	comprimido
295	sulfato de morfina	30 mg	cápsula de liberação prolongada
296	sulfato de morfina	60 mg	cápsula de liberação prolongada
297	sulfato de morfina	100 mg	cápsula de liberação prolongada
298	tacrolimo	1 mg	cápsula
299	tacrolimo	5 mg	cápsula
300	teriflunomida	14 mg	comprimido
301	tafamidis	20 mg	cápsula
302	tobramicina	300 mg	solução inalatória
303	tocilizumabe	20 mg/mL	solução injetável (frasco com 4 mL)
304	tofacitinibe	5 mg	comprimido
305	tolcapona	100 mg	comprimido
306	topiramato	25 mg	comprimido
307	topiramato	50 mg	comprimido
308	topiramato	100 mg	comprimido
309	toxina botulínica A	100 U	pó para solução injetável
310	toxina botulínica A	500 U	pó para solução injetável
311	travoprosta	0,04 mg/mL	solução oftálmica (frasco com 2,5 mL)
312	trientina	250 mg	cápsula
313	triptorrelina	3,75 mg	pó para suspensão injetável
314	triptorrelina	11,25 mg	pó para suspensão injetável
315	ustequinumabe	45 mg	solução injetável
316	vigabatrina	500 mg	comprimido
317	xinafoato de salmeterol	50 mcg	aerossol bucal
318	xinafoato de salmeterol	50 mcg	pó para inalação
\.


--
-- Data for Name: processos_processo; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.processos_processo (id, anamnese, prescricao, tratou, tratamentos_previos, data1, preenchido_por, dados_condicionais, clinica_id, doenca_id, emissor_id, medico_id, paciente_id, usuario_id) FROM stdin;
1	Anamnese está aqui. Qualquer coisa.	{"1": {"id_med1": "100", "med1_via": "Oral", "qtd_med1_mes1": "30", "qtd_med1_mes2": "30", "qtd_med1_mes3": "30", "qtd_med1_mes4": "30", "qtd_med1_mes5": "30", "qtd_med1_mes6": "30", "med1_posologia_mes1": "Tomar 1cp à noite.", "med1_posologia_mes2": "Tomar 1cp à noite.", "med1_posologia_mes3": "Tomar 1cp à noite.", "med1_posologia_mes4": "Tomar 1cp à noite.", "med1_posologia_mes5": "Tomar 1cp à noite.", "med1_posologia_mes6": "Tomar 1cp à noite."}}	f		\N	paciente	{}	1	72	1	1	1	1
2	Anamnese está aqui. Qualquer coisa.	{"1": {"id_med1": "100", "med1_via": "Oral", "qtd_med1_mes1": "30", "qtd_med1_mes2": "30", "qtd_med1_mes3": "30", "qtd_med1_mes4": "30", "qtd_med1_mes5": "30", "qtd_med1_mes6": "30", "med1_posologia_mes1": "Tomar 1cp à noite.", "med1_posologia_mes2": "Tomar 1cp à noite.", "med1_posologia_mes3": "Tomar 1cp à noite.", "med1_posologia_mes4": "Tomar 1cp à noite.", "med1_posologia_mes5": "Tomar 1cp à noite.", "med1_posologia_mes6": "Tomar 1cp à noite."}}	f		\N	paciente	{}	1	72	1	1	1	1
3	Anamnese está aqui. Qualquer coisa.	{"1": {"id_med1": "100", "med1_via": "Oral", "qtd_med1_mes1": "30", "qtd_med1_mes2": "30", "qtd_med1_mes3": "30", "qtd_med1_mes4": "30", "qtd_med1_mes5": "30", "qtd_med1_mes6": "30", "med1_posologia_mes1": "Tomar 1cp à noite.", "med1_posologia_mes2": "Tomar 1cp à noite.", "med1_posologia_mes3": "Tomar 1cp à noite.", "med1_posologia_mes4": "Tomar 1cp à noite.", "med1_posologia_mes5": "Tomar 1cp à noite.", "med1_posologia_mes6": "Tomar 1cp à noite."}}	f		\N	paciente	{}	1	72	1	1	1	1
\.


--
-- Data for Name: processos_processo_medicamentos; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.processos_processo_medicamentos (id, processo_id, medicamento_id) FROM stdin;
1	1	100
2	2	100
3	3	100
\.


--
-- Data for Name: processos_protocolo; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.processos_protocolo (id, nome, arquivo, dados_condicionais) FROM stdin;
1	acne_grave	1_acnegrave_v8_2.pdf	\N
2	acromegalia	2_acromegalia_v5.pdf	\N
3	anemia_aplastica__mielodisplasia_e_neutropenias_constitucionais	4_anaplasticamielodneutconst_v6.pdf	\N
4	anemia_aplastica_adquirida	3_anemia_aplastica_adquirida_v3.pdf	\N
5	anemia_hemolitica_auto_imune	7_anemiahemoliticaautoimune_v6.pdf	\N
6	anemia_em_pacientes_com_insuficiencia_renal_crônica___alfapoetina	5_anemiapacientesinsrencr-alfaepoetina_v4.pdf	\N
7	anemia_em_pacientes_com_insuficiencia_renal_crônica___reposicao_de_ferro	6_anemiapacientesinsrencr_-_repferro_v5.pdf	\N
8	angioedema	8_angioedema_v8.pdf	\N
9	aplasia_pura_adquirida_da_serie_vermelha	9_aplasiapura_v5.pdf	\N
10	artrite_psoriaca	10_artritepsoriacav15.pdf	\N
11	artrite_reativa___doenca_de_reiter	11_artritereativa_v5.pdf	\N
12	artrite_reumatoide	12_artritereumatoide_v21.pdf	\N
13	asma	13_asmav8.pdf	\N
14	comportamento_agressivo_no_transtorno_do_espectro_do_autismo	76_comport_agressivo_transt_espectro_autismo_v3.pdf	\N
15	deficiencia_de_hormônio_do_crescimento___hipopituitarismo	14_defhormcresc__hipopituitarismo_v9.pdf	\N
16	deficiencia_de_biotinidase	274_deficienciabiotinidase_v1.pdf	\N
17	dermatomiosite_e_polimiosite	15_dermatomiositepolimiosite_v3.pdf	\N
18	diabetes_insipido	16_diabetesinsipido_v4.pdf	\N
19	diabetes_mellitus_tipo_i	200_diabetesmellitus_tipoi__v2.pdf	\N
20	dislipidemia	17_dislipidemiav12.pdf	\N
21	distonia_e_espasmo_hemifacial	18_distoniasespasmohemifacial_v3.pdf	\N
22	disturbio_mineral_osseo_na_doenca_renal	79_disturbio_mineral_osseo_doenca_renal_v2.pdf	\N
23	doenca_de_alzheimer	19_doencadealzheimerv10.pdf	\N
24	doenca_de_chron	20_doencadecrohnv9.pdf	\N
25	doenca_de_gaucher	21_doencadegaucherv11.pdf	\N
26	doenca_falciforme	25_doencafalciformev8.pdf	\N
27	doenca_de_paget	22_doencapaget_v3.pdf	\N
28	doenca_de_parkinson	23_doencaparkinson_v7.pdf	\N
29	doenca_de_wilson	24_doencawilson_v3.pdf	\N
30	dor_crônica	26_dorcronica_v5.pdf	\N
31	dpoc	27_dpoc_v3.pdf	\N
32	endometriose	28_endometriose_v5.pdf	\N
33	epilepsia	29_epilepsia_v5.pdf	\N
34	esclerose_lateral_amiotrofica	30_escleroselateralamiotrofica_v6.pdf	\N
35	esclerose_multipla	31_esclerosemultipla_v17.pdf	\N
36	esclerose_sistemica	32_esclerosesistemica_v4.pdf	\N
37	espasticidade	33_espasticidade_v2.pdf	\N
38	espondilite_ancilosante	34_espondiliteancilosante_v16.pdf	\N
39	esquizofrenia	35_esquizofreniav7.pdf	\N
40	fenilcetonuria	36_fenilcetonuria_v4.pdf	\N
41	fibrose_cistica___insuficiencia_pancreatica	37_fibrose_cistica-insuficienciapancreatica_v4.pdf	\N
42	fibrose_cistica___manifestacões_pulmonares	38_fibrose_cistica-manifestacoespulmonares_v2.pdf	\N
43	hemangioma_infantil	40_hemangiomainfantil_v3_2.pdf	\N
44	hepatite_viral_b_e_coinfeccões	42_hepatite_viral_b_coinfeccoes_v7_2.pdf	\N
45	hepatite_viral_c_e_coinfeccões	43_hepatite_viral_c_coinfeccoes_v21.pdf	\N
46	hepatite_autoimune	41_hepatiteautoimune_v4.pdf	\N
47	hiperplasia_adrenal_congenita	45_hiperpadrecong_v3_3.pdf	\N
48	hiperprolactinemia	46_hiperprolactinemia_v5.pdf	\N
49	hipertensao_arterial_pulmonar	47_hipertensaoarterialpulmonar_v3.pdf	\N
50	hipoparatiroidismo	48_hipoparatireoidismo_v3.pdf	\N
51	ictioses_hereditarias	49_ictioseshereditarias_v6.pdf	\N
52	imunodeficiencia_primaria_com_predominância_de_defeitos_de_anticorpos	50_imunodprimpreddefant_v1_2.pdf	\N
53	imunosupressao_no_transplante_hepatico_em_pediatria	51_imuntransphepped_v6_2.pdf	\N
54	imunossupressao_no_transplante_renal	52_imuntransprrenal_v3.pdf	\N
55	insuficiencia_adrenal_primaria___doenca_de_addison	53_insadrenprimaria_v3.pdf	\N
56	insuficiencia_pancreatica_exocrina	54_inspacexoc_v4.pdf	\N
57	leiomioma_de_útero	55_leiomiomautero_v4.pdf	\N
58	lupus_eritematoso_sistemico	56_lupuseritsist_v4.pdf	\N
59	miastenia_gravis	57_miasteniagravis_v5_2.pdf	\N
60	mucopolissacaridose_tipo_i	80_mucopolissacaridose_tipoi_v1.pdf	\N
61	mucopolissacaridose_tipo_ii	272_mucopolissacaridose_tipoii_v2.pdf	\N
62	colangite_biliar_primaria	277-colangitebiliarprimaria-v1.pdf	\N
63	osteoporose	59_osteoporose_v4.pdf	\N
64	polineuropatia_amiloidotica_familiar	273_polineuropatiaamfam_v3.pdf	\N
65	profilaxia_da_reinfecao_do_virus_da_hepatite_b_pos_transplante_hepatico	60_profilaxiavirushepbptransphep_v1_2.pdf	\N
66	psoriase	61_psoriase_v9.pdf	\N
67	puberdade_precoce	62_puberdade_precoce_central_v7.pdf	\N
68	purpura_trombocitopenica_idiopatica	63_purpuratrombidiop_v6.pdf	\N
69	raquitismo_e_osteomalacia	64_raquitismoosteomalacia_v4_2.pdf	\N
70	retocolite_ulcerativa	65_retocoliteulcerativa_v2.pdf	\N
71	sindrome_coronariana_aguda	66_sindcoronaguda_v1_2.pdf	\N
72	sindrome_nefrotica_primaria_em_adultos	70_sindnefprimaadultos_v2.pdf	\N
73	sindrome_nefrotica_primaria_em_criancas_e_adolescentes	71_sindnefprimacrianadol_v3.pdf	\N
74	sindrome_de_ovarios_policisticos_e_hirsutismo/acne	68_sindovpolichirs_v3.pdf	\N
75	sindrome_de_guillain_barre	67_sindromeguillain-barre_v4_2.pdf	\N
76	sindrome_de_turner	69_sindrometurner_v5.pdf	\N
77	sobrecarga_de_ferro	72_sobrecarga_ferro_v3_2.pdf	\N
78	imunossupressao_no_transplante_hepatico_em_adultos	78_transplante_hep_adultos_2.pdf	\N
79	transtorno_afetivo_bipolar	75_transtornoafetivobipolar_v2.pdf	\N
80	transtorno_esquizoafetivo	73_transtornoesquizoafetivov6.pdf	\N
81	uveites_nao_infecciosas	74_uveitesnaoinfecciosas_v6.pdf	\N
\.


--
-- Data for Name: processos_protocolo_medicamentos; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.processos_protocolo_medicamentos (id, protocolo_id, medicamento_id) FROM stdin;
1	12	1
7	12	2
13	20	23
21	20	24
29	20	25
37	51	29
42	66	29
46	51	30
51	66	30
55	12	31
68	10	31
71	24	31
74	38	31
76	66	31
80	81	31
85	42	34
87	22	36
88	7	36
89	3	36
90	45	36
92	22	37
93	7	37
94	3	37
95	45	37
97	22	38
98	7	38
99	3	38
100	45	38
102	22	39
103	7	39
104	3	39
105	45	39
107	22	40
108	7	40
109	3	40
110	45	40
112	22	41
113	7	41
114	3	41
115	45	41
117	22	42
118	7	42
119	3	42
120	45	42
122	22	43
123	7	43
124	3	43
125	45	43
127	43	44
128	43	45
129	43	46
130	65	47
132	45	47
134	65	48
136	45	48
138	65	49
140	45	49
142	65	50
144	45	50
146	28	103
147	49	54
150	49	55
153	20	56
161	20	57
169	20	58
177	20	59
185	4	60
186	12	60
187	24	60
190	35	60
191	58	60
195	59	60
196	68	60
197	70	60
204	54	60
206	78	60
210	3	60
211	81	60
216	35	61
217	35	62
218	35	63
219	35	64
220	20	65
228	20	66
236	49	69
239	49	70
242	28	231
243	13	77
246	31	77
249	13	78
252	31	78
255	13	79
258	31	79
261	13	80
264	31	80
267	13	165
270	31	165
273	13	166
276	31	166
279	13	167
282	31	167
285	13	168
288	31	168
291	2	81
292	66	82
296	27	83
298	63	83
316	27	84
318	63	84
336	27	85
338	63	85
356	69	86
357	22	86
359	50	86
363	63	86
381	7	86
383	69	87
384	22	87
386	50	87
390	63	87
408	7	87
410	12	88
415	24	88
418	38	88
420	5	89
422	58	89
426	68	89
427	73	89
445	5	90
447	4	90
452	10	90
455	12	90
456	58	90
460	59	90
461	66	90
465	70	90
472	73	90
490	78	90
494	3	90
495	54	90
497	81	90
502	5	91
504	4	91
509	10	91
512	12	91
513	58	91
517	59	91
518	66	91
522	70	91
529	73	91
547	78	91
551	3	91
552	54	91
554	81	91
559	5	92
561	4	92
566	10	92
569	12	92
570	58	92
574	59	92
575	66	92
579	70	92
586	73	92
604	78	92
608	3	92
609	54	92
611	81	92
616	5	93
618	4	93
623	10	93
626	12	93
627	58	93
631	59	93
632	66	93
636	70	93
643	73	93
661	78	93
665	3	93
666	54	93
668	81	93
673	5	94
675	4	94
680	10	94
683	12	94
684	58	94
688	59	94
689	66	94
693	70	94
700	73	94
718	78	94
722	3	94
723	54	94
725	81	94
730	5	95
732	4	95
737	10	95
740	12	95
741	58	95
745	59	95
746	66	95
750	70	95
757	73	95
775	78	95
779	3	95
780	54	95
782	81	95
787	69	104
788	22	104
790	69	105
791	22	105
793	20	96
801	47	3
802	67	3
803	47	17
804	67	17
805	33	100
814	33	101
823	66	259
827	66	260
831	71	102
854	12	135
860	58	135
864	12	290
870	58	290
874	28	120
875	39	120
883	28	121
884	39	121
892	30	157
894	30	158
896	30	159
898	30	160
900	40	122
902	8	125
903	32	125
910	58	125
914	68	125
915	8	126
916	32	126
923	58	126
927	68	126
928	77	127
930	77	128
932	77	129
934	77	130
936	69	232
937	22	232
939	77	232
941	18	4
942	18	5
943	18	6
944	23	106
950	23	107
956	68	138
957	68	139
958	28	141
959	65	142
961	65	143
963	10	144
966	12	144
972	38	144
974	66	144
978	10	145
981	12	145
987	38	145
989	66	145
993	33	147
1002	54	148
1004	78	148
1008	54	149
1010	78	149
1014	54	150
1016	78	150
1020	20	151
1028	20	152
1036	13	73
1039	31	73
1042	3	153
1045	4	153
1051	45	153
1053	35	154
1054	47	7
1055	47	18
1056	13	163
1059	31	163
1062	13	164
1065	31	164
1116	35	161
1117	35	162
1118	33	170
1127	30	170
1129	33	171
1138	30	171
1140	23	74
1146	23	75
1152	23	76
1158	20	173
1166	20	174
1174	10	175
1177	12	175
1182	38	175
1184	32	10
1191	57	10
1194	67	10
1195	32	11
1202	57	11
1205	67	11
1216	49	185
1219	25	186
1220	25	187
1221	5	188
1223	59	188
1224	68	188
1225	54	188
1227	5	189
1229	59	189
1230	68	189
1231	54	189
1233	5	190
1235	59	190
1236	68	190
1237	54	190
1239	5	191
1241	59	191
1242	68	191
1243	54	191
1245	5	192
1247	59	192
1248	68	192
1249	54	192
1251	5	193
1253	59	193
1254	68	193
1255	54	193
1257	5	194
1259	59	194
1260	68	194
1261	54	194
1263	5	195
1265	59	195
1266	68	195
1267	54	195
1269	5	196
1271	59	196
1272	68	196
1273	54	196
1275	5	197
1277	59	197
1278	68	197
1279	54	197
1281	5	198
1283	59	198
1284	68	198
1285	54	198
1287	5	199
1289	59	199
1290	68	199
1291	54	199
1293	5	200
1295	59	200
1296	68	200
1297	54	200
1299	5	201
1301	59	201
1302	68	201
1303	54	201
1305	12	202
1311	10	202
1314	24	202
1317	38	202
1319	19	204
1329	1	205
1332	1	206
1335	65	207
1341	65	208
1347	33	209
1356	33	210
1365	33	211
1374	2	12
1375	2	13
1376	2	14
1377	60	212
1378	10	214
1381	12	214
1387	57	15
1390	67	15
1391	32	15
1398	57	16
1401	67	16
1402	32	16
1409	33	215
1418	33	216
1427	33	217
1436	23	222
1442	24	223
1445	70	223
1452	24	224
1455	70	224
1462	24	225
1465	70	225
1472	24	226
1475	70	226
1482	24	227
1485	70	227
1492	24	228
1495	70	228
1502	24	229
1505	70	229
1512	24	230
1515	70	230
1522	30	109
1524	30	110
1526	30	111
1528	24	234
1531	78	234
1534	54	234
1536	3	234
1537	81	234
1542	10	235
1545	12	235
1551	24	235
1554	38	235
1556	58	235
1560	66	235
1564	10	236
1567	12	236
1573	24	236
1576	38	236
1578	58	236
1582	66	236
1586	78	237
1590	54	237
1592	78	238
1596	54	238
1598	78	239
1602	54	239
1604	25	240
1605	30	291
1607	30	292
1609	30	293
1611	30	294
1613	30	295
1615	30	296
1617	30	297
1619	10	241
1622	12	241
1628	38	241
1630	10	242
1633	12	242
1639	38	242
1641	35	243
1642	2	19
1643	2	20
1644	2	21
1645	2	245
1646	39	246
1654	39	247
1662	39	248
1670	63	249
1688	41	250
1689	42	250
1690	41	251
1691	42	251
1692	69	252
1693	22	252
1695	29	253
1696	59	72
1697	28	132
1698	28	133
1699	28	134
1700	20	254
1708	20	255
1716	20	256
1724	33	257
1733	33	258
1742	39	176
1750	39	177
1758	39	178
1766	39	179
1774	63	113
1792	28	233
1793	45	261
1795	34	262
1796	63	263
1814	63	264
1832	14	265
1837	39	265
1845	14	266
1850	39	266
1858	14	267
1863	39	267
1871	14	268
1876	39	268
1884	12	269
1889	23	270
1895	23	271
1901	23	272
1907	23	273
1913	23	274
1919	23	275
1925	23	276
1931	22	277
1932	7	277
1933	10	278
1936	38	278
1938	66	278
1942	28	114
1943	28	115
1944	49	97
1947	49	98
1950	49	99
1953	54	279
1955	78	279
1957	54	280
1959	78	280
1961	45	281
1963	15	282
1964	15	283
1965	15	284
1966	15	285
1967	15	286
1968	15	287
1969	15	288
1970	10	289
1973	70	289
1980	12	289
1986	24	289
1989	38	289
1991	64	301
1992	73	298
2001	78	298
2005	54	298
2007	73	299
2016	78	299
2020	54	299
2022	65	169
2024	35	300
2025	12	303
2031	12	304
2036	33	306
2045	33	307
2054	33	308
2063	28	117
2064	57	313
2067	67	313
2068	32	313
2075	57	314
2078	67	314
2079	32	314
2086	33	316
2095	39	118
2102	39	119
\.


--
-- Data for Name: usuarios_usuario; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.usuarios_usuario (id, password, last_login, is_superuser, email, is_staff, is_active, date_joined, is_medico, is_clinica) FROM stdin;
1	pbkdf2_sha256$180000$2eq4imtMlyAx$lyVGU72YKcOX28tRBo+GIij0APAZJ73mJNWist7420E=	2025-03-26 12:30:12.108284+00	f	lcsavb@gmail.com	f	t	2025-03-26 12:30:03.9515+00	t	f
\.


--
-- Data for Name: usuarios_usuario_groups; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.usuarios_usuario_groups (id, usuario_id, group_id) FROM stdin;
\.


--
-- Data for Name: usuarios_usuario_user_permissions; Type: TABLE DATA; Schema: public; Owner: lucas
--

COPY public.usuarios_usuario_user_permissions (id, usuario_id, permission_id) FROM stdin;
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 64, true);


--
-- Name: clinicas_clinica_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.clinicas_clinica_id_seq', 1, true);


--
-- Name: clinicas_clinicausuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.clinicas_clinicausuario_id_seq', 1, true);


--
-- Name: clinicas_emissor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.clinicas_emissor_id_seq', 1, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 16, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 28, true);


--
-- Name: medicos_medico_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.medicos_medico_id_seq', 1, true);


--
-- Name: medicos_medicousuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.medicos_medicousuario_id_seq', 1, true);


--
-- Name: pacientes_paciente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.pacientes_paciente_id_seq', 1, true);


--
-- Name: pacientes_paciente_usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.pacientes_paciente_usuarios_id_seq', 3, true);


--
-- Name: processos_doenca_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.processos_doenca_id_seq', 235, true);


--
-- Name: processos_medicamento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.processos_medicamento_id_seq', 318, true);


--
-- Name: processos_processo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.processos_processo_id_seq', 3, true);


--
-- Name: processos_processo_medicamentos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.processos_processo_medicamentos_id_seq', 3, true);


--
-- Name: processos_protocolo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.processos_protocolo_id_seq', 81, true);


--
-- Name: processos_protocolo_medicamentos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.processos_protocolo_medicamentos_id_seq', 2108, true);


--
-- Name: usuarios_usuario_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.usuarios_usuario_groups_id_seq', 1, false);


--
-- Name: usuarios_usuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.usuarios_usuario_id_seq', 1, true);


--
-- Name: usuarios_usuario_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: lucas
--

SELECT pg_catalog.setval('public.usuarios_usuario_user_permissions_id_seq', 1, false);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: clinicas_clinica clinicas_clinica_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.clinicas_clinica
    ADD CONSTRAINT clinicas_clinica_pkey PRIMARY KEY (id);


--
-- Name: clinicas_clinicausuario clinicas_clinicausuario_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.clinicas_clinicausuario
    ADD CONSTRAINT clinicas_clinicausuario_pkey PRIMARY KEY (id);


--
-- Name: clinicas_emissor clinicas_emissor_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.clinicas_emissor
    ADD CONSTRAINT clinicas_emissor_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: medicos_medico medicos_medico_cns_medico_key; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.medicos_medico
    ADD CONSTRAINT medicos_medico_cns_medico_key UNIQUE (cns_medico);


--
-- Name: medicos_medico medicos_medico_crm_medico_key; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.medicos_medico
    ADD CONSTRAINT medicos_medico_crm_medico_key UNIQUE (crm_medico);


--
-- Name: medicos_medico medicos_medico_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.medicos_medico
    ADD CONSTRAINT medicos_medico_pkey PRIMARY KEY (id);


--
-- Name: medicos_medicousuario medicos_medicousuario_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.medicos_medicousuario
    ADD CONSTRAINT medicos_medicousuario_pkey PRIMARY KEY (id);


--
-- Name: pacientes_paciente pacientes_paciente_cpf_paciente_key; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.pacientes_paciente
    ADD CONSTRAINT pacientes_paciente_cpf_paciente_key UNIQUE (cpf_paciente);


--
-- Name: pacientes_paciente pacientes_paciente_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.pacientes_paciente
    ADD CONSTRAINT pacientes_paciente_pkey PRIMARY KEY (id);


--
-- Name: pacientes_paciente_usuarios pacientes_paciente_usuar_paciente_id_usuario_id_62936f4e_uniq; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.pacientes_paciente_usuarios
    ADD CONSTRAINT pacientes_paciente_usuar_paciente_id_usuario_id_62936f4e_uniq UNIQUE (paciente_id, usuario_id);


--
-- Name: pacientes_paciente_usuarios pacientes_paciente_usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.pacientes_paciente_usuarios
    ADD CONSTRAINT pacientes_paciente_usuarios_pkey PRIMARY KEY (id);


--
-- Name: processos_doenca processos_doenca_cid_key; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_doenca
    ADD CONSTRAINT processos_doenca_cid_key UNIQUE (cid);


--
-- Name: processos_doenca processos_doenca_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_doenca
    ADD CONSTRAINT processos_doenca_pkey PRIMARY KEY (id);


--
-- Name: processos_medicamento processos_medicamento_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_medicamento
    ADD CONSTRAINT processos_medicamento_pkey PRIMARY KEY (id);


--
-- Name: processos_processo_medicamentos processos_processo_medic_processo_id_medicamento__3fba2a06_uniq; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_processo_medicamentos
    ADD CONSTRAINT processos_processo_medic_processo_id_medicamento__3fba2a06_uniq UNIQUE (processo_id, medicamento_id);


--
-- Name: processos_processo_medicamentos processos_processo_medicamentos_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_processo_medicamentos
    ADD CONSTRAINT processos_processo_medicamentos_pkey PRIMARY KEY (id);


--
-- Name: processos_processo processos_processo_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_processo
    ADD CONSTRAINT processos_processo_pkey PRIMARY KEY (id);


--
-- Name: processos_protocolo_medicamentos processos_protocolo_medi_protocolo_id_medicamento_6b9bb077_uniq; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_protocolo_medicamentos
    ADD CONSTRAINT processos_protocolo_medi_protocolo_id_medicamento_6b9bb077_uniq UNIQUE (protocolo_id, medicamento_id);


--
-- Name: processos_protocolo_medicamentos processos_protocolo_medicamentos_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_protocolo_medicamentos
    ADD CONSTRAINT processos_protocolo_medicamentos_pkey PRIMARY KEY (id);


--
-- Name: processos_protocolo processos_protocolo_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_protocolo
    ADD CONSTRAINT processos_protocolo_pkey PRIMARY KEY (id);


--
-- Name: usuarios_usuario usuarios_usuario_email_key; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.usuarios_usuario
    ADD CONSTRAINT usuarios_usuario_email_key UNIQUE (email);


--
-- Name: usuarios_usuario_groups usuarios_usuario_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.usuarios_usuario_groups
    ADD CONSTRAINT usuarios_usuario_groups_pkey PRIMARY KEY (id);


--
-- Name: usuarios_usuario_groups usuarios_usuario_groups_usuario_id_group_id_4ed5b09e_uniq; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.usuarios_usuario_groups
    ADD CONSTRAINT usuarios_usuario_groups_usuario_id_group_id_4ed5b09e_uniq UNIQUE (usuario_id, group_id);


--
-- Name: usuarios_usuario usuarios_usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.usuarios_usuario
    ADD CONSTRAINT usuarios_usuario_pkey PRIMARY KEY (id);


--
-- Name: usuarios_usuario_user_permissions usuarios_usuario_user_pe_usuario_id_permission_id_217cadcd_uniq; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.usuarios_usuario_user_permissions
    ADD CONSTRAINT usuarios_usuario_user_pe_usuario_id_permission_id_217cadcd_uniq UNIQUE (usuario_id, permission_id);


--
-- Name: usuarios_usuario_user_permissions usuarios_usuario_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.usuarios_usuario_user_permissions
    ADD CONSTRAINT usuarios_usuario_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: clinicas_clinicausuario_clinica_id_66a84d82; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX clinicas_clinicausuario_clinica_id_66a84d82 ON public.clinicas_clinicausuario USING btree (clinica_id);


--
-- Name: clinicas_clinicausuario_usuario_id_1066a6b8; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX clinicas_clinicausuario_usuario_id_1066a6b8 ON public.clinicas_clinicausuario USING btree (usuario_id);


--
-- Name: clinicas_emissor_clinica_id_56f5fc2e; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX clinicas_emissor_clinica_id_56f5fc2e ON public.clinicas_emissor USING btree (clinica_id);


--
-- Name: clinicas_emissor_medico_id_28c299c3; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX clinicas_emissor_medico_id_28c299c3 ON public.clinicas_emissor USING btree (medico_id);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: medicos_medico_cns_medico_2adb8ca5_like; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX medicos_medico_cns_medico_2adb8ca5_like ON public.medicos_medico USING btree (cns_medico varchar_pattern_ops);


--
-- Name: medicos_medico_crm_medico_e731f026_like; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX medicos_medico_crm_medico_e731f026_like ON public.medicos_medico USING btree (crm_medico varchar_pattern_ops);


--
-- Name: medicos_medicousuario_medico_id_68b34c01; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX medicos_medicousuario_medico_id_68b34c01 ON public.medicos_medicousuario USING btree (medico_id);


--
-- Name: medicos_medicousuario_usuario_id_f6f64802; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX medicos_medicousuario_usuario_id_f6f64802 ON public.medicos_medicousuario USING btree (usuario_id);


--
-- Name: pacientes_paciente_cpf_paciente_6194a625_like; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX pacientes_paciente_cpf_paciente_6194a625_like ON public.pacientes_paciente USING btree (cpf_paciente varchar_pattern_ops);


--
-- Name: pacientes_paciente_usuarios_paciente_id_50087ad7; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX pacientes_paciente_usuarios_paciente_id_50087ad7 ON public.pacientes_paciente_usuarios USING btree (paciente_id);


--
-- Name: pacientes_paciente_usuarios_usuario_id_97a7a21b; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX pacientes_paciente_usuarios_usuario_id_97a7a21b ON public.pacientes_paciente_usuarios USING btree (usuario_id);


--
-- Name: processos_doenca_cid_b19d67ec_like; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX processos_doenca_cid_b19d67ec_like ON public.processos_doenca USING btree (cid varchar_pattern_ops);


--
-- Name: processos_doenca_protocolo_id_93a29296; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX processos_doenca_protocolo_id_93a29296 ON public.processos_doenca USING btree (protocolo_id);


--
-- Name: processos_processo_clinica_id_b92900b1; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX processos_processo_clinica_id_b92900b1 ON public.processos_processo USING btree (clinica_id);


--
-- Name: processos_processo_doenca_id_405b86dc; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX processos_processo_doenca_id_405b86dc ON public.processos_processo USING btree (doenca_id);


--
-- Name: processos_processo_emissor_id_25f0ddb8; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX processos_processo_emissor_id_25f0ddb8 ON public.processos_processo USING btree (emissor_id);


--
-- Name: processos_processo_medicamentos_medicamento_id_79bd0b77; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX processos_processo_medicamentos_medicamento_id_79bd0b77 ON public.processos_processo_medicamentos USING btree (medicamento_id);


--
-- Name: processos_processo_medicamentos_processo_id_c340d4a0; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX processos_processo_medicamentos_processo_id_c340d4a0 ON public.processos_processo_medicamentos USING btree (processo_id);


--
-- Name: processos_processo_medico_id_9c52e6aa; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX processos_processo_medico_id_9c52e6aa ON public.processos_processo USING btree (medico_id);


--
-- Name: processos_processo_paciente_id_b4d35342; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX processos_processo_paciente_id_b4d35342 ON public.processos_processo USING btree (paciente_id);


--
-- Name: processos_processo_usuario_id_19934384; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX processos_processo_usuario_id_19934384 ON public.processos_processo USING btree (usuario_id);


--
-- Name: processos_protocolo_medicamentos_medicamento_id_5b4a4231; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX processos_protocolo_medicamentos_medicamento_id_5b4a4231 ON public.processos_protocolo_medicamentos USING btree (medicamento_id);


--
-- Name: processos_protocolo_medicamentos_protocolo_id_5f395a08; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX processos_protocolo_medicamentos_protocolo_id_5f395a08 ON public.processos_protocolo_medicamentos USING btree (protocolo_id);


--
-- Name: usuarios_usuario_email_0a82e5f9_like; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX usuarios_usuario_email_0a82e5f9_like ON public.usuarios_usuario USING btree (email varchar_pattern_ops);


--
-- Name: usuarios_usuario_groups_group_id_e77f6dcf; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX usuarios_usuario_groups_group_id_e77f6dcf ON public.usuarios_usuario_groups USING btree (group_id);


--
-- Name: usuarios_usuario_groups_usuario_id_7a34077f; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX usuarios_usuario_groups_usuario_id_7a34077f ON public.usuarios_usuario_groups USING btree (usuario_id);


--
-- Name: usuarios_usuario_user_permissions_permission_id_4e5c0f2f; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX usuarios_usuario_user_permissions_permission_id_4e5c0f2f ON public.usuarios_usuario_user_permissions USING btree (permission_id);


--
-- Name: usuarios_usuario_user_permissions_usuario_id_60aeea80; Type: INDEX; Schema: public; Owner: lucas
--

CREATE INDEX usuarios_usuario_user_permissions_usuario_id_60aeea80 ON public.usuarios_usuario_user_permissions USING btree (usuario_id);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: clinicas_clinicausuario clinicas_clinicausuario_clinica_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.clinicas_clinicausuario
    ADD CONSTRAINT clinicas_clinicausuario_clinica_id_fkey FOREIGN KEY (clinica_id) REFERENCES public.clinicas_clinica(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: clinicas_clinicausuario clinicas_clinicausuario_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.clinicas_clinicausuario
    ADD CONSTRAINT clinicas_clinicausuario_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios_usuario(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: clinicas_emissor clinicas_emissor_clinica_id_56f5fc2e_fk_clinicas_clinica_id; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.clinicas_emissor
    ADD CONSTRAINT clinicas_emissor_clinica_id_56f5fc2e_fk_clinicas_clinica_id FOREIGN KEY (clinica_id) REFERENCES public.clinicas_clinica(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: clinicas_emissor clinicas_emissor_medico_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.clinicas_emissor
    ADD CONSTRAINT clinicas_emissor_medico_id_fkey FOREIGN KEY (medico_id) REFERENCES public.medicos_medico(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_usuarios_usuario_id; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_usuarios_usuario_id FOREIGN KEY (user_id) REFERENCES public.usuarios_usuario(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: medicos_medicousuario medicos_medicousuario_medico_id_68b34c01_fk_medicos_medico_id; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.medicos_medicousuario
    ADD CONSTRAINT medicos_medicousuario_medico_id_68b34c01_fk_medicos_medico_id FOREIGN KEY (medico_id) REFERENCES public.medicos_medico(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: medicos_medicousuario medicos_medicousuario_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.medicos_medicousuario
    ADD CONSTRAINT medicos_medicousuario_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios_usuario(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pacientes_paciente_usuarios pacientes_paciente_u_paciente_id_50087ad7_fk_pacientes; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.pacientes_paciente_usuarios
    ADD CONSTRAINT pacientes_paciente_u_paciente_id_50087ad7_fk_pacientes FOREIGN KEY (paciente_id) REFERENCES public.pacientes_paciente(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pacientes_paciente_usuarios pacientes_paciente_u_usuario_id_97a7a21b_fk_usuarios_; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.pacientes_paciente_usuarios
    ADD CONSTRAINT pacientes_paciente_u_usuario_id_97a7a21b_fk_usuarios_ FOREIGN KEY (usuario_id) REFERENCES public.usuarios_usuario(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: processos_doenca processos_doenca_protocolo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_doenca
    ADD CONSTRAINT processos_doenca_protocolo_id_fkey FOREIGN KEY (protocolo_id) REFERENCES public.processos_protocolo(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: processos_processo processos_processo_clinica_id_b92900b1_fk_clinicas_clinica_id; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_processo
    ADD CONSTRAINT processos_processo_clinica_id_b92900b1_fk_clinicas_clinica_id FOREIGN KEY (clinica_id) REFERENCES public.clinicas_clinica(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: processos_processo processos_processo_doenca_id_405b86dc_fk_processos_doenca_id; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_processo
    ADD CONSTRAINT processos_processo_doenca_id_405b86dc_fk_processos_doenca_id FOREIGN KEY (doenca_id) REFERENCES public.processos_doenca(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: processos_processo processos_processo_emissor_id_25f0ddb8_fk_clinicas_emissor_id; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_processo
    ADD CONSTRAINT processos_processo_emissor_id_25f0ddb8_fk_clinicas_emissor_id FOREIGN KEY (emissor_id) REFERENCES public.clinicas_emissor(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: processos_processo_medicamentos processos_processo_m_medicamento_id_79bd0b77_fk_processos; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_processo_medicamentos
    ADD CONSTRAINT processos_processo_m_medicamento_id_79bd0b77_fk_processos FOREIGN KEY (medicamento_id) REFERENCES public.processos_medicamento(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: processos_processo_medicamentos processos_processo_m_processo_id_c340d4a0_fk_processos; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_processo_medicamentos
    ADD CONSTRAINT processos_processo_m_processo_id_c340d4a0_fk_processos FOREIGN KEY (processo_id) REFERENCES public.processos_processo(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: processos_processo processos_processo_medico_id_9c52e6aa_fk_medicos_medico_id; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_processo
    ADD CONSTRAINT processos_processo_medico_id_9c52e6aa_fk_medicos_medico_id FOREIGN KEY (medico_id) REFERENCES public.medicos_medico(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: processos_processo processos_processo_paciente_id_b4d35342_fk_pacientes; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_processo
    ADD CONSTRAINT processos_processo_paciente_id_b4d35342_fk_pacientes FOREIGN KEY (paciente_id) REFERENCES public.pacientes_paciente(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: processos_processo processos_processo_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_processo
    ADD CONSTRAINT processos_processo_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios_usuario(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: processos_protocolo_medicamentos processos_protocolo__medicamento_id_5b4a4231_fk_processos; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_protocolo_medicamentos
    ADD CONSTRAINT processos_protocolo__medicamento_id_5b4a4231_fk_processos FOREIGN KEY (medicamento_id) REFERENCES public.processos_medicamento(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: processos_protocolo_medicamentos processos_protocolo__protocolo_id_5f395a08_fk_processos; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.processos_protocolo_medicamentos
    ADD CONSTRAINT processos_protocolo__protocolo_id_5f395a08_fk_processos FOREIGN KEY (protocolo_id) REFERENCES public.processos_protocolo(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: usuarios_usuario_groups usuarios_usuario_gro_usuario_id_7a34077f_fk_usuarios_; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.usuarios_usuario_groups
    ADD CONSTRAINT usuarios_usuario_gro_usuario_id_7a34077f_fk_usuarios_ FOREIGN KEY (usuario_id) REFERENCES public.usuarios_usuario(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: usuarios_usuario_groups usuarios_usuario_groups_group_id_e77f6dcf_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.usuarios_usuario_groups
    ADD CONSTRAINT usuarios_usuario_groups_group_id_e77f6dcf_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: usuarios_usuario_user_permissions usuarios_usuario_use_permission_id_4e5c0f2f_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.usuarios_usuario_user_permissions
    ADD CONSTRAINT usuarios_usuario_use_permission_id_4e5c0f2f_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: usuarios_usuario_user_permissions usuarios_usuario_use_usuario_id_60aeea80_fk_usuarios_; Type: FK CONSTRAINT; Schema: public; Owner: lucas
--

ALTER TABLE ONLY public.usuarios_usuario_user_permissions
    ADD CONSTRAINT usuarios_usuario_use_usuario_id_60aeea80_fk_usuarios_ FOREIGN KEY (usuario_id) REFERENCES public.usuarios_usuario(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--


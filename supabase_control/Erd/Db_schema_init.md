| schema_sql                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| -- Table: USER
CREATE TABLE USER (
  email character varying NOT NULL,
  user_id integer NOT NULL DEFAULT nextval('"USER_user_id_seq"'::regclass),
  last_login timestamp with time zone,
  is_active boolean DEFAULT true,
  auth_provider character varying DEFAULT 'Email'::character varying,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  password_hash character varying NOT NULL
);                                                                                                                                                                                                |
| -- Table: application_record
CREATE TABLE application_record (
  user_feedback jsonb,
  application_status character varying DEFAULT 'applied'::character varying,
  application_id integer NOT NULL DEFAULT nextval('application_record_application_id_seq'::regclass),
  user_id integer,
  job_id integer,
  version_id integer,
  applied_at timestamp with time zone NOT NULL DEFAULT now(),
  status_updated_at timestamp with time zone,
  days_since_application integer
);                                                                                                                          |
| -- Table: career_analysis_report
CREATE TABLE career_analysis_report (
  generated_at timestamp with time zone DEFAULT now(),
  skill_gap_analysis jsonb,
  report_id integer NOT NULL DEFAULT nextval('career_analysis_report_report_id_seq'::regclass),
  career_readiness_score double precision,
  market_insights jsonb,
  career_path_suggestions jsonb,
  resume_id integer,
  survey_id integer
);                                                                                                                                                                                                   |
| -- Table: career_survey
CREATE TABLE career_survey (
  career_motivation jsonb,
  survey_id integer NOT NULL DEFAULT nextval('career_survey_survey_id_seq'::regclass),
  location_preference character varying,
  remote_preference character varying,
  updated_at timestamp with time zone DEFAULT now(),
  completed_at timestamp with time zone,
  user_id integer,
  salary_max integer,
  salary_min integer,
  skill_self_assessment jsonb,
  career_preference jsonb
);                                                                                                                              |
| -- Table: company_info
CREATE TABLE company_info (
  company_name character varying NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  company_id integer NOT NULL DEFAULT nextval('company_info_company_id_seq'::regclass),
  industry character varying,
  description text,
  website character varying,
  location character varying,
  company_size character varying
);                                                                                                                                                                                                                  |
| -- Table: job_matching
CREATE TABLE job_matching (
  job_id integer,
  matching_algorithm character varying,
  matched_at timestamp with time zone DEFAULT now(),
  matching_id integer NOT NULL DEFAULT nextval('job_matching_matching_id_seq'::regclass),
  resume_id integer,
  overall_match_score double precision
);                                                                                                                                                                                                                                                                                   |
| -- Table: job_posting
CREATE TABLE job_posting (
  is_active boolean DEFAULT true,
  source_url character varying,
  source_platform character varying,
  remote_option character varying,
  location character varying,
  requirements text,
  job_description text,
  job_title character varying,
  job_id integer NOT NULL DEFAULT nextval('job_posting_job_id_seq'::regclass),
  company_id integer,
  salary_min integer,
  salary_max integer,
  job_details jsonb,
  posted_date date,
  scraped_at timestamp with time zone DEFAULT now(),
  vector_id uuid,
  is_embedded boolean DEFAULT false
); |
| -- Table: job_skill_requirement
CREATE TABLE job_skill_requirement (
  proficiency_level integer,
  importance character varying,
  job_id integer,
  requirement_id integer NOT NULL DEFAULT nextval('job_skill_requirement_requirement_id_seq'::regclass),
  skill_id integer
);                                                                                                                                                                                                                                                                                                                           |
| -- Table: match_score
CREATE TABLE match_score (
  score_breakdown jsonb,
  location_match_score double precision,
  salary_match_score double precision,
  experience_match_score double precision,
  skill_match_score double precision,
  matching_id integer,
  score_id integer NOT NULL DEFAULT nextval('match_score_score_id_seq'::regclass),
  created_at timestamp with time zone DEFAULT now()
);                                                                                                                                                                                                  |
| -- Table: ocr_result
CREATE TABLE ocr_result (
  event_id integer,
  ocr_status character varying,
  ocr_id integer NOT NULL DEFAULT nextval('ocr_result_ocr_id_seq'::regclass),
  raw_text text,
  resume_id integer,
  extracted_data jsonb,
  confidence_score double precision,
  is_manual_review_needed boolean DEFAULT false,
  processed_at timestamp with time zone DEFAULT now()
);                                                                                                                                                                                                                |
| -- Table: resume
CREATE TABLE resume (
  resume_id integer NOT NULL DEFAULT nextval('resume_resume_id_seq'::regclass),
  resume_type character varying NOT NULL,
  vector_id uuid,
  user_id integer,
  template_id integer,
  normalized_data jsonb,
  structured_data jsonb,
  updated_at timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  is_primary boolean DEFAULT false,
  is_embedded boolean DEFAULT false
);                                                                                                                                 |
| -- Table: resume_template
CREATE TABLE resume_template (
  template_id integer NOT NULL DEFAULT nextval('resume_template_template_id_seq'::regclass),
  template_structure jsonb,
  template_type character varying,
  template_name character varying NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now()
);                                                                                                                                                                                                                                                                             |
| -- Table: resume_version
CREATE TABLE resume_version (
  optimization_target character varying,
  version_id integer NOT NULL DEFAULT nextval('resume_version_version_id_seq'::regclass),
  resume_id integer,
  version_number integer NOT NULL,
  content jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  file_path character varying
);                                                                                                                                                                                                                                            |
| -- Table: side_project_recommendation
CREATE TABLE side_project_recommendation (
  gap_id integer,
  project_description text,
  difficulty_level character varying,
  estimated_hours integer,
  required_skills jsonb,
  created_at timestamp with time zone DEFAULT now(),
  project_name character varying,
  recommendation_id integer NOT NULL DEFAULT nextval('side_project_recommendation_recommendation_id_seq'::regclass),
  project_url character varying
);                                                                                                                                      |
| -- Table: skill_gap
CREATE TABLE skill_gap (
  target_level integer,
  skill_id integer,
  skill_roi_score double precision,
  priority_rank integer,
  current_level integer,
  time_investment_hours double precision,
  gap_id integer NOT NULL DEFAULT nextval('skill_gap_gap_id_seq'::regclass),
  report_id integer
);                                                                                                                                                                                                                                                                                 |
| -- Table: skill_master
CREATE TABLE skill_master (
  skill_id integer NOT NULL DEFAULT nextval('skill_master_skill_id_seq'::regclass),
  skill_category character varying,
  synonyms jsonb,
  skill_name character varying NOT NULL,
  created_at timestamp with time zone DEFAULT now()
);                                                                                                                                                                                                                                                                                                                 |
| -- Table: upload_event
CREATE TABLE upload_event (
  status character varying DEFAULT 'pending'::character varying,
  file_name character varying NOT NULL,
  metadata jsonb,
  uploaded_at timestamp with time zone NOT NULL DEFAULT now(),
  user_id integer,
  file_path character varying NOT NULL,
  upload_type character varying,
  event_id integer NOT NULL DEFAULT nextval('upload_event_event_id_seq'::regclass)
);                                                                                                                                                                               |
| -- Table: user_profile
CREATE TABLE user_profile (
  profile_id integer NOT NULL DEFAULT nextval('user_profile_profile_id_seq'::regclass),
  user_id integer,
  github_repo character varying,
  full_name character varying,
  location character varying,
  years_of_experience integer,
  current_position character varying,
  education_background text,
  privacy_settings jsonb,
  updated_at timestamp with time zone DEFAULT now()
);                                                                                                                                                               |
| -- Table: user_skill
CREATE TABLE user_skill (
  skill_id integer,
  user_skill_id integer NOT NULL DEFAULT nextval('user_skill_user_skill_id_seq'::regclass),
  verified boolean DEFAULT false,
  years_of_experience double precision,
  proficiency_level integer,
  created_at timestamp with time zone DEFAULT now(),
  user_id integer
);                                                                                                                                                                                                                                                              |
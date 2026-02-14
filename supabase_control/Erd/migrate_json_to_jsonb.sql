-- =============================================================================
-- 將所有 JSON 欄位改為 JSONB（僅處理目前型態為 json 的欄位，已是 jsonb 則跳過）
-- 適用：Supabase PostgreSQL
-- =============================================================================

DO $$
DECLARE
  r RECORD;
BEGIN
  FOR r IN
    SELECT table_schema, table_name, column_name
    FROM information_schema.columns
    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
      AND data_type = 'json'
  LOOP
    EXECUTE format(
      'ALTER TABLE %I.%I ALTER COLUMN %I TYPE jsonb USING %I::jsonb',
      r.table_schema, r.table_name, r.column_name, r.column_name
    );
    RAISE NOTICE 'Altered %.%.% → JSONB', r.table_schema, r.table_name, r.column_name;
  END LOOP;
END $$;


-- =============================================================================
-- 以下為「手動逐條」寫法參考（若不想用動態 SQL，可改為逐條執行）
-- 僅在「該欄位目前是 json」時才需要執行；已是 jsonb 的欄位執行會報錯，故建議用上方 DO 區塊即可。
-- =============================================================================
/*
-- user_profile
ALTER TABLE user_profile ALTER COLUMN privacy_settings TYPE jsonb USING privacy_settings::jsonb;

-- career_survey
ALTER TABLE career_survey ALTER COLUMN career_preference TYPE jsonb USING career_preference::jsonb;
ALTER TABLE career_survey ALTER COLUMN skill_self_assessment TYPE jsonb USING skill_self_assessment::jsonb;
ALTER TABLE career_survey ALTER COLUMN career_motivation TYPE jsonb USING career_motivation::jsonb;

-- resume
ALTER TABLE resume ALTER COLUMN structured_data TYPE jsonb USING structured_data::jsonb;
ALTER TABLE resume ALTER COLUMN normalized_data TYPE jsonb USING normalized_data::jsonb;

-- resume_version
ALTER TABLE resume_version ALTER COLUMN content TYPE jsonb USING content::jsonb;

-- resume_template
ALTER TABLE resume_template ALTER COLUMN template_structure TYPE jsonb USING template_structure::jsonb;

-- upload_event
ALTER TABLE upload_event ALTER COLUMN metadata TYPE jsonb USING metadata::jsonb;

-- ocr_result
ALTER TABLE ocr_result ALTER COLUMN extracted_data TYPE jsonb USING extracted_data::jsonb;

-- job_posting
ALTER TABLE job_posting ALTER COLUMN job_details TYPE jsonb USING job_details::jsonb;

-- skill_master
ALTER TABLE skill_master ALTER COLUMN synonyms TYPE jsonb USING synonyms::jsonb;

-- match_score
ALTER TABLE match_score ALTER COLUMN score_breakdown TYPE jsonb USING score_breakdown::jsonb;

-- application_record
ALTER TABLE application_record ALTER COLUMN user_feedback TYPE jsonb USING user_feedback::jsonb;

-- career_analysis_report
ALTER TABLE career_analysis_report ALTER COLUMN skill_gap_analysis TYPE jsonb USING skill_gap_analysis::jsonb;
ALTER TABLE career_analysis_report ALTER COLUMN career_path_suggestions TYPE jsonb USING career_path_suggestions::jsonb;
ALTER TABLE career_analysis_report ALTER COLUMN market_insights TYPE jsonb USING market_insights::jsonb;
-- 若為新增欄位且尚未建立，請用 ADD COLUMN；若已存在為 json 則用下方
-- ALTER TABLE career_analysis_report ALTER COLUMN preliminary_summary TYPE jsonb USING preliminary_summary::jsonb;
-- ALTER TABLE career_analysis_report ALTER COLUMN radar_chart TYPE jsonb USING radar_chart::jsonb;
-- ALTER TABLE career_analysis_report ALTER COLUMN gap_analysis TYPE jsonb USING gap_analysis::jsonb;
-- ALTER TABLE career_analysis_report ALTER COLUMN action_plan TYPE jsonb USING action_plan::jsonb;

-- side_project_recommendation
ALTER TABLE side_project_recommendation ALTER COLUMN required_skills TYPE jsonb USING required_skills::jsonb;
*/

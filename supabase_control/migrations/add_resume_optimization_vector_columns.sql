-- 為 resume_optimization 表新增 vector_id、is_embedded 欄位
-- 用途：優化後履歷寫入 Qdrant optimized_resume_vectors 後回填，供職缺推薦時選擇「優化前/後」履歷做向量比對
-- 執行方式：在 Supabase SQL Editor 或 migration 工具中執行

ALTER TABLE resume_optimization
  ADD COLUMN IF NOT EXISTS vector_id UUID,
  ADD COLUMN IF NOT EXISTS is_embedded BOOLEAN NOT NULL DEFAULT FALSE;

COMMENT ON COLUMN resume_optimization.vector_id IS '對應 Qdrant optimized_resume_vectors 中的 Point ID，向量化腳本回填用';
COMMENT ON COLUMN resume_optimization.is_embedded IS '是否已寫入 Qdrant optimized_resume_vectors';

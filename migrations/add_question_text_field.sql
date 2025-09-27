-- 数据库迁移：为 ingest_items 表添加 question_text 字段
-- 用于支持格式保持功能

-- 添加新字段
ALTER TABLE ingest_items ADD COLUMN IF NOT EXISTS question_text TEXT;

-- 添加索引以提升查询性能
CREATE INDEX IF NOT EXISTS idx_ingest_items_question_text ON ingest_items(question_text) WHERE question_text IS NOT NULL;

-- 为现有数据迁移文本内容（从 ocr_json 中提取）
UPDATE ingest_items 
SET question_text = COALESCE(
    (ocr_json->>'text'), 
    (ocr_json->>'content'), 
    (ocr_json->>'question'),
    '识别文本为空'
)
WHERE question_text IS NULL AND ocr_json IS NOT NULL;

-- 添加注释
COMMENT ON COLUMN ingest_items.question_text IS '格式化后的题目文本，保持原有排版格式';

-- Smart Exam System (V3.1) - Enhanced SQL Schema (PostgreSQL)
-- Generated: 2025-09-26
-- Features: Complete indexing, constraints, and optimizations for MVP

-- Users & Classes
CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(120) NOT NULL,
  role VARCHAR(20) NOT NULL CHECK (role IN ('admin','teacher','student')),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE UNIQUE INDEX IF NOT EXISTS uniq_users_email ON users(email);

CREATE TABLE IF NOT EXISTS classes (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  grade VARCHAR(50),
  owner_teacher_id BIGINT REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS class_students (
  class_id BIGINT REFERENCES classes(id) ON DELETE CASCADE,
  student_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  joined_at TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (class_id, student_id)
);

-- Knowledge & Questions
CREATE TABLE IF NOT EXISTS knowledge_points (
  id BIGSERIAL PRIMARY KEY,
  subject VARCHAR(80) NOT NULL,
  module VARCHAR(120),
  point VARCHAR(200),
  subskill VARCHAR(200),
  code VARCHAR(120) UNIQUE,
  parent_id BIGINT REFERENCES knowledge_points(id),
  level INT CHECK (level >= 1 AND level <= 4)
);

CREATE INDEX IF NOT EXISTS idx_kp_subject_module ON knowledge_points(subject, module);
CREATE UNIQUE INDEX IF NOT EXISTS uniq_kp_code ON knowledge_points(code) WHERE code IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_kp_parent ON knowledge_points(parent_id);

CREATE TABLE IF NOT EXISTS questions (
  id BIGSERIAL PRIMARY KEY,
  stem TEXT NOT NULL,
  type VARCHAR(20) NOT NULL CHECK (type IN ('single','multiple','fill','judge','subjective')),
  difficulty INT DEFAULT 2 CHECK (difficulty BETWEEN 1 AND 5),
  options_json JSONB,
  answer_json JSONB,
  analysis TEXT,
  source_meta JSONB,
  created_by BIGINT REFERENCES users(id),
  status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','reviewing','published')),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_questions_type_difficulty ON questions(type, difficulty);
CREATE INDEX IF NOT EXISTS idx_questions_status ON questions(status);
CREATE INDEX IF NOT EXISTS idx_questions_created_by ON questions(created_by);
CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions(created_at);

CREATE TABLE IF NOT EXISTS question_knowledge_map (
  question_id BIGINT REFERENCES questions(id) ON DELETE CASCADE,
  kp_id BIGINT REFERENCES knowledge_points(id) ON DELETE CASCADE,
  PRIMARY KEY (question_id, kp_id)
);

CREATE TABLE IF NOT EXISTS question_assets (
  id BIGSERIAL PRIMARY KEY,
  question_id BIGINT REFERENCES questions(id) ON DELETE CASCADE,
  file_uri TEXT NOT NULL,
  kind VARCHAR(40)
);

-- Papers
CREATE TABLE IF NOT EXISTS papers (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  subject VARCHAR(80),
  grade VARCHAR(50),
  layout_json JSONB,
  qr_schema JSONB,
  created_by BIGINT REFERENCES users(id),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS paper_questions (
  paper_id BIGINT REFERENCES papers(id) ON DELETE CASCADE,
  question_id BIGINT REFERENCES questions(id) ON DELETE CASCADE,
  seq INT NOT NULL,
  score NUMERIC(6,2) NOT NULL DEFAULT 0,
  section VARCHAR(80),
  PRIMARY KEY (paper_id, question_id)
);

CREATE TABLE IF NOT EXISTS paper_versions (
  id BIGSERIAL PRIMARY KEY,
  paper_id BIGINT REFERENCES papers(id) ON DELETE CASCADE,
  version_no INT NOT NULL,
  pdf_uri TEXT NOT NULL,
  checksum VARCHAR(128),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Answer Sheets & Grading
CREATE TABLE IF NOT EXISTS answer_sheets (
  id BIGSERIAL PRIMARY KEY,
  paper_id BIGINT REFERENCES papers(id),
  student_id BIGINT REFERENCES users(id),
  class_id BIGINT REFERENCES classes(id),
  qr_token VARCHAR(120),
  upload_uri TEXT,
  status VARCHAR(20) NOT NULL DEFAULT 'uploaded' CHECK (status IN ('uploaded','processed','graded','error')),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS answers (
  id BIGSERIAL PRIMARY KEY,
  sheet_id BIGINT REFERENCES answer_sheets(id) ON DELETE CASCADE,
  question_id BIGINT REFERENCES questions(id),
  raw_omr JSONB,
  raw_ocr JSONB,
  parsed_json JSONB,
  spent_ms INT,
  is_objective BOOLEAN DEFAULT TRUE,
  is_correct BOOLEAN,
  score NUMERIC(6,2),
  error_flag BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_answers_sheet_qid ON answers(sheet_id, question_id);
CREATE INDEX IF NOT EXISTS idx_answers_qid_correct ON answers(question_id, is_correct);
CREATE INDEX IF NOT EXISTS idx_answers_is_objective ON answers(is_objective);
CREATE INDEX IF NOT EXISTS idx_answers_error_flag ON answers(error_flag) WHERE error_flag = TRUE;

CREATE TABLE IF NOT EXISTS grading_logs (
  id BIGSERIAL PRIMARY KEY,
  answer_id BIGINT REFERENCES answers(id) ON DELETE CASCADE,
  mode VARCHAR(20) NOT NULL CHECK (mode IN ('auto','ai_suggest','manual')),
  prev_score NUMERIC(6,2),
  new_score NUMERIC(6,2),
  reason TEXT,
  grader_id BIGINT REFERENCES users(id),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS data_quality_issues (
  id BIGSERIAL PRIMARY KEY,
  sheet_id BIGINT REFERENCES answer_sheets(id) ON DELETE CASCADE,
  question_id BIGINT REFERENCES questions(id),
  issue_code VARCHAR(40) NOT NULL,
  detail TEXT,
  severity VARCHAR(20) DEFAULT 'low',
  resolved BOOLEAN DEFAULT FALSE
);

-- Student Stats & Wrong Book
CREATE TABLE IF NOT EXISTS student_stats (
  student_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  kp_id BIGINT REFERENCES knowledge_points(id) ON DELETE CASCADE,
  total INT DEFAULT 0,
  wrong INT DEFAULT 0,
  last3_wrong_rate NUMERIC(5,2),
  first_pass_rate NUMERIC(5,2),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (student_id, kp_id)
);

CREATE INDEX IF NOT EXISTS idx_student_stats_student_kp ON student_stats(student_id, kp_id);
CREATE INDEX IF NOT EXISTS idx_student_stats_updated_at ON student_stats(updated_at);

CREATE TABLE IF NOT EXISTS wrong_book (
  id BIGSERIAL PRIMARY KEY,
  student_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  question_id BIGINT REFERENCES questions(id) ON DELETE CASCADE,
  first_wrong_at TIMESTAMP NOT NULL DEFAULT NOW(),
  last_retry_at TIMESTAMP,
  retry_count INT DEFAULT 0,
  last_result BOOLEAN
);

CREATE INDEX IF NOT EXISTS idx_wrong_book_student ON wrong_book(student_id);
CREATE INDEX IF NOT EXISTS idx_wrong_book_question ON wrong_book(question_id);
CREATE INDEX IF NOT EXISTS idx_wrong_book_last_result ON wrong_book(last_result);

-- Ingest Sessions (Reverse Paper → Question Bank)
CREATE TABLE IF NOT EXISTS ingest_sessions (
  id BIGSERIAL PRIMARY KEY,
  uploader_id BIGINT REFERENCES users(id),
  file_uri TEXT NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'uploaded' CHECK (status IN ('uploaded','parsing','awaiting_review','partially_approved','completed')),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ingest_sessions_uploader ON ingest_sessions(uploader_id);
CREATE INDEX IF NOT EXISTS idx_ingest_sessions_status ON ingest_sessions(status);
CREATE INDEX IF NOT EXISTS idx_ingest_sessions_created_at ON ingest_sessions(created_at);

CREATE TABLE IF NOT EXISTS ingest_items (
  id BIGSERIAL PRIMARY KEY,
  session_id BIGINT REFERENCES ingest_sessions(id) ON DELETE CASCADE,
  seq INT,
  crop_uri TEXT,
  ocr_json JSONB,
  candidate_type VARCHAR(20),
  candidate_kps_json JSONB,
  confidence NUMERIC(5,2),
  review_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending','approved','rejected','edited')),
  approved_question_id BIGINT REFERENCES questions(id)
);

CREATE INDEX IF NOT EXISTS idx_ingest_items_session ON ingest_items(session_id);
CREATE INDEX IF NOT EXISTS idx_ingest_items_review_status ON ingest_items(review_status);
CREATE INDEX IF NOT EXISTS idx_ingest_items_confidence ON ingest_items(confidence) WHERE confidence IS NOT NULL;

-- Additional indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_answer_sheets_student_paper ON answer_sheets(student_id, paper_id);
CREATE INDEX IF NOT EXISTS idx_answer_sheets_class ON answer_sheets(class_id);
CREATE INDEX IF NOT EXISTS idx_answer_sheets_status ON answer_sheets(status);
CREATE INDEX IF NOT EXISTS idx_answer_sheets_created_at ON answer_sheets(created_at);

CREATE INDEX IF NOT EXISTS idx_papers_created_by ON papers(created_by);
CREATE INDEX IF NOT EXISTS idx_papers_subject_grade ON papers(subject, grade);
CREATE INDEX IF NOT EXISTS idx_papers_created_at ON papers(created_at);

CREATE INDEX IF NOT EXISTS idx_grading_logs_answer ON grading_logs(answer_id);
CREATE INDEX IF NOT EXISTS idx_grading_logs_mode ON grading_logs(mode);
CREATE INDEX IF NOT EXISTS idx_grading_logs_grader ON grading_logs(grader_id);

CREATE INDEX IF NOT EXISTS idx_data_quality_issues_sheet ON data_quality_issues(sheet_id);
CREATE INDEX IF NOT EXISTS idx_data_quality_issues_resolved ON data_quality_issues(resolved) WHERE resolved = FALSE;
CREATE INDEX IF NOT EXISTS idx_data_quality_issues_severity ON data_quality_issues(severity);

-- Functions and triggers for auto-updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to student_stats table
CREATE TRIGGER update_student_stats_updated_at BEFORE UPDATE ON student_stats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Initial data for testing (MVP)
INSERT INTO users (email, password_hash, name, role) VALUES 
('admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.hGKc8m/EO', 'Administrator', 'admin'),
('teacher@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.hGKc8m/EO', 'Teacher Zhang', 'teacher'),
('student@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.hGKc8m/EO', 'Student A', 'student')
ON CONFLICT (email) DO NOTHING;

-- Sample knowledge points
INSERT INTO knowledge_points (subject, module, point, subskill, code, level) VALUES 
('Math', 'Algebra', 'Quadratic Equations', 'Quadratic Formula', 'MATH_ALG_QUAD_ROOT', 2),
('Math', 'Algebra', 'Quadratic Equations', 'Discriminant', 'MATH_ALG_QUAD_DISC', 2),
('Math', 'Geometry', 'Triangles', 'Pythagorean Theorem', 'MATH_GEO_TRI_PYTH', 2),
('Chinese', 'Reading', 'Modern Text Reading', 'Main Idea', 'LANG_READ_MAIN_IDEA', 3),
('English', 'Grammar', 'Tenses', 'Past Tense', 'ENG_GRAM_PAST_TENSE', 2)
ON CONFLICT (code) DO NOTHING;

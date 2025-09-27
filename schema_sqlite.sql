-- 智能考试系统 SQLite Schema

-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(120) NOT NULL,
  role VARCHAR(20) NOT NULL CHECK (role IN ('admin','teacher','student')),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 知识点表
CREATE TABLE IF NOT EXISTS knowledge_points (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  subject VARCHAR(80) NOT NULL,
  module VARCHAR(120),
  point VARCHAR(200),
  subskill VARCHAR(200),
  code VARCHAR(120) UNIQUE,
  parent_id INTEGER REFERENCES knowledge_points(id),
  level INTEGER CHECK (level >= 1 AND level <= 4)
);

-- 题目表
CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  stem TEXT NOT NULL,
  type VARCHAR(20) NOT NULL CHECK (type IN ('single','multiple','fill','judge','subjective')),
  difficulty INTEGER DEFAULT 2 CHECK (difficulty BETWEEN 1 AND 5),
  options_json TEXT,
  answer_json TEXT,
  analysis TEXT,
  source_meta TEXT,
  created_by INTEGER REFERENCES users(id),
  status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','reviewing','published')),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 拆题会话表
CREATE TABLE IF NOT EXISTS ingest_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id VARCHAR(120),
  name VARCHAR(200),
  created_by INTEGER REFERENCES users(id),
  file_uri TEXT NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'uploaded' CHECK (status IN ('uploaded','parsing','awaiting_review','partially_approved','completed','failed')),
  total_items INTEGER DEFAULT 0,
  processed_items INTEGER DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 拆题项目表（包含新的question_text字段）
CREATE TABLE IF NOT EXISTS ingest_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER REFERENCES ingest_sessions(id) ON DELETE CASCADE,
  seq INTEGER,
  crop_uri TEXT,
  ocr_json TEXT,
  question_text TEXT,  -- 新增：保存格式化后的题目文本
  candidate_type VARCHAR(20),
  candidate_kps_json TEXT,
  confidence REAL,
  review_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending','approved','rejected','edited')),
  approved_question_id INTEGER REFERENCES questions(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(type);
CREATE INDEX IF NOT EXISTS idx_questions_created_by ON questions(created_by);
CREATE INDEX IF NOT EXISTS idx_ingest_sessions_created_by ON ingest_sessions(created_by);
CREATE INDEX IF NOT EXISTS idx_ingest_items_session_id ON ingest_items(session_id);
CREATE INDEX IF NOT EXISTS idx_ingest_items_review_status ON ingest_items(review_status);

-- 插入测试数据
INSERT OR IGNORE INTO users (email, password_hash, name, role) VALUES 
('admin@example.com', 'password', 'Administrator', 'admin'),
('teacher@example.com', 'password', 'Teacher Zhang', 'teacher'),
('student@example.com', 'password', 'Student A', 'student');

-- 插入知识点样例数据
INSERT OR IGNORE INTO knowledge_points (subject, module, point, subskill, code, level) VALUES 
('Math', 'Algebra', 'Quadratic Equations', 'Quadratic Formula', 'MATH_ALG_QUAD_ROOT', 2),
('Math', 'Algebra', 'Quadratic Equations', 'Discriminant', 'MATH_ALG_QUAD_DISC', 2),
('Math', 'Geometry', 'Triangles', 'Pythagorean Theorem', 'MATH_GEO_TRI_PYTH', 2);
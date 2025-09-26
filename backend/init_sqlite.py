#!/usr/bin/env python3
"""
Initialize SQLite database for testing
"""
import sqlite3
from datetime import datetime
import hashlib

# Create SQLite database
conn = sqlite3.connect('test_exam.db')
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(120) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin','teacher','student')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
''')

# Create knowledge_points table
cursor.execute('''
CREATE TABLE IF NOT EXISTS knowledge_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject VARCHAR(80) NOT NULL,
    module VARCHAR(120),
    point VARCHAR(200),
    subskill VARCHAR(200),
    code VARCHAR(120) UNIQUE,
    parent_id INTEGER REFERENCES knowledge_points(id),
    level INTEGER CHECK (level >= 1 AND level <= 4)
)
''')

# Create questions table
cursor.execute('''
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
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
''')

# Create question_knowledge_map table
cursor.execute('''
CREATE TABLE IF NOT EXISTS question_knowledge_map (
    question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
    kp_id INTEGER REFERENCES knowledge_points(id) ON DELETE CASCADE,
    PRIMARY KEY (question_id, kp_id)
)
''')

# Insert test user (teacher)
password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewOyJOxrJAzNx9ae"  # password: password
cursor.execute('''
INSERT OR REPLACE INTO users (email, password_hash, name, role)
VALUES ('teacher@example.com', ?, '测试教师', 'teacher')
''', (password_hash,))

# Insert test knowledge points
knowledge_points = [
    ('数学', '代数', '函数', '一次函数', 'MATH_ALGEBRA_FUNC_LINEAR', 1),
    ('数学', '代数', '函数', '二次函数', 'MATH_ALGEBRA_FUNC_QUADRATIC', 1),
    ('数学', '几何', '三角形', '全等三角形', 'MATH_GEOMETRY_TRIANGLE_CONGRUENT', 1),
    ('语文', '阅读理解', '现代文', '记叙文', 'CHINESE_READING_MODERN_NARRATIVE', 1),
    ('语文', '写作', '议论文', '论证方法', 'CHINESE_WRITING_ARGUMENTATIVE_PROOF', 1),
]

for kp in knowledge_points:
    cursor.execute('''
    INSERT OR REPLACE INTO knowledge_points (subject, module, point, subskill, code, level)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', kp)

# Insert test questions
questions = [
    ('下列哪个是一次函数？', 'single', 2, '{"A": "y = x²", "B": "y = 2x + 1", "C": "y = 1/x", "D": "y = x³"}', '{"answer": "B"}', '一次函数的形式为 y = kx + b'),
    ('解方程：x² - 5x + 6 = 0', 'fill', 3, '{}', '{"answer": "x = 2 或 x = 3"}', '利用因式分解：(x-2)(x-3) = 0'),
    ('判断：所有的矩形都是正方形', 'judge', 1, '{}', '{"answer": false}', '矩形的四个角都是直角，但四边不一定相等'),
]

for i, question in enumerate(questions, 1):
    cursor.execute('''
    INSERT OR REPLACE INTO questions (id, stem, type, difficulty, options_json, answer_json, analysis, created_by, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'published')
    ''', (i, *question))

# Insert knowledge point mappings
cursor.execute('INSERT OR REPLACE INTO question_knowledge_map (question_id, kp_id) VALUES (1, 1)')
cursor.execute('INSERT OR REPLACE INTO question_knowledge_map (question_id, kp_id) VALUES (2, 2)')
cursor.execute('INSERT OR REPLACE INTO question_knowledge_map (question_id, kp_id) VALUES (3, 3)')

conn.commit()
conn.close()

print("SQLite数据库初始化完成！")
print("测试用户: teacher@example.com / password")
print("已创建3道测试题目和5个知识点")
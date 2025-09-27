#!/usr/bin/env python3
import sqlite3
import sys
import os

def create_database():
    """创建SQLite数据库和表结构"""
    
    # 连接数据库（如果不存在会自动创建）
    conn = sqlite3.connect('test_exam.db')
    cursor = conn.cursor()
    
    # 删除现有表（如果存在）
    print("删除现有表...")
    tables = ['ingest_items', 'ingest_sessions', 'question_knowledge_map', 'paper_questions', 
              'papers', 'questions', 'knowledge_points', 'class_students', 'classes', 'users']
    
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    
    print("创建用户表...")
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(100) NOT NULL,
            role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'teacher', 'student')),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("创建班级表...")
    cursor.execute('''
        CREATE TABLE classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            grade VARCHAR(50) NOT NULL,
            owner_teacher_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE class_students (
            class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
            student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (class_id, student_id)
        )
    ''')
    
    print("创建知识点表...")
    cursor.execute('''
        CREATE TABLE knowledge_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject VARCHAR(50) NOT NULL,
            module VARCHAR(100) NOT NULL,
            point VARCHAR(100) NOT NULL,
            subskill VARCHAR(100),
            code VARCHAR(50),
            level INTEGER DEFAULT 1,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("创建题目表...")
    cursor.execute('''
        CREATE TABLE questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stem TEXT NOT NULL,
            type VARCHAR(20) NOT NULL CHECK (type IN ('single', 'multiple', 'fill', 'judge', 'subjective')),
            difficulty INTEGER DEFAULT 2 CHECK (difficulty BETWEEN 1 AND 5),
            options_json TEXT,
            answer_json TEXT,
            analysis TEXT,
            source_meta TEXT,
            created_by INTEGER REFERENCES users(id),
            status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE question_knowledge_map (
            question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
            kp_id INTEGER REFERENCES knowledge_points(id) ON DELETE CASCADE,
            PRIMARY KEY (question_id, kp_id)
        )
    ''')
    
    print("创建试卷表...")
    cursor.execute('''
        CREATE TABLE papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            subject VARCHAR(50),
            grade VARCHAR(50),
            duration INTEGER DEFAULT 90,
            total_score INTEGER DEFAULT 100,
            layout_json TEXT,
            created_by INTEGER REFERENCES users(id),
            status VARCHAR(20) DEFAULT 'draft',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE paper_questions (
            paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
            question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
            seq INTEGER,
            score REAL DEFAULT 0,
            section VARCHAR(50),
            PRIMARY KEY (paper_id, question_id)
        )
    ''')
    
    print("创建拆题入库表...")
    cursor.execute('''
        CREATE TABLE ingest_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id VARCHAR(50),
            name VARCHAR(200),
            created_by INTEGER REFERENCES users(id),
            status VARCHAR(30) NOT NULL DEFAULT 'uploaded',
            total_items INTEGER DEFAULT 0,
            processed_items INTEGER DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE ingest_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER REFERENCES ingest_sessions(id) ON DELETE CASCADE,
            seq INTEGER,
            crop_uri TEXT,
            ocr_json TEXT,
            candidate_type VARCHAR(20),
            candidate_kps_json TEXT,
            confidence REAL,
            review_status VARCHAR(20) NOT NULL DEFAULT 'pending',
            approved_question_id INTEGER REFERENCES questions(id)
        )
    ''')
    
    print("插入测试用户数据...")
    # 插入测试用户（密码都是 "password"）
    users_data = [
        ('admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewOyJOxrJAzNx9ae', 'Admin', 'admin'),
        ('teacher@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewOyJOxrJAzNx9ae', 'Teacher Zhang', 'teacher'),
        ('student@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewOyJOxrJAzNx9ae', 'Student Li', 'student'),
    ]
    
    cursor.executemany('''
        INSERT INTO users (email, password_hash, name, role) VALUES (?, ?, ?, ?)
    ''', users_data)
    
    print("插入知识点数据...")
    kp_data = [
        ('数学', '代数', '一元二次方程', '求根公式', 'MATH_ALG_QUAD_FORMULA', 2),
        ('数学', '几何', '三角形', '全等三角形', 'MATH_GEO_TRIANGLE_CONGRUENT', 2),
        ('语文', '阅读理解', '现代文', '记叙文', 'CHINESE_READING_MODERN_NARRATIVE', 1),
        ('英语', '语法', '时态', '一般现在时', 'ENGLISH_GRAMMAR_TENSE_PRESENT', 1),
    ]
    
    cursor.executemany('''
        INSERT INTO knowledge_points (subject, module, point, subskill, code, level) VALUES (?, ?, ?, ?, ?, ?)
    ''', kp_data)
    
    print("插入示例题目...")
    questions_data = [
        ('1+1等于几？', 'single', 1, '{"A": "1", "B": "2", "C": "3", "D": "4"}', '{"answer": "B"}', '这是基本的数学运算', None, 2, 'published'),
        ('x² - 5x + 6 = 0 的解是？', 'fill', 3, '{}', '{"answer": "x = 2 或 x = 3"}', '利用因式分解求解', None, 2, 'published'),
    ]
    
    cursor.executemany('''
        INSERT INTO questions (stem, type, difficulty, options_json, answer_json, analysis, source_meta, created_by, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', questions_data)
    
    # 提交更改
    conn.commit()
    
    print("验证表结构...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"创建的表: {[table[0] for table in tables]}")
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"用户数量: {user_count}")
    
    cursor.execute("SELECT COUNT(*) FROM questions")
    question_count = cursor.fetchone()[0]
    print(f"题目数量: {question_count}")
    
    # 关闭连接
    conn.close()
    print("✅ 数据库创建完成！")

if __name__ == "__main__":
    create_database()
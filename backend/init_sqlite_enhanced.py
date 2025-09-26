#!/usr/bin/env python3
"""
Enhanced SQLite initialization script for Smart Exam System
Enhanced test data including all tables and relationships
"""
import sqlite3
from datetime import datetime
import json

def init_enhanced_sqlite():
    # Create SQLite database
    conn = sqlite3.connect('test_exam_enhanced.db')
    cursor = conn.cursor()

    # Create all tables (simplified versions for SQLite)
    tables = [
        '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(120) NOT NULL,
            role VARCHAR(20) NOT NULL CHECK (role IN ('admin','teacher','student')),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )''',
        
        '''CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(120) NOT NULL,
            grade VARCHAR(50),
            owner_teacher_id INTEGER REFERENCES users(id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS class_students (
            class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
            student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (class_id, student_id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS knowledge_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject VARCHAR(80) NOT NULL,
            module VARCHAR(120),
            point VARCHAR(200),
            subskill VARCHAR(200),
            code VARCHAR(120) UNIQUE,
            parent_id INTEGER REFERENCES knowledge_points(id),
            level INTEGER CHECK (level >= 1 AND level <= 4)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS questions (
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
        )''',
        
        '''CREATE TABLE IF NOT EXISTS question_knowledge_map (
            question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
            kp_id INTEGER REFERENCES knowledge_points(id) ON DELETE CASCADE,
            PRIMARY KEY (question_id, kp_id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            subject VARCHAR(80),
            grade VARCHAR(50),
            layout_json TEXT,
            qr_schema TEXT,
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )''',
        
        '''CREATE TABLE IF NOT EXISTS paper_questions (
            paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
            question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
            seq INTEGER NOT NULL,
            score REAL NOT NULL DEFAULT 0,
            section VARCHAR(80),
            PRIMARY KEY (paper_id, question_id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS answer_sheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id INTEGER REFERENCES papers(id),
            student_id INTEGER REFERENCES users(id),
            class_id INTEGER REFERENCES classes(id),
            qr_token VARCHAR(120),
            upload_uri TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'uploaded' CHECK (status IN ('uploaded','processed','graded','error')),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )''',
        
        '''CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sheet_id INTEGER REFERENCES answer_sheets(id) ON DELETE CASCADE,
            question_id INTEGER REFERENCES questions(id),
            raw_omr TEXT,
            raw_ocr TEXT,
            parsed_json TEXT,
            spent_ms INTEGER,
            is_objective BOOLEAN DEFAULT TRUE,
            is_correct BOOLEAN,
            score REAL,
            error_flag BOOLEAN DEFAULT FALSE
        )'''
    ]
    
    # Create tables
    for table_sql in tables:
        cursor.execute(table_sql)
    
    # Insert test data
    password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewOyJOxrJAzNx9ae"  # password: password
    
    # Users
    users_data = [
        ('admin@example.com', password_hash, 'Admin', 'admin'),
        ('teacher@example.com', password_hash, 'Teacher Zhang', 'teacher'),
        ('teacher2@example.com', password_hash, 'Teacher Wang', 'teacher'),
        ('student@example.com', password_hash, 'Student Li', 'student'),
        ('student2@example.com', password_hash, 'Student Chen', 'student'),
        ('student3@example.com', password_hash, 'Student Liu', 'student')
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO users (email, password_hash, name, role)
        VALUES (?, ?, ?, ?)
    ''', users_data)
    
    # Classes
    classes_data = [
        ('初一(1)班', '七年级', 2),
        ('初一(2)班', '七年级', 2),
        ('初二(1)班', '八年级', 3)
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO classes (name, grade, owner_teacher_id)
        VALUES (?, ?, ?)
    ''', classes_data)
    
    # Class students
    class_students_data = [
        (1, 4), (1, 5), (1, 6),
        (2, 5), (2, 6),
        (3, 4)
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO class_students (class_id, student_id)
        VALUES (?, ?)
    ''', class_students_data)
    
    # Knowledge points
    kp_data = [
        ('数学', '数论', '质数', '基本概念', 'MATH_NT_PRIME_BASIC', 1),
        ('数学', '数论', '质数', '判定方法', 'MATH_NT_PRIME_METHOD', 2),
        ('数学', '数论', '合数', '分解质因数', 'MATH_NT_COMPOSITE_FACTOR', 2),
        ('数学', '数论', '最大公约数', '辗转相除法', 'MATH_NT_GCD_EUCLIDEAN', 3),
        ('数学', '代数', '一元二次方程', '求根公式', 'MATH_ALG_QUAD_FORMULA', 2),
        ('数学', '代数', '一元二次方程', '配方法', 'MATH_ALG_QUAD_COMPLETE', 2),
        ('数学', '代数', '一元二次方程', '因式分解法', 'MATH_ALG_QUAD_FACTOR', 2),
        ('数学', '代数', '函数', '一次函数', 'MATH_ALG_FUNC_LINEAR', 1),
        ('数学', '代数', '函数', '二次函数', 'MATH_ALG_FUNC_QUADRATIC', 2),
        ('数学', '几何', '三角形', '全等三角形', 'MATH_GEO_TRIANGLE_CONGRUENT', 2),
        ('数学', '几何', '三角形', '相似三角形', 'MATH_GEO_TRIANGLE_SIMILAR', 3),
        ('数学', '几何', '圆', '圆的性质', 'MATH_GEO_CIRCLE_PROPERTY', 2),
        ('语文', '阅读理解', '现代文', '记叙文', 'CHINESE_READING_MODERN_NARRATIVE', 1),
        ('语文', '阅读理解', '现代文', '议论文', 'CHINESE_READING_MODERN_ARGUMENT', 2),
        ('语文', '阅读理解', '现代文', '说明文', 'CHINESE_READING_MODERN_EXPLAIN', 2),
        ('语文', '写作', '记叙文', '叙事技巧', 'CHINESE_WRITING_NARRATIVE_SKILL', 2),
        ('语文', '写作', '议论文', '论证方法', 'CHINESE_WRITING_ARGUMENT_PROOF', 2),
        ('英语', '语法', '时态', '一般现在时', 'ENGLISH_GRAMMAR_TENSE_PRESENT', 1),
        ('英语', '语法', '时态', '一般过去时', 'ENGLISH_GRAMMAR_TENSE_PAST', 1),
        ('英语', '语法', '时态', '现在完成时', 'ENGLISH_GRAMMAR_TENSE_PERFECT', 2),
        ('英语', '词汇', '名词', '可数与不可数', 'ENGLISH_VOCAB_NOUN_COUNTABLE', 1),
        ('英语', '阅读', '理解', '主旨大意', 'ENGLISH_READING_MAIN_IDEA', 2)
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO knowledge_points (subject, module, point, subskill, code, level)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', kp_data)
    
    # Questions
    questions_data = [
        ('下列哪个是质数？', 'single', 2, 
         json.dumps({"A": "4", "B": "9", "C": "11", "D": "15"}),
         json.dumps({"answer": "C"}),
         '质数定义：大于1且仅能被1和自身整除的自然数。11只能被1和11整除，所以是质数。',
         json.dumps({"source": "数学基础练习", "difficulty_level": "基础"}), 2, 'published'),
        
        ('下列哪些是质数？（多选）', 'multiple', 3,
         json.dumps({"A": "2", "B": "3", "C": "4", "D": "5", "E": "6"}),
         json.dumps({"answer": ["A", "B", "D"]}),
         '2、3、5都是质数。4=2×2，6=2×3，都是合数。',
         json.dumps({"source": "数学基础练习", "difficulty_level": "中等"}), 2, 'published'),
        
        ('一元二次方程 x² - 5x + 6 = 0 的解是 ______', 'fill', 2,
         json.dumps({}),
         json.dumps({"answer": "x = 2 或 x = 3"}),
         '利用因式分解：x² - 5x + 6 = (x-2)(x-3) = 0，所以 x = 2 或 x = 3。',
         json.dumps({"source": "代数练习册", "page": 45}), 2, 'published'),
        
        ('一元二次方程求根公式是 ______', 'fill', 3,
         json.dumps({}),
         json.dumps({"answer": "x = [-b ± √(b²-4ac)] / (2a)"}),
         '对于一般形式 ax² + bx + c = 0 (a≠0)，求根公式为 x = [-b ± √(b²-4ac)] / (2a)。',
         json.dumps({"source": "代数教材", "chapter": "二次方程"}), 2, 'published'),
        
        ('判断：所有的矩形都是正方形', 'judge', 1,
         json.dumps({}),
         json.dumps({"answer": False}),
         '矩形的四个角都是直角，但四边不一定相等。只有四边相等的矩形才是正方形。',
         json.dumps({"source": "几何基础"}), 2, 'published'),
        
        ('三角形的内角和是多少度？', 'single', 1,
         json.dumps({"A": "90°", "B": "180°", "C": "270°", "D": "360°"}),
         json.dumps({"answer": "B"}),
         '三角形内角和定理：任意三角形的三个内角和都等于180°。',
         json.dumps({"source": "几何基础"}), 2, 'published'),
        
        ('下列词语中字音全部正确的一组是', 'single', 2,
         json.dumps({"A": "畸形(qí) 纤细(xiān) 拘泥(nì)", "B": "症结(zhēng) 倾轧(yà) 强迫(qiǎng)", "C": "模样(mú) 处理(chǔ) 分外(fèn)", "D": "血泊(pō) 炽热(chì) 埋怨(mán)"}),
         json.dumps({"answer": "D"}),
         'A项：畸形应读jī；B项：症结应读zhèng；C项：分外应读fèn wài。',
         json.dumps({"source": "语文基础训练"}), 2, 'published'),
        
        ('《朝花夕拾》的作者是______', 'fill', 1,
         json.dumps({}),
         json.dumps({"answer": "鲁迅"}),
         '《朝花夕拾》是鲁迅的回忆性散文集，原名《旧事重提》。',
         json.dumps({"source": "文学常识"}), 2, 'published'),
        
        ('I ______ to school every day.', 'single', 1,
         json.dumps({"A": "go", "B": "goes", "C": "going", "D": "went"}),
         json.dumps({"answer": "A"}),
         '主语I是第一人称，在一般现在时中动词用原形。',
         json.dumps({"source": "英语语法练习"}), 2, 'published'),
        
        ('He ______ his homework yesterday.', 'single', 1,
         json.dumps({"A": "do", "B": "does", "C": "did", "D": "doing"}),
         json.dumps({"answer": "C"}),
         'yesterday表示过去时间，要用一般过去时，do的过去式是did。',
         json.dumps({"source": "英语语法练习"}), 2, 'published'),
        
        ('阅读下面的文言文，回答问题：\n\n学而时习之，不亦说乎？有朋自远方来，不亦乐乎？人不知而不愠，不亦君子乎？\n\n请解释这段话的含义并谈谈你的理解。', 'subjective', 4,
         json.dumps({}),
         json.dumps({"points": ["理解原文含义", "结合个人理解", "语言表达"], "total_score": 10}),
         '这是《论语》开篇，体现了孔子关于学习、交友、修养的思想。学生需要准确理解原文并结合自己的体会。',
         json.dumps({"source": "语文阅读理解", "type": "文言文"}), 2, 'published')
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO questions (stem, type, difficulty, options_json, answer_json, analysis, source_meta, created_by, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', questions_data)
    
    # Question knowledge map
    qk_map = [
        (1, 1), (2, 1), (2, 2), (3, 5), (3, 7), (4, 5),
        (5, 10), (6, 10), (7, 13), (8, 13), (9, 18), (10, 19), (11, 14)
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO question_knowledge_map (question_id, kp_id)
        VALUES (?, ?)
    ''', qk_map)
    
    # Papers
    papers_data = [
        ('数学基础测试A卷', '数学', '七年级', 
         json.dumps({"sections": [{"name": "选择题", "type": "single", "count": 3}, {"name": "填空题", "type": "fill", "count": 2}, {"name": "判断题", "type": "judge", "count": 1}]}), 2),
        ('语文综合练习B卷', '语文', '七年级',
         json.dumps({"sections": [{"name": "基础知识", "type": "single", "count": 1}, {"name": "文学常识", "type": "fill", "count": 1}, {"name": "阅读理解", "type": "subjective", "count": 1}]}), 2),
        ('英语语法专项练习', '英语', '七年级',
         json.dumps({"sections": [{"name": "语法选择", "type": "single", "count": 2}]}), 2)
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO papers (name, subject, grade, layout_json, created_by)
        VALUES (?, ?, ?, ?, ?)
    ''', papers_data)
    
    # Paper questions
    pq_data = [
        # 数学基础测试A卷
        (1, 1, 1, 3, '选择题'), (1, 2, 2, 4, '选择题'), (1, 6, 3, 3, '选择题'),
        (1, 3, 4, 5, '填空题'), (1, 4, 5, 6, '填空题'),
        (1, 5, 6, 2, '判断题'),
        # 语文综合练习B卷
        (2, 7, 1, 4, '基础知识'), (2, 8, 2, 3, '文学常识'), (2, 11, 3, 15, '阅读理解'),
        # 英语语法专项练习
        (3, 9, 1, 5, '语法选择'), (3, 10, 2, 5, '语法选择')
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO paper_questions (paper_id, question_id, seq, score, section)
        VALUES (?, ?, ?, ?, ?)
    ''', pq_data)
    
    # Answer sheets (sample data)
    as_data = [
        (1, 4, 1, 'QR_TOKEN_001', '/uploads/sheet_001.jpg', 'uploaded'),
        (1, 5, 1, 'QR_TOKEN_002', '/uploads/sheet_002.jpg', 'processed'),
        (2, 4, 1, 'QR_TOKEN_003', '/uploads/sheet_003.jpg', 'graded')
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO answer_sheets (paper_id, student_id, class_id, qr_token, upload_uri, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', as_data)
    
    # Sample answers
    answers_data = [
        (1, 1, json.dumps({"detected": "C"}), None, json.dumps({"answer": "C"}), True, True, 3),
        (1, 2, json.dumps({"detected": ["A", "B"]}), None, json.dumps({"answer": ["A", "B"]}), True, False, 2),
        (1, 3, None, json.dumps({"text": "x=2或x=3"}), json.dumps({"answer": "x=2或x=3"}), False, True, 5),
        (2, 1, json.dumps({"detected": "C"}), None, json.dumps({"answer": "C"}), True, True, 3),
        (2, 2, json.dumps({"detected": ["A", "B", "D"]}), None, json.dumps({"answer": ["A", "B", "D"]}), True, True, 4),
        (3, 7, json.dumps({"detected": "D"}), None, json.dumps({"answer": "D"}), True, True, 4),
        (3, 8, None, json.dumps({"text": "鲁迅"}), json.dumps({"answer": "鲁迅"}), False, True, 3)
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO answers (sheet_id, question_id, raw_omr, raw_ocr, parsed_json, is_objective, is_correct, score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', answers_data)
    
    conn.commit()
    conn.close()
    
    print("Enhanced SQLite数据库初始化完成！")
    print("数据库文件: test_exam_enhanced.db")
    print("测试用户账号:")
    print("- 管理员: admin@example.com / password")
    print("- 教师1: teacher@example.com / password") 
    print("- 教师2: teacher2@example.com / password")
    print("- 学生1: student@example.com / password")
    print("- 学生2: student2@example.com / password")
    print("- 学生3: student3@example.com / password")
    print("\n数据统计:")
    print("- 用户: 6个")
    print("- 班级: 3个")
    print("- 知识点: 22个")
    print("- 题目: 11道")
    print("- 试卷: 3套")
    print("- 答题记录: 3份")

if __name__ == "__main__":
    init_enhanced_sqlite()
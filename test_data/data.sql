-- Test Users
INSERT INTO users (email, password_hash, name, role) VALUES
('admin@example.com', 'hash_admin', 'Admin', 'admin'),
('t1@example.com', 'hash_t1', 'Teacher Zhang', 'teacher'),
('s1@example.com', 'hash_s1', 'Student Li', 'student');

-- Class
INSERT INTO classes (name, grade, owner_teacher_id) VALUES
('初一(1)班', '七年级', 2);

INSERT INTO class_students (class_id, student_id) VALUES (1, 3);

-- Knowledge Points
INSERT INTO knowledge_points (subject, module, point, subskill, code, level) VALUES
('数学','数论','质数','基本概念','MATH.NT.PRIME',3),
('数学','代数','一元二次方程','求根公式','MATH.ALG.QUAD.FORMULA',4);

-- Questions (simplified)
INSERT INTO questions (stem, type, difficulty, options_json, answer_json, analysis, source_meta, created_by, status) VALUES
('下列哪个是质数？','single',2, '["A. 9","B. 11","C. 15","D. 21"]', '{"choice":"B"}', '质数定义：仅能被1和自身整除。', '{"source":"样例"}', 2, 'published'),
('一元二次方程求根公式是？','fill',3, NULL, '{"text":"x=[-b±√(b^2-4ac)]/(2a)"}', '标准求根公式。', '{"source":"样例"}', 2, 'published');

-- Map KPs
INSERT INTO question_knowledge_map (question_id, kp_id) VALUES (1, 1), (2, 2);

-- Paper
INSERT INTO papers (name, subject, grade, created_by) VALUES ('数学样例试卷A', '数学', '七年级', 2);

INSERT INTO paper_questions (paper_id, question_id, seq, score, section) VALUES
(1, 1, 1, 2, '选择题'),
(1, 2, 2, 5, '填空题');

-- Smart Exam System - 完整测试数据
-- 包含用户/班级、知识点、题库、试卷与题目映射的初始化数据

-- 清理现有数据（可选）
-- TRUNCATE TABLE question_knowledge_map, paper_questions, papers, questions, knowledge_points, class_students, classes, users RESTART IDENTITY CASCADE;

-- ===========================================
-- 1. 测试用户数据
-- ===========================================
INSERT INTO users (email, password_hash, name, role) VALUES
('admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewOyJOxrJAzNx9ae', 'Admin', 'admin'),
('teacher@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewOyJOxrJAzNx9ae', 'Teacher Zhang', 'teacher'),
('teacher2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewOyJOxrJAzNx9ae', 'Teacher Wang', 'teacher'),
('student@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewOyJOxrJAzNx9ae', 'Student Li', 'student'),
('student2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewOyJOxrJAzNx9ae', 'Student Chen', 'student'),
('student3@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewOyJOxrJAzNx9ae', 'Student Liu', 'student');

-- ===========================================
-- 2. 班级数据
-- ===========================================
INSERT INTO classes (name, grade, owner_teacher_id) VALUES
('初一(1)班', '七年级', 2),
('初一(2)班', '七年级', 2),
('初二(1)班', '八年级', 3);

INSERT INTO class_students (class_id, student_id) VALUES 
(1, 4), (1, 5), (1, 6),
(2, 5), (2, 6),
(3, 4);

-- ===========================================
-- 3. 知识点体系（树形结构）
-- ===========================================
INSERT INTO knowledge_points (subject, module, point, subskill, code, level) VALUES
-- 数学 - 数论
('数学', '数论', '质数', '基本概念', 'MATH_NT_PRIME_BASIC', 1),
('数学', '数论', '质数', '判定方法', 'MATH_NT_PRIME_METHOD', 2),
('数学', '数论', '合数', '分解质因数', 'MATH_NT_COMPOSITE_FACTOR', 2),
('数学', '数论', '最大公约数', '辗转相除法', 'MATH_NT_GCD_EUCLIDEAN', 3),

-- 数学 - 代数
('数学', '代数', '一元二次方程', '求根公式', 'MATH_ALG_QUAD_FORMULA', 2),
('数学', '代数', '一元二次方程', '配方法', 'MATH_ALG_QUAD_COMPLETE', 2),
('数学', '代数', '一元二次方程', '因式分解法', 'MATH_ALG_QUAD_FACTOR', 2),
('数学', '代数', '函数', '一次函数', 'MATH_ALG_FUNC_LINEAR', 1),
('数学', '代数', '函数', '二次函数', 'MATH_ALG_FUNC_QUADRATIC', 2),

-- 数学 - 几何
('数学', '几何', '三角形', '全等三角形', 'MATH_GEO_TRIANGLE_CONGRUENT', 2),
('数学', '几何', '三角形', '相似三角形', 'MATH_GEO_TRIANGLE_SIMILAR', 3),
('数学', '几何', '圆', '圆的性质', 'MATH_GEO_CIRCLE_PROPERTY', 2),

-- 语文
('语文', '阅读理解', '现代文', '记叙文', 'CHINESE_READING_MODERN_NARRATIVE', 1),
('语文', '阅读理解', '现代文', '议论文', 'CHINESE_READING_MODERN_ARGUMENT', 2),
('语文', '阅读理解', '现代文', '说明文', 'CHINESE_READING_MODERN_EXPLAIN', 2),
('语文', '写作', '记叙文', '叙事技巧', 'CHINESE_WRITING_NARRATIVE_SKILL', 2),
('语文', '写作', '议论文', '论证方法', 'CHINESE_WRITING_ARGUMENT_PROOF', 2),

-- 英语
('英语', '语法', '时态', '一般现在时', 'ENGLISH_GRAMMAR_TENSE_PRESENT', 1),
('英语', '语法', '时态', '一般过去时', 'ENGLISH_GRAMMAR_TENSE_PAST', 1),
('英语', '语法', '时态', '现在完成时', 'ENGLISH_GRAMMAR_TENSE_PERFECT', 2),
('英语', '词汇', '名词', '可数与不可数', 'ENGLISH_VOCAB_NOUN_COUNTABLE', 1),
('英语', '阅读', '理解', '主旨大意', 'ENGLISH_READING_MAIN_IDEA', 2);

-- ===========================================
-- 4. 题目数据（覆盖各种题型）
-- ===========================================
INSERT INTO questions (stem, type, difficulty, options_json, answer_json, analysis, source_meta, created_by, status) VALUES
-- 数学题目
('下列哪个是质数？', 'single', 2, 
 '{"A": "4", "B": "9", "C": "11", "D": "15"}', 
 '{"answer": "C"}', 
 '质数定义：大于1且仅能被1和自身整除的自然数。11只能被1和11整除，所以是质数。', 
 '{"source": "数学基础练习", "difficulty_level": "基础"}', 2, 'published'),

('下列哪些是质数？（多选）', 'multiple', 3,
 '{"A": "2", "B": "3", "C": "4", "D": "5", "E": "6"}',
 '{"answer": ["A", "B", "D"]}',
 '2、3、5都是质数。4=2×2，6=2×3，都是合数。',
 '{"source": "数学基础练习", "difficulty_level": "中等"}', 2, 'published'),

('一元二次方程 x² - 5x + 6 = 0 的解是 ______', 'fill', 2,
 '{}',
 '{"answer": "x = 2 或 x = 3"}',
 '利用因式分解：x² - 5x + 6 = (x-2)(x-3) = 0，所以 x = 2 或 x = 3。',
 '{"source": "代数练习册", "page": 45}', 2, 'published'),

('一元二次方程求根公式是 ______', 'fill', 3,
 '{}',
 '{"answer": "x = [-b ± √(b²-4ac)] / (2a)"}',
 '对于一般形式 ax² + bx + c = 0 (a≠0)，求根公式为 x = [-b ± √(b²-4ac)] / (2a)。',
 '{"source": "代数教材", "chapter": "二次方程"}', 2, 'published'),

('判断：所有的矩形都是正方形', 'judge', 1,
 '{}',
 '{"answer": false}',
 '矩形的四个角都是直角，但四边不一定相等。只有四边相等的矩形才是正方形。',
 '{"source": "几何基础"}', 2, 'published'),

('三角形的内角和是多少度？', 'single', 1,
 '{"A": "90°", "B": "180°", "C": "270°", "D": "360°"}',
 '{"answer": "B"}',
 '三角形内角和定理：任意三角形的三个内角和都等于180°。',
 '{"source": "几何基础"}', 2, 'published'),

-- 语文题目
('下列词语中字音全部正确的一组是', 'single', 2,
 '{"A": "畸形(qí) 纤细(xiān) 拘泥(nì)", "B": "症结(zhēng) 倾轧(yà) 强迫(qiǎng)", "C": "模样(mú) 处理(chǔ) 分外(fèn)", "D": "血泊(pō) 炽热(chì) 埋怨(mán)"}',
 '{"answer": "D"}',
 'A项：畸形应读jī；B项：症结应读zhèng；C项：分外应读fèn wài。',
 '{"source": "语文基础训练"}', 2, 'published'),

('《朝花夕拾》的作者是______', 'fill', 1,
 '{}',
 '{"answer": "鲁迅"}',
 '《朝花夕拾》是鲁迅的回忆性散文集，原名《旧事重提》。',
 '{"source": "文学常识"}', 2, 'published'),

-- 英语题目
('I ______ to school every day.', 'single', 1,
 '{"A": "go", "B": "goes", "C": "going", "D": "went"}',
 '{"answer": "A"}',
 '主语I是第一人称，在一般现在时中动词用原形。',
 '{"source": "英语语法练习"}', 2, 'published'),

('He ______ his homework yesterday.', 'single', 1,
 '{"A": "do", "B": "does", "C": "did", "D": "doing"}',
 '{"answer": "C"}',
 'yesterday表示过去时间，要用一般过去时，do的过去式是did。',
 '{"source": "英语语法练习"}', 2, 'published'),

-- 主观题示例
('阅读下面的文言文，回答问题：\n\n学而时习之，不亦说乎？有朋自远方来，不亦乐乎？人不知而不愠，不亦君子乎？\n\n请解释这段话的含义并谈谈你的理解。', 'subjective', 4,
 '{}',
 '{"points": ["理解原文含义", "结合个人理解", "语言表达"], "total_score": 10}',
 '这是《论语》开篇，体现了孔子关于学习、交友、修养的思想。学生需要准确理解原文并结合自己的体会。',
 '{"source": "语文阅读理解", "type": "文言文"}', 2, 'published');

-- ===========================================
-- 5. 题目与知识点映射
-- ===========================================
INSERT INTO question_knowledge_map (question_id, kp_id) VALUES
(1, 1), -- 质数单选 -> 质数基本概念
(2, 1), (2, 2), -- 质数多选 -> 质数基本概念+判定方法
(3, 5), (3, 7), -- 二次方程解 -> 求根公式+因式分解法
(4, 5), -- 求根公式 -> 求根公式
(5, 10), -- 矩形判断 -> 全等三角形
(6, 10), -- 三角形内角和 -> 三角形相关
(7, 13), -- 语文字音 -> 现代文基础
(8, 13), -- 文学常识 -> 现代文基础
(9, 18), -- 英语一般现在时 -> 一般现在时
(10, 19), -- 英语过去时 -> 一般过去时
(11, 14); -- 文言文阅读 -> 议论文理解

-- ===========================================
-- 6. 试卷数据
-- ===========================================
INSERT INTO papers (name, subject, grade, layout_json, created_by) VALUES
('数学基础测试A卷', '数学', '七年级', 
 '{"sections": [{"name": "选择题", "type": "single", "count": 3}, {"name": "填空题", "type": "fill", "count": 2}, {"name": "判断题", "type": "judge", "count": 1}]}', 2),
 
('语文综合练习B卷', '语文', '七年级',
 '{"sections": [{"name": "基础知识", "type": "single", "count": 1}, {"name": "文学常识", "type": "fill", "count": 1}, {"name": "阅读理解", "type": "subjective", "count": 1}]}', 2),

('英语语法专项练习', '英语', '七年级',
 '{"sections": [{"name": "语法选择", "type": "single", "count": 2}]}', 2);

-- ===========================================
-- 7. 试卷题目映射
-- ===========================================
INSERT INTO paper_questions (paper_id, question_id, seq, score, section) VALUES
-- 数学基础测试A卷
(1, 1, 1, 3, '选择题'),
(1, 2, 2, 4, '选择题'), 
(1, 6, 3, 3, '选择题'),
(1, 3, 4, 5, '填空题'),
(1, 4, 5, 6, '填空题'),
(1, 5, 6, 2, '判断题'),

-- 语文综合练习B卷
(2, 7, 1, 4, '基础知识'),
(2, 8, 2, 3, '文学常识'),
(2, 11, 3, 15, '阅读理解'),

-- 英语语法专项练习
(3, 9, 1, 5, '语法选择'),
(3, 10, 2, 5, '语法选择');

-- ===========================================
-- 8. 试卷版本（PDF生成记录）
-- ===========================================
INSERT INTO paper_versions (paper_id, version_no, pdf_uri, checksum) VALUES
(1, 1, '/papers/math_test_a_v1.pdf', 'md5_hash_example_123'),
(2, 1, '/papers/chinese_test_b_v1.pdf', 'md5_hash_example_456'),
(3, 1, '/papers/english_grammar_v1.pdf', 'md5_hash_example_789');

-- ===========================================
-- 9. 模拟答题记录（用于测试）
-- ===========================================
INSERT INTO answer_sheets (paper_id, student_id, class_id, qr_token, upload_uri, status) VALUES
(1, 4, 1, 'QR_TOKEN_001', '/uploads/sheet_001.jpg', 'uploaded'),
(1, 5, 1, 'QR_TOKEN_002', '/uploads/sheet_002.jpg', 'processed'),
(2, 4, 1, 'QR_TOKEN_003', '/uploads/sheet_003.jpg', 'graded');

INSERT INTO answers (sheet_id, question_id, raw_omr, raw_ocr, parsed_json, is_objective, is_correct, score) VALUES
-- 学生4的数学答题
(1, 1, '{"detected": "C"}', null, '{"answer": "C"}', true, true, 3),
(1, 2, '{"detected": ["A", "B"]}', null, '{"answer": ["A", "B"]}', true, false, 2),
(1, 3, null, '{"text": "x=2或x=3"}', '{"answer": "x=2或x=3"}', false, true, 5),

-- 学生5的数学答题
(2, 1, '{"detected": "C"}', null, '{"answer": "C"}', true, true, 3),
(2, 2, '{"detected": ["A", "B", "D"]}', null, '{"answer": ["A", "B", "D"]}', true, true, 4),

-- 学生4的语文答题
(3, 7, '{"detected": "D"}', null, '{"answer": "D"}', true, true, 4),
(3, 8, null, '{"text": "鲁迅"}', '{"answer": "鲁迅"}', false, true, 3);

-- ===========================================
-- 10. 数据质量检查记录
-- ===========================================
INSERT INTO data_quality_issues (sheet_id, question_id, issue_code, detail, severity) VALUES
(1, 2, 'OMR_UNCLEAR', '选项B识别不清晰，置信度较低', 'medium'),
(3, 11, 'OCR_HANDWRITING', '手写字迹识别困难，需人工核对', 'high');

-- 完成提示
SELECT 'Test data imported successfully! 测试数据导入完成！' as status;

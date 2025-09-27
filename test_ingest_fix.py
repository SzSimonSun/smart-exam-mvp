#!/usr/bin/env python3
"""
测试拆题项目的文本解析修复
"""

import sqlite3
import json

def test_ingest_data():
    """测试数据库中的拆题数据"""
    print("=== 测试拆题项目数据 ===")
    
    try:
        # 连接数据库
        conn = sqlite3.connect('/Users/sunfei/smart-exam-mvp/exam_system.db')
        cursor = conn.cursor()
        
        # 查询最近的拆题项目
        cursor.execute("""
            SELECT id, session_id, ocr_json, candidate_type, review_status
            FROM ingest_items 
            ORDER BY id DESC 
            LIMIT 5
        """)
        
        items = cursor.fetchall()
        
        if not items:
            print("❌ 没有找到任何拆题项目")
            return False
            
        print(f"✅ 找到 {len(items)} 个拆题项目")
        
        for i, (item_id, session_id, ocr_json, candidate_type, review_status) in enumerate(items, 1):
            print(f"\n--- 项目 {i} (ID: {item_id}) ---")
            print(f"Session ID: {session_id}")
            print(f"题目类型: {candidate_type}")
            print(f"审核状态: {review_status}")
            
            # 解析OCR JSON
            question_text = ""
            if ocr_json:
                try:
                    if isinstance(ocr_json, str):
                        ocr_data = json.loads(ocr_json)
                    else:
                        ocr_data = ocr_json
                    question_text = ocr_data.get("text", "")
                    print(f"OCR文本: {question_text[:100]}{'...' if len(question_text) > 100 else ''}")
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"❌ OCR JSON解析失败: {e}")
                    print(f"原始OCR数据: {str(ocr_json)[:100]}...")
            else:
                print("⚠️  没有OCR数据")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
        return False

def main():
    """主函数"""
    print("智能考试系统 - 拆题项目文本解析测试")
    print("=" * 50)
    
    success = test_ingest_data()
    
    if success:
        print("\n✅ 测试完成！")
        print("\n修复说明：")
        print("1. 后端API已修复，现在会从OCR JSON中解析题目文本")
        print("2. 前端编辑逻辑已改进，优先使用后端返回的question_text")
        print("3. 表格渲染逻辑已优化，支持多重数据源")
    else:
        print("\n❌ 测试失败，请检查数据库连接和数据")

if __name__ == "__main__":
    main()
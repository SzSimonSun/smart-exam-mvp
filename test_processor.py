#!/usr/bin/env python3
"""
直接测试文档处理器
"""

import sys
import os
sys.path.append('/Users/sunfei/smart-exam-mvp/backend')

from app.services.real_document_processor import DocumentProcessor

# 测试文档处理器
print("测试文档处理器...")

with open('/Users/sunfei/smart-exam-mvp/test_paper.pdf', 'rb') as f:
    content = f.read()

processor = DocumentProcessor()
try:
    result = processor.process_document(content, 'application/pdf', 'test_paper.pdf')
    print(f"✅ 处理成功: {result['success']}")
    if result['success']:
        print(f"文件类型: {result['file_type']}")
        print(f"题目数量: {len(result['items'])}")
        for i, item in enumerate(result['items']):
            print(f"题目{i+1}:")
            print(f"  序号: {item['seq']}")
            print(f"  类型: {item['question_type']}")
            print(f"  置信度: {item['confidence']}")
            print(f"  文本: {item['question_text'][:100]}...")
            print()
    else:
        print(f"❌ 处理失败: {result.get('error')}")
        
except Exception as e:
    print(f"❌ 异常: {e}")
    import traceback
    traceback.print_exc()
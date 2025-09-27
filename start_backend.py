#!/usr/bin/env python3
"""
后端服务启动脚本
"""

import uvicorn
import sys
import os

# 添加backend目录到Python路径
backend_dir = os.path.dirname(os.path.abspath(__file__))
if 'backend' not in backend_dir:
    backend_dir = os.path.join(backend_dir, 'backend')
sys.path.insert(0, backend_dir)

def start_server():
    """启动后端服务"""
    print("🚀 正在启动智能考试系统后端服务...")
    print(f"📁 工作目录: {backend_dir}")
    
    try:
        # 测试导入
        from app.main import app
        print("✅ 应用模块导入成功")
        
        from app.database import engine
        print("✅ 数据库引擎创建成功")
        
        # 启动服务
        print("🔗 启动服务: http://127.0.0.1:8001")
        
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8001,
            reload=False,  # 禁用reload避免不稳定
            access_log=True,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # 切换到backend目录
    os.chdir(backend_dir)
    start_server()
#!/bin/bash

# 智能试卷系统 - 启动脚本
echo "🚀 正在启动智能试卷系统..."

# 终止现有进程
echo "📛 停止现有服务..."
pkill -f "uvicorn.*app.main:app" 2>/dev/null
pkill -f "vite.*frontend_vite" 2>/dev/null
sleep 2

# 启动后端 (FastAPI)
echo "🔧 启动后端服务 (FastAPI) - http://localhost:8000"
cd backend && nohup python3 -m uvicorn app.main:app --reload --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端 (Vite + React)
echo "🌐 启动前端服务 (Vite + React) - http://localhost:5173"
cd ../frontend_vite && nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# 等待前端启动
sleep 5

# 检查服务状态
echo ""
echo "📊 检查服务状态..."

# 检查后端
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ 后端服务正常 - http://localhost:8000"
else
    echo "❌ 后端服务启动失败"
fi

# 检查前端
if curl -s http://localhost:5173 >/dev/null; then
    echo "✅ 前端服务正常 - http://localhost:5173"
else
    echo "❌ 前端服务启动失败"
fi

echo ""
echo "🎉 智能试卷系统启动完成！"
echo "🌐 前端访问地址: http://localhost:5173"
echo "🔧 后端API地址: http://localhost:8000"
echo "📋 后端API文档: http://localhost:8000/docs"
echo ""
echo "💡 要停止服务，请运行: ./stop.sh"
echo "📝 查看日志: tail -f backend/backend.log 或 tail -f frontend_vite/frontend.log"
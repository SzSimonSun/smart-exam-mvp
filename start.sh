#!/bin/bash

# 智能考试系统启动脚本
# 使用PID文件管理进程，确保可靠的启停控制

PID_DIR=".pids"
BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"

echo "正在启动智能考试系统..."

# 检查是否在正确的目录
if [ ! -f "backend/app/main.py" ] || [ ! -f "frontend_vite/package.json" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 创建PID目录
mkdir -p "$PID_DIR"

# 清理端口函数
cleanup_ports() {
    echo "🔧 检查并清理端口占用..."
    
    # 检查5173端口
    if lsof -i :5173 >/dev/null 2>&1; then
        echo "端口5173被占用，正在清理..."
        lsof -ti :5173 | xargs kill -9 2>/dev/null || true
    fi
    
    # 检查5174端口（备用端口）
    if lsof -i :5174 >/dev/null 2>&1; then
        echo "端口5174被占用，正在清理..."
        lsof -ti :5174 | xargs kill -9 2>/dev/null || true
    fi
    
    # 检查8000端口
    if lsof -i :8000 >/dev/null 2>&1; then
        echo "端口8000被占用，正在清理..."
        lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    fi
    
    sleep 2
    echo "✅ 端口清理完成"
}

# 停止旧服务
echo "🛑 停止旧服务..."
./stop.sh 2>/dev/null || true
sleep 1

# 清理端口
cleanup_ports

# 启动后端服务
echo "🚀 启动后端服务..."
cd backend

# 激活虚拟环境
if [ -f "../.venv/bin/activate" ]; then
    source ../.venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "⚠️  警告：未找到虚拟环境，使用系统Python"
fi

# 确保PID目录存在
mkdir -p "../$PID_DIR"

# 启动后端
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "../$BACKEND_PID_FILE"
echo "✅ 后端服务已启动，PID: $BACKEND_PID"
cd ..

# 等待后端服务启动
echo "⏳ 等待后端服务就绪..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ 后端服务已就绪"
        break
    fi
    sleep 1
    echo "等待中... ($i/10)"
done

# 启动前端服务
echo "🚀 启动前端服务..."
cd frontend_vite

# 确保PID目录存在
mkdir -p "../$PID_DIR"

# 确保强制使用5173端口
nohup npm run dev -- --port 5173 --host 0.0.0.0 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "../$FRONTEND_PID_FILE"
echo "✅ 前端服务已启动，PID: $FRONTEND_PID"
cd ..

# 等待前端服务启动
echo "⏳ 等待前端服务就绪..."
for i in {1..15}; do
    if curl -s http://localhost:5173 >/dev/null 2>&1; then
        echo "✅ 前端服务已就绪"
        break
    fi
    sleep 1
    echo "等待中... ($i/15)"
done

echo ""
echo "================================"
echo "🎉 智能考试系统启动完成！"
echo "🌐 前端地址: http://localhost:5173"
echo "🔧 后端地址: http://localhost:8000"
echo "📋 后端文档: http://localhost:8000/docs"
echo "================================"
echo ""
echo "📊 服务状态:"
echo "后端PID: $BACKEND_PID (保存在 $BACKEND_PID_FILE)"
echo "前端PID: $FRONTEND_PID (保存在 $FRONTEND_PID_FILE)"
echo ""
echo "💡 使用命令:"
echo "  ./stop.sh          - 停止所有服务"
echo "  tail -f backend.log  - 查看后端日志"
echo "  tail -f frontend.log - 查看前端日志"
echo "  lsof -i :5173      - 检查前端端口"
echo "  lsof -i :8000      - 检查后端端口"
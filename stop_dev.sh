#!/bin/bash

# 智能考试系统开发环境停止脚本
echo "🛑 停止智能考试系统开发环境..."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 停止前端 (Vite)
echo "停止前端服务器..."
pkill -f "vite" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 前端服务器已停止${NC}"
else
    echo -e "${YELLOW}ℹ️  前端服务器未在运行${NC}"
fi

# 停止后端 (uvicorn)
echo "停止后端服务器..."
pkill -f "uvicorn" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 后端服务器已停止${NC}"
else
    echo -e "${YELLOW}ℹ️  后端服务器未在运行${NC}"
fi

# 等待进程完全停止
sleep 2

# 检查端口是否释放
if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 && ! lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}🎉 所有服务已成功停止${NC}"
else
    echo -e "${YELLOW}⚠️  一些端口可能仍被占用，请手动检查${NC}"
    echo "检查端口占用："
    echo "- 后端端口 8000: lsof -i :8000"
    echo "- 前端端口 5173: lsof -i :5173"
fi
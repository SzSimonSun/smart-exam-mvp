#!/bin/bash

# 智能试卷系统 - 停止脚本
echo "🛑 正在停止智能试卷系统..."

# 停止后端服务
echo "📛 停止后端服务..."
pkill -f "uvicorn.*app.main:app"

# 停止前端服务  
echo "📛 停止前端服务..."
pkill -f "vite.*frontend_vite"
pkill -f "npm run dev"

sleep 2

echo "✅ 智能试卷系统已停止"
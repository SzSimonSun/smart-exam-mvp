# Worker服务启动脚本 (PowerShell)

Write-Host "=== 智能试卷系统 Worker 服务启动 ===" -ForegroundColor Green

# 检查Docker是否运行
$dockerRunning = docker info 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: Docker未运行，请先启动Docker" -ForegroundColor Red
    exit 1
}

# 检查基础服务是否运行
Write-Host "检查基础服务状态..." -ForegroundColor Yellow

$services = @("postgres", "redis", "rabbitmq", "minio")
foreach ($service in $services) {
    $container = docker ps --filter "name=$service" --format "{{.Names}}" | Select-String $service
    if (-not $container) {
        Write-Host "警告: $service 服务未运行" -ForegroundColor Red
    } else {
        Write-Host "✓ $service 服务运行正常" -ForegroundColor Green
    }
}

# 安装Worker依赖
Write-Host "`n安装Worker依赖包..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot"

if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 依赖安装完成" -ForegroundColor Green
    } else {
        Write-Host "错误: 依赖安装失败" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "警告: requirements.txt 文件不存在" -ForegroundColor Yellow
}

# 提供启动选项
Write-Host "`n请选择启动方式:" -ForegroundColor Cyan
Write-Host "1. 启动所有Worker (推荐)"
Write-Host "2. 启动OCR Worker"
Write-Host "3. 启动AutoGrade Worker"
Write-Host "4. 启动Ingest Worker"
Write-Host "5. 测试Worker服务"
Write-Host "6. 退出"

$choice = Read-Host "请输入选择 (1-6)"

switch ($choice) {
    "1" {
        Write-Host "`n启动所有Worker服务..." -ForegroundColor Green
        
        # 启动OCR Worker
        Start-Process pwsh -ArgumentList "-Command", "& { $env:WORKER_TYPE='ocr'; python worker_startup.py }" -WindowStyle Normal
        Start-Sleep 2
        
        # 启动AutoGrade Worker
        Start-Process pwsh -ArgumentList "-Command", "& { $env:WORKER_TYPE='autograde'; python worker_startup.py }" -WindowStyle Normal
        Start-Sleep 2
        
        # 启动Ingest Worker
        Start-Process pwsh -ArgumentList "-Command", "& { $env:WORKER_TYPE='ingest'; python worker_startup.py }" -WindowStyle Normal
        
        Write-Host "✓ 所有Worker服务已启动" -ForegroundColor Green
        Write-Host "注意: 每个Worker在独立窗口中运行" -ForegroundColor Yellow
    }
    "2" {
        Write-Host "`n启动OCR Worker..." -ForegroundColor Green
        $env:WORKER_TYPE = "ocr"
        python worker_startup.py
    }
    "3" {
        Write-Host "`n启动AutoGrade Worker..." -ForegroundColor Green
        $env:WORKER_TYPE = "autograde"
        python worker_startup.py
    }
    "4" {
        Write-Host "`n启动Ingest Worker..." -ForegroundColor Green
        $env:WORKER_TYPE = "ingest"
        python worker_startup.py
    }
    "5" {
        Write-Host "`n测试Worker服务..." -ForegroundColor Green
        python test_workers.py
    }
    "6" {
        Write-Host "退出" -ForegroundColor Yellow
        exit 0
    }
    default {
        Write-Host "无效选择，退出" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
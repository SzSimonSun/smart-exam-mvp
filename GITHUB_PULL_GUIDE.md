# 📥 从GitHub获取最新代码指南

## 🔄 获取最新分支的几种方式

### 方式一：拉取当前分支的最新更新 (推荐)
```bash
# 获取最新的远程信息
git fetch origin

# 拉取并合并最新的main分支代码
git pull origin main

# 或者使用简化命令 (如果已设置上游分支)
git pull
```

### 方式二：重置到远程分支的最新状态
```bash
# 强制同步到远程分支 (会丢失本地未提交的更改!)
git fetch origin
git reset --hard origin/main
```

### 方式三：创建新的分支跟踪远程分支
```bash
# 查看所有远程分支
git branch -r

# 创建并切换到新分支，跟踪远程分支
git checkout -b feature-branch origin/feature-branch
```

## 📋 常用Git命令

### 查看状态和分支
```bash
# 查看当前状态
git status

# 查看所有分支 (本地和远程)
git branch -a

# 查看远程仓库信息
git remote -v

# 查看提交历史
git log --oneline -10
```

### 同步远程信息
```bash
# 获取远程仓库的最新信息 (不合并)
git fetch origin

# 查看远程分支状态
git remote show origin

# 比较本地和远程分支的差异
git diff main origin/main
```

### 处理冲突
```bash
# 如果拉取时出现冲突，查看冲突文件
git status

# 手动解决冲突后，添加文件
git add <解决冲突的文件>

# 完成合并
git commit
```

## 🚨 重要注意事项

### 1. 保存本地更改
在拉取最新代码之前，确保保存本地更改：
```bash
# 暂存本地更改
git stash

# 拉取最新代码
git pull origin main

# 恢复本地更改
git stash pop
```

### 2. 检查工作目录状态
```bash
# 确保工作目录干净
git status

# 如果有未提交的更改，先提交或暂存
git add .
git commit -m "保存本地更改"
```

### 3. 分支管理
```bash
# 查看当前分支
git branch

# 切换分支
git checkout main

# 创建新分支
git checkout -b new-feature
```

## 📊 当前项目状态

### 最新提交历史
```
651e1c3 - docs: 添加GitHub上传成功报告
5620106 - docs: 更新README文档  
6a70c30 - feat: 实现完整的登录功能和前后端集成
84b968a - 初始提交：智能试卷系统MVP版本
```

### 远程仓库
- **URL**: https://github.com/SzSimonSun/smart-exam-mvp.git
- **主分支**: main
- **状态**: 已同步

## 🔧 故障排除

### 问题1: 拉取失败
```bash
# 如果网络问题导致拉取失败，重试
git pull origin main

# 如果持续失败，检查网络和GitHub连接
ping github.com
```

### 问题2: 合并冲突
```bash
# 查看冲突文件
git status

# 使用编辑器解决冲突后
git add <文件名>
git commit
```

### 问题3: 本地分支落后
```bash
# 查看本地分支与远程分支的差异
git log --oneline main..origin/main

# 强制更新到最新状态
git reset --hard origin/main
```

## 🎯 最佳实践

1. **定期同步**: 每天开始工作前执行 `git pull`
2. **提交频率**: 经常提交小的更改，避免大量冲突
3. **分支策略**: 使用功能分支开发，定期合并到主分支
4. **备份重要更改**: 重要更改及时推送到远程仓库

## 📝 快速操作示例

```bash
# 每日工作流程
cd /path/to/smart-exam-mvp
git status                    # 检查状态
git pull origin main         # 获取最新代码
# ... 进行开发工作 ...
git add .                     # 暂存更改
git commit -m "描述更改"      # 提交更改
git push origin main         # 推送到远程仓库
```

---

**💡 提示**: 使用这些命令时，确保您在正确的项目目录中，并且有网络连接到GitHub。
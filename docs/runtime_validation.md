# 最新版后端运行性检查

## 环境
- Python 3.12.10（容器内默认运行环境）
- 未启动任何 docker-compose 中定义的依赖服务（PostgreSQL、Redis、MinIO、RabbitMQ）

## 检查步骤
1. 通过 `uvicorn backend.app.main:app` 启动 FastAPI 应用，确认应用可以完成启动流程。
2. 调用 `/health` 接口确认基础路由可访问。
3. 调用 `/api/auth/login` 以最常用的登录流程验证数据库连接是否正常。

## 发现
- `/health` 正常返回，说明应用实例本身可以在无外部依赖时启动。
- 登录接口报 500，日志显示 `psycopg2.OperationalError: could not translate host name "postgres" to address`，表明默认配置直接连接 docker-compose 内的 PostgreSQL 服务，在本地未运行对应容器时会立即失败。
- 由于 `database_url` 默认值写死为 `postgresql://exam:exam@postgres:5432/examdb`，在未部署依赖时，任何需要数据库的接口都会异常退出。【F:backend/app/config.py†L1-L38】
- 上传答题卡会在 `store_answer_sheet_file` 内创建 MinIO 客户端并检查 bucket；默认 `minio:9000` 同样依赖 docker-compose 提供的服务，在未启动 MinIO 时会抛出 `RuntimeError("Unable to prepare storage bucket")`，因此即便数据库问题解决，上传功能仍需额外的对象存储服务。【F:backend/app/storage.py†L21-L77】

## 结论
- 目前代码在没有 docker-compose 依赖服务的环境下无法完成核心业务流程。
- 要在开发或测试环境运行，需要：
  1. 启动 `docker-compose` 中的 PostgreSQL、Redis、MinIO 等服务，或
  2. 调整配置使用本地可用的替代服务（例如改用 SQLite、禁用 MinIO 上传）。

## 附录：关键日志
```
psycopg2.OperationalError: could not translate host name "postgres" to address: Name or service not known
```
【bcc057†L1-L134】

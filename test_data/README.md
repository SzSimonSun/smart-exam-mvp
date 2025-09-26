# 测试数据导入

## 方式一：SQL
```bash
docker cp test_data/data.sql smart_exam_pg:/data.sql
docker exec -it smart_exam_pg psql -U exam -d examdb -f /data.sql
```

## 方式二：CSV（容器内 COPY）
> 需要在容器中创建可访问目录并执行 COPY。
```sql
-- 在容器 psql 中执行：
COPY knowledge_points(subject,module,point,subskill,code,level)
FROM '/var/lib/postgresql/knowledge_points.csv' DELIMITER ',' CSV HEADER;

COPY questions(stem,type,difficulty,options_json,answer_json,analysis,source_meta,status)
FROM '/var/lib/postgresql/questions.csv' DELIMITER ',' CSV HEADER;
```

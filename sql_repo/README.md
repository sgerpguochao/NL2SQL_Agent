# sql_repo - SQLite3 测试数据库

本目录提供独立的 SQLite3 初始化脚本，用于生成供测试使用的示例数据库，无需依赖主项目后端。

## 数据库路径

- **文件**: `sql_repo/data/test.db`
- 首次运行 `init_db.py` 时会自动创建 `data` 目录及数据库文件。

## 表结构（与主项目示例库一致）

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| departments | 部门 | id, name, manager, budget, created_at |
| employees | 员工 | id, name, department_id, position, salary, hire_date |
| products | 产品 | id, name, category, price, stock |
| sales | 销售记录 | id, employee_id, product_id, amount, quantity, sale_date |

## 使用方法

在项目根目录或 `sql_repo` 目录下执行：

```bash
# 首次创建或数据库不存在时初始化
python sql_repo/init_db.py

# 强制重建（删除已有 test.db 后重新创建）
python sql_repo/init_db.py --force
```

或进入 sql_repo 后：

```bash
cd sql_repo
python init_db.py
python init_db.py --force   # 重建
```

## 用于主项目测试

若希望主项目后端使用本库进行测试，可将 `backend/.env` 中的 `DB_PATH` 改为指向本库的**绝对路径**，例如：

- Windows: `DB_PATH=G:/nl2sql_agent/sql_repo/data/test.db`
- 或复制 `sql_repo/data/test.db` 到 `backend/data/business.db` 后启动后端。

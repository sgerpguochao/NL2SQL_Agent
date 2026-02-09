"""
示例数据初始化 - 创建销售业务示例数据库
包含：departments（部门）、employees（员工）、sales（销售记录）、products（产品）
"""

import os
import sqlite3
from app.config import get_settings


def init_sample_database():
    """
    初始化示例数据库，如果数据库已存在则跳过。
    调用此函数会在 DB_PATH 位置创建 SQLite 数据库并填充示例数据。
    """
    settings = get_settings()
    db_path = settings.DB_PATH

    # 确保目录存在
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    # 如果数据库已存在且非空，跳过初始化
    if os.path.exists(db_path) and os.path.getsize(db_path) > 0:
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ---- 部门表 ----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            manager TEXT,
            budget REAL,
            created_at TEXT DEFAULT (date('now'))
        )
    """)

    # ---- 员工表 ----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department_id INTEGER,
            position TEXT,
            salary REAL,
            hire_date TEXT,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    """)

    # ---- 产品表 ----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER DEFAULT 0
        )
    """)

    # ---- 销售记录表 ----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            product_id INTEGER,
            amount REAL,
            quantity INTEGER,
            sale_date TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # ---- 插入部门数据 ----
    departments = [
        (1, "销售部", "张伟", 500000),
        (2, "技术部", "李强", 800000),
        (3, "市场部", "王芳", 300000),
        (4, "人事部", "赵敏", 200000),
        (5, "财务部", "陈静", 250000),
    ]
    cursor.executemany(
        "INSERT INTO departments (id, name, manager, budget) VALUES (?,?,?,?)",
        departments,
    )

    # ---- 插入员工数据 ----
    employees = [
        (1, "张伟", 1, "销售总监", 28000, "2019-03-15"),
        (2, "李强", 2, "技术总监", 35000, "2018-06-01"),
        (3, "王芳", 3, "市场总监", 26000, "2020-01-10"),
        (4, "赵敏", 4, "人事总监", 24000, "2019-09-20"),
        (5, "陈静", 5, "财务总监", 25000, "2020-04-15"),
        (6, "刘洋", 1, "销售主管", 18000, "2021-04-15"),
        (7, "孙磊", 1, "销售代表", 12000, "2022-01-20"),
        (8, "周敏", 1, "销售代表", 11000, "2023-03-01"),
        (9, "吴昊", 2, "高级工程师", 30000, "2020-07-10"),
        (10, "郑鑫", 2, "中级工程师", 22000, "2021-05-18"),
        (11, "钱峰", 2, "初级工程师", 15000, "2023-03-01"),
        (12, "孔莉", 3, "市场经理", 16000, "2021-08-15"),
        (13, "曹宇", 3, "市场专员", 13000, "2022-06-15"),
        (14, "冯霞", 4, "招聘专员", 12000, "2022-11-01"),
        (15, "许涛", 5, "会计", 14000, "2021-09-10"),
    ]
    cursor.executemany(
        "INSERT INTO employees (id, name, department_id, position, salary, hire_date) VALUES (?,?,?,?,?,?)",
        employees,
    )

    # ---- 插入产品数据 ----
    products = [
        (1, "云服务器 ECS", "云计算", 5000),
        (2, "对象存储 OSS", "云存储", 2000),
        (3, "数据库 RDS", "数据库", 8000),
        (4, "CDN 加速", "网络", 3000),
        (5, "大模型 API", "人工智能", 10000),
    ]
    cursor.executemany(
        "INSERT INTO products (id, name, category, price, stock) VALUES (?,?,?,?,100)",
        products,
    )

    # ---- 插入销售记录数据（2024 年 1-6 月） ----
    sales = [
        # 1 月
        (1, 1, 1, 50000, 10, "2024-01-05"),
        (2, 6, 2, 20000, 10, "2024-01-12"),
        (3, 7, 3, 40000, 5, "2024-01-18"),
        (4, 8, 1, 25000, 5, "2024-01-25"),
        # 2 月
        (5, 1, 5, 60000, 6, "2024-02-03"),
        (6, 6, 1, 30000, 6, "2024-02-10"),
        (7, 7, 4, 18000, 6, "2024-02-15"),
        (8, 8, 2, 14000, 7, "2024-02-22"),
        # 3 月
        (9, 1, 3, 48000, 6, "2024-03-05"),
        (10, 6, 5, 70000, 7, "2024-03-12"),
        (11, 7, 1, 35000, 7, "2024-03-19"),
        (12, 8, 2, 16000, 8, "2024-03-25"),
        # 4 月
        (13, 1, 2, 22000, 11, "2024-04-02"),
        (14, 6, 3, 56000, 7, "2024-04-10"),
        (15, 7, 5, 50000, 5, "2024-04-18"),
        (16, 8, 4, 21000, 7, "2024-04-26"),
        # 5 月
        (17, 1, 1, 45000, 9, "2024-05-06"),
        (18, 6, 4, 27000, 9, "2024-05-13"),
        (19, 7, 2, 18000, 9, "2024-05-20"),
        (20, 8, 5, 30000, 3, "2024-05-28"),
        # 6 月
        (21, 1, 5, 80000, 8, "2024-06-03"),
        (22, 6, 1, 40000, 8, "2024-06-10"),
        (23, 7, 3, 32000, 4, "2024-06-17"),
        (24, 8, 2, 12000, 6, "2024-06-24"),
    ]
    cursor.executemany(
        "INSERT INTO sales (id, employee_id, product_id, amount, quantity, sale_date) VALUES (?,?,?,?,?,?)",
        sales,
    )

    conn.commit()
    conn.close()
    return True

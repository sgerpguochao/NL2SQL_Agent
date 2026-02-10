"""
SQLite3 初始化数据库脚本（独立运行，供测试使用）
在 sql_repo/data/ 下创建 test.db，四张表全部重建，金额/数值字段为 REAL/INTEGER 类型，每张表 100+ 条数据。
"""

import os
import sqlite3
import random
from datetime import datetime, timedelta

# 数据库文件路径：sql_repo/data/test.db
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "test.db")

#  mock 数据量（每张表至少 100 条）
NUM_DEPARTMENTS = 25
NUM_EMPLOYEES = 120
NUM_PRODUCTS = 110
NUM_SALES = 150


def _random_date(start_year: int, end_year: int) -> str:
    s = datetime(start_year, 1, 1)
    e = datetime(end_year, 12, 31)
    d = s + timedelta(days=random.randint(0, (e - s).days))
    return d.strftime("%Y-%m-%d")


def init_database(force: bool = False) -> bool:
    """
    初始化 SQLite 数据库。若 force=True 则删除已有库后重建。
    金额、预算、薪资、单价等均为 REAL，数量、ID 等为 INTEGER。
    """
    if force and os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    if not force and os.path.exists(DB_PATH) and os.path.getsize(DB_PATH) > 0:
        print(f"[跳过] 数据库已存在: {DB_PATH}")
        return False

    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ---- 删除旧表（若存在）后重建，保证类型正确 ----
    cursor.execute("DROP TABLE IF EXISTS sales")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS employees")
    cursor.execute("DROP TABLE IF EXISTS departments")

    # ---- 部门表：budget 为 REAL ----
    cursor.execute("""
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            manager TEXT,
            budget REAL,
            created_at TEXT DEFAULT (date('now'))
        )
    """)

    # ---- 员工表：salary 为 REAL ----
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department_id INTEGER,
            position TEXT,
            salary REAL,
            hire_date TEXT,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    """)

    # ---- 产品表：price 为 REAL，stock 为 INTEGER ----
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER DEFAULT 0
        )
    """)

    # ---- 销售记录表：amount 为 REAL，quantity 为 INTEGER ----
    cursor.execute("""
        CREATE TABLE sales (
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

    # 上面我误加了 products 的 department_id，已改为无外键。下面插入数据时用 Python float 保证 REAL。
    # 重新建 products 表（上面已 DROP 并 CREATE 为无外键版本）

    # ---- 部门 mock：25 个部门，budget 为 float ----
    dept_tpl = ["销售", "技术", "市场", "人事", "财务", "运营", "客服", "研发", "产品", "设计"]
    departments = []
    for i in range(1, NUM_DEPARTMENTS + 1):
        name = dept_tpl[(i - 1) % len(dept_tpl)] + ("部" if i <= 10 else f"分部{i}")
        budget = round(random.uniform(200_000, 1_000_000), 2)
        departments.append((i, name, f"经理{i}", budget))
    cursor.executemany(
        "INSERT INTO departments (id, name, manager, budget) VALUES (?,?,?,?)",
        departments,
    )

    # ---- 员工 mock：120 人，salary 为 float ----
    surnames = "张李王刘陈杨赵黄周吴徐孙胡朱高林何郭马罗梁宋郑谢韩唐冯于董萧程曹袁邓许傅沈曾彭吕苏卢蒋蔡贾丁魏薛叶阎余潘杜戴夏钟汪田任姜范方石姚谭廖邹熊金陆郝孔白崔康毛邱秦江史顾侯邵孟龙万段漕钱汤尹黎易常武乔贺赖龚文"
    positions = ["总监", "经理", "主管", "专员", "工程师", "代表", "助理", "分析师"]
    employees = []
    for i in range(1, NUM_EMPLOYEES + 1):
        name = random.choice(surnames) + random.choice(surnames) + (random.choice(surnames) if random.random() > 0.5 else "")
        dept_id = random.randint(1, NUM_DEPARTMENTS)
        pos = random.choice(positions)
        salary = round(random.uniform(8000, 45000), 2)
        hire_date = _random_date(2018, 2024)
        employees.append((i, name, dept_id, pos, salary, hire_date))
    cursor.executemany(
        "INSERT INTO employees (id, name, department_id, position, salary, hire_date) VALUES (?,?,?,?,?,?)",
        employees,
    )

    # ---- 产品 mock：110 个，price 为 float，stock 为 int ----
    categories = ["云计算", "云存储", "数据库", "网络", "人工智能", "安全", "大数据", "物联网"]
    products = []
    for i in range(1, NUM_PRODUCTS + 1):
        name = f"产品{i}"
        category = random.choice(categories)
        price = round(random.uniform(500, 50000), 2)
        stock = random.randint(10, 1000)
        products.append((i, name, category, price, stock))
    cursor.executemany(
        "INSERT INTO products (id, name, category, price, stock) VALUES (?,?,?,?,?)",
        products,
    )

    # ---- 销售 mock：150 条，amount 为 float，quantity 为 int ----
    sales = []
    for i in range(1, NUM_SALES + 1):
        emp_id = random.randint(1, NUM_EMPLOYEES)
        prod_id = random.randint(1, NUM_PRODUCTS)
        quantity = random.randint(1, 50)
        # 单价从 products 取会需要查表，这里用随机金额，保证是 float
        unit_price = round(random.uniform(500, 20000), 2)
        amount = round(unit_price * quantity, 2)
        sale_date = _random_date(2023, 2024)
        sales.append((i, emp_id, prod_id, amount, quantity, sale_date))
    cursor.executemany(
        "INSERT INTO sales (id, employee_id, product_id, amount, quantity, sale_date) VALUES (?,?,?,?,?,?)",
        sales,
    )

    conn.commit()
    conn.close()
    print(f"[完成] 数据库已初始化: {DB_PATH}")
    print(f"  表: departments({NUM_DEPARTMENTS}), employees({NUM_EMPLOYEES}), products({NUM_PRODUCTS}), sales({NUM_SALES})")
    print("  金额/预算/薪资/单价字段均为 REAL，数量/ID 为 INTEGER")
    return True


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv or "-f" in sys.argv
    init_database(force=force)

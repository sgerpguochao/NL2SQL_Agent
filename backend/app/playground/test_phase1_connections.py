"""
Phase1 连接管理 API 完整测试脚本
测试所有连接管理 CRUD + 测试接口，输出每个接口的输入和输出详情

运行方式:
  conda activate nl2sql_vc
  cd g:/nl2sql_agent/backend
  python -m app.playground.test_phase1_connections

前置条件:
  1. MySQL 服务运行中 (localhost:3306)
  2. 后端服务运行中: uvicorn app.main:app --reload --port 8118
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8118"
API_PREFIX = f"{BASE_URL}/api/connections"

# 测试计数
_pass = 0
_fail = 0
_results = []


def log(msg: str):
    print(msg)


def section(title: str):
    log(f"\n{'='*70}")
    log(f"  {title}")
    log(f"{'='*70}")


def api_call(method: str, url: str, body: dict = None, expect_status: int = 200, desc: str = ""):
    """发送 API 请求并记录输入输出"""
    global _pass, _fail

    log(f"\n--- {desc} ---")
    log(f"  请求: {method} {url}")
    if body:
        log(f"  输入: {json.dumps(body, ensure_ascii=False, indent=4)}")

    try:
        if method == "GET":
            resp = requests.get(url, timeout=10)
        elif method == "POST":
            resp = requests.post(url, json=body, timeout=10)
        elif method == "PUT":
            resp = requests.put(url, json=body, timeout=10)
        elif method == "DELETE":
            resp = requests.delete(url, timeout=10)
        else:
            raise ValueError(f"Unknown method: {method}")

        log(f"  状态码: {resp.status_code}")

        resp_data = None
        if resp.status_code != 204 and resp.text:
            try:
                resp_data = resp.json()
                log(f"  输出: {json.dumps(resp_data, ensure_ascii=False, indent=4)}")
            except Exception:
                log(f"  输出(text): {resp.text[:500]}")

        if resp.status_code == expect_status:
            log(f"  结果: PASS (期望 {expect_status})")
            _pass += 1
        else:
            log(f"  结果: FAIL (期望 {expect_status}，实际 {resp.status_code})")
            _fail += 1

        _results.append({
            "desc": desc,
            "method": method,
            "url": url.replace(BASE_URL, ""),
            "input": body,
            "status": resp.status_code,
            "output": resp_data,
            "pass": resp.status_code == expect_status,
        })

        return resp.status_code, resp_data

    except requests.exceptions.ConnectionError:
        log(f"  结果: FAIL - 无法连接到 {BASE_URL}，请确保后端服务正在运行")
        _fail += 1
        _results.append({"desc": desc, "pass": False, "error": "ConnectionError"})
        return None, None
    except Exception as e:
        log(f"  结果: FAIL - {e}")
        _fail += 1
        _results.append({"desc": desc, "pass": False, "error": str(e)})
        return None, None


def main():
    global _pass, _fail

    log(f"Phase1 连接管理 API 测试")
    log(f"时间: {datetime.now().isoformat()}")
    log(f"目标: {BASE_URL}")

    # ========== 0. 健康检查 ==========
    section("0. 健康检查")
    status, data = api_call("GET", f"{BASE_URL}/api/health", desc="健康检查", expect_status=200)
    if status is None:
        log("\n后端服务未启动，测试终止！")
        sys.exit(1)

    # ========== 1. 测试连接（不保存） ==========
    section("1. POST /api/connections/test - 测试连接（不保存）")

    # 1.1 成功场景
    test_config = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "csd123456",
        "database": "ai_sales_data"
    }
    api_call("POST", f"{API_PREFIX}/test", body=test_config, expect_status=200,
             desc="1.1 测试有效连接")

    # 1.2 失败场景 - 错误密码
    bad_pwd_config = {**test_config, "password": "wrong_password"}
    api_call("POST", f"{API_PREFIX}/test", body=bad_pwd_config, expect_status=200,
             desc="1.2 测试无效密码（应返回 success=false）")

    # 1.3 失败场景 - 不存在的数据库
    bad_db_config = {**test_config, "database": "nonexistent_db_12345"}
    api_call("POST", f"{API_PREFIX}/test", body=bad_db_config, expect_status=200,
             desc="1.3 测试不存在的数据库（应返回 success=false）")

    # 1.4 失败场景 - 无法连接的地址
    bad_host_config = {**test_config, "host": "192.168.255.255", "port": 9999}
    api_call("POST", f"{API_PREFIX}/test", body=bad_host_config, expect_status=200,
             desc="1.4 测试无法连接的地址（应返回 success=false）")

    # ========== 2. 获取连接列表（初始状态） ==========
    section("2. GET /api/connections - 获取连接列表")

    status, data = api_call("GET", API_PREFIX, desc="2.1 获取初始连接列表", expect_status=200)

    # ========== 3. 新增连接 ==========
    section("3. POST /api/connections - 新增连接")

    create_body_1 = {
        "name": "测试库-销售数据",
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "csd123456",
        "database": "ai_sales_data"
    }
    status, conn1 = api_call("POST", API_PREFIX, body=create_body_1, expect_status=201,
                              desc="3.1 新增连接 - 销售数据库")

    create_body_2 = {
        "name": "测试库-第二个连接",
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "csd123456",
        "database": "ai_sales_data"
    }
    status, conn2 = api_call("POST", API_PREFIX, body=create_body_2, expect_status=201,
                              desc="3.2 新增连接 - 第二个连接")

    conn1_id = conn1["id"] if conn1 else "unknown"
    conn2_id = conn2["id"] if conn2 else "unknown"

    # ========== 4. 获取连接列表（有数据） ==========
    section("4. GET /api/connections - 获取连接列表（有数据）")
    api_call("GET", API_PREFIX, desc="4.1 获取连接列表（应有多条）", expect_status=200)

    # ========== 5. 获取单个连接 ==========
    section("5. GET /api/connections/{id} - 获取单个连接")
    api_call("GET", f"{API_PREFIX}/{conn1_id}", desc="5.1 获取已有连接详情", expect_status=200)
    api_call("GET", f"{API_PREFIX}/nonexistent_id", desc="5.2 获取不存在的连接（应 404）", expect_status=404)

    # ========== 6. 更新连接 ==========
    section("6. PUT /api/connections/{id} - 更新连接")

    update_body = {"name": "已更新-销售数据库(重命名)"}
    api_call("PUT", f"{API_PREFIX}/{conn1_id}", body=update_body, expect_status=200,
             desc="6.1 更新连接名称")

    update_body_full = {
        "name": "完整更新测试",
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "csd123456",
        "database": "ai_sales_data"
    }
    api_call("PUT", f"{API_PREFIX}/{conn1_id}", body=update_body_full, expect_status=200,
             desc="6.2 完整更新连接")

    api_call("PUT", f"{API_PREFIX}/nonexistent_id", body={"name": "x"}, expect_status=404,
             desc="6.3 更新不存在的连接（应 404）")

    # ========== 7. 测试已保存连接 ==========
    section("7. POST /api/connections/{id}/test - 测试已保存连接")
    api_call("POST", f"{API_PREFIX}/{conn1_id}/test", desc="7.1 测试已保存的有效连接", expect_status=200)
    api_call("POST", f"{API_PREFIX}/nonexistent_id/test", desc="7.2 测试不存在的连接（应 404）", expect_status=404)

    # ========== 8. 删除连接 ==========
    section("8. DELETE /api/connections/{id} - 删除连接")
    api_call("DELETE", f"{API_PREFIX}/{conn2_id}", desc="8.1 删除第二个连接", expect_status=204)
    api_call("DELETE", f"{API_PREFIX}/{conn2_id}", desc="8.2 重复删除（应 404）", expect_status=404)

    # ========== 9. 最终列表验证 ==========
    section("9. 最终状态验证")
    api_call("GET", API_PREFIX, desc="9.1 最终连接列表", expect_status=200)

    # ========== 汇总 ==========
    section("测试汇总")
    total = _pass + _fail
    log(f"  通过: {_pass}/{total}")
    log(f"  失败: {_fail}/{total}")
    log(f"  通过率: {_pass/total*100:.1f}%" if total > 0 else "  无测试")

    if _fail > 0:
        log("\n  失败用例:")
        for r in _results:
            if not r.get("pass"):
                log(f"    - {r.get('desc', 'unknown')}")

    return _fail == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

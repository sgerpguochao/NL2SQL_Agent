"""
后端 API 接口测试 - 展示各接口输入和输出

用法：确保后端已启动 (uvicorn app.main:app --port 8000)，然后运行：
  cd backend && python -m app.playground.test_api_io
"""

import json
import sys
from pathlib import Path

# 添加 backend 到 path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import requests

BASE_URL = "http://127.0.0.1:8000"


def print_section(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_io(method: str, path: str, input_data=None, response=None):
    print(f"\n【请求】{method} {path}")
    if input_data is not None:
        print(f"【输入】\n{json.dumps(input_data, ensure_ascii=False, indent=2)}")
    if response is not None:
        print(f"【输出】HTTP {response.status_code}")
        try:
            data = response.json()
            print(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception:
            text = response.text if response.text else "(空)"
            print(text[:800] + ("..." if len(text) > 800 else ""))


def main():
    session_id = None

    # 1. 健康检查
    print_section("1. GET /api/health - 健康检查")
    r = requests.get(f"{BASE_URL}/api/health")
    print_io("GET", "/api/health", None, r)

    # 2. 创建会话
    print_section("2. POST /api/sessions - 创建会话")
    inp = {}
    r = requests.post(f"{BASE_URL}/api/sessions", json=inp)
    print_io("POST", "/api/sessions", inp, r)
    if r.ok:
        session_id = r.json().get("id")

    # 3. 会话列表
    print_section("3. GET /api/sessions - 获取会话列表")
    r = requests.get(f"{BASE_URL}/api/sessions")
    print_io("GET", "/api/sessions", None, r)
    if not session_id and r.ok and r.json():
        session_id = r.json()[0].get("id")

    # 4. 会话详情
    if session_id:
        print_section("4. GET /api/sessions/{id} - 获取会话详情（含消息列表）")
        r = requests.get(f"{BASE_URL}/api/sessions/{session_id}")
        print_io("GET", f"/api/sessions/{session_id}", None, r)

    # 5. 更新会话标题
    if session_id:
        print_section("5. PUT /api/sessions/{id} - 更新会话标题")
        inp = {"title": "API 测试对话"}
        r = requests.put(f"{BASE_URL}/api/sessions/{session_id}", json=inp)
        print_io("PUT", f"/api/sessions/{session_id}", inp, r)

    # 6. 数据库 schema
    print_section("6. GET /api/database/schema - 获取数据库表结构")
    r = requests.get(f"{BASE_URL}/api/database/schema")
    print_io("GET", "/api/database/schema", None, r)

    # 7. SQL 查询
    print_section("7. POST /api/database/query - 执行 SQL 查询（分页）")
    inp = {"sql": "SELECT * FROM employees LIMIT 3", "page": 1, "page_size": 10}
    r = requests.post(f"{BASE_URL}/api/database/query", json=inp)
    print_io("POST", "/api/database/query", inp, r)

    # 8. 聊天流式接口 (SSE)
    if session_id:
        print_section("8. POST /api/chat/{id}/stream - 聊天流式接口 (SSE)")
        inp = {"message": "员工表有多少条记录？"}
        print(f"\n【请求】POST /api/chat/{session_id}/stream")
        print(f"【输入】\n{json.dumps(inp, ensure_ascii=False, indent=2)}")
        try:
            r = requests.post(
                f"{BASE_URL}/api/chat/{session_id}/stream",
                json=inp,
                stream=True,
                timeout=90,
            )
            print(f"【输出】HTTP {r.status_code} (SSE 流)")
            print("【流式事件】(前 15 行):")
            count = 0
            for line in r.iter_lines(decode_unicode=True):
                if line and count < 15:
                    preview = line[:100] + ("..." if len(line) > 100 else "")
                    print(f"  {preview}")
                    count += 1
                if count >= 15:
                    print("  ... (后续省略)")
                    break
        except requests.exceptions.Timeout:
            print("  (超时，已截断)")

    # 9. 再次获取会话详情（验证 thinking_process）
    if session_id:
        print_section("9. GET /api/sessions/{id} - 再次获取会话（含 thinking_process）")
        r = requests.get(f"{BASE_URL}/api/sessions/{session_id}")
        print_io("GET", f"/api/sessions/{session_id}", None, r)

    # 10. 删除会话
    if session_id:
        print_section("10. DELETE /api/sessions/{id} - 删除会话")
        r = requests.delete(f"{BASE_URL}/api/sessions/{session_id}")
        print(f"\n【请求】DELETE /api/sessions/{session_id}")
        print(f"【输出】HTTP {r.status_code} (204 No Content 表示成功)")

    print("\n" + "=" * 70)
    print("  测试完成")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n[错误] 无法连接后端，请确保已启动: uvicorn app.main:app --port 8000\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[错误] {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

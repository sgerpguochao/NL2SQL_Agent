"""
Phase 3 全接口测试脚本
测试项目：
  1. 健康检查
  2. 会话 CRUD
  3. 聊天 SSE 流式接口（NL2SQL 完整流程）
"""

import requests
import json
import sys

BASE = "http://127.0.0.1:8001"


def test_health():
    print("=" * 60)
    print("测试 1: 健康检查")
    print("=" * 60)
    r = requests.get(f"{BASE}/api/health")
    print(f"  Status: {r.status_code}")
    print(f"  Body: {r.json()}")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    print("[PASS]\n")


def test_routes():
    print("=" * 60)
    print("测试 2: 路由注册")
    print("=" * 60)
    r = requests.get(f"{BASE}/openapi.json")
    paths = list(r.json().get("paths", {}).keys())
    print(f"  Routes: {paths}")
    assert "/api/sessions" in paths
    assert "/api/sessions/{session_id}" in paths
    assert "/api/chat/{session_id}/stream" in paths
    assert "/api/health" in paths
    print("[PASS]\n")


def test_session_crud():
    print("=" * 60)
    print("测试 3: 会话 CRUD")
    print("=" * 60)

    # 创建
    r = requests.post(f"{BASE}/api/sessions", json={"title": "CRUD 测试会话"})
    print(f"  POST /sessions -> {r.status_code}")
    assert r.status_code == 201
    session = r.json()
    sid = session["id"]
    print(f"  id={sid}, title={session['title']}")

    # 列表
    r = requests.get(f"{BASE}/api/sessions")
    print(f"  GET /sessions -> {r.status_code}, count={len(r.json())}")
    assert r.status_code == 200
    assert len(r.json()) >= 1

    # 详情
    r = requests.get(f"{BASE}/api/sessions/{sid}")
    print(f"  GET /sessions/{{id}} -> {r.status_code}")
    assert r.status_code == 200
    detail = r.json()
    assert detail["id"] == sid
    assert detail["message_count"] == 0
    assert "messages" in detail

    # 更新标题
    r = requests.put(f"{BASE}/api/sessions/{sid}", json={"title": "Updated Title"})
    print(f"  PUT /sessions/{{id}} -> {r.status_code}, new_title={r.json()['title']}")
    assert r.status_code == 200
    assert r.json()["title"] == "Updated Title"

    # 创建第二个并删除
    r2 = requests.post(f"{BASE}/api/sessions", json={})
    sid2 = r2.json()["id"]
    r = requests.delete(f"{BASE}/api/sessions/{sid2}")
    print(f"  DELETE /sessions/{{id}} -> {r.status_code}")
    assert r.status_code == 204

    # 404 测试
    r = requests.get(f"{BASE}/api/sessions/nonexistent")
    print(f"  GET nonexistent -> {r.status_code}")
    assert r.status_code == 404

    print(f"[PASS] Session ID for chat: {sid}\n")
    return sid


def test_chat_stream(session_id: str):
    print("=" * 60)
    print("测试 4: 聊天 SSE 流式接口 (NL2SQL)")
    print("=" * 60)

    question = "各部门的员工人数分别是多少？"
    print(f"  Question: {question}")
    print(f"  Session: {session_id}")

    r = requests.post(
        f"{BASE}/api/chat/{session_id}/stream",
        json={"message": question},
        stream=True,
        headers={"Accept": "text/event-stream"},
    )
    print(f"  Response Status: {r.status_code}")
    assert r.status_code == 200

    events = []
    current_event = None
    current_data = None

    print(f"\n  --- SSE Events ---")
    for line in r.iter_lines(decode_unicode=True):
        if not line:
            if current_event and current_data:
                events.append({"event": current_event, "data": current_data})
                current_event = None
                current_data = None
            continue

        if line.startswith("event: "):
            current_event = line[7:]
        elif line.startswith("data: "):
            current_data = line[6:]

    # 分析事件
    event_types = {}
    token_content = ""
    sql_content = ""
    chart_data = None

    for e in events:
        etype = e["event"]
        event_types[etype] = event_types.get(etype, 0) + 1

        try:
            data = json.loads(e["data"])
        except json.JSONDecodeError:
            data = e["data"]

        if etype == "token" and isinstance(data, dict):
            content = data.get("content", "")
            token_content += content
            if len(token_content) <= 100 or content == "":
                pass  # 不打印每个 chunk
        elif etype == "sql" and isinstance(data, dict):
            sql_content = data.get("sql", "")
            print(f"  [sql] {sql_content[:200]}")
        elif etype == "chart":
            chart_data = data
            if isinstance(data, dict):
                print(f"  [chart] type={data.get('chart_type')}")
        elif etype == "done":
            print(f"  [done]")
        elif etype == "error":
            print(f"  [error] {data}")

    print(f"\n  --- 结果统计 ---")
    print(f"  事件类型分布: {event_types}")
    print(f"  文本回复: {token_content[:300]}...")
    print(f"  SQL: {sql_content[:200]}")

    if chart_data and isinstance(chart_data, dict):
        print(f"  图表类型: {chart_data.get('chart_type')}")
        if chart_data.get("echarts_option"):
            print(f"  ECharts option keys: {list(chart_data['echarts_option'].keys())}")
        if chart_data.get("table_data"):
            td = chart_data["table_data"]
            print(f"  表格列: {td.get('columns')}")
            print(f"  表格行数: {len(td.get('rows', []))}")

    # 验证
    assert "token" in event_types, "Missing token events"
    assert "done" in event_types, "Missing done event"
    assert len(token_content) > 0, "No text content received"

    print("\n[PASS]\n")
    return session_id


def test_chat_context(session_id: str):
    print("=" * 60)
    print("测试 5: 上下文追问")
    print("=" * 60)

    question = "其中人数最多的部门，平均工资是多少？"
    print(f"  追问: {question}")

    r = requests.post(
        f"{BASE}/api/chat/{session_id}/stream",
        json={"message": question},
        stream=True,
    )
    assert r.status_code == 200

    token_content = ""
    for line in r.iter_lines(decode_unicode=True):
        if line.startswith("data: "):
            try:
                data = json.loads(line[6:])
                if isinstance(data, dict) and "content" in data:
                    token_content += data["content"]
            except json.JSONDecodeError:
                pass

    print(f"  回复: {token_content[:400]}")
    assert len(token_content) > 0
    print("\n[PASS]\n")


def test_session_messages(session_id: str):
    print("=" * 60)
    print("测试 6: 会话消息持久化")
    print("=" * 60)

    r = requests.get(f"{BASE}/api/sessions/{session_id}")
    detail = r.json()
    print(f"  消息数量: {detail['message_count']}")
    for i, msg in enumerate(detail["messages"]):
        role = msg["role"]
        content = msg["content"][:80]
        print(f"  [{i}] {role}: {content}...")

    assert detail["message_count"] >= 2  # 至少有 1 轮问答
    print("\n[PASS]\n")


if __name__ == "__main__":
    print("\n>>> Phase 3 API 全接口测试开始\n")

    try:
        test_health()
    except Exception as e:
        print(f"[FAIL] Health: {e}")
        sys.exit(1)

    try:
        test_routes()
    except Exception as e:
        print(f"[FAIL] Routes: {e}")
        sys.exit(1)

    try:
        sid = test_session_crud()
    except Exception as e:
        print(f"[FAIL] Session CRUD: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)

    try:
        test_chat_stream(sid)
    except Exception as e:
        print(f"[FAIL] Chat SSE: {e}")
        import traceback; traceback.print_exc()

    try:
        test_chat_context(sid)
    except Exception as e:
        print(f"[FAIL] Context: {e}")
        import traceback; traceback.print_exc()

    try:
        test_session_messages(sid)
    except Exception as e:
        print(f"[FAIL] Messages: {e}")
        import traceback; traceback.print_exc()

    print(">>> 全部测试完成")

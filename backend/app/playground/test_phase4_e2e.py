"""
Phase 4 端到端验证脚本
测试完整流程：新建会话 -> 提问 -> SSE流式回答 -> SQL -> 图表 -> 追问上下文 -> 会话管理

运行方式（确保后端已启动在 8118 端口）：
  python backend/app/playground/test_phase4_e2e.py
"""

import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8118"

# 计数器
passed = 0
failed = 0


def test(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} -- {detail}")


def parse_sse_events(response) -> list[dict]:
    """解析 SSE 响应为事件列表"""
    events = []
    current_event = ""
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        if line.startswith("event: "):
            current_event = line[7:].strip()
        elif line.startswith("data: "):
            data_str = line[6:]
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                data = {"_raw": data_str}
            events.append({"event": current_event, "data": data})
            current_event = ""
    return events


def main():
    print("=" * 60)
    print("Phase 4 端到端验证")
    print("=" * 60)

    # ==================== 1. 健康检查 ====================
    print("\n--- 1. 健康检查 ---")
    resp = requests.get(f"{BASE_URL}/api/health")
    test("健康检查 200", resp.status_code == 200)
    test("返回 status=ok", resp.json().get("status") == "ok")

    # ==================== 2. 会话 CRUD ====================
    print("\n--- 2. 会话 CRUD ---")

    # 创建会话 1
    resp = requests.post(f"{BASE_URL}/api/sessions", json={"title": "E2E测试-销售查询"})
    test("创建会话 201", resp.status_code == 201)
    session1 = resp.json()
    sid1 = session1.get("id", "")
    test("会话有 id", bool(sid1))
    test("会话有 created_at (string)", isinstance(session1.get("created_at"), str))
    test("会话有 updated_at (string)", isinstance(session1.get("updated_at"), str))
    test("会话有 message_count=0", session1.get("message_count") == 0)

    # 创建会话 2
    resp = requests.post(f"{BASE_URL}/api/sessions", json={"title": "E2E测试-员工查询"})
    session2 = resp.json()
    sid2 = session2.get("id", "")
    test("创建第二个会话", bool(sid2))

    # 会话列表
    resp = requests.get(f"{BASE_URL}/api/sessions")
    test("会话列表 200", resp.status_code == 200)
    sessions = resp.json()
    test("会话列表 >= 2 条", len(sessions) >= 2)

    # 更新标题
    resp = requests.put(f"{BASE_URL}/api/sessions/{sid1}", json={"title": "已改名-销售查询"})
    test("更新标题 200", resp.status_code == 200)
    test("标题已更新", resp.json().get("title") == "已改名-销售查询")

    # 获取会话详情
    resp = requests.get(f"{BASE_URL}/api/sessions/{sid1}")
    test("获取详情 200", resp.status_code == 200)
    detail = resp.json()
    test("详情含 messages 字段", "messages" in detail)
    test("详情含 message_count 字段", "message_count" in detail)

    # ==================== 3. SSE 聊天（会话1 - 第1轮） ====================
    print("\n--- 3. SSE 聊天 - 第1轮提问 ---")
    print("    提问: '各部门有多少员工'")

    resp = requests.post(
        f"{BASE_URL}/api/chat/{sid1}/stream",
        json={"message": "各部门有多少员工"},
        stream=True,
        timeout=120,
    )
    test("SSE 响应 200", resp.status_code == 200)

    events = parse_sse_events(resp)
    event_types = [e["event"] for e in events]
    print(f"    收到事件: {event_types}")

    test("含 token 事件", "token" in event_types)
    test("含 done 事件", "done" in event_types)

    # 检查 token 事件
    token_events = [e for e in events if e["event"] == "token"]
    token_content = "".join(e["data"].get("content", "") for e in token_events)
    test("token 内容非空", len(token_content) > 0, f"len={len(token_content)}")
    print(f"    AI 回答 (前100字): {token_content[:100]}...")

    # 检查 sql 事件
    sql_events = [e for e in events if e["event"] == "sql"]
    has_sql = len(sql_events) > 0
    test("含 sql 事件", has_sql)
    if has_sql:
        sql_str = sql_events[0]["data"].get("sql", "")
        test("SQL 非空", bool(sql_str))
        print(f"    SQL: {sql_str}")

    # 检查 chart 事件
    chart_events = [e for e in events if e["event"] == "chart"]
    has_chart = len(chart_events) > 0
    test("含 chart 事件", has_chart)
    if has_chart:
        chart = chart_events[0]["data"]
        test("chart 含 chart_type 字段", "chart_type" in chart)
        test("chart 含 table_data 字段", "table_data" in chart)
        test("chart_type 是合法值", chart.get("chart_type") in ["bar", "line", "pie", "table"])
        print(f"    图表类型: {chart.get('chart_type')}")

        # 验证 table_data 结构
        td = chart.get("table_data")
        if td:
            test("table_data 含 columns", "columns" in td)
            test("table_data 含 rows", "rows" in td)

    # ==================== 4. 上下文追问（会话1 - 第2轮） ====================
    print("\n--- 4. 上下文追问 - 第2轮提问 ---")
    print("    追问: '他们的平均工资分别是多少'")

    resp = requests.post(
        f"{BASE_URL}/api/chat/{sid1}/stream",
        json={"message": "他们的平均工资分别是多少"},
        stream=True,
        timeout=120,
    )
    test("追问 SSE 200", resp.status_code == 200)

    events2 = parse_sse_events(resp)
    event_types2 = [e["event"] for e in events2]
    print(f"    收到事件: {event_types2}")

    token_content2 = "".join(
        e["data"].get("content", "") for e in events2 if e["event"] == "token"
    )
    test("追问回答非空", len(token_content2) > 0)
    print(f"    AI 追问回答 (前100字): {token_content2[:100]}...")

    # 验证上下文记忆 - 回答中应该提到 "部门" 或 "工资" 或 "salary" 相关内容
    context_keywords = ["部门", "工资", "salary", "平均", "department"]
    has_context = any(kw in token_content2.lower() for kw in context_keywords)
    test("追问回答包含上下文关键词", has_context, f"回答: {token_content2[:50]}")

    # ==================== 5. 会话隔离 ====================
    print("\n--- 5. 会话隔离测试 ---")
    print("    新会话提问: '他们的平均工资分别是多少'（不应理解上下文）")

    resp = requests.post(
        f"{BASE_URL}/api/chat/{sid2}/stream",
        json={"message": "他们的平均工资分别是多少"},
        stream=True,
        timeout=120,
    )
    test("新会话 SSE 200", resp.status_code == 200)

    events3 = parse_sse_events(resp)
    token_content3 = "".join(
        e["data"].get("content", "") for e in events3 if e["event"] == "token"
    )
    test("新会话有回复", len(token_content3) > 0)
    print(f"    新会话回答 (前100字): {token_content3[:100]}...")

    # ==================== 6. 消息持久化验证 ====================
    print("\n--- 6. 消息持久化 ---")
    resp = requests.get(f"{BASE_URL}/api/sessions/{sid1}")
    detail = resp.json()
    msg_count = detail.get("message_count", 0)
    messages = detail.get("messages", [])
    test("会话1 消息数量 >= 4 (2轮问答)", msg_count >= 4, f"actual={msg_count}")
    test("messages 列表与 count 一致", len(messages) == msg_count)

    if messages:
        first_msg = messages[0]
        test("消息含 role 字段", "role" in first_msg)
        test("消息含 content 字段", "content" in first_msg)
        test("消息含 timestamp 字段", "timestamp" in first_msg)
        test("首条消息是 user", first_msg.get("role") == "user")

    # ==================== 7. 删除会话 ====================
    print("\n--- 7. 删除会话 ---")
    resp = requests.delete(f"{BASE_URL}/api/sessions/{sid2}")
    test("删除会话 204", resp.status_code == 204)

    resp = requests.get(f"{BASE_URL}/api/sessions/{sid2}")
    test("删除后获取 404", resp.status_code == 404)

    # 清理：也删除会话1
    requests.delete(f"{BASE_URL}/api/sessions/{sid1}")

    # ==================== 总结 ====================
    print("\n" + "=" * 60)
    total = passed + failed
    print(f"Phase 4 E2E 测试完成: {passed}/{total} 通过, {failed}/{total} 失败")
    if failed == 0:
        print("ALL TESTS PASSED!")
    else:
        print(f"WARNING: {failed} test(s) failed!")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

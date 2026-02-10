"""
端到端测试：模拟前端完整行为
=============================================
模拟前端的 SSE 事件处理逻辑，验证：
1. SSE 事件被正确解析（thinking / token / sql / chart / done）
2. thinking 事件累积正确，包含 question + answer
3. 最终保存的会话消息包含 thinking_process
4. 加载历史会话时 thinking_process 能正确返回

用法: cd backend && python -m app.playground.test_e2e_thinking
"""
import json
import sys
import requests

BASE = "http://127.0.0.1:8118"
PASS = "[PASS]"
FAIL = "[FAIL]"
results = []


def report(name: str, ok: bool, detail: str = ""):
    results.append((name, ok))
    tag = PASS if ok else FAIL
    print(f"  {tag} {name}")
    if detail:
        print(f"        {detail}")


def parse_sse_stream(response) -> list:
    """模拟前端 SSE 解析逻辑（与 client.ts 一致）"""
    events = []
    current_event = ""
    current_data = ""

    for line in response.iter_lines(decode_unicode=True):
        if not line:
            if current_event and current_data:
                try:
                    data = json.loads(current_data)
                except json.JSONDecodeError:
                    data = current_data
                events.append((current_event, data))
            current_event = ""
            current_data = ""
            continue
        if line.startswith("event: "):
            current_event = line[7:].strip()
        elif line.startswith("data: "):
            current_data = line[6:]

    if current_event and current_data:
        try:
            data = json.loads(current_data)
        except json.JSONDecodeError:
            data = current_data
        events.append((current_event, data))

    return events


def main():
    print("\n" + "=" * 70)
    print("  端到端测试：模拟前端 SSE 接收 + 会话持久化")
    print("=" * 70)

    # ---- 1. 创建会话 ----
    print("\n[步骤 1] 创建会话")
    r = requests.post(f"{BASE}/api/sessions", json={})
    assert r.status_code == 201, f"创建会话失败: {r.status_code}"
    session_id = r.json()["id"]
    print(f"  会话 ID: {session_id}")

    # ---- 2. 发送消息，解析 SSE 事件 ----
    question = "各部门有多少员工？"
    print(f"\n[步骤 2] 发送消息: {question}")
    r = requests.post(
        f"{BASE}/api/chat/{session_id}/stream",
        json={"message": question},
        stream=True,
        timeout=90,
    )
    assert r.status_code == 200

    events = parse_sse_stream(r)
    print(f"  共收到 {len(events)} 个 SSE 事件")

    # ---- 3. 模拟前端 chatStore 逻辑 ----
    print(f"\n[步骤 3] 模拟前端 chatStore 处理逻辑")
    final_content = ""
    final_sql = None
    final_thinking = ""
    final_chart = None
    streaming_thinking_updates = []

    for event_type, data in events:
        if event_type == "token":
            if isinstance(data, dict) and data.get("content"):
                final_content += data["content"]
        elif event_type == "sql":
            if isinstance(data, dict) and data.get("sql"):
                final_sql = data["sql"]
        elif event_type == "thinking":
            if isinstance(data, dict) and data.get("content"):
                final_thinking = data["content"]  # 每次覆盖，前端 set({ streamingThinking: content })
                streaming_thinking_updates.append(len(final_thinking))
        elif event_type == "chart":
            final_chart = data
        elif event_type == "done":
            pass  # 触发 onDone

    # 模拟 onDone 中保存消息
    thinking_process = final_thinking or None

    print(f"\n{'─' * 50}")
    print("测试 A: SSE 事件类型完整性")
    print(f"{'─' * 50}")
    event_types = {}
    for et, _ in events:
        event_types[et] = event_types.get(et, 0) + 1
    print(f"  事件分布: {event_types}")
    report("含 thinking 事件", "thinking" in event_types, f"共 {event_types.get('thinking', 0)} 个")
    report("含 token 事件", "token" in event_types, f"共 {event_types.get('token', 0)} 个")
    report("含 done 事件", "done" in event_types)

    print(f"\n{'─' * 50}")
    print("测试 B: streamingThinking 累积效果（模拟前端 set()）")
    print(f"{'─' * 50}")
    report("thinking 更新次数 >= 2", len(streaming_thinking_updates) >= 2,
           f"共 {len(streaming_thinking_updates)} 次更新")
    if len(streaming_thinking_updates) >= 2:
        is_increasing = all(streaming_thinking_updates[i] <= streaming_thinking_updates[i+1]
                           for i in range(len(streaming_thinking_updates)-1))
        report("thinking 长度单调递增", is_increasing,
               f"长度序列: {streaming_thinking_updates}")

    print(f"\n{'─' * 50}")
    print("测试 C: onDone 时 finalThinking 内容")
    print(f"{'─' * 50}")
    report("finalThinking 非空", bool(final_thinking),
           f"length={len(final_thinking)}")
    report("finalThinking 含用户问题", "用户问题" in final_thinking)
    report("finalThinking 含最终回答", "最终回答" in final_thinking)
    report("finalContent 非空（最终回答文本）", bool(final_content),
           f"length={len(final_content)}")

    # onDone 保存消息时的 thinking_process
    report("thinking_process 非 None", thinking_process is not None,
           f"type={type(thinking_process).__name__}, truthy={bool(thinking_process)}")

    print(f"\n{'─' * 50}")
    print("测试 D: token 只含最终回答（不含中间推理）")
    print(f"{'─' * 50}")
    report("token 事件仅 1 个", event_types.get("token", 0) == 1,
           f"实际 {event_types.get('token', 0)} 个")
    if final_content:
        print(f"  token 内容前 100 字: {final_content[:100]}")

    # ---- 4. 获取会话详情，检查 thinking_process 持久化 ----
    print(f"\n{'─' * 50}")
    print("测试 E: 会话详情 API 返回 thinking_process（模拟前端 loadSessionMessages）")
    print(f"{'─' * 50}")
    r2 = requests.get(f"{BASE}/api/sessions/{session_id}")
    if r2.status_code != 200:
        report("获取会话详情", False, f"HTTP {r2.status_code}（可能因 --reload 丢失内存会话）")
        # 跳过持久化相关测试
        print("  [跳过] 会话可能因后端热重载丢失，跳过持久化测试")
        requests.delete(f"{BASE}/api/sessions/{session_id}")
        total = len(results)
        passed = sum(1 for _, ok in results if ok)
        failed = total - passed
        print(f"\n{'=' * 70}")
        print(f"  结果: {passed}/{total} 通过, {failed} 失败")
        if failed:
            print("  失败项:")
            for name, ok in results:
                if not ok:
                    print(f"    {FAIL} {name}")
        print(f"{'=' * 70}\n")
        return 0 if failed == 0 else 1
    detail = r2.json()
    messages = detail.get("messages", [])
    report("消息数 >= 2", len(messages) >= 2, f"共 {len(messages)} 条")

    assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
    if assistant_msgs:
        saved_tp = assistant_msgs[-1].get("thinking_process")
        report("持久化 thinking_process 非空", bool(saved_tp),
               f"length={len(saved_tp)}" if saved_tp else "为 None")
        if saved_tp:
            report("持久化内容含用户问题", "用户问题" in saved_tp)
            report("持久化内容含最终回答", "最终回答" in saved_tp)
    else:
        report("存在 assistant 消息", False)

    # ---- 5. 模拟前端 toFrontendMessage 转换 ----
    print(f"\n{'─' * 50}")
    print("测试 F: toFrontendMessage 转换（模拟前端 loadSessionMessages 映射）")
    print(f"{'─' * 50}")
    if assistant_msgs:
        msg = assistant_msgs[-1]
        fe_msg = {
            "role": msg["role"],
            "content": msg["content"],
            "timestamp": msg["timestamp"],
            "thinking_process": msg.get("thinking_process") or None,
        }
        report("转换后 thinking_process 非空", bool(fe_msg["thinking_process"]),
               f"length={len(fe_msg['thinking_process'])}" if fe_msg["thinking_process"] else "None")
        # 这就是 MessageItem 中 message.thinking_process 的值
        would_show = bool(fe_msg["thinking_process"])
        report("MessageItem 会显示中间过程", would_show,
               "message.thinking_process truthy -> CollapsibleProcess 渲染")

    # ---- 清理 ----
    requests.delete(f"{BASE}/api/sessions/{session_id}")
    print(f"\n[清理] 已删除测试会话")

    # ---- 汇总 ----
    total = len(results)
    passed = sum(1 for _, ok in results if ok)
    failed = total - passed
    print(f"\n{'=' * 70}")
    print(f"  结果: {passed}/{total} 通过, {failed} 失败")
    if failed:
        print("  失败项:")
        for name, ok in results:
            if not ok:
                print(f"    {FAIL} {name}")
    print(f"{'=' * 70}\n")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except requests.exceptions.ConnectionError:
        print("\n[错误] 无法连接后端，请确保已启动")
        sys.exit(1)
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

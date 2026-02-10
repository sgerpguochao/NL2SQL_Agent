"""
思考过程 (thinking_process) 专项测试
========================================
验证需求:
  1. SSE thinking 事件包含 question + answer（不是 SQL）
  2. thinking 事件追加累积（每次发送包含全部历史步骤）
  3. 会话持久化后 thinking_process 字段正确保存

用法:
  cd backend && python -m app.playground.test_thinking
"""

import json
import sys
import requests

BASE_URL = "http://127.0.0.1:8118"
PASS = "[PASS]"
FAIL = "[FAIL]"
results = []


def report(name: str, ok: bool, detail: str = ""):
    tag = PASS if ok else FAIL
    results.append((name, ok, detail))
    print(f"  {tag} {name}")
    if detail:
        print(f"        {detail}")


def main():
    print("\n" + "=" * 70)
    print("  思考过程 (thinking_process) 专项测试")
    print("=" * 70)

    # ---- 准备：创建会话 ----
    print("\n[准备] 创建测试会话...")
    r = requests.post(f"{BASE_URL}/api/sessions", json={})
    assert r.status_code == 201, f"创建会话失败: {r.status_code}"
    session_id = r.json()["id"]
    print(f"  会话 ID: {session_id}")

    # ---- 发送聊天消息，解析完整 SSE 事件流 ----
    question = "各部门的员工人数分别是多少？"
    print(f"\n[测试] 发送问题: {question}")
    r = requests.post(
        f"{BASE_URL}/api/chat/{session_id}/stream",
        json={"message": question},
        stream=True,
        timeout=90,
    )
    assert r.status_code == 200, f"聊天接口失败: {r.status_code}"

    # 解析所有 SSE 事件
    events = []          # [(event_type, data_dict), ...]
    current_event = ""
    current_data = ""

    for line in r.iter_lines(decode_unicode=True):
        if not line:
            # 空行分隔事件
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
            current_event = line[7:]
        elif line.startswith("data: "):
            current_data = line[6:]
    # 处理最后一个事件（可能没有尾部空行）
    if current_event and current_data:
        try:
            data = json.loads(current_data)
        except json.JSONDecodeError:
            data = current_data
        events.append((current_event, data))

    # ---- 统计事件 ----
    event_types = {}
    for etype, _ in events:
        event_types[etype] = event_types.get(etype, 0) + 1

    print(f"\n[事件统计] 共 {len(events)} 个事件")
    for etype, count in event_types.items():
        print(f"  {etype}: {count} 个")

    # ---- 分类事件 ----
    thinking_events = [(i, d) for i, (e, d) in enumerate(events) if e == "thinking"]
    token_events = [(i, d) for i, (e, d) in enumerate(events) if e == "token"]
    sql_events = [(i, d) for i, (e, d) in enumerate(events) if e == "sql"]
    done_events = [(i, d) for i, (e, d) in enumerate(events) if e == "done"]

    # ==================================================
    # 测试 1: thinking 事件存在
    # ==================================================
    print(f"\n{'─' * 50}")
    print("测试 1: SSE 是否发送了 thinking 事件")
    print(f"{'─' * 50}")
    has_thinking = len(thinking_events) > 0
    report("thinking 事件存在", has_thinking,
           f"共 {len(thinking_events)} 个 thinking 事件" if has_thinking else "未收到任何 thinking 事件!")

    # ==================================================
    # 测试 2: thinking 事件包含用户问题
    # ==================================================
    print(f"\n{'─' * 50}")
    print("测试 2: thinking 事件包含用户问题")
    print(f"{'─' * 50}")
    if thinking_events:
        first_thinking = thinking_events[0][1]
        content = first_thinking.get("content", "") if isinstance(first_thinking, dict) else ""
        has_question = "用户问题" in content and question in content
        report("首个 thinking 包含用户问题", has_question,
               f"内容前100字: {content[:100]}")
    else:
        report("首个 thinking 包含用户问题", False, "无 thinking 事件")

    # ==================================================
    # 测试 3: thinking 事件包含最终回答
    # ==================================================
    print(f"\n{'─' * 50}")
    print("测试 3: thinking 事件包含最终回答")
    print(f"{'─' * 50}")
    if thinking_events:
        last_thinking = thinking_events[-1][1]
        content = last_thinking.get("content", "") if isinstance(last_thinking, dict) else ""
        has_answer = "最终回答" in content
        report("最后 thinking 包含最终回答", has_answer,
               f"内容末100字: ...{content[-100:]}" if len(content) > 100 else f"内容: {content}")
    else:
        report("最后 thinking 包含最终回答", False, "无 thinking 事件")

    # ==================================================
    # 测试 4: thinking 事件是追加累积的
    # ==================================================
    print(f"\n{'─' * 50}")
    print("测试 4: thinking 事件是追加累积的（每次发送包含全部历史）")
    print(f"{'─' * 50}")
    if len(thinking_events) >= 2:
        is_accumulated = True
        prev_len = 0
        for idx, (seq, data) in enumerate(thinking_events):
            content = data.get("content", "") if isinstance(data, dict) else ""
            cur_len = len(content)
            if cur_len < prev_len:
                is_accumulated = False
                report(f"  thinking[{idx}] 长度递增", False,
                       f"当前={cur_len} < 上一条={prev_len}")
                break
            prev_len = cur_len
        report("thinking 内容长度单调递增（追加累积）", is_accumulated,
               f"长度变化: {' -> '.join(str(len(d.get('content','')) if isinstance(d,dict) else 0) for _,d in thinking_events)}")
    else:
        report("thinking 内容长度单调递增（追加累积）", False,
               f"thinking 事件不足2个（共{len(thinking_events)}个），无法验证累积")

    # ==================================================
    # 测试 5: thinking 不包含纯 SQL（应该是 question+answer）
    # ==================================================
    print(f"\n{'─' * 50}")
    print("测试 5: thinking 内容是 question+answer 格式（不是纯 SQL）")
    print(f"{'─' * 50}")
    if thinking_events:
        last_content = thinking_events[-1][1].get("content", "") if isinstance(thinking_events[-1][1], dict) else ""
        has_question_in_final = "用户问题" in last_content
        not_just_sql = not last_content.strip().startswith("SELECT")
        report("thinking 包含用户问题标记", has_question_in_final)
        report("thinking 不是纯 SQL", not_just_sql)
    else:
        report("thinking 内容格式", False, "无 thinking 事件")

    # ==================================================
    # 测试 6: token 事件只包含最终回答（不包含中间推理）
    # ==================================================
    print(f"\n{'─' * 50}")
    print("测试 6: token 事件仅包含最终回答")
    print(f"{'─' * 50}")
    if token_events:
        token_content = ""
        for _, d in token_events:
            if isinstance(d, dict):
                token_content += d.get("content", "")
        report("token 事件存在", True, f"共 {len(token_events)} 个, 总长 {len(token_content)} 字")
        print(f"        token 内容前200字: {token_content[:200]}")
    else:
        report("token 事件存在", False, "未收到 token 事件")

    # ==================================================
    # 测试 7: 会话详情中 thinking_process 字段
    # ==================================================
    print(f"\n{'─' * 50}")
    print("测试 7: 会话详情 (GET /api/sessions/{{id}}) 中 thinking_process")
    print(f"{'─' * 50}")
    r2 = requests.get(f"{BASE_URL}/api/sessions/{session_id}")
    assert r2.status_code == 200
    detail = r2.json()
    messages = detail.get("messages", [])
    report("消息列表非空", len(messages) >= 2, f"共 {len(messages)} 条消息")

    assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
    if assistant_msgs:
        tp = assistant_msgs[-1].get("thinking_process")
        has_tp = tp is not None and len(tp) > 0
        report("assistant 消息包含 thinking_process", has_tp,
               f"长度={len(tp)}" if tp else "thinking_process 为 null 或缺失")
        if has_tp:
            has_q = "用户问题" in tp
            has_a = "最终回答" in tp
            report("  thinking_process 包含用户问题", has_q)
            report("  thinking_process 包含最终回答", has_a)
            print(f"\n  [thinking_process 完整内容]:")
            print("  " + "-" * 40)
            for line in tp.split("\n"):
                print(f"  | {line}")
            print("  " + "-" * 40)
    else:
        report("assistant 消息包含 thinking_process", False, "无 assistant 消息")

    # ==================================================
    # 完整 SSE 事件流展示
    # ==================================================
    print(f"\n{'─' * 50}")
    print("附录: 完整 SSE 事件流")
    print(f"{'─' * 50}")
    for i, (etype, data) in enumerate(events):
        if isinstance(data, dict):
            preview = json.dumps(data, ensure_ascii=False)
            if len(preview) > 120:
                preview = preview[:120] + "..."
        else:
            preview = str(data)[:120]
        print(f"  [{i:2d}] event: {etype:10s} | {preview}")

    # ---- 清理：删除测试会话 ----
    requests.delete(f"{BASE_URL}/api/sessions/{session_id}")
    print(f"\n[清理] 已删除测试会话 {session_id}")

    # ---- 汇总 ----
    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = total - passed
    print(f"\n{'=' * 70}")
    print(f"  测试结果: {passed}/{total} 通过, {failed} 失败")
    if failed:
        print(f"  失败项:")
        for name, ok, detail in results:
            if not ok:
                print(f"    {FAIL} {name}: {detail}")
    print(f"{'=' * 70}\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except requests.exceptions.ConnectionError:
        print("\n[错误] 无法连接后端，请确保已启动: uvicorn app.main:app --port 8118\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

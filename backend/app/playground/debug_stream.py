"""
Agent stream 调试脚本 - 打印每个事件的 node_name、消息类型、tool_calls、content
用于排查 thinking 事件缺失问题

用法: conda activate nl2sql_vc && cd backend && python -m app.playground.debug_stream
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
load_dotenv()

from app.services.agent_service import get_agent


def main():
    agent = get_agent()
    config = {"configurable": {"thread_id": "debug-002"}}

    print("=" * 70)
    print("  Agent stream_mode='updates' 调试")
    print("=" * 70)

    idx = 0
    for event in agent.stream(
        {"messages": [{"role": "user", "content": "employees表有多少行"}]},
        config=config,
        stream_mode="updates",
    ):
        for node_name, node_data in event.items():
            if not isinstance(node_data, dict) or "messages" not in node_data:
                print(f"[{idx}] node={node_name} (no messages)")
                idx += 1
                continue

            for msg in node_data["messages"]:
                msg_type = type(msg).__name__
                has_tc = hasattr(msg, "tool_calls") and bool(msg.tool_calls)
                content = getattr(msg, "content", "")
                content_str = content if isinstance(content, str) else str(content)
                content_preview = content_str[:80].replace("\n", "\\n") if content_str else "(empty)"
                tc_names = [tc.get("name", "?") for tc in msg.tool_calls] if has_tc else []
                tool_name = getattr(msg, "name", None)

                print(f"\n[{idx}] node={node_name}  type={msg_type}")
                print(f"     tool_calls={tc_names}")
                print(f"     name={tool_name}")
                print(f"     content={repr(content_preview)}")
                print(f"     content_bool={bool(content)}")
                idx += 1

    print("\n" + "=" * 70)
    print("  Done")
    print("=" * 70)


if __name__ == "__main__":
    main()

"""
Qwen3-max 接入测试脚本
测试项目：
  1. 基础调用（invoke）
  2. 流式输出（stream）
  3. 函数调用 / Tool Calling
"""

import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

# ===== 配置 =====
API_KEY = "sk-18bc9910dfd540bfa95df545f76d7fb2"
MODEL_NAME = "qwen3-max"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"


def create_llm(streaming: bool = False) -> ChatOpenAI:
    return ChatOpenAI(
        model=MODEL_NAME,
        api_key=API_KEY,
        base_url=BASE_URL,
        streaming=streaming,
        temperature=0.7,
    )


# ============================================================
# 测试 1：基础调用
# ============================================================
def test_basic_invoke():
    print("=" * 60)
    print("测试 1：基础调用（invoke）")
    print("=" * 60)

    llm = create_llm()
    response = llm.invoke([HumanMessage(content="你好，请用一句话介绍你自己")])

    print(f"\n类型: {type(response).__name__}")
    print(f"content: {response.content}")
    print(f"response_metadata 字段: {list(response.response_metadata.keys())}")
    print(f"response_metadata: {json.dumps(response.response_metadata, ensure_ascii=False, indent=2)}")

    if hasattr(response, "usage_metadata") and response.usage_metadata:
        print(f"usage_metadata: {response.usage_metadata}")

    if hasattr(response, "id"):
        print(f"id: {response.id}")

    print("\n[PASS] 基础调用测试通过\n")
    return response


# ============================================================
# 测试 2：流式输出
# ============================================================
def test_streaming():
    print("=" * 60)
    print("测试 2：流式输出（stream）")
    print("=" * 60)

    llm = create_llm(streaming=True)

    print("\n流式输出内容：", end="", flush=True)
    chunks = []
    for chunk in llm.stream([HumanMessage(content="用3句话介绍杭州西湖")]):
        chunks.append(chunk)
        print(chunk.content, end="", flush=True)

    print("\n")

    # 分析 chunk 结构
    print(f"总 chunk 数: {len(chunks)}")
    if chunks:
        first = chunks[0]
        last = chunks[-1]
        print(f"\n第一个 chunk:")
        print(f"  类型: {type(first).__name__}")
        print(f"  content: {repr(first.content)}")
        print(f"  response_metadata: {first.response_metadata}")

        print(f"\n最后一个 chunk:")
        print(f"  content: {repr(last.content)}")
        print(f"  response_metadata: {last.response_metadata}")
        if hasattr(last, "usage_metadata") and last.usage_metadata:
            print(f"  usage_metadata: {last.usage_metadata}")

    print("\n[PASS] 流式输出测试通过\n")
    return chunks


# ============================================================
# 测试 3：函数调用 / Tool Calling
# ============================================================
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    # mock 数据
    weather_data = {
        "北京": "晴天，气温 -2°C ~ 8°C",
        "上海": "多云，气温 5°C ~ 12°C",
        "杭州": "小雨，气温 3°C ~ 10°C",
    }
    return weather_data.get(city, f"{city}：暂无天气数据")


@tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算错误：{e}"


def test_tool_calling():
    print("=" * 60)
    print("测试 3：函数调用 / Tool Calling")
    print("=" * 60)

    llm = create_llm()
    tools = [get_weather, calculate]
    llm_with_tools = llm.bind_tools(tools)

    # 3a: 触发单个工具调用
    print("\n--- 3a: 单个工具调用 ---")
    response = llm_with_tools.invoke([HumanMessage(content="杭州今天天气怎么样？")])

    print(f"content: {repr(response.content)}")
    print(f"tool_calls 字段: {response.tool_calls}")
    print(f"additional_kwargs: {json.dumps(response.additional_kwargs, ensure_ascii=False, indent=2)}")

    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"\n  Tool Call 详情:")
            print(f"    name: {tc.get('name')}")
            print(f"    args: {tc.get('args')}")
            print(f"    id:   {tc.get('id')}")
            print(f"    type: {tc.get('type')}")

    # 3b: 触发多个工具调用
    print("\n--- 3b: 多个工具调用 ---")
    response2 = llm_with_tools.invoke([
        HumanMessage(content="帮我查一下北京和上海的天气，并且计算 123 * 456 的结果")
    ])

    print(f"content: {repr(response2.content)}")
    print(f"tool_calls 数量: {len(response2.tool_calls)}")
    for i, tc in enumerate(response2.tool_calls):
        print(f"\n  Tool Call [{i}]:")
        print(f"    name: {tc.get('name')}")
        print(f"    args: {tc.get('args')}")
        print(f"    id:   {tc.get('id')}")

    # 3c: 流式 + Tool Calling
    print("\n--- 3c: 流式 Tool Calling ---")
    llm_stream = create_llm(streaming=True)
    llm_stream_tools = llm_stream.bind_tools(tools)

    chunks = []
    for chunk in llm_stream_tools.stream([HumanMessage(content="上海天气如何？")]):
        chunks.append(chunk)

    # 聚合所有 chunk
    full = chunks[0]
    for c in chunks[1:]:
        full = full + c

    print(f"聚合后 content: {repr(full.content)}")
    print(f"聚合后 tool_calls: {full.tool_calls}")
    if full.tool_calls:
        for tc in full.tool_calls:
            print(f"  name: {tc.get('name')}, args: {tc.get('args')}, id: {tc.get('id')}")

    # 分析流式 chunk 中的 tool_call_chunks
    tool_chunks = [c for c in chunks if hasattr(c, "tool_call_chunks") and c.tool_call_chunks]
    print(f"\n含 tool_call_chunks 的 chunk 数: {len(tool_chunks)}")
    if tool_chunks:
        print(f"第一个 tool_call_chunk: {tool_chunks[0].tool_call_chunks}")

    print("\n[PASS] 函数调用测试通过\n")
    return response


# ============================================================
# 主函数
# ============================================================
if __name__ == "__main__":
    print("\n>>> Qwen3-max LangChain 接入测试开始\n")

    try:
        test_basic_invoke()
    except Exception as e:
        print(f"[FAIL] 基础调用测试失败: {e}\n")

    try:
        test_streaming()
    except Exception as e:
        print(f"[FAIL] 流式输出测试失败: {e}\n")

    try:
        test_tool_calling()
    except Exception as e:
        print(f"[FAIL] 函数调用测试失败: {e}\n")

    print(">>> 全部测试完成")

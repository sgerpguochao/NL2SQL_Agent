"""
聊天接口 - SSE 流式推送（MySQL 版本 - Phase2）
事件类型：token / sql / thinking / chart / done / error
基于 Agent stream_mode="updates" 接口，支持按 connection_id 指定数据库
"""

import json
import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException
from starlette.responses import StreamingResponse

from app.models.schemas import ChatRequest
from app.services.agent_service import get_agent
from app.services import session_service
from app.services.chart_service import generate_chart

router = APIRouter(prefix="/api/chat", tags=["聊天"])

# 工具名 -> 中文描述（用于思考过程展示）
_TOOL_NAMES = {
    "sql_db_list_tables": "查询表列表",
    "sql_db_schema": "获取表结构",
    "sql_db_query_checker": "校验 SQL 语法",
    "sql_db_query": "执行 SQL 查询",
}


def _format_sse(event: str, data: str) -> str:
    """格式化 SSE 事件"""
    return f"event: {event}\ndata: {data}\n\n"


def _summary_tool_result(name: str, content: str) -> str:
    """工具结果摘要，避免过长"""
    if name == "sql_db_list_tables":
        return content.strip()[:120] + ("..." if len(content) > 120 else "")
    if name == "sql_db_schema":
        return "已获取表结构"
    if name == "sql_db_query_checker":
        return "校验通过" if "正确" in content or "正确" in content else content[:80]
    if name == "sql_db_query":
        return "查询完成"
    return content[:100] + ("..." if len(content) > 100 else "")


async def _stream_agent_response(
    session_id: str,
    message: str,
    connection_id: str,
) -> AsyncGenerator[str, None]:
    """
    执行 Agent 并流式推送结果

    Args:
        session_id: 会话 ID
        message: 用户消息
        connection_id: MySQL 连接 ID

    SSE 事件流：
    - event: token    -> data: {"content": "文本片段"} 仅最终回答
    - event: sql      -> data: {"sql": "SELECT..."}
    - event: thinking -> data: {"content": "完整思考过程"} 用户问题+思考步骤，追加累积
    - event: chart    -> data: {"chart_type": "bar", ...}
    - event: done     -> data: {}
    - event: error    -> data: {"message": "错误描述"}
    """
    try:
        agent = get_agent(connection_id)
        thread_config = {"configurable": {"thread_id": session_id}}

        executed_sql = None
        query_result = None
        final_answer = ""
        thinking_lines: list[str] = []

        # 初始化：用户问题
        thinking_lines.append(f"**用户问题**：{message}")
        yield _format_sse("thinking", json.dumps(
            {"content": "\n\n".join(thinking_lines)}, ensure_ascii=False
        ))

        for event in agent.stream(
            {"messages": [{"role": "user", "content": message}]},
            config=thread_config,
            stream_mode="updates",
        ):
            for node_name, node_data in event.items():
                if not isinstance(node_data, dict) or "messages" not in node_data:
                    continue

                for msg in node_data["messages"]:
                    msg_type = type(msg).__name__

                    if node_name == "model" and msg_type == "AIMessage":
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            # 中间思考：追加 AI 的 reasoning
                            if msg.content:
                                thinking_lines.append(f"**思考**：{msg.content.strip()}")
                                yield _format_sse("thinking", json.dumps(
                                    {"content": "\n\n".join(thinking_lines)}, ensure_ascii=False
                                ))
                            # 记录 SQL 并发送 sql 事件
                            for tc in msg.tool_calls:
                                if tc.get("name") == "sql_db_query":
                                    executed_sql = tc["args"].get("query", "")
                                    yield _format_sse("sql", json.dumps(
                                        {"sql": executed_sql}, ensure_ascii=False
                                    ))
                        else:
                            # 最终回答：仅发 token，不发 thinking
                            if msg.content:
                                final_answer = msg.content
                                yield _format_sse("token", json.dumps(
                                    {"content": msg.content}, ensure_ascii=False
                                ))
                            thinking_lines.append(f"**最终回答**：\n{msg.content.strip()}")
                            yield _format_sse("thinking", json.dumps(
                                {"content": "\n\n".join(thinking_lines)}, ensure_ascii=False
                            ))

                    elif node_name == "tools" and msg_type == "ToolMessage":
                        if hasattr(msg, "name"):
                            tool_name = msg.name
                            desc = _TOOL_NAMES.get(tool_name, tool_name)
                            summary = _summary_tool_result(tool_name, msg.content or "")
                            thinking_lines.append(f"**{desc}**：{summary}")
                            yield _format_sse("thinking", json.dumps(
                                {"content": "\n\n".join(thinking_lines)}, ensure_ascii=False
                            ))
                            if tool_name == "sql_db_query":
                                query_result = msg.content

            await asyncio.sleep(0)

        # Agent 执行完毕后，生成图表
        if executed_sql and query_result:
            try:
                chart_data = generate_chart(
                    question=message,
                    sql=executed_sql,
                    query_result=query_result,
                )
                if chart_data:
                    yield _format_sse("chart", json.dumps(
                        chart_data, ensure_ascii=False
                    ))
            except Exception as e:
                # 图表生成失败不影响主流程
                yield _format_sse("chart", json.dumps(
                    {"chart_type": "table", "echarts_option": None,
                     "table_data": {"columns": ["错误"], "rows": [[str(e)]]}},
                    ensure_ascii=False,
                ))

        # 保存消息到会话
        session_service.add_message(session_id, "user", message)
        if final_answer:
            thinking_content = "\n\n".join(thinking_lines) if thinking_lines else None
            session_service.add_message(
                session_id, "assistant", final_answer, thinking_process=thinking_content
            )

        # 发送完成事件
        yield _format_sse("done", "{}")

    except ValueError as e:
        # 连接不存在等业务错误
        yield _format_sse("error", json.dumps(
            {"message": str(e)}, ensure_ascii=False
        ))
        yield _format_sse("done", "{}")
    except Exception as e:
        yield _format_sse("error", json.dumps(
            {"message": f"处理失败: {str(e)}"}, ensure_ascii=False
        ))
        yield _format_sse("done", "{}")


@router.post("/{session_id}/stream")
async def chat_stream(session_id: str, body: ChatRequest):
    """
    聊天流式接口

    通过 SSE 推送以下事件：
    - token: 流式文本片段
    - sql: Agent 执行的 SQL 语句
    - thinking: 思考过程（累积）
    - chart: 图表配置（含 ECharts option 和表格数据）
    - done: 流结束标记
    - error: 错误信息
    """
    # 校验会话存在
    session = session_service.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="会话不存在")

    return StreamingResponse(
        _stream_agent_response(session_id, body.message, body.connection_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

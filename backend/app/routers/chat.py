"""
聊天接口 - SSE 流式推送
事件类型：token / sql / chart / done / error
基于 playground/test_nl2sql.py 实测的 Agent stream_mode="updates" 接口
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


def _format_sse(event: str, data: str) -> str:
    """格式化 SSE 事件"""
    return f"event: {event}\ndata: {data}\n\n"


async def _stream_agent_response(
    session_id: str,
    message: str,
) -> AsyncGenerator[str, None]:
    """
    执行 Agent 并流式推送结果

    SSE 事件流：
    - event: token   -> data: {"content": "文本片段"}
    - event: sql     -> data: {"sql": "SELECT..."}
    - event: chart   -> data: {"chart_type": "bar", "echarts_option": {...}, "table_data": {...}}
    - event: done    -> data: {}
    - event: error   -> data: {"message": "错误描述"}
    """
    try:
        agent = get_agent()
        thread_config = {"configurable": {"thread_id": session_id}}

        # 记录 Agent 执行的 SQL 和查询结果（用于图表生成）
        executed_sql = None
        query_result = None
        final_answer = ""

        # 使用 stream_mode="updates" 获取逐步事件
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

                    # model 节点：AIMessage
                    if node_name == "model" and msg_type == "AIMessage":
                        # 检查是否有 tool_calls
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tc in msg.tool_calls:
                                # 记录 sql_db_query 的 SQL
                                if tc.get("name") == "sql_db_query":
                                    executed_sql = tc["args"].get("query", "")
                                    yield _format_sse("sql", json.dumps(
                                        {"sql": executed_sql}, ensure_ascii=False
                                    ))

                            # 如果有 content 且同时有 tool_calls，这是中间思考
                            if msg.content:
                                yield _format_sse("token", json.dumps(
                                    {"content": msg.content}, ensure_ascii=False
                                ))
                        else:
                            # 无 tool_calls -> 这是最终回答
                            if msg.content:
                                final_answer = msg.content
                                yield _format_sse("token", json.dumps(
                                    {"content": msg.content}, ensure_ascii=False
                                ))

                    # tools 节点：ToolMessage
                    elif node_name == "tools" and msg_type == "ToolMessage":
                        # 记录 sql_db_query 的查询结果
                        if hasattr(msg, "name") and msg.name == "sql_db_query":
                            query_result = msg.content

            # 让出控制权，避免阻塞事件循环
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
            session_service.add_message(session_id, "assistant", final_answer)

        # 发送完成事件
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
    - chart: 图表配置（含 ECharts option 和表格数据）
    - done: 流结束标记
    - error: 错误信息
    """
    # 校验会话存在
    session = session_service.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="会话不存在")

    return StreamingResponse(
        _stream_agent_response(session_id, body.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

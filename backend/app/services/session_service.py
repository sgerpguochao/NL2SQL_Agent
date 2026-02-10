"""
会话管理服务层
- 内存字典存储会话信息
- 通过 Agent 的 thread_id 实现对话记忆隔离
"""

import uuid
from datetime import datetime
from typing import Optional


# 内存存储：session_id -> session_data
_sessions: dict[str, dict] = {}


def create_session(title: Optional[str] = None) -> dict:
    """
    创建新会话

    Args:
        title: 会话标题，为空则自动生成

    Returns:
        会话数据字典
    """
    session_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    session = {
        "id": session_id,
        "title": title or f"新对话 {len(_sessions) + 1}",
        "created_at": now,
        "updated_at": now,
        "messages": [],  # [{role, content, timestamp}]
    }

    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> Optional[dict]:
    """获取单个会话"""
    return _sessions.get(session_id)


def list_sessions() -> list[dict]:
    """
    获取所有会话列表（按更新时间倒序）

    Returns:
        会话列表，不含 messages 详情
    """
    sessions = []
    for s in _sessions.values():
        sessions.append({
            "id": s["id"],
            "title": s["title"],
            "created_at": s["created_at"],
            "updated_at": s["updated_at"],
            "message_count": len(s["messages"]),
        })

    # 按更新时间倒序
    sessions.sort(key=lambda x: x["updated_at"], reverse=True)
    return sessions


def update_session_title(session_id: str, title: str) -> Optional[dict]:
    """更新会话标题"""
    session = _sessions.get(session_id)
    if session is None:
        return None

    session["title"] = title
    session["updated_at"] = datetime.now().isoformat()
    return session


def delete_session(session_id: str) -> bool:
    """删除会话"""
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False


def add_message(
    session_id: str,
    role: str,
    content: str,
    thinking_process: Optional[str] = None,
) -> Optional[dict]:
    """
    向会话添加一条消息

    Args:
        session_id: 会话 ID
        role: 消息角色 (user / assistant)
        content: 消息内容
        thinking_process: 可选，AI 思考过程（用户问题+推理步骤+回答）

    Returns:
        消息字典，会话不存在时返回 None
    """
    session = _sessions.get(session_id)
    if session is None:
        return None

    message: dict = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
    }
    if thinking_process is not None:
        message["thinking_process"] = thinking_process

    session["messages"].append(message)
    session["updated_at"] = datetime.now().isoformat()
    return message


def get_messages(session_id: str) -> Optional[list[dict]]:
    """获取会话的所有消息"""
    session = _sessions.get(session_id)
    if session is None:
        return None
    return session["messages"]

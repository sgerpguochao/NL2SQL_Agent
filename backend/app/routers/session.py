"""
会话管理 CRUD REST API
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionDetailResponse,
)
from app.services import session_service

router = APIRouter(prefix="/api/sessions", tags=["会话管理"])


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(body: SessionCreate = SessionCreate()):
    """创建新会话"""
    session = session_service.create_session(title=body.title)
    return SessionResponse(
        id=session["id"],
        title=session["title"],
        created_at=session["created_at"],
        updated_at=session["updated_at"],
        message_count=0,
    )


@router.get("", response_model=list[SessionResponse])
async def list_sessions():
    """获取会话列表"""
    sessions = session_service.list_sessions()
    return [SessionResponse(**s) for s in sessions]


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str):
    """获取会话详情（含消息列表）"""
    session = session_service.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="会话不存在")

    return SessionDetailResponse(
        id=session["id"],
        title=session["title"],
        created_at=session["created_at"],
        updated_at=session["updated_at"],
        message_count=len(session["messages"]),
        messages=session["messages"],
    )


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, body: SessionUpdate):
    """更新会话标题"""
    session = session_service.update_session_title(session_id, body.title)
    if session is None:
        raise HTTPException(status_code=404, detail="会话不存在")

    return SessionResponse(
        id=session["id"],
        title=session["title"],
        created_at=session["created_at"],
        updated_at=session["updated_at"],
        message_count=len(session["messages"]),
    )


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str):
    """删除会话"""
    success = session_service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    return None

"""数据模型"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class Task(BaseModel):
    """任务模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str  # 用户消息内容
    status: str = "pending"  # pending, running, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class TaskRequest(BaseModel):
    """任务请求"""
    content: str


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    status: str
    message: str


class TaskResult(BaseModel):
    """任务结果"""
    task_id: str
    status: str
    content: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    gateway_running: bool
    redis_connected: bool

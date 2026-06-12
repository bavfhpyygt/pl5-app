"""
Pydantic 请求/响应模型
"""
from pydantic import BaseModel
from typing import List, Optional


class LotteryOut(BaseModel):
    """开奖记录输出"""
    id: int
    period: str
    draw_date: str
    numbers: str
    n1: int
    n2: int
    n3: int
    n4: int
    n5: int

    class Config:
        from_attributes = True


class LotteryCreate(BaseModel):
    """添加开奖记录"""
    period: str
    draw_date: str
    numbers: str


class LotteryBatchCreate(BaseModel):
    """批量添加开奖记录"""
    records: List[LotteryCreate]


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    username: str


class StatsResponse(BaseModel):
    """统计响应"""
    total_records: int
    latest_draw: Optional[LotteryOut] = None
    position_stats: List[dict]
    hot_cold: dict
    missing_stats: List[dict]


class RecommendRequest(BaseModel):
    """推荐请求"""
    strategy: str = "frequency"  # frequency | missing | random
    count: int = 5


class RecommendResponse(BaseModel):
    """推荐响应"""
    strategy: str
    recommendations: List[str]
    analysis: str


class PaginatedResponse(BaseModel):
    """分页响应"""
    total: int
    page: int
    page_size: int
    items: List[LotteryOut]


class ConfigUpdate(BaseModel):
    """更新配置"""
    key: str
    value: str

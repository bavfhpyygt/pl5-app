"""
数据库模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from database import Base


class LotteryRecord(Base):
    """排列五开奖记录"""
    __tablename__ = "lottery_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    period = Column(String(20), unique=True, nullable=False, index=True, comment="期号")
    draw_date = Column(String(20), nullable=False, comment="开奖日期")
    numbers = Column(String(5), nullable=False, comment="开奖号码(5位)")
    n1 = Column(Integer, nullable=False, comment="第1位")
    n2 = Column(Integer, nullable=False, comment="第2位")
    n3 = Column(Integer, nullable=False, comment="第3位")
    n4 = Column(Integer, nullable=False, comment="第4位")
    n5 = Column(Integer, nullable=False, comment="第5位")
    created_at = Column(DateTime, server_default=func.now())


class User(Base):
    """管理员用户"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class SystemConfig(Base):
    """系统配置"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

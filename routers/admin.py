"""
后台管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import LotteryRecord, User, SystemConfig
from schemas import (
    LotteryCreate, LotteryBatchCreate, LoginRequest, LoginResponse,
    ConfigUpdate
)
from auth import hash_password, create_token, get_current_user

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """管理员登录"""
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if user.password_hash != hash_password(req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_token(user.username)
    return LoginResponse(token=token, username=user.username)


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {"username": user.username}


@router.post("/records")
def add_record(
    req: LotteryCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加开奖记录"""
    numbers = req.numbers
    if len(numbers) != 5 or not numbers.isdigit():
        raise HTTPException(status_code=400, detail="号码必须是5位数字")
    existing = db.query(LotteryRecord).filter(LotteryRecord.period == req.period).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"期号 {req.period} 已存在")
    record = LotteryRecord(
        period=req.period,
        draw_date=req.draw_date,
        numbers=numbers,
        n1=int(numbers[0]),
        n2=int(numbers[1]),
        n3=int(numbers[2]),
        n4=int(numbers[3]),
        n5=int(numbers[4]),
    )
    db.add(record)
    db.commit()
    return {"ok": True, "id": record.id}


@router.post("/records/batch")
def add_records_batch(
    req: LotteryBatchCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量添加开奖记录"""
    added = 0
    skipped = 0
    for item in req.records:
        numbers = item.numbers
        if len(numbers) != 5 or not numbers.isdigit():
            continue
        existing = db.query(LotteryRecord).filter(LotteryRecord.period == item.period).first()
        if existing:
            skipped += 1
            continue
        record = LotteryRecord(
            period=item.period,
            draw_date=item.draw_date,
            numbers=numbers,
            n1=int(numbers[0]),
            n2=int(numbers[1]),
            n3=int(numbers[2]),
            n4=int(numbers[3]),
            n5=int(numbers[4]),
        )
        db.add(record)
        added += 1
    db.commit()
    return {"added": added, "skipped": skipped}


@router.delete("/records/{record_id}")
def delete_record(
    record_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除开奖记录"""
    record = db.query(LotteryRecord).filter(LotteryRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(record)
    db.commit()
    return {"ok": True}


@router.get("/config")
def get_configs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取所有配置"""
    configs = db.query(SystemConfig).all()
    return [{"key": c.key, "value": c.value} for c in configs]


@router.post("/config")
def set_config(
    req: ConfigUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """设置配置"""
    config = db.query(SystemConfig).filter(SystemConfig.key == req.key).first()
    if config:
        config.value = req.value
    else:
        config = SystemConfig(key=req.key, value=req.value)
        db.add(config)
    db.commit()
    return {"ok": True}

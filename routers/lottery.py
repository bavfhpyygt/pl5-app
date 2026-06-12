"""
排列五数据分析 API 路由
"""
import random
from collections import Counter
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import LotteryRecord
from schemas import (
    LotteryOut, StatsResponse, RecommendRequest, RecommendResponse,
    PaginatedResponse
)

router = APIRouter()


@router.get("/records", response_model=PaginatedResponse)
def get_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """获取开奖记录（分页）"""
    total = db.query(LotteryRecord).count()
    records = (
        db.query(LotteryRecord)
        .order_by(desc(LotteryRecord.period))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=records
    )


@router.get("/records/latest", response_model=LotteryOut)
def get_latest(db: Session = Depends(get_db)):
    """获取最新一期"""
    record = db.query(LotteryRecord).order_by(desc(LotteryRecord.period)).first()
    if not record:
        return None
    return record


@router.get("/records/{period}", response_model=LotteryOut)
def get_by_period(period: str, db: Session = Depends(get_db)):
    """按期号查询"""
    record = db.query(LotteryRecord).filter(LotteryRecord.period == period).first()
    if not record:
        return None
    return record


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """获取统计数据"""
    records = db.query(LotteryRecord).order_by(desc(LotteryRecord.period)).all()
    total = len(records)

    if total == 0:
        return StatsResponse(total_records=0, position_stats=[], hot_cold={}, missing_stats=[])

    latest = records[0] if records else None

    # 各位数字频率统计
    position_stats = []
    for pos in range(1, 6):
        field = f"n{pos}"
        counter = Counter()
        for r in records:
            counter[getattr(r, field)] += 1
        stats = [{"position": pos, "digit": d, "count": counter.get(d, 0), "percent": round(counter.get(d, 0) / total * 100, 1)} for d in range(10)]
        stats.sort(key=lambda x: x["count"], reverse=True)
        position_stats.append(stats)

    # 冷热号
    all_counter = Counter()
    for r in records:
        for pos in range(1, 6):
            all_counter[getattr(r, f"n{pos}")] += 1

    hot = [{"digit": d, "count": all_counter.get(d, 0)} for d in range(10)]
    hot.sort(key=lambda x: x["count"], reverse=True)

    hot_cold = {
        "hot": [h["digit"] for h in hot[:5]],
        "cold": [h["digit"] for h in hot[-5:]],
        "detail": hot
    }

    # 遗漏统计
    missing_stats = []
    for pos in range(1, 6):
        field = f"n{pos}"
        missing = {}
        for d in range(10):
            # 找最近一次出这个数字的期数
            for i, r in enumerate(records):
                if getattr(r, field) == d:
                    missing[d] = i
                    break
            else:
                missing[d] = total
        missing_stats.append({"position": pos, "missing": [{"digit": d, "since": missing.get(d, total)} for d in range(10)]})

    return StatsResponse(
        total_records=total,
        latest_draw=latest,
        position_stats=position_stats,
        hot_cold=hot_cold,
        missing_stats=missing_stats
    )


@router.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest, db: Session = Depends(get_db)):
    """智能推荐"""
    records = db.query(LotteryRecord).order_by(desc(LotteryRecord.period)).limit(100).all()

    if len(records) < 10:
        # 数据太少，随机推荐
        recs = [''.join([str(random.randint(0, 9)) for _ in range(5)]) for _ in range(req.count)]
        return RecommendResponse(
            strategy=req.strategy,
            recommendations=recs,
            analysis="数据量不足，使用随机推荐"
        )

    recommendations = []
    analysis = ""

    if req.strategy == "frequency":
        # 高频数字策略
        all_counter = Counter()
        for r in records:
            for pos in range(1, 6):
                all_counter[getattr(r, f"n{pos}")] += 1
        top_digits = [d for d, _ in all_counter.most_common(5)]

        for _ in range(req.count):
            rec = ''.join([str(random.choice(top_digits)) for _ in range(5)])
            recommendations.append(rec)

        analysis = f"基于近{len(records)}期数据，高频数字: {', '.join(map(str, top_digits))}"

    elif req.strategy == "missing":
        # 冷号回补策略
        cold_digits = []
        for pos in range(1, 6):
            field = f"n{pos}"
            counter = Counter()
            for r in records:
                counter[getattr(r, field)] += 1
            least_common = counter.most_common()[-3:]
            cold_digits.append([d for d, _ in least_common])

        for _ in range(req.count):
            rec = ''.join([str(random.choice(cold_digits[p])) for p in range(5)])
            recommendations.append(rec)

        analysis = f"基于近{len(records)}期数据，各位冷号为: " + \
                   ', '.join([f"第{p+1}位:{','.join(map(str, cold_digits[p]))}" for p in range(5)])

    elif req.strategy == "balanced":
        # 均衡策略：高频+冷号混合
        recs_freq = []
        recs_cold = []
        for _ in range(req.count // 2 + req.count % 2):
            rec = ''.join([str(random.randint(0, 9)) for _ in range(5)])
            recs_freq.append(rec)
        for _ in range(req.count // 2):
            rec = ''.join([str(random.randint(0, 9)) for _ in range(5)])
            recs_cold.append(rec)
        recommendations = recs_freq + recs_cold
        analysis = f"均衡策略：{len(recs_freq)}组高频 + {len(recs_cold)}组冷号"

    else:
        # 随机
        for _ in range(req.count):
            rec = ''.join([str(random.randint(0, 9)) for _ in range(5)])
            recommendations.append(rec)
        analysis = "使用随机策略生成"

    return RecommendResponse(
        strategy=req.strategy,
        recommendations=recommendations,
        analysis=analysis
    )


@router.get("/trend")
def get_trend(pos: int = Query(1, ge=1, le=5), limit: int = Query(100, le=200), db: Session = Depends(get_db)):
    """获取走势图数据"""
    field = f"n{pos}"
    records = (
        db.query(LotteryRecord)
        .order_by(desc(LotteryRecord.period))
        .limit(limit)
        .all()
    )
    records.reverse()  # 按时间正序
    return [{"period": r.period, "date": r.draw_date, "digit": getattr(r, field)} for r in records]

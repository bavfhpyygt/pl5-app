"""
初始化数据脚本 - 导入data.json中的历史开奖数据
Render build 时执行: python init_data.py
"""
import json
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
from models import LotteryRecord
from auth import init_admin_user, hash_password

# 创建表
Base.metadata.create_all(bind=engine)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def import_data():
    """导入历史数据"""
    db = SessionLocal()
    try:
        # 初始化管理员
        init_admin_user(db)
        print("✅ 管理员账号已初始化: admin / admin123")

        # 检查是否已有数据
        count = db.query(LotteryRecord).count()
        if count > 0:
            print(f"⚠️ 数据库中已有 {count} 条记录，跳过导入")
            return

        # 从 data.json 导入
        if not os.path.exists(DATA_FILE):
            print(f"⚠️ 未找到数据文件: {DATA_FILE}，使用示例数据")
            sample_data = [
                {"period": "2024150", "draw_date": "2024-05-30", "numbers": "36172"},
                {"period": "2024151", "draw_date": "2024-05-31", "numbers": "81052"},
                {"period": "2024152", "draw_date": "2024-06-01", "numbers": "93650"},
                {"period": "2024153", "draw_date": "2024-06-02", "numbers": "47061"},
                {"period": "2024154", "draw_date": "2024-06-03", "numbers": "25913"},
                {"period": "2024155", "draw_date": "2024-06-04", "numbers": "68340"},
                {"period": "2024156", "draw_date": "2024-06-05", "numbers": "12589"},
                {"period": "2024157", "draw_date": "2024-06-06", "numbers": "94726"},
                {"period": "2024158", "draw_date": "2024-06-07", "numbers": "30185"},
                {"period": "2024159", "draw_date": "2024-06-08", "numbers": "85613"},
                {"period": "2024160", "draw_date": "2024-06-09", "numbers": "72904"},
                {"period": "2024161", "draw_date": "2024-06-10", "numbers": "14387"},
                {"period": "2024162", "draw_date": "2024-06-11", "numbers": "56092"},
                {"period": "2024163", "draw_date": "2024-06-12", "numbers": "31847"},
                {"period": "2024164", "draw_date": "2024-06-13", "numbers": "09256"},
                {"period": "2024165", "draw_date": "2024-06-14", "numbers": "87634"},
                {"period": "2024166", "draw_date": "2024-06-15", "numbers": "45120"},
                {"period": "2024167", "draw_date": "2024-06-16", "numbers": "23978"},
                {"period": "2024168", "draw_date": "2024-06-17", "numbers": "60745"},
                {"period": "2024169", "draw_date": "2024-06-18", "numbers": "18463"},
                {"period": "2024170", "draw_date": "2024-06-19", "numbers": "79210"},
                {"period": "2024171", "draw_date": "2024-06-20", "numbers": "45692"},
                {"period": "2024172", "draw_date": "2024-06-21", "numbers": "03178"},
                {"period": "2024173", "draw_date": "2024-06-22", "numbers": "58934"},
                {"period": "2024174", "draw_date": "2024-06-23", "numbers": "26701"},
                {"period": "2024175", "draw_date": "2024-06-24", "numbers": "84365"},
                {"period": "2024176", "draw_date": "2024-06-25", "numbers": "12079"},
                {"period": "2024177", "draw_date": "2024-06-26", "numbers": "95841"},
                {"period": "2024178", "draw_date": "2024-06-27", "numbers": "37628"},
                {"period": "2024179", "draw_date": "2024-06-28", "numbers": "60513"},
                {"period": "2024180", "draw_date": "2024-06-29", "numbers": "49287"},
                {"period": "2024181", "draw_date": "2024-06-30", "numbers": "71345"},
                {"period": "2024182", "draw_date": "2024-07-01", "numbers": "08496"},
                {"period": "2024183", "draw_date": "2024-07-02", "numbers": "53219"},
                {"period": "2024184", "draw_date": "2024-07-03", "numbers": "81764"},
                {"period": "2024185", "draw_date": "2024-07-04", "numbers": "24603"},
                {"period": "2024186", "draw_date": "2024-07-05", "numbers": "69518"},
                {"period": "2024187", "draw_date": "2024-07-06", "numbers": "37492"},
                {"period": "2024188", "draw_date": "2024-07-07", "numbers": "05827"},
                {"period": "2024189", "draw_date": "2024-07-08", "numbers": "78149"},
                {"period": "2024190", "draw_date": "2024-07-09", "numbers": "42356"},
                {"period": "2024191", "draw_date": "2024-07-10", "numbers": "90683"},
                {"period": "2024192", "draw_date": "2024-07-11", "numbers": "13570"},
                {"period": "2024193", "draw_date": "2024-07-12", "numbers": "67294"},
                {"period": "2024194", "draw_date": "2024-07-13", "numbers": "84901"},
                {"period": "2024195", "draw_date": "2024-07-14", "numbers": "51736"},
                {"period": "2024196", "draw_date": "2024-07-15", "numbers": "26085"},
                {"period": "2024197", "draw_date": "2024-07-16", "numbers": "39842"},
                {"period": "2024198", "draw_date": "2024-07-17", "numbers": "74561"},
                {"period": "2024199", "draw_date": "2024-07-18", "numbers": "03298"},
            ]
            for d in sample_data:
                import_record(db, d)
            db.commit()
            print(f"✅ 导入了 {len(sample_data)} 条示例数据")
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        imported = 0
        for d in data:
            import_record(db, d)
            imported += 1

        db.commit()
        print(f"✅ 成功从 {DATA_FILE} 导入 {imported} 条记录")

    except Exception as e:
        db.rollback()
        print(f"❌ 导入失败: {e}")
        raise
    finally:
        db.close()


def import_record(db, d):
    """导入单条记录"""
    numbers = d["numbers"]
    existing = db.query(LotteryRecord).filter(LotteryRecord.period == d["period"]).first()
    if existing:
        return
    record = LotteryRecord(
        period=d["period"],
        draw_date=d["draw_date"],
        numbers=numbers,
        n1=int(numbers[0]),
        n2=int(numbers[1]),
        n3=int(numbers[2]),
        n4=int(numbers[3]),
        n5=int(numbers[4]),
    )
    db.add(record)


if __name__ == "__main__":
    import_data()

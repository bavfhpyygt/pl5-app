"""
导入排列五全部历史开奖数据
从 Excel 文件读取 7613 条真实数据，写入 SQLite 数据库
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from database import SessionLocal, engine, Base
from models import LotteryRecord
from sqlalchemy import text

EXCEL_PATH = r"C:\Users\ADMINI~1\AppData\Local\Temp\workbuddy-weixin-media\inbound\weixin-file-9ae564ef498215f9-排列五全部历史开奖数据.xlsx"

def main():
    # 读取 Excel
    print("正在读取 Excel 文件...")
    df = pd.read_excel(EXCEL_PATH, header=None)
    print(f"原始数据: {df.shape[0]} 行 x {df.shape[1]} 列")
    
    # 数据从第4行(index=3)开始，列映射:
    # col 0: 序号, col 1: 期号, col 2: 开奖日期, col 3: 开奖号码
    # col 4: 万位, col 5: 千位, col 6: 百位, col 7: 十位, col 8: 个位
    data_rows = df.iloc[3:]
    
    records = []
    skipped = 0
    
    for _, row in data_rows.iterrows():
        try:
            serial = row.iloc[0]
            period = str(row.iloc[1]).strip()
            draw_date = str(row.iloc[2]).strip()
            numbers = str(row.iloc[3]).strip()
            n1 = int(row.iloc[4])
            n2 = int(row.iloc[5])
            n3 = int(row.iloc[6])
            n4 = int(row.iloc[7])
            n5 = int(row.iloc[8])
            
            # 跳过无效行
            if period in ('nan', 'NaN', '', '期号') or len(period) < 3:
                skipped += 1
                continue
            
            records.append({
                'period': period,
                'draw_date': draw_date,
                'numbers': numbers,
                'n1': n1,
                'n2': n2,
                'n3': n3,
                'n4': n4,
                'n5': n5,
            })
        except (ValueError, TypeError, IndexError) as e:
            skipped += 1
            continue
    
    print(f"解析到 {len(records)} 条有效记录, 跳过 {skipped} 行")
    
    # 写入数据库
    print("正在清空旧数据...")
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM lottery_records"))
        db.commit()
        print("旧数据已清空")
        
        print(f"正在插入 {len(records)} 条记录...")
        batch_size = 500
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            db.bulk_insert_mappings(LotteryRecord, batch)
            db.commit()
            print(f"  已插入 {min(i+batch_size, len(records))}/{len(records)} 条")
        
        # 验证
        count = db.query(LotteryRecord).count()
        print(f"\n✅ 导入完成! 数据库共 {count} 条记录")
        
        # 显示最新5条
        latest = db.query(LotteryRecord).order_by(LotteryRecord.period.desc()).limit(5).all()
        print("\n最新5条:")
        for r in latest:
            print(f"  期号:{r.period} 日期:{r.draw_date} 号码:{r.numbers}")
        
        # 显示最早5条
        earliest = db.query(LotteryRecord).order_by(LotteryRecord.period.asc()).limit(5).all()
        print("\n最早5条:")
        for r in earliest:
            print(f"  期号:{r.period} 日期:{r.draw_date} 号码:{r.numbers}")
            
    finally:
        db.close()

if __name__ == "__main__":
    main()

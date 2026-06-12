"""
数据库初始化脚本 - 创建所有数据表
在 PythonAnywhere 上运行：python3.10 init_db.py
"""
import os
import sys

# 确保能导入项目模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
from models import LotteryRecord, User, SystemConfig


def init_database():
    """初始化数据库，创建所有表"""
    print("正在创建数据表...")

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    # 确认 data 目录存在
    from database import DB_DIR
    db_file = os.path.join(DB_DIR, "lottery.db")
    print(f"✅ 数据库文件位置: {db_file}")
    print("✅ 数据库初始化完成！")

    # 检查是否有默认管理员账号
    from sqlalchemy.orm import SessionLocal
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            # 创建默认管理员
            admin = User(username="admin", hashed_password="admin123", is_admin=True)
            db.add(admin)
            db.commit()
            print("✅ 已创建默认管理员账号: admin / admin123")
        else:
            print(f"✅ 管理员账号已存在: {admin.username}")
    finally:
        db.close()


if __name__ == "__main__":
    init_database()

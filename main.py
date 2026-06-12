"""
排列五数据分析与推荐系统 - 主入口
FastAPI 全栈应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from routers import lottery, admin

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="排列五数据分析系统",
    description="排列五历史数据分析、走势查看、智能推荐工具",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(lottery.router, prefix="/api", tags=["彩票数据"])
app.include_router(admin.router, prefix="/api/admin", tags=["后台管理"])

# 静态文件
app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "排列五数据分析系统"}

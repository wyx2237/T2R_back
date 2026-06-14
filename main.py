"""应用入口 —— 挂载路由、CORS、生命周期"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services import tool_store, metric_store
from routers import tools, metrics, compute


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时加载数据文件到内存"""
    tool_store.load_tools()
    metric_store.load_metrics()
    yield
    

app = FastAPI(title="T2R API", lifespan=lifespan)

# CORS：允许前端开发服务器跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由，统一 /api 前缀
app.include_router(tools.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(compute.router, prefix="/api")

@app.get("/")
def root():
    return {"data": "Welcome To Text2Rule Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5500, reload=True)
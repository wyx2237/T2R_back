# T2R API

医学临床计算指标管理系统。

## 环境构建

```bash
./setup_venv.sh
```

## 启动服务

```bash
# 激活虚拟环境
source venv/bin/activate

# 默认 8000 端口启动
uvicorn main:app --reload

# 指定端口
uvicorn main:app --reload --port 8080

# 指定 host + port（允许外部访问）
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--host` | `127.0.0.1` | `0.0.0.0` 监听所有网卡 |
| `--port` | `8000` | 服务端口 |
| `--reload` | 无 | 代码变更时自动重启 |

## API 概览

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/metrics` | 分页查询指标列表 |
| GET | `/api/metrics/{id}` | 获取指标详情 |
| POST | `/api/metrics` | 创建指标 |
| PUT | `/api/metrics/{id}` | 更新指标 |
| DELETE | `/api/metrics/{id}` | 删除指标 |

启动后访问 http://localhost:8000/docs 查看 Swagger 文档。

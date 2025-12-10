# 基于大模型的轻量化记忆系统

## 项目概述

这是一个基于大模型的轻量化记忆系统，使用FastAPI + SQLite3 + Chroma构建，能够帮助用户存储、管理和查询聊天历史记忆。系统会自动抽取聊天记录中的关键要素，并支持记忆的合并、过期清理等功能。

## 功能特性

### 核心功能
- ✅ 聊天历史提交与记忆生成
- ✅ 基于相似度的记忆查询
- ✅ 记忆的增删改查
- ✅ 自动要素抽取（基于大模型）
- ✅ 重复记忆自动合并
- ✅ 记忆过期清理策略

### 技术特性
- ✅ 轻量化设计，易于部署
- ✅ 模块化架构，便于扩展
- ✅ 支持多种大模型和Embedding服务
- ✅ RESTful API设计
- ✅ 自动生成API文档
- ✅ 定时任务管理
- ✅ 多租户支持（基于user_id和app_name）
- ✅ 完整的前端页面
- ✅ 响应式设计，适配不同设备

## 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: SQLite3
- **向量数据库**: Chroma 0.4.14
- **大模型**: OpenAI API
- **Embedding**: OpenAI Ada-002
- **ORM**: SQLAlchemy 2.0.23
- **Schema验证**: Pydantic 2.4.2
- **定时任务**: Schedule 1.2.0
- **前端框架**: Bootstrap 5 + jQuery

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/intohole/beeMemory.git
cd beeMemory
```

### 2. 创建虚拟环境（可选）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建`.env`文件，添加以下配置：

```env
# 应用配置
APP_NAME=MemoryService
APP_VERSION=1.0.0
DEBUG=True

# 数据库配置
DATABASE_URL=sqlite:///./memory.db

# Embedding服务配置
EMBEDDING_API_KEY=your-openai-api-key
EMBEDDING_MODEL=text-embedding-ada-002

# LLM服务配置
LLM_API_KEY=your-openai-api-key
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=1000

# Chroma配置
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_COLLECTION_NAME=user_memories

# 定时任务配置
MERGE_INTERVAL_MINUTES=60
CLEANUP_INTERVAL_MINUTES=1440
```

### 5. 启动应用

```bash
uvicorn app.main:app --reload
```

### 6. 访问应用

- **前端页面**: http://127.0.0.1:8000
- **API文档**: http://127.0.0.1:8000/docs
- **ReDoc文档**: http://127.0.0.1:8000/redoc

## 项目结构

```
app/
├── api/                    # API路由
│   ├── __init__.py
│   └── memory.py           # 记忆相关接口
├── core/                   # 核心配置
│   ├── __init__.py
│   ├── config.py           # 全局配置
│   └── task_scheduler.py   # 定时任务调度
├── crud/                   # 数据库操作（预留）
│   └── __init__.py
├── db/                     # 数据库相关
│   ├── __init__.py
│   ├── base.py             # 数据库基类
│   └── session.py          # 数据库会话
├── models/                 # 数据模型
│   ├── __init__.py
│   └── memory.py           # 记忆相关模型
├── schemas/                # Schema定义
│   ├── __init__.py
│   └── memory.py           # 记忆相关Schema
├── services/               # 业务逻辑服务
│   ├── __init__.py
│   ├── embedding/          # Embedding服务
│   │   ├── __init__.py
│   │   ├── base.py         # Embedding基类
│   │   └── openai.py       # OpenAI Embedding服务
│   ├── llm/                # 大模型服务
│   │   ├── __init__.py
│   │   ├── base.py         # LLM基类
│   │   └── openai.py       # OpenAI LLM服务
│   ├── memory/             # 记忆管理
│   │   ├── __init__.py
│   │   ├── manager.py      # 记忆管理器
│   │   ├── merger.py       # 重复合并
│   │   └── cleanup.py      # 记忆清理
│   └── chroma/             # Chroma客户端
│       ├── __init__.py
│       └── client.py       # Chroma客户端
├── static/                 # 前端静态文件
│   ├── index.html          # 主页面
│   ├── css/                # 样式文件
│   │   └── style.css       # 自定义样式
│   └── js/                 # 前端逻辑
│       ├── main.js         # 主逻辑
│       ├── submit.js       # 聊天历史提交
│       ├── query.js        # 记忆查询
│       ├── manage.js       # 记忆管理
│       └── config.js       # 配置管理
├── utils/                  # 工具函数
│   └── __init__.py
└── main.py                 # 应用入口
requirements.txt            # 依赖文件
README.md                   # 说明文档
.gitignore                  # Git忽略文件
```

## 核心功能说明

### 1. 记忆生成流程

1. 接收聊天历史请求
2. 存储聊天历史到数据库
3. 调用大模型抽取关键要素
4. 生成Embedding向量
5. 存储记忆到数据库和Chroma
6. 触发重复记忆合并检查

### 2. 记忆查询流程

1. 接收查询请求
2. 生成查询Embedding
3. 调用Chroma查询相似记忆
4. 更新记忆最后访问时间
5. 返回查询结果

### 3. 重复记忆合并

- 定时任务（默认每60分钟）
- 按user_id和app_name分组
- 计算记忆间相似度
- 合并相似度超过阈值的记忆
- 软删除重复记忆

### 4. 记忆清理策略

#### 过期策略
- **never**: 永不过期
- **last_access**: 根据最后访问时间过期

#### 清理流程
- 定时任务（默认每1440分钟）
- 清理已过期的记忆
- 清理长期未访问的记忆
- 同时清理数据库和Chroma数据

## API接口

### 1. 提交聊天历史

```
POST /api/memory/submit
```

**请求体**:
```json
{
  "user_id": "user123",
  "app_name": "myapp",
  "messages": [
    {
      "role": "user",
      "content": "你好，我是张三",
      "timestamp": "2023-01-01T00:00:00Z"
    },
    {
      "role": "assistant",
      "content": "你好，张三，有什么可以帮助你的吗？",
      "timestamp": "2023-01-01T00:00:01Z"
    }
  ]
}
```

### 2. 查询记忆

```
POST /api/memory/query
```

**请求体**:
```json
{
  "user_id": "user123",
  "app_name": "myapp",
  "query": "张三是谁？",
  "top_k": 5
}
```

### 3. 删除记忆

```
DELETE /api/memory/{memory_id}
```

### 4. 获取记忆配置

```
GET /api/memory/config?user_id=user123&app_name=myapp
```

### 5. 更新记忆配置

```
PUT /api/memory/config?user_id=user123&app_name=myapp
```

**请求体**:
```json
{
  "extraction_prompt": "自定义抽取提示词",
  "merge_threshold": 0.8,
  "expiry_strategy": "last_access",
  "expiry_days": 30
}
```

## 前端功能

### 1. 聊天历史提交
- 支持动态添加/删除聊天消息
- 表单验证
- 提交结果反馈

### 2. 记忆查询
- 支持设置查询参数
- 显示查询结果，包括相似度
- 结果按相似度排序

### 3. 记忆管理
- 直接输入记忆ID进行删除
- 删除确认提示

### 4. 配置管理
- 加载当前配置
- 编辑配置参数
- 保存配置

## 开发说明

### 代码风格

- 遵循PEP 8规范
- 使用Type hints
- 完整的文档字符串
- 模块化设计

### 运行测试

```bash
# 目前未实现测试，后续可添加
```

### 部署建议

#### 开发环境

```bash
uvicorn app.main:app --reload
```

#### 生产环境

```bash
# 使用gunicorn部署
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

#### Docker部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 扩展建议

1. **支持更多大模型**: 可扩展支持Anthropic Claude、Google Gemini等
2. **支持更多Embedding模型**: 可扩展支持开源Embedding模型
3. **添加缓存机制**: 缓存常用Embedding和LLM调用结果
4. **添加监控**: 监控API调用情况、记忆使用情况等
5. **支持多模态记忆**: 支持图片、语音等多模态内容
6. **添加权限管理**: 添加API密钥验证、用户认证等
7. **支持分布式部署**: 后续可扩展到分布式部署
8. **添加数据可视化**: 如记忆数量统计、使用频率等

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎提交Issue或Pull Request。

## 更新日志

### v1.0.0 (2025-01-01)
- 初始版本发布
- 实现了聊天历史提交与记忆生成
- 实现了基于相似度的记忆查询
- 实现了记忆的增删改查
- 实现了自动要素抽取
- 实现了重复记忆自动合并
- 实现了记忆过期清理策略
- 实现了完整的前端页面

---

**项目地址**: https://github.com/intohole/beeMemory
**API文档**: http://127.0.0.1:8000/docs
**前端页面**: http://127.0.0.1:8000
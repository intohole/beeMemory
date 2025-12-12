# 基于大模型的轻量化记忆系统

## 项目概述

这是一个基于大模型的轻量化记忆系统，使用FastAPI + SQLite3 + Chroma构建，能够帮助用户存储、管理和查询聊天历史记忆。系统会自动抽取聊天记录中的关键要素，并支持记忆的合并、过期清理等功能。系统采用单机单进程设计，无需Redis等额外组件，资源消耗低，易于部署和维护。

## 功能特性

### 核心功能
- ✅ 聊天历史提交与记忆生成
- ✅ 基于嵌入向量的记忆查询（替代关键词相似度）
- ✅ 聊天历史查询
- ✅ 记忆的增删改查
- ✅ 自动要素抽取（基于大模型）
- ✅ 重复记忆自动合并
- ✅ 记忆过期清理策略
- ✅ 应用级配置管理
- ✅ 基于app_name的记忆提取模板
- ✅ 优先级基于记忆管理
- ✅ 嵌入缓存机制
- ✅ 对话与记忆分离存储

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
- ✅ 可视化配置编辑
- ✅ 国内CDN依赖
- ✅ 统一日志系统
- ✅ 时区支持（默认Asia/Shanghai）
- ✅ 嵌入向量归一化
- ✅ 内存缓存机制

## 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: SQLite3
- **向量数据库**: Chroma 0.4.14
- **大模型**: 智谱AI (GLM-4-Flash)
- **Embedding**: 智谱AI (embedding-3)
- **ORM**: SQLAlchemy 2.0.23
- **Schema验证**: Pydantic 2.4.2
- **定时任务**: Schedule 1.2.0
- **前端框架**: Bootstrap 5 + jQuery
- **日志系统**: 统一JSON/标准格式日志
- **缓存机制**: 内存缓存
- **时区支持**: pytz (默认Asia/Shanghai)
- **配置管理**: YAML配置文件 + 环境变量

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

### 4. 配置方式

本项目支持多种配置方式，优先级从高到低依次为：
1. 环境变量
2. YAML配置文件
3. 默认值

#### 4.1 YAML配置文件（推荐）

创建`config.yaml`文件（可参考`config.example.yaml`模板），配置内容如下：

```yaml
# 应用配置
app:
  name: "MemoryService"
  version: "1.0.0"
  debug: true

# 数据库配置
database:
  url: "sqlite:///./memory.db"

# 大模型配置
llm:
  model: "glm-4-flash"
  api_key: "your_llm_api_key"
  base_url: "https://open.bigmodel.cn/api/paas/v4/"
  timeout: 360
  max_retries: 3
  temperature: 0.1
  max_tokens: 2048

# 嵌入服务配置
embedding:
  model: "embedding-3"
  api_key: "your_embedding_api_key"
  base_url: "https://open.bigmodel.cn/api/paas/v4/"
  timeout: 30
  max_retries: 3
  dimension: 1536
  normalize: true

# Chroma向量数据库配置
chroma:
  host: "localhost"
  port: 8999
  collection_name: "prompts"
  timeout: 30
  persist_directory: "./chroma_data"
  use_persistent_client: true

# 定时任务配置
scheduler:
  merge_interval_minutes: 60
  cleanup_interval_minutes: 1440

# 记忆管理默认配置
memory:
  default_extraction_prompt: "Extract key elements from the following conversation."
  default_merge_threshold: 0.8
  default_expiry_strategy: "last_access"
  default_expiry_days: 30
  max_memories_per_user: 1000
  max_memories_per_app: 500
  embedding_cache_ttl: 604800
  llm_cache_ttl: 604800

# 日志配置
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  use_json: false

# 时区配置
timezone: "Asia/Shanghai"
```

#### 4.2 环境变量

环境变量可以覆盖YAML配置文件中的值，格式为：`SECTION__KEY`（双下划线分隔）。例如：

```env
# 应用配置
APP__NAME=MyMemoryService
APP__DEBUG=True

# LLM配置
LLM__API_KEY=your_llm_api_key
LLM__MODEL=glm-4-flash
LLM__BASE_URL=https://open.bigmodel.cn/api/paas/v4/

# Embedding配置
EMBEDDING__API_KEY=your_embedding_api_key
EMBEDDING__MODEL=embedding-3

# Chroma配置
CHROMA__USE_PERSISTENT_CLIENT=true

# 时区配置
TIMEZONE=Asia/Shanghai
```

#### 4.3 配置模板

项目根目录提供了`config.example.yaml`模板文件，您可以直接复制为`config.yaml`并修改相关配置：

```bash
cp config.example.yaml config.yaml
# 然后编辑config.yaml文件
```

### 5. 启动应用

#### 使用启动脚本（推荐）

项目提供了便捷的启动脚本 `start.sh`，支持配置端口、运行环境等参数：

```bash
# 查看帮助信息
./start.sh --help

# 使用默认配置启动（开发环境，端口8080）
./start.sh

# 指定端口启动
./start.sh --port 8000

# 生产环境启动
./start.sh --port 8000 --env production

# 指定主机地址和配置文件
./start.sh --host 127.0.0.1 --port 8081 --config config.prod.yaml
```

#### 直接使用uvicorn启动

```bash
# 使用默认配置启动（开发环境）
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# 生产环境启动
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### 6. 访问应用

- **前端页面**: http://127.0.0.1:8080
- **API文档**: http://127.0.0.1:8080/docs
- **ReDoc文档**: http://127.0.0.1:8080/redoc

### 7. 插入样例数据

系统提供了样例数据插入脚本，方便快速测试功能：

```bash
python3 test_insert_sample.py
```

样例数据包含：
- 用户ID: test_user_123
- 应用名称: test_app
- 多条聊天记录和生成的记忆

可以使用以下查询示例测试：
- 张三的旅行计划是什么？
- 张三喜欢什么？
- 张三的职业是什么？

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
│       ├── chat_history.js # 聊天历史查询
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

### 1. 对话与记忆分离设计

- **聊天历史**: 完整存储用户和助手的对话记录
- **记忆**: 从对话中提取的关键信息，经过总结和要素提取
- **分离优势**: 
  - 节省存储空间
  - 提高查询效率
  - 支持不同的记忆提取策略
  - 便于记忆更新和合并

### 2. 记忆生成流程

1. 接收聊天历史请求
2. 存储聊天历史到数据库（独立表）
3. 对对话进行总结（基于大模型）
4. 提取关键要素（基于app_name配置的模板）
5. 生成Embedding向量（带缓存机制）
6. 存储记忆到数据库和Chroma
7. 触发重复记忆合并检查

### 3. 记忆查询流程

1. 接收查询请求
2. 生成查询Embedding（使用缓存）
3. 调用Chroma查询相似记忆（基于嵌入向量相似度）
4. 更新记忆最后访问时间
5. 返回查询结果，按相似度排序

### 4. 应用级配置管理

- 基于app_name的独立配置
- 支持可视化编辑
- 可配置项：
  - 提取模板
  - 对话更新轮数
  - 最大总结长度
  - 相似度阈值
  - 优先级权重
  - 自动总结开关
  - 要素提取开关

### 5. 基于嵌入向量的相似度计算

- 替代传统关键词相似度
- 基于大模型嵌入向量
- 支持多种嵌入模型
- 归一化向量处理
- 缓存嵌入结果，提高性能

### 6. 重复记忆合并

- 定时任务（默认每60分钟）
- 按user_id和app_name分组
- 计算记忆间嵌入向量相似度
- 合并相似度超过阈值的记忆
- 保留最新的记忆，软删除重复记忆
- 更新合并后的记忆嵌入

### 7. 优先级记忆管理

- 基于内容类型的优先级
- 支持用户自定义优先级
- 优先级影响记忆的保留策略
- 高优先级记忆优先保留

### 8. 记忆清理策略

#### 过期策略
- **never**: 永不过期
- **last_access**: 根据最后访问时间过期

#### 清理流程
- 定时任务（默认每1440分钟）
- 清理已过期的记忆
- 清理长期未访问的记忆
- 同时清理数据库和Chroma数据
- 按优先级顺序清理，低优先级先清理

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

### 6. 获取所有记忆列表

```
GET /api/memory/list?user_id=user123&app_name=myapp
```

### 7. 获取应用配置

```
GET /api/memory/app/config?app_name=myapp
```

### 8. 更新应用配置

```
PUT /api/memory/app/config?app_name=myapp
```

**请求体**:
```json
{
  "extraction_template": "自定义提取模板",
  "conversation_rounds": 3,
  "max_summary_length": 500,
  "enable_auto_summarize": true,
  "enable_element_extraction": true,
  "similarity_threshold": 0.8,
  "priority_weights": {
    "content_length": 0.3,
    "element_count": 0.4,
    "access_frequency": 0.3
  }
}
```

### 9. 获取用户应用配置

```
GET /api/memory/user/app/config?user_id=user123&app_name=myapp
```

### 10. 更新用户应用配置

```
PUT /api/memory/user/app/config?user_id=user123&app_name=myapp
```

**请求体**:
```json
{
  "use_default": true,
  "custom_config": {}
}
```

### 11. 查询聊天历史

```
GET /api/memory/chat/history?user_id=user123&app_name=myapp&session_id=optional_session_id
```

**查询参数**:
- `user_id` (必填): 用户ID
- `app_name` (必填): 应用名称
- `session_id` (可选): 会话ID，用于过滤特定会话的聊天记录

**响应示例**:
```json
{
  "success": true,
  "message": "Chat history retrieved successfully",
  "data": {
    "chat_history": [
      {
        "id": 1,
        "user_id": "user123",
        "app_name": "myapp",
        "session_id": "session_123",
        "role": "user",
        "content": "你好，我是张三",
        "timestamp": "2023-01-01T00:00:00Z"
      },
      {
        "id": 2,
        "user_id": "user123",
        "app_name": "myapp",
        "session_id": "session_123",
        "role": "assistant",
        "content": "你好，张三，有什么可以帮助你的吗？",
        "timestamp": "2023-01-01T00:00:01Z"
      }
    ]
  }
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
- 基于嵌入向量相似度计算

### 3. 记忆管理
- 支持加载指定用户和应用的所有记忆
- 列表展示记忆详情
- 支持直接删除记忆
- 删除确认提示

### 4. 配置管理
- 加载应用配置
- 可视化编辑配置参数
- 保存配置到数据库
- 支持基于app_name的独立配置

### 5. 应用级配置
- 基于app_name的记忆提取模板
- 可配置对话更新轮数
- 支持设置最大总结长度
- 可调整相似度阈值
- 支持配置优先级权重
- 自动总结和要素提取开关

### 6. 聊天历史查询
- 支持按用户ID和应用名称查询聊天历史
- 支持可选的会话ID过滤
- 聊天记录按时间顺序显示
- 区分用户和助手消息
- 现代化的聊天界面设计
- 支持多种消息样式

## 应用配置说明

### 应用级配置（AppConfig）

应用级配置是针对每个app_name的全局配置，所有使用该app_name的用户都会继承这些配置，除非用户设置了自定义配置。

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| extraction_template | str | 请从以下对话中提取关键信息... | 记忆提取的提示词模板 |
| conversation_rounds | int | 3 | 多少轮对话更新一次记忆 |
| max_summary_length | int | 500 | 记忆总结的最大长度 |
| enable_auto_summarize | bool | true | 是否启用自动总结 |
| enable_element_extraction | bool | true | 是否启用要素提取 |
| similarity_threshold | float | 0.8 | 记忆相似度阈值 |
| priority_weights | dict | {"content_length": 0.3, "element_count": 0.4, "access_frequency": 0.3} | 记忆优先级计算权重 |

### 用户应用配置（UserAppConfig）

用户应用配置允许用户覆盖默认的应用配置，设置自定义的记忆提取和管理策略。

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| use_default | bool | true | 是否使用默认应用配置 |
| custom_config | dict | {} | 自定义配置，覆盖默认配置 |

## 记忆模板配置

系统支持基于app_name配置不同的记忆提取模板，模板用于指导大模型从聊天记录中提取关键信息。模板可以在前端配置页面中进行编辑和保存。

### 模板示例

```
请从以下对话中提取需要长期记住的关键要素，包括但不限于：
1. 用户的基本信息（姓名、年龄、职业等）
2. 用户的偏好和习惯（喜欢的食物、音乐、运动等）
3. 用户的计划和安排（会议、旅行、重要日期等）
4. 用户的需求和问题
5. 重要的事实和事件
6. 其他需要记住的重要信息

请以JSON格式返回，键名要清晰易懂，值要准确简洁。确保JSON格式正确，不包含任何额外内容。如果没有可提取的要素，返回空JSON对象 {}。
```

## 优先级管理

### 记忆优先级计算

记忆优先级由以下因素决定：
1. **内容长度**: 较长的记忆通常更重要
2. **要素数量**: 包含更多要素的记忆更重要
3. **访问频率**: 经常访问的记忆更重要

优先级计算权重可以通过配置进行调整。

### 优先级等级

- **1级**: 最低优先级（不重要的记忆）
- **2级**: 低优先级
- **3级**: 中等优先级（默认）
- **4级**: 高优先级
- **5级**: 最高优先级（重要记忆）

## 性能优化

### 1. 嵌入缓存

- 缓存频繁使用的嵌入结果
- 减少大模型API调用次数
- 提高查询效率

### 2. 批量操作

- 批量处理聊天记录
- 批量生成嵌入向量
- 批量更新记忆

### 3. 定时任务优化

- 记忆合并任务：默认每60分钟运行一次
- 记忆清理任务：默认每1440分钟运行一次
- 可根据实际需求调整任务频率

### 4. 索引优化

- 数据库表添加适当索引
- Chroma向量索引优化
- 查询条件优化

## 部署与运维

### 环境要求

- Python 3.8+
- pip 21.0+

### 依赖安装

```bash
pip install -r requirements.txt
```

### 启动命令

```bash
# 开发环境
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# 生产环境建议使用gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8080
```

### 日志配置

系统使用统一的日志系统，支持JSON格式和标准格式，可以通过配置文件进行调整。

### 监控与维护

- 定期检查日志文件
- 监控应用内存使用情况
- 定期备份数据库文件
- 根据实际使用情况调整定时任务频率

## 最佳实践

### 1. 应用设计

- 为不同的业务场景创建不同的app_name
- 为每个app_name配置合适的提取模板
- 根据业务需求调整相似度阈值

### 2. 记忆管理

- 定期检查和清理过期记忆
- 根据业务重要性调整记忆优先级
- 合理设置记忆过期策略

### 3. 性能优化

- 合理设置嵌入缓存TTL
- 根据实际使用情况调整定时任务频率
- 监控系统资源使用情况，及时调整配置

### 4. 安全性

- 保护API密钥和配置文件
- 限制API访问权限
- 定期更新依赖库
- 监控异常访问情况

## 更新日志

### v1.1.0 (2025-12-12)
- 新增聊天历史查询功能
- 新增聊天历史查询API端点
- 新增聊天历史查询前端页面
- 优化记忆查询API，修复空结果问题
- 优化前端样式，修复tab白色文字问题
- 改进聊天记录的显示效果
- 增强应用级配置管理
- 优化数据库查询性能

### v1.0.0 (2025-12-11)
- 初始版本发布
- 实现了聊天历史提交与记忆生成
- 实现了基于嵌入向量的记忆查询
- 实现了记忆的增删改查
- 实现了自动要素抽取
- 实现了重复记忆自动合并
- 实现了记忆过期清理策略
- 实现了完整的前端页面
- 实现了应用级配置管理
- 实现了基于app_name的记忆提取模板
- 实现了优先级基于记忆管理
- 实现了嵌入缓存机制
- 实现了对话与记忆分离存储
- 实现了可视化配置编辑
- 实现了国内CDN依赖
- 实现了统一日志系统
- 实现了时区支持
- 实现了嵌入向量归一化

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
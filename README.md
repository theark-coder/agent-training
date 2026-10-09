# Agent Training

基于 Python、FastAPI、SQLAlchemy 和 MySQL 的 AI Agent 工程学习项目。

## 1. 项目介绍

本项目用于学习 Python 后端开发和 AI Agent 工程基础，逐步实现用户管理、会话管理、消息存储及后续的大模型调用功能。

当前阶段主要学习：

- FastAPI 接口开发
- Pydantic 请求参数校验
- Service 和 Repository 分层架构
- SQLAlchemy ORM
- MySQL 数据持久化

## 2. 技术栈

- Python 3.12+
- FastAPI
- SQLAlchemy
- MySQL
- PyMySQL
- uv
- pytest

## 3. 环境安装

首先安装 Python 3.12 或更高版本、MySQL 和 uv。

克隆项目：

```bash
git clone https://github.com/theark-coder/agent-training.git
cd agent-training
```

安装项目依赖：

```bash
uv sync
```

## 4. 数据库配置

确保 MySQL 服务已经启动。

首先在 MySQL 中创建数据库：

```sql
CREATE DATABASE IF NOT EXISTS agent_training
CHARACTER SET utf8mb4;
```

在项目根目录创建 `.env` 文件：

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=YOUR_PASSWORD
MYSQL_DATABASE=agent_training
```

根据实际环境修改连接信息。

`.env` 文件包含敏感配置，不要提交到 GitHub。

首次初始化数据库表：

```bash
uv run python -c "from agent_training.database import engine; from agent_training.models import Base; Base.metadata.create_all(bind=engine)"
```

此命令适用于当前开发阶段，后续可学习数据库迁移工具。

## 5. 启动项目

运行：

```bash
uv run uvicorn agent_training.main:app --reload
```

成功启动后，终端应显示类似：



打开 API 文档：

http://127.0.0.1:8000/docs

## 6. 接口示例
GET /health：检查应用是否能响应请求。



GET /ready：检查数据库是否可连接。
### 创建用户

`POST /users`

请求示例：

```json
{
  "id": 1001,
  "name": "test_user",
  "role": "student"
}
```

注意：用户 ID 必须唯一。重复提交相同 ID 会导致主键冲突。

### 创建会话

`POST /conversations`

请求示例：

```json
{
  "user_id": 1001,
  "title": "Day 1 Test Conversation"
}
```

成功后，接口返回会话 ID、用户 ID 和标题。

### 创建消息

`POST /messages`

请求示例：

```json
{
  "conversation_id": 1,
  "role": "user",
  "content": "Hello Agent"
}
```

其中 `conversation_id` 应替换为实际创建成功的会话 ID。

## 7. 数据验证

在 MySQL 中运行：

```sql
SELECT * FROM users;
SELECT * FROM conversations;
SELECT * FROM messages;
```

确认相应记录已经保存。

## 8. 测试

运行已有的自动化测试：

```bash
uv run pytest
```

## 9. 项目结构

```text
agent-training/
├── src/agent_training/
│   ├── main.py                 # HTTP 路由
│   ├── schemas.py              # 请求/响应校验
│   ├── config.py               # 环境变量配置
│   ├── database.py             # SQLAlchemy 引擎和 Session
│   ├── models.py               # ORM 数据模型
│   ├── repositories/           # 数据访问层
│   ├── services/               # 业务逻辑层
│   ├── async_demo.py           # 异步、超时、并发实验
│   └── llm_test.py             # 模型调用实验代码
├── tests/                      # 自动化测试
├── .env.example                # 配置模板，无真实密钥
├── pyproject.toml
├── uv.lock
└── README.md
```

主要模块职责：

- `main.py`：API 路由和请求处理
- `database.py`：数据库连接和会话管理
- `models.py`：ORM 数据模型
- `repositories/`：数据库访问
- `services/`：业务逻辑

## 10. 学习进展

Day 1：Python 工程结构、FastAPI 调用链、数据库连接与会话创建。

后续继续完善输入校验、环境配置、事务、测试和 Agent 能力。
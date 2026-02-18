# 完整项目目录结构与图谱

---

## 📂 **完整目录树**

```
C:\Users\10952\.openclaw\
├── agents\
│   └── main\                          # OpenClaw主代理
│       ├── sessions\                  # 会话管理
│       ├── agent\                     # Agent核心
│       └── ...                        # 其他文件
│
├── canvas\                            # Canvas系统
├── cron\                              # Cron任务调度
├── devices\                           # 设备管理
├── identity\                          # 身份认证
│   └── device-auth.json
│
├── workspace\                         # 【当前工作区 - 主要开发区】⭐⭐⭐
│   ├── AGENTS.md                      # 代理信息
│   ├── BACKUP_COMPLETE_REPORT_DINGTALK.md
│   ├── BACKUP_COMPLETE_REPORT.md
│   ├── BACKUP_AND_GIT_STATUS.md
│   ├── BOOTSTRAP.md
│   ├── HEARTBEAT.md
│   ├── IDENTITY.md                    # 身份信息
│   ├── MEMORY.md                      # 长期记忆 ⭐
│   ├── PROJECT_LIST.md                # 项目清单 ⭐
│   ├── SOUL.md                        # Agent灵魂
│   ├── TODO.md                        # 项目待办 ⭐
│   ├── TOOLS.md
│   ├── USER.md                        # 用户信息
│   ├── full_backup_all.py             # 完整备份工具
│   ├── quick_backup.py                # 快速备份工具
│   ├── test_memory*.py                # 记忆测试脚本
│   ├── test_redis_cache.ps1
│   │
│   ├── memory\                        # 记忆系统（短期）
│   │   ├── 2026-02-15.md
│   │   ├── 2026-02-15_API_RATE_LIMIT.md
│   │   ├── 2026-02-16.md
│   │   ├── 2026-02-16_BACKUP_COMPLETE.md
│   │   ├── 2026-02-16_MEMORY_SYSTEM_VERIFICATION.md
│   │   ├── 2026-02-16_multi_model_integration.md
│   │   ├── THREE_LAYER_MEMORY_TEST_REPORT.md
│   │   └── v1_memory.db               # SQLite数据库
│   │
│   └── openclaw_async_architecture\   # 【V2 MVP项目】⭐⭐⭐
│       ├── 01_technical_proposal.md
│       ├── 02_security_and_crash_protection.md
│       ├── 03_benefits_and_optimization.md
│       ├── 04_development_standards.md
│       ├── API_CONFIG_FINAL.json
│       ├── API_IMPLEMENTATION_GUIDE.md
│       ├── API_SPEED_TEST_COMPLETE_REPORT.md
│       ├── API_SPEED_TEST_FINAL_REPORT.md
│       ├── API_SPEED_TEST_RESULTS.md
│       ├── BACKUP_DEPLOYMENT.md
│       ├── FEASIBILITY_INVESTIGATION.md
│       ├── MULTI_MODEL_STRATEGY_DISCUSSION.md
│       ├── README.md
│       ├── api_quick_test.py
│       ├── api_speed_test.py
│       ├── test_mvp.py
│       ├── test_v1_api.py
│       ├── test_v1_memory.py
│       ├── test_zhipu.py
│       │
│       └── mvp\                       # MVP核心代码
│           ├── launcher.py
│           ├── check_env.py
│           ├── requirements.txt
│           ├── README.md
│           ├── .env.example
│           │
│           ├── src\
│           │   ├── gateway\           # Gateway（FastAPI）
│           │   │   ├── __init__.py
│           │   │   └── main.py        # Gateway主程序
│           │   │
│           │   ├── worker\            # Worker
│           │   │   ├── __init__.py
│           │   │   ├── main.py        # Worker主程序
│           │   │   ├── worker.py      # V1 API调用
│           │   │   └── enhanced_worker.py  # 多模型Worker
│           │   │
│           │   ├── queue\             # 任务队列
│           │   │   ├── __init__.py
│           │   │   └── redis_queue.py
│           │   │
│           │   ├── store\             # 存储层
│           │   │   ├── __init__.py
│           │   │   ├── redis_store.py
│           │   │   └── hybrid_store.py  # SQLite+Redis混合
│           │   │
│           │   └── common\            # 公共模块
│           │       ├── __init__.py
│           │       ├── config.py      # 配置管理
│           │       ├── models.py      # 数据模型
│           │       ├── v1_memory_integration.py  # V1集成
│           │       ├── multi_model_limiter.py    # 速率限制器
│           │       ├── task_classifier.py        # 任务分类器
│           │       └── load_balancer.py          # 负载均衡器
│           │
│           ├── tests\
│           │   ├── __init__.py
│           │   └── test_mvp.py
│           │
│           └── src\
│               └── common\
│                   └── __init__.py
│
└── openclaw.cherry.json              # OpenClaw配置

---

D:\.openclaw\                        # 【旧工作区 - 历史代码区】⭐⭐
└── workspace\                        # 老workspace
    ├── agents\                       # 【钉钉代理系统】⭐
    │   └── main\
    │       ├── sessions\
    │       └── agent\
    │
    ├── claw_agent_demo\              # 【钉钉AI Agent】⭐⭐⭐（17个文件）
    │   ├── config\                   # 配置
    │   │   └── __init__.py
    │   │
    │   ├── demo\                     # 演示代码
    │   │   ├── dingtalk.py           # 钉钉适配器（最关键）
    │   │   ├── crypto_utils.py       # 加密解密（最重要）⭐
    │   │   ├── server.py             # Flask服务器
    │   │   ├── agent.py              # Agent处理
    │   │   ├── llm_wrapper.py        # LLM包装
    │   │   └── test_webhook.py       # Webhook测试
    │   │
    │   ├── .env                      # 【环境配置文件】包含API密钥 ⚠️
    │   ├── .env.example              # 配置示例
    │   ├── requirements.txt          # Python依赖
    │   ├── README.md                 # 完整文档 ⭐
    │   ├── QUICKSTART.md             # 快速开始
    │   ├── CPOLAR_GUIDE.md           # cpolar指南
    │   ├── NGROK_GUIDE.md            # ngrok指南
    │   ├── ENV_SETUP.md              # 环境配置
    │   └── __init__.py
    │
    ├── chapters_export\              # 章节导出工具
    ├── config\                       # 配置文件
    ├── core\                         # 核心代码
    ├── docs\                         # 文档
    ├── embeddings_backup\            # Embedding备份
    ├── llm\                          # LLM相关
    ├── logs\                         # 日志文件
    ├── memory\                       # 记忆系统
    ├── memory_system\                # 记忆系统
    ├── novel\                        # 小说项目
    ├── novel_memory\                 # 小说记忆
    ├── novel_tools\                  # 小说工具
    ├── openclaw_memory_system\       # OpenClaw记忆系统
    ├── openclaw_v2\                  # 【V2实验性版本】
    ├── openclaw钉钉系统\             # 钉钉系统备份
    ├── pipelines\                    # 工具流水线
    ├── scripts\                      # 脚本
    ├── state\                        # 状态管理
    ├── tools\                        # 工具集
    ├── workspace\                    # 子workspace
    └── _archive\                     # 归档区

---

D:\ClawBackups\                      # 【备份目录】⭐⭐⭐
├── ares\                            # ARES项目备份
│   └── initial\
│
├── CLAW_COMPLETE_BACKUP_v1\          # V1完整备份（2026-02-14）
│   ├── memory\
│   ├── novel_tools\
│   ├── pipelines\
│   └── tools\
│
├── WORKSPACE_BACKUP_20260216_024746.zip     # 当前workspace备份
├── WORKSPACE_BACKUP_20260216_024746.txt
├── FULL_WORKSPACE_BACKUP_20260216_030839.zip # 【完整备份】⭐⭐⭐
│   └── 包含：
│       ├── workspace_current/       # C:\Users\10952\.openclaw\workspace
│       └── workspace_legacy/        # D:\.openclaw\workspace
│
└── FULL_WORKSPACE_BACKUP_20260216_030839.txt
```

---

## 🗺️ **项目关系图谱**

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw 生态系统                          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    【当前工作区】       【旧工作区】         【备份区】
    (开发中)            (历史代码)           (安全备份)
  C:\...\.openclaw\   D:\.openclaw\         D:\ClawBackups\
     workspace/          workspace/
```

---

### 📍 **当前工作区** - 主要开发区

```
C:\Users\10952\.openclaw\workspace\
│
├── 【核心文档】(9个)
│   ├── MEMORY.md          ← 长期记忆（最重要）
│   ├── TODO.md            ← 项目待办清单
│   ├── PROJECT_LIST.md    ← 项目总览
│   ├── SOUL.md            ← Agent灵魂
│   ├── USER.md            ← 用户信息
│   ├── TOOLS.md           ← 工具笔记
│   └── AGENTS.md          ← 代理信息
│
├── 【V2 MVP项目】⭐⭐⭐
│   └── openclaw_async_architecture/
│       ├── mvp/src/       ← 核心代码
│       │   ├── gateway/   ← Gateway (FastAPI)
│       │   ├── worker/    ← Worker (多模型)
│       │   ├── queue/     ← Redis队列
│       │   ├── store/     ← SQLite+Redis存储
│       │   └── common/    ← 多模型策略
│       │   │   ├── multi_model_limiter.py
│       │   │   ├── task_classifier.py
│       │   │   └── load_balancer.py
│       └── 文档（14个，~80,000字）
│
├── 【记忆系统】(8个文件)
│   └── memory/
│       ├── 2026-02-15.md
│       ├── 2026-02-16.md
│       └── v1_memory.db   ← SQLite数据库
│
└── 【备份工具】
    ├── full_backup_all.py      ← 完整备份工具
    └── quick_backup.py         ← 快速备份工具
```

---

### 📍 **旧工作区** - 历史代码区

```
D:\.openclaw\workspace\
│
├── 【钉钉系统】⭐⭐⭐
│   └── claw_agent_demo/          ← 钉钉AI Agent
│       └── demo/
│           ├── dingtalk.py       ← 钉钉适配器
│           ├── crypto_utils.py   ← 加密解密 ⭐
│           ├── server.py         ← Flask服务器
│           ├── agent.py          ← Agent核心
│           ├── llm_wrapper.py    ← LLM包装
│           └── test_webhook.py   ← 测试脚本
│       ├── .env                  ← 环境配置 ⚠️
│       └── 文档（7个，~24,000字）
│
├── 【钉钉代理系统】
│   └── agents/main/
│       └── sessions/
│
├── 【小说工具】
│   ├── novel_tools/
│   └── novel_memory/
│
├── 【V2实验版本】
│   └── openclaw_v2/
│
└── 【其他工具】
    ├── pipelines/
    ├── tools/
    ├── scripts/
    └── ...
```

---

### 📍 **备份区** - 安全备份区

```
D:\ClawBackups\
│
├── 【最新完整备份】⭐⭐⭐
│   ├── FULL_WORKSPACE_BACKUP_20260216_030839.zip
│   │   ├── workspace_current/     ← 当前workspace
│   │   │   ├── openclaw_async_architecture/  ← V2 MVP
│   │   │   ├── memory/               ← 记忆系统
│   │   │   └── *.md                  ← 文档
│   │   │
│   │   └── workspace_legacy/      ← 旧workspace
│   │       ├── claw_agent_demo/    ← 钉钉系统
│   │       ├── agents/
│   │       ├── novel_tools/
│   │       └── ...
│   │
│   └── FULL_WORKSPACE_BACKUP_20260216_030839.txt
│
├── 【旧备份】
│   ├── CLAW_COMPLETE_BACKUP_v1/  ← V1备份（2026-02-14）
│   │   ├── memory/
│   │   ├── novel_tools/
│   │   ├── pipelines/
│   │   └── tools/
│   │
│   └── ares/
│       └── initial/
│
└── 【临时备份】
    ├── WORKSPACE_BACKUP_20260216_024746.zip
    └── WORKSPACE_BACKUP_20260216_024746.txt
```

---

## 🔗 **项目关联关系图**

```
┌─────────────────────────────────────────────────────────┐
│                       用户（博）                          │
│                  目标：赚钱买显卡                          │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    【主要项目】        【完成项目】        【工具】
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │  ARE    │       │ 钉钉系统 │       │ 记忆系统│
   │  全能   │       │ AI Agent │       │         │
   │  系统   │       │         │       │         │
   └────┬────┘       └────┬────┘       └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │ V2 MVP 基础 │
                    │ 异步架构    │
                    │ 多模型策略  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ 三层记忆系统 │
                    │ SQLite+Redis│
                    └──────┬──────┘
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
 ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
 │Gateway  │          │ Worker  │          │ 队列   │
 │ FastAPI │          │ 多模型  │          │ Redis  │
 └─────────┘          └─────────┘          └─────────┘
```

---

## 📊 **快速查找表**

| 要找什么？ | 位置 | 优先级 |
|-----------|------|--------|
| **V2 MVP代码** | `C:\...\.openclaw\workspace\openclaw_async_architecture\mvp\src\` | ⭐⭐⭐ |
| **钉钉系统** | `D:\.openclaw\workspace\claw_agent_demo\` | ⭐⭐⭐ |
| **项目待办** | `C:\...\.openclaw\workspace\TODO.md` | ⭐⭐ |
| **项目清单** | `C:\...\.openclaw\workspace\PROJECT_LIST.md` | ⭐⭐ |
| **长期记忆** | `C:\...\.openclaw\workspace\MEMORY.md` | ⭐⭐⭐ |
| **最新备份** | `D:\ClawBackups\FULL_WORKSPACE_BACKUP_20260216_030839.zip` | ⭐⭐⭐ |
| **多模型策略** | `mvp/src/common/` (3个文件) | ⭐⭐ |
| **文档总览** | `openclaw_async_architecture/` (14个文档) | ⭐ |

---

## 💡 **简单总结**

### 3个主要区域

1. **当前工作区**（C盘）- 开发中的项目
   - V2 MVP（新项目）⭐⭐⭐
   - 记忆系统
   - 项目管理文档

2. **旧工作区**（D盘）- 历史代码
   - 钉钉系统（有问题，但已备份）⭐⭐⭐
   - 小说工具
   - 钉钉代理系统

3. **备份区**（D盘）- 安全备份
   - 最新完整备份（496文件，1.36MB）⭐⭐⭐
   - V1旧备份
   - ARES项目

---

**最后更新：** 2026-02-16 03:15
**维护者：** Claw + 博

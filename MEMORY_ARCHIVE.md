# MEMORY_ARCHIVE.md - 历史记忆归档

**归档时间：** 2026-02-18 17:10  
**归档原因：** MEMORY.md 超过 20000 字符限制，需要精简  
**归档范围：** 2026-02-18 之前的历史项目记录

---

## 📦 归档内容

### 1. 钉钉机器人项目（2026-02-12 ~ 2026-02-13）

**时间线：**
- 2026-02-12 晚 - 开始钉钉 Demo 开发
- 2026-02-13 01:20 - 钉钉 Demo 成功（明文 webhook）
- 2026-02-13 01:30-02:45 - Agent 框架开发
- 2026-02-13 完整 - 真正寄宿体架构完成
- 2026-02-13 15:00 - 加密消息处理（从老代码复制）

**目录结构：**
```
C:\Users\10952\.openclaw\
├── workspace\
│   ├── agents\ # Agent 框架（主）
│   │   ├── main.py # Flask 入口（端口 3000）
│   │   ├── openclaw_api.py # HTTP API（端口 3001）
│   │   ├── openclaw_poller.py # 消息轮询器
│   │   ├── core\agent.py # Agent 核心
│   │   └── .env # 环境配置
│   └── platforms\dingtalk\ # 平台适配器
│       └── __init__.py # DingtalkAdapter
└── claw_agent_demo\ # 老代码（参考）
    └── demo\
        ├── dingtalk.py # 老的 DingtalkPlatform
        └── crypto_utils.py # 完整的加解密实现
```

**关键技术点：**
1. **加密解密**
   - `crypto_utils.py` 完整实现（与 Java 官方代码一致）
   - IV 从 aesKey 前 16 字节取
   - AES/CBC/NoPadding 模式
   - 手动去除 PKCS7 Padding（块大小 32）
   - 格式：`random(16) + msg_len(4，网络字节序) + msg + corpId`
   - 验证 CorpId 必须匹配

2. **签名验证**
   - 和 Java 代码 getSignature 一致
   - 对 `[token, timestamp, nonce, encrypt]` 排序
   - 拼接后计算 SHA-1

3. **PM2 服务管理**
   - 已部署
   - `claw-agent` - Flask 服务（端口 3000）
   - `openclaw-api` - HTTP API（端口 3001）
   - Web UI: http://localhost:5000

**环境配置：**
- Python 3.11
- Anaconda 环境：`claw_agent_demo`
- 依赖：flask, requests, pycryptodome, python-dotenv

**钉钉配置：**
- App Key: `dingqmlx7x...`
- Token 和 EncodingAESKey 在 `.env` 中配置

**成功案例：**
- ✅ 钉钉 webhook 接收@消息（明文）
- ✅ 加密消息解密（2026-02-13 15:00 修复）
- ✅ 异步处理（避免 1 秒超时）
- ✅ 身份和记忆共享（SOUL.md + MEMORY.md）
- ✅ PM2 服务管理 + Web UI

**遇到的问题：**
1. **编码问题（2026-02-13 14:50）**
   - Windows GBK 编码无法处理 emoji
   - 解决：`sys.stdout.reconfigure(encoding='utf-8')`

---

### 2. 工具系统

#### MemorySystem（2026-02-13 集成）
- 三层记忆系统（SQLite + ChromaDB + Redis）
- Level 1 已整合，逐渐被 MemorySystem 替代

#### 其他工具
- 记忆搜索系统（向量搜索）
- 完整备份系统（D 盘备份，一键恢复）
- PM2 服务管理（Web UI + 系统托盘）

---

### 3. 学习记录

**已学习技术：**
1. 钉钉 Webhook - 加密/签名验证
2. PM2 - 进程管理、监控
3. Python 加密 - pycryptodome、AES/CBC
4. Flask 异步 - 避免 webhook 超时
5. cpolar - 内网穿透

**技术债务：** 暂无明显技术债务

---

### 4. 项目统计

**完成项目：**
1. **钉钉 AI Agent** - 2026-02-13 完成
   - 时间：约 8 小时（2 天）
   - 成功：webhook、加密解密、PM2 管理、Web UI
   - 支持平台：钉钉
   - 模型：NVIDIA GLM-4.7

---

### 5. 高优先级问题

#### exec 命令输出延迟问题（2026-02-14 00:56→01:28）
**优先级：** 🔴 非常高  
**状态：** ✅ 已解决（立即可用）

**问题描述：**
- 执行 `exec` 命令时，输出延迟 1-2 分钟
- 命令实际只需 2-3 秒完成
- 严重影响用户体验

**根本原因：**
`background=true` 模式下，系统默认 60 秒轮询一次输出

**解决方案：**
- **短命令（<30 秒）：** 前台 PTY 模式 `exec pty=true`
- **长期服务（>1 分钟）：** 后台模式 `exec background=true`

**参数对比：**
| 模式 | 参数 | 适用场景 | 延迟 |
|------|------|----------|------|
| 前台 PTY ⭐ | `pty=true, background=false` | 短命令（<30 秒） | <1 秒 ✅ |
| 后台 | `background=true` | 长期服务（>1 分钟） | 60 秒 |

---

### 6. 用户偏好

#### Token 使用预警（2026-02-15 22:39）
- 预警阈值：> 80%
- 触发条件：主会话状态显示 > 80%
- 实施方式：在消息开头提示

#### 主会话状态显示格式（2026-02-14 00:35）
```
## 📊 主会话状态
**XX%（X / Y tokens）**
- ✅ 状态：安全范围/中高/高
- 📝 建议：继续对话/开新会话
```

---

### 7. 关键词索引

**钉钉：** webhook, 加密，解密，签名，sessionWebhook, 明文，验证，corpId  
**工具：** memory_search, PM2, cpolar, Flask, pycryptodome  
**项目：** claw-agent, openclaw-api, dingtalk-adapter, crypto-utils  
**问题：** GBK 编码，emoji, UnicodeEncodeError, PKCS7, Padding, unpad

---

*归档时间：2026-02-18 17:10*  
*此文件包含历史项目记录，新内容请写入 memory/YYYY-MM-DD.md*

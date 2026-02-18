# 重启后必读 - 快速恢复指南

## 🎯 重要提醒（优先级：P0）

### 2026-02-17 重要更新

**V2使用规则（重启后必须执行）**
- 📄 详细规则：`memory/V2_RULES.md`
- 📄 速查卡：`memory/V2_QUICK_REFERENCE.md`
- 🛠️ 决策助手：`v2_decision_helper.py`

**规则核心：**
```
长任务用V2
多任务用V2
要流式用V2
高频用V2
```

---

## 🚀 立即开始使用

### 1. V2决策助手（判断何时用V2）

```bash
# 快速判断
python v2_decision_helper.py 编译项目

# 查看所有规则
python v2_decision_helper.py
```

### 2. V2 MVP系统（已100%完成）

**Gateway流式对话：**
```bash
cd openclaw_async_architecture/streaming-service
python use_gateway.py --interactive
```

**Worker Pool：**
```bash
cd openclaw_async_architecture/mvp
python tests/test_worker_pool_simple.py
```

---

## 📚 重要文档位置

| 文档 | 路径 | 说明 |
|------|------|------|
| **V2规则详细** | `memory/V2_RULES.md` | 完整的使用规则 |
| **V2速查卡** | `memory/V2_QUICK_REFERENCE.md` | 三句话记住 |
| **V2完成报告** | `memory/V2_MVP_COMPLETED.md` | MVP完成总结 |
| **历史记录** | `memory/2026-02-17.md` | 今日完整记录 |

---

## 🔍 搜索重要信息

```bash
# 搜索V2规则
memory_search "V2使用规则"

# 搜索V2 MVP
memory_search "V2 MVP"

# 搜索效率提升
memory_search "效率提升"
```

---

## ⚡ 快速恢复步骤

### 第1步：了解重要规则（5分钟）

1. 阅读 `memory/V2_QUICK_REFERENCE.md`
2. 测试 `v2_decision_helper.py 编译项目`
3. 理解何时使用V2

### 第2步：启动服务（2分钟）

1. Gateway：`python use_gateway.py --interactive`
2. 验证流式对话

### 第3步：回顾项目情况（10分钟）

1. 检查 `memory/PROJECT_STREAMING.md`
2. 检查 `memory/V2_MVP_COMPLETED.md`
3. 了解当前项目状态

---

## 🎯 当前里程碑

**✅ 已完成：**
- V2 MVP 100%完成
- Gateway流式服务
- Worker Pool多Worker并发
- V2使用规则制定
- V2决策助手

**⚙️ 进行中：**
- 场景扩展
- 性能优化
- 文档完善

**📋 待办：**
- MVP全能AI整合
- 渐进式脱离OpenClaw
- 对齐终极目标（超越JARVIS）

---

## 💡 重要记忆点

1. **永远不要考虑时间成本** - 质量第一
2. **V2规则是强制性的** - 长任务必须用V2
3. **Gateway流式体验极佳** - 用户验证"很不错"
4. **快速原型法优于复杂集成** - 立即可用

---

**🔴 记住：重启后第一件事：阅读 V2_QUICK_REFERENCE.md！**

---

**最后更新：** 2026-02-17 01:55
**负责人：** Claw

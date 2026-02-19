# OpenClaw Control Center v4.0

**🎉 P0 + P1 功能 100% 完成！测试通过率 100%！**

[![Version](https://img.shields.io/badge/version-4.0-orange.svg)](https://github.com/zhoushibo/project_manager_gui)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey.svg)](https://www.microsoft.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-57%2F57%20passed-brightgreen.svg)](test_all_features.py)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](test_all_features.py)

---

## 📖 简介

OpenClaw Control Center 是一个功能强大的 AI 开发环境管理控制台，集成了服务管理、知识库、AI 学习、项目跟踪等核心功能。专为 AI 开发者设计，让开发环境管理变得简单高效。

### ✨ 核心亮点

- 🚀 **一键启动** - 自动启动所有开发服务
- 🧠 **AI 学习** - 集成 V2 学习系统，自动学习新知识
- 📚 **知识管理** - 快速搜索和管理知识库
- 🔍 **智能诊断** - 自动检测并修复问题
- 🎨 **多主题** - 3 套精美主题随意切换
- 💻 **后台运行** - 系统托盘支持，最小化不中断
- ⚙️ **配置管理** - 图形化编辑项目配置

---

## 🎯 功能特性

### 8 个核心标签页

| 标签页 | 功能 | 状态 |
|--------|------|------|
| 🚀 快速启动 | 一键启动所有服务 | ✅ 完成 |
| 📚 知识库 | 搜索/导入/管理知识 | ✅ 完成 |
| 🧠 V2 学习 | AI 自动学习系统 | ✅ 完成 |
| 📊 仪表盘 | 实时监控服务状态 | ✅ 完成 |
| 🔍 智能诊断 | 自动检测修复问题 | ✅ 完成 |
| 🔧 服务管理 | 手动控制服务 | ✅ 完成 |
| ⚙️ 配置编辑器 | 图形化配置管理 | ✅ 完成 |
| 📁 项目管理 | 项目进度跟踪 | ✅ 完成 |

### 增强功能

- 🎨 **3 套主题** - 深色/浅色/赛博朋克
- 💻 **系统托盘** - 后台运行 + 快捷菜单
- 🔔 **托盘通知** - 实时状态提醒
- 📊 **14+ 项目** - 完整项目跟踪
- 🧪 **自动化测试** - 57 项测试 100% 通过

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd project_manager_gui
pip install -r requirements.txt
```

**依赖列表：**
- PyQt5 >= 5.15.0
- psutil >= 5.9.0
- streamlit >= 1.28.0 (知识库 Web UI)

### 2. 启动程序

```bash
python main_v3.py
```

### 3. 一键启动服务

1. 程序启动后，默认显示 **快速启动** 标签页
2. 点击 **"🚀 一键启动服务"** 按钮
3. 等待进度条完成（约 5-10 秒）
4. 切换到 **仪表盘** 查看服务状态

### 4. 开始使用

- **搜索知识：** [📚 知识库] → 输入关键词 → 搜索
- **学习新知：** [🧠 V2 学习] → 输入主题 → 开始学习
- **查看状态：** [📊 仪表盘] → 实时监控
- **管理项目：** [📁 项目管理] → 更新进度

---

## 📋 功能详解

### 🚀 快速启动

一键自动启动 Gateway 和知识库服务，无需手动操作。

**特点：**
- 顺序启动（Gateway → 知识库）
- 实时进度显示
- 后台异步执行
- 错误自动处理

### 📚 知识库

快速搜索和管理知识库内容。

**功能：**
- 语义搜索（支持中英文）
- 相似度百分比显示
- 一键导入文件
- Web UI 快速访问

### 🧠 V2 学习

集成 V2 学习系统，自动学习新知识并保存到知识库。

**学习模式：**
- ⚡ 快速学习（10-15 秒，1 个视角）
- 🔍 深度学习（20-30 秒，3 个视角）⭐ 推荐
- 📖 全面学习（40-60 秒，5 个视角）

**特性：**
- 实时进度监控
- 学习历史记录
- 自动保存到知识库
- Worker 数量可调（1-5）

### 📊 仪表盘

实时监控系统状态和服务健康度。

**监控内容：**
- 服务运行状态
- CPU/内存使用率
- 端口占用情况
- 进程详细信息

### 🔍 智能诊断

自动检测并修复常见问题。

**检测项目：**
- 端口占用检测（8001/8501）
- 依赖安装检测（Streamlit/PyQt5）
- 配置文件完整性
- 服务状态检查

**一键修复：**
- 停止占用端口的进程
- 安装缺失的依赖
- 修复配置文件格式

### 🔧 服务管理

手动控制各个服务的启动和停止。

**支持服务：**
- Gateway（端口 8001）
- 知识库 Web UI（端口 8501）

**操作：**
- 启动/停止/重启
- 查看日志
- 在浏览器中打开

### ⚙️ 配置编辑器

图形化编辑项目配置和系统设置。

**功能：**
- 编辑项目信息（名称/状态/完成度）
- 添加新项目
- 管理缺失项和下一步计划
- 保存/加载配置

### 📁 项目管理

查看所有项目进度和状态。

**特性：**
- 完成度可视化（进度条）
- 状态标签（规划中/进行中/已完成）
- 多种排序方式
- 快速操作按钮

---

## 🎨 主题系统

### 可用主题

1. **🌑 深色主题**（默认）
   - 护眼舒适
   - 适合长时间使用

2. **☀️ 浅色主题**
   - 明亮清晰
   - 适合演示展示

3. **🌃 赛博朋克主题**
   - 炫酷科技感
   - 橙色/紫色强调

### 切换方法

- **菜单：** 主题 → 选择主题
- **快捷键：** Ctrl+1/2/3

---

## 💻 系统托盘

### 托盘功能

- **双击图标** - 恢复窗口
- **右键菜单** - 8 个快捷操作
- **自动最小化** - 点击最小化按钮时
- **托盘通知** - 服务状态提醒

### 托盘菜单

- 🖥️ 显示主窗口
- 🚀 快速启动服务
- ⏹️ 停止所有服务
- 📚 打开知识库
- 🧠 打开 V2 学习
- 📥 最小化到托盘
- 📤 从托盘恢复
- ❌ 退出

---

## 🧪 测试

### 运行测试

```bash
python test_all_features.py
```

### 测试结果

```
Total tests:  57
Passed:       57 (100.0%)
Failed:       0 (0.0%)

[SUCCESS] ALL TESTS PASSED!
```

### 测试覆盖

- ✅ 文件结构检查（15 项）
- ✅ 模块导入检查（5 项）
- ✅ GUI 启动测试（2 项）
- ✅ STATE.json 验证（6 项）
- ✅ V2 学习系统集成（4 项）
- ✅ 知识库集成（5 项）
- ✅ 服务管理脚本（6 项）
- ✅ 主题系统（4 项）
- ✅ 系统托盘集成（5 项）
- ✅ 配置编辑器（5 项）

---

## 📁 项目结构

```
project_manager_gui/
├── main_v3.py                  # 主入口
├── README.md                   # 项目说明
├── USER_GUIDE.md              # 用户指南
├── QUICK_REFERENCE.md         # 快速参考
├── requirements.txt           # 依赖列表
├── test_all_features.py       # 综合测试
│
├── gui/                       # GUI 组件
│   ├── main_window_v3.py      # 主窗口
│   ├── quick_start.py         # 快速启动
│   ├── knowledge_base_panel.py # 知识库
│   ├── v2_learning_panel.py   # V2 学习
│   ├── system_tray.py         # 系统托盘
│   ├── config_editor.py       # 配置编辑器
│   ├── diagnostic_panel.py    # 智能诊断
│   ├── themes.py              # 主题管理
│   ├── dashboard.py           # 仪表盘
│   ├── service_manager.py     # 服务管理
│   └── project_list.py        # 项目管理
│
├── services/                  # 服务组件
│   ├── gateway_service.py     # Gateway 服务
│   ├── knowledge_base_service.py # 知识库服务
│   └── diagnostic.py          # 智能诊断
│
└── data/                      # 数据目录
    └── learning_history.json  # 学习历史
```

---

## 📊 系统要求

### 最低配置

- **操作系统：** Windows 10
- **Python：** 3.12+
- **内存：** 4GB
- **磁盘空间：** 500MB

### 推荐配置

- **操作系统：** Windows 11
- **Python：** 3.12.7+
- **内存：** 8GB+
- **磁盘空间：** 1GB+

---

## 📖 文档

- **📖 用户指南：** [USER_GUIDE.md](USER_GUIDE.md) - 完整功能说明
- **📋 快速参考：** [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 速查卡片
- **🧪 测试报告：** [test_all_features.py](test_all_features.py) - 测试结果

---

## 🔗 相关项目

- **知识库系统：** [knowledge_base](../knowledge_base)
- **V2 学习系统：** [v2_learning_system_real](../v2_learning_system_real)
- **Gateway 服务：** [streaming-service](../openclaw_async_architecture/streaming-service)

---

## 🎉 版本历史

### v4.0 (2026-02-19) ⭐ 最新版

**🎉 P0 + P1 功能 100% 完成！**

**新增功能：**
- ✅ 📚 知识库快速访问
- ✅ 🧠 V2 学习系统集成
- ✅ 💻 系统托盘图标
- ✅ ⚙️ 配置编辑器

**改进：**
- ✅ 8 个功能标签页
- ✅ 3 套主题切换
- ✅ 智能诊断优化
- ✅ 自动化测试（57 项 100% 通过）

**修复：**
- ✅ 端口占用检测
- ✅ 依赖安装检查
- ✅ 配置文件验证

### v3.2 (2026-02-18)

- 知识库快速访问
- 智能诊断优化

### v3.0 (2026-02-17)

- 初始版本
- 基础服务管理

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 贡献方式

1. **Fork 项目**
2. **创建功能分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **创建 Pull Request**

### 报告问题

请在 GitHub Issues 中报告问题，包含：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 系统环境

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📞 联系方式

- **开发者：** Claw
- **项目：** OpenClaw Control Center
- **版本：** v4.0
- **GitHub:** [https://github.com/zhoushibo/project_manager_gui](https://github.com/zhoushibo/project_manager_gui)

---

## 🎯 下一步计划

### P2 功能（规划中）

- [ ] 插件系统
- [ ] 云同步
- [ ] 多语言支持
- [ ] 自定义工作流
- [ ] 数据导出/导入
- [ ] 远程管理

### P3 功能（未来）

- [ ] 移动端应用
- [ ] Web 版本
- [ ] AI 助手集成
- [ ] 自动化脚本
- [ ] 团队协作

---

**⭐ 如果喜欢这个项目，请给个 Star！**

**🎉 感谢使用 OpenClaw Control Center v4.0！**

---

**最后更新：** 2026-02-19 13:30  
**状态：** ✅ P0+P1 完成 | ✅ 测试 100% | ✅ 文档完整

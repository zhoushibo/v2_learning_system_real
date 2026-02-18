# OpenClaw项目管理器 (MVP)

带系统托盘的OpenClaw项目管理GUI工具，避免cmd启动的繁琐操作。

---

## 🚀 **快速启动**

### 1. 安装依赖
```bash
cd project_manager_gui
pip install -r requirements.txt
```

### 2. 运行
```bash
python main.py
```

---

## ✨ **功能特点**

### 核心功能
- ✅ 可视化项目列表
- ✅ 一键启动/停止项目组件
- ✅ 右下角系统托盘图标
- ✅ 实时进程监控
- ✅ 日志输出显示

### 支持的项目
1. **V2 MVP** - OpenClaw V2异步架构
   - Gateway（端口8000）
   - Worker（处理AI任务）

2. **钉钉AI Agent** - 钉钉AI助手
   - Flask Server（端口3000）

---

## 📂 **项目结构**

```
project_manager_gui/
├── main.py                    # 程序入口
├── requirements.txt           # 依赖列表
├── README.md                  # 说明文档
├── gui/                       # GUI模块
│   ├── __init__.py
│   ├── main_window.py         # 主窗口
│   ├── project_list.py        # 项目列表
│   └── tray_icon.py           # 托盘图标
├── core/                      # 核心逻辑
│   ├── __init__.py
│   ├── project_manager.py     # 项目管理器
│   └── process_manager.py     # 进程管理器
└── config/
    └── projects.json          # 项目配置
```

---

## 🎯 **使用说明**

### 启动项目
1. 在项目列表中找到目标项目
2. 点击"启动"按钮
3. 查看日志输出确认启动成功

### 停止项目
1. 找到运行中的项目组件
2. 点击"停止"按钮
3. 等待进程优雅退出

### 托盘图标
- **右键菜单**：显示窗口、退出
- **通知**：启动/停止时会显示通知

---

## ⚙️ **配置项目**

编辑 `config/projects.json` 添加新项目：

```json
{
  "projects": [
    {
      "id": "your_project",
      "name": "项目名称",
      "type": "project_type",
      "path": "C:\\path\\to\\project",
      "launcher": "launcher.py",
      "description": "项目描述",
      "components": [
        {
          "id": "gateway",
          "name": "组件名称",
          "command": "python launcher.py gateway",
          "working_dir": "C:\\path\\to\\project",
          "port": 8000,
          "health_check": "http://127.0.0.1:8000/health"
        }
      ]
    }
  ]
}
```

---

## 📊 **技术栈**

- **GUI框架**：PyQt5 5.15.10
- **进程管理**：subprocess + psutil
- **配置管理**：JSON
- **HTTP请求**：requests

---

## 🎉 **MVP完成状态**

### 已实现功能
- ✅ 主窗口UI
- ✅ 项目列表显示
- ✅ 启动/停止功能
- ✅ 托盘图标
- ✅ 进程监控
- ✅ 日志输出

### 待开发功能 (v0.2)
- 🔄 日志查看器
- 🔄 任务提交界面
- 🔄 性能统计
- 🔄 多项目管理

---

## 🐛 **已知问题**

- [ ] 组件健康检查尚未完成
- [ ] 按钮状态未实时更新
- [ ] 端口检查可能不准确
- [ ] 缺少错误提示

---

## 📝 **开发日志**

### 2026-02-16 04:10-04:30
- ✅ 可行性验证通过
- ✅ 创建项目结构
- ✅ 实现核心功能
- ✅ MVP开发完成

---

**版本：** v0.1.0 (MVP)
**开发时间：** 约30分钟
**状态：** ✅ 可用

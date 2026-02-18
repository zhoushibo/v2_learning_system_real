# OpenClaw 灾难恢复系统 🛡️

## 📋 **概述**

一套完整的OpenClaw灾难恢复系统，包括：
- **一键恢复** - 从备份快速恢复工作区
- **系统健康检查** - 诊断系统状态
- **快速诊断** - 快速定位和修复常见问题

---

## 🚀 **快速开始**

### **情况1：OpenClaw崩溃了，想恢复**

**一键恢复：**
```bash
# 方法1：批处理脚本（推荐Windows用户）
emergency_restore.bat

# 方法2：Python脚本
python one_click_restore.py
```

**操作步骤：**
1. 运行脚本
2. 选择要恢复的备份
3. 确认恢复
4. 等待完成
5. 验证恢复结果

---

### **情况2：系统状态异常，想诊断**

**系统健康检查：**
```bash
python system_health_check.py
```

**输出：**
- Python环境状态
- OpenClaw安装状态
- 工作区文件状态
- 备份可用性
- V2系统状态
- Redis连接状态
- Git项目状态
- 服务运行状态

---

### **情况3：快速定位问题**

**快速诊断和修复：**
```bash
python quick_diagnose.py
```

**功能：**
- 自动诊断常见问题
- 提供修复建议
- 支持一键修复

---

## 📦 **恢复系统组件**

### **1. one_click_restore.py - 一键恢复**

**功能：**
- 列出所有可用备份
- 按时间排序（最新的在前）
- 选择恢复哪个备份
- 自动备份当前目录
- 验证恢复完整性

**使用方法：**
```bash
python one_click_restore.py
```

**恢复过程：**
1. 列出所有备份
2. 选择备份（最新/指定编号）
3. 确认恢复
4. 备份当前目录（防止失误）
5. 解压备份文件
6. 恢复文件
7. 验证恢复结果

---

### **2. emergency_restore.bat - 批处理版一键恢复**

**功能：**
- 检查环境（Python、备份）
- 列出可用备份
- 选择恢复选项
- 检查备份完整性
- 调用Python脚本恢复

**使用方法：**
```bash
emergency_restore.bat
```

**选项：**
1. 恢复最新备份
2. 恢复指定备份
3. 仅检查备份完整性
4. 取消

---

### **3. system_health_check.py - 系统健康检查**

**功能：**
- 检查Python环境
- 检查OpenClaw安装
- 检查工作区状态
- 检查备份状态
- 检查V2系统状态
- 检查Redis连接
- 检查Git项目
- 检查服务状态

**使用方法：**
```bash
python system_health_check.py
```

**输出：**
- 每个组件的详细状态
- 健康报告（保存到文件）
- 总体评分（通过/总数）
- 状态建议（健康/大部分正常/需要关注）

---

### **4. quick_diagnose.py - 快速诊断和修复**

**功能：**
- 快速诊断常见问题
- 提供自动修复选项
- 智能推荐解决方案

**使用方法：**
```bash
python quick_diagnose.py
```

**诊断项：**
1. Python环境
2. OpenClaw安装
3. 工作区损坏
4. V2服务状态
5. Redis状态
6. 备份可用性

**修复选项：**
- 从备份恢复
- 重启V2服务
- 启动Redis
- 查看完整健康报告

---

## 🛡️ **备份策略**

### **备份类型**

| 类型 | 脚本 | 说明 | 位置 |
|------|------|------|------|
| **项目备份** | `backup_by_project.py` | 按项目单独备份 | `D:\ClawBackups\project_*.zip` |
| **完整备份** | `full_backup_all.py` | 所有工作区完整备份 | `D:\ClawBackups\FULL_WORKSPACE_BACKUP_*.zip` |
| **快速备份** | `quick_backup.py` | 快速备份当前工作区 | `D:\ClawBackups\quick_*.zip` |

### **备份内容**

- **项目备份：**
  - V2 MVP代码
  - 工具系统
  - 记忆系统
  - 文档

- **完整备份：**
  - 项目备份的所有内容
  - 钉钉系统
  - 小说工具
  - 代理系统

---

## 🚨 **极端情况恢复**

### **情况1：OpenClaw主进程崩溃**

**症状：**
- 无法启动OpenClaw
- 命令无响应
- 服务一直挂起

**解决方案：**
```bash
# 步骤1：诊断
python quick_diagnose.py

# 步骤2：如果OpenClaw问题，重新安装
npm install -g @qingchencloud/openclaw-zh --force

# 步骤3：恢复配置和工作区
python one_click_restore.py
```

---

### **情况2：V2系统损坏**

**症状：**
- V2 Gateway无法启动
- Worker无法连接
- 任务执行失败

**解决方案：**
```bash
# 步骤1：检查V2健康
python system_health_check.py

# 步骤2：恢复V2代码
python one_click_restore.py
# 选择 project_v2_mvp_*.zip

# 步骤3：重启V2
cd openclaw_async_architecture\mvp
python launcher.py
```

---

### **情况3：工作区丢失或损坏**

**症状：**
- 工作区文件丢失
- MEMORY.md损坏
- 无法读取记忆

**解决方案：**
```bash
# 直接恢复最新备份
python one_click_restore.py

# 或使用批处理脚本
emergency_restore.bat
```

---

### **情况4：磁盘损坏**

**症状：**
- 无法读取工作区
- 文件系统错误
- 磁盘故障

**解决方案：**
1. **立即停止写入** - 防止数据进一步损坏
2. **磁盘诊断** - 使用磁盘检测工具
3. **检查备份** - 确认D盘备份可用
4. **数据恢复** - 使用专业数据恢复工具
5. **重新安装** - 格式化后从D盘恢复

---

### **情况5：彻底系统崩溃**

**症状：**
- 操作系统无法启动
- 所有数据丢失
- 无法进入系统

**解决方案：**
1. **重装系统**
2. **安装必要环境**
   - Python 3.11
   - Node.js 18+
   - Redis
   - Git
3. **安装OpenClaw**
   ```bash
   npm install -g @qingchencloud/openclaw-zh
   ```
4. **恢复工作区**
   ```bash
   python one_click_restore.py
   ```
5. **验证系统**
   ```bash
   python system_health_check.py
   ```

---

## 📊 **备份验证**

### **自动验证**

备份后会自动验证：
```bash
python system_health_check.py
```

选择选项3：仅检查备份完整性

### **手动验证**

```python
import zipfile

# 检查zip文件完整性
with zipfile.ZipFile('backup.zip', 'r') as zip_ref:
    bad_files = zip_ref.testzip()
    if bad_files:
        print("损坏的文件:", bad_files)
    else:
        print("备份完整，无损坏")
```

---

## 🔧 **恢复后的验证步骤**

恢复完成后，建议按以下步骤验证：

1. **检查Python环境**
   ```bash
   python --version
   ```

2. **检查OpenClaw**
   ```bash
   openclaw --version
   openclaw agent status
   ```

3. **检查工作区**
   ```bash
   cd C:\Users\10952\.openclaw\workspace
   dir AGENTS.md SOUL.md MEMORY.md
   ```

4. **检查V2系统**
   ```bash
   cd openclaw_async_architecture\mvp
   python launcher.py health
   ```

5. **运行健康检查**
   ```bash
   python system_health_check.py
   ```

---

## 💡 **最佳实践**

1. **定期备份**
   - 每天：快速备份
   - 每周：完整备份
   - 重大更新前：手动备份

2. **测试恢复**
   - 定期测试恢复流程
   - 确保备份可用

3. **监控健康**
   - 每周运行健康检查
   - 修复发现的问题

4. **保持更新**
   - 及时备份重要修改
   - 不要依赖单一备份

5. **保留多个备份**
   - 不要只保留最新备份
   - 保留最近一周的备份

---

## 📝 **恢复报告**

恢复后会生成报告：
```bash
health_report_20260216_085000.txt
```

报告包含：
- 检查时间和结果
- 组件状态
- 总体评分
- 状态建议

---

## 🆘 **紧急联系**

如果遇到无法解决的问题：

1. **日志文件**
   - 查看错误日志
   - 收集诊断信息

2. **文档**
   - 查看OpenClaw官方文档
   - 查看V2系统文档

3. **社区**
   - GitHub Issues
   - 用户社区

---

## 📈 **系统维护计划**

| 频率 | 任务 | 命令 |
|------|------|------|
| **每天** | 快速备份 | `python quick_backup.py` |
| **每周** | 完整备份 | `python full_backup_all.py` |
| **每周** | 健康检查 | `python system_health_check.py` |
| **每月** | 恢复测试 | 测试恢复流程 |
| **重大更新前** | 额外备份 | `python backup_by_project.py` |

---

**恢复系统已就绪！遇到问题时不要慌，按步骤操作即可恢复。** 🛡️

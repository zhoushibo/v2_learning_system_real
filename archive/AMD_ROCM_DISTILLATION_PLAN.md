# 🚀 AMD ROCm 蒸馏训练完整方案

**设备：** 摩尔线程 M1A Pro+（Radeon 8060S, 96GB 显存）
**系统：** Windows 11 → WSL2 + Ubuntu 22.04
**目标：** 创建可控制的蒸馏训练服务（有空运行/没空关闭）
**完成时间：** 2026-02-18

---

## 📋 完整方案总结

| 项目 | 方案 |
|------|------|
| **操作系统** | WSL2 + Ubuntu 22.04 |
| **GPU 驱动** | ROCm 6.0+ |
| **训练框架** | LLaMA-Factory（ROCm 支持最好） |
| **服务管理** | bash 脚本 + tmux |
| **控制命令** | start/stop/status.sh |
| **断点续训** | 每 500 步自动保存 checkpoint |
| **资源监控** | rocm-smi + 自定义脚本 |
| **推理引擎** | llama.cpp / Ollama（待确认 ROCm 支持） |
| **Claw 集成** | 本地 HTTP API 端点 |

---

## 🔧 第 1 步：WSL2 安装（10 分钟）

```bash
# 1. 启用 WSL2（Windows 管理员 PowerShell）
wsl --install -d Ubuntu-22.04

# 2. 设置 WSL2 为默认版本
wsl --set-default-version 2

# 3. 验证安装
wsl --list --verbose

# 4. 进入 WSL2
wsl -d Ubuntu-22.04
```

**验证：**
```bash
# 在 WSL2 中执行
uname -a  # 应显示 Linux 内核
```

---

## 🔧 第 2 步：ROCm 6.0 安装（30 分钟）

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装必要依赖
sudo apt install -y wget gnupg2 software-properties-common

# 3. 添加 ROCm 仓库
wget https://repo.radeon.com/rocm/rocm.gpg.key
gpg --dearmor rocm.gpg.key
sudo mv rocm.gpg.key /etc/apt/trusted.gpg.d/
sudo add-apt-repository 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/6.0 jammy main'

# 4. 安装 ROCm
sudo apt update
sudo apt install -y rocm-dkms rocm-smi-lib rocm-opencl-runtime

# 5. 添加用户到 video 和 render 组
sudo usermod -aG video $USER
sudo usermod -aG render $USER

# 6. 设置环境变量
echo 'export PATH=/opt/rocm/bin:$PATH' >> ~/.bashrc
echo 'export HSA_OVERRIDE_GFX_VERSION=11.0.0' >> ~/.bashrc
source ~/.bashrc

# 7. 验证 ROCm 安装
rocm-smi --showall
```

**预期输出：** 显示 GPU 信息、温度、显存等

---

## 🔧 第 3 步：Python 环境 + LLaMA-Factory 安装（20 分钟）

```bash
# 1. 安装 Python 3.10+
sudo apt install -y python3 python3-pip python3-venv

# 2. 创建项目目录
mkdir -p ~/amd-rocm-training
cd ~/amd-rocm-training

# 3. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 4. 安装 PyTorch ROCm 版本
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.0

# 5. 验证 PyTorch 识别 GPU
python3 -c "import torch; print(f'CUDA 可用：{torch.cuda.is_available()}'); print(f'GPU 数量：{torch.cuda.device_count()}')"

# 6. 安装 LLaMA-Factory
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e .[torch,metrics]

# 7. 验证安装
llamafactory-cli version
```

---

## 🔧 第 4 步：创建训练脚本（15 分钟）

### 目录结构
```bash
cd ~/amd-rocm-training
mkdir -p scripts config checkpoints logs
```

### training_config.yaml
```yaml
# config/training_config.yaml
model_name_or_path: Qwen/Qwen2.5-7B-Instruct
adapter_name_or_path: null
template: qwen
finetuning_type: lora
lora_target: all

# 数据集
dataset: alpaca_en_demo  # 替换为你的数据集
dataset_dir: ../data
cutoff_len: 2048
preprocessing_num_workers: 4

# 训练参数
output_dir: ./checkpoints
per_device_train_batch_size: 2
gradient_accumulation_steps: 4
learning_rate: 2.0e-4
num_train_epochs: 3
lr_scheduler_type: cosine
warmup_ratio: 0.1
fp16: true  # ROCm 支持 FP16

# Checkpoint 保存
save_strategy: steps
save_steps: 500
save_total_limit: 3
save_safetensors: true

# 断点续训
resume_from_checkpoint: true
load_best_model_at_end: true

# 日志
logging_dir: ../logs
logging_steps: 10
report_to: none
```

### start_training.sh
```bash
#!/bin/bash
set -e

TRAINING_DIR="$HOME/amd-rocm-training"
CHECKPOINT_DIR="$TRAINING_DIR/checkpoints"
LOG_DIR="$TRAINING_DIR/logs"
TMUX_SESSION="rocm_training"

# 创建目录
mkdir -p "$CHECKPOINT_DIR" "$LOG_DIR"

# 检查是否已有运行会话
if tmux has-session -t $TMUX_SESSION 2>/dev/null; then
  echo "⚠️ 训练会话已在运行中"
  tmux attach -t $TMUX_SESSION
  exit 0
fi

# 启动训练会话
echo "🚀 启动 ROCm 训练会话..."
tmux new-session -d -s $TMUX_SESSION

# 在会话中运行训练
tmux send-keys -t $TMUX_SESSION "cd $TRAINING_DIR/LLaMA-Factory" C-m
tmux send-keys -t $TMUX_SESSION "source ../.venv/bin/activate" C-m
tmux send-keys -t $TMUX_SESSION "export HSA_OVERRIDE_GFX_VERSION=11.0.0" C-m
tmux send-keys -t $TMUX_SESSION "python -m llamafactory.cli train ../config/training_config.yaml 2>&1 | tee ../logs/training.log" C-m

# 附加到会话
tmux attach -t $TMUX_SESSION
```

### stop_training.sh
```bash
#!/bin/bash

TMUX_SESSION="rocm_training"

if ! tmux has-session -t $TMUX_SESSION 2>/dev/null; then
  echo "❌ 训练会话未运行"
  exit 1
fi

echo "🛑 优雅停止训练..."

# 发送 Ctrl+C 信号
tmux send-keys -t $TMUX_SESSION C-c

# 等待 5 秒让 checkpoint 保存
sleep 5

# 检查进程是否还在运行
if tmux has-session -t $TMUX_SESSION 2>/dev/null; then
  echo "⚠️ 强制终止会话..."
  tmux kill-session -t $TMUX_SESSION
fi

echo "✅ 训练已停止"
```

### status.sh
```bash
#!/bin/bash

TMUX_SESSION="rocm_training"

echo "=== 📊 ROCm 训练状态 ==="
echo ""

# 检查 tmux 会话
if tmux has-session -t $TMUX_SESSION 2>/dev/null; then
  echo "✅ 训练会话：运行中"
  echo "  会话名：$TMUX_SESSION"
  echo "  附加命令：tmux attach -t $TMUX_SESSION"
else
  echo "❌ 训练会话：未运行"
fi

echo ""
echo "=== 🖥️ GPU 状态 ==="
rocm-smi --showall 2>/dev/null || echo "⚠️ rocm-smi 不可用"

echo ""
echo "=== 💾 最新 Checkpoint ==="
CHECKPOINT_DIR="$HOME/amd-rocm-training/checkpoints"
if [ -d "$CHECKPOINT_DIR" ]; then
  ls -lt "$CHECKPOINT_DIR" | head -5
else
  echo "无 checkpoint 目录"
fi

echo ""
echo "=== 📝 最新日志 ==="
LOG_DIR="$HOME/amd-rocm-training/logs"
if [ -f "$LOG_DIR/training.log" ]; then
  tail -20 "$LOG_DIR/training.log"
fi
```

### 赋予执行权限
```bash
chmod +x scripts/*.sh
```

---

## 🔧 第 5 步：资源监控（10 分钟）

### monitor.sh
```bash
#!/bin/bash

echo "=== 🔍 ROCm GPU 监控 ==="
echo "时间：$(date)"
echo ""

# GPU 状态
echo "📊 GPU 使用率："
rocm-smi --showuse

echo ""
echo "🌡️ 温度："
rocm-smi --showtemp

echo ""
echo "💾 显存使用："
rocm-smi --showmeminfo vram

echo ""
echo "⚡ 功耗："
rocm-smi --showpower

# 告警检查
TEMP=$(rocm-smi --showtemp | grep -oP '\d+' | head -1)
if [ "$TEMP" -gt 85 ]; then
  echo ""
  echo "🚨 警告：GPU 温度过高 ($TEMP°C)"
  echo "  建议：降低 batch_size 或增加冷却"
fi

VRAM_USED=$(rocm-smi --showmeminfo vram | grep -oP '\d+' | head -1)
VRAM_TOTAL=96  # 96GB
VRAM_PERCENT=$((VRAM_USED * 100 / VRAM_TOTAL))

if [ "$VRAM_PERCENT" -gt 90 ]; then
  echo ""
  echo "🚨 警告：显存使用率过高 ($VRAM_PERCENT%)"
  echo "  建议：降低 batch_size 或使用梯度累积"
fi
```

### 使用方式
```bash
# 手动监控
./scripts/monitor.sh

# 或定期监控（每 60 秒）
watch -n 60 './scripts/monitor.sh'
```

---

## 🔧 第 6 步：模型导出 + Claw 集成（待验证）

### 方案 A：llama.cpp（推荐）
```bash
# 1. 安装 llama.cpp
cd ~
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j

# 2. 导出模型为 GGUF
python convert-hf-to-gguf.py ~/amd-rocm-training/checkpoints/best_model/ --outfile qwen2.5-7b-distilled.gguf

# 3. 运行推理
./server -m qwen2.5-7b-distilled.gguf --host 0.0.0.0 --port 8080
```

### 方案 B：Ollama（需验证 ROCm 支持）
```bash
# 1. 安装 Ollama（Linux 版本）
curl -fsSL https://ollama.com/install.sh | sh

# 2. 创建 Modelfile
echo "FROM ./qwen2.5-7b-distilled.gguf" > Modelfile
echo "PARAMETER temperature 0.7" >> Modelfile

# 3. 导入模型
ollama create qwen2.5-7b-distilled -f Modelfile

# 4. 运行
ollama run qwen2.5-7b-distilled
```

### Claw 配置（示例）
```yaml
# claw_config.yaml
models:
  primary:
    provider: nvidia
    api_key: ${NVIDIA_API_KEY}
    model: llama-3.1-70b-instruct
  
  fallback:
    provider: local
    endpoint: http://localhost:8080  # llama.cpp server
    model: qwen2.5-7b-distilled
  
  switch_policy:
    - on_api_error
    - on_rate_limit
    - manual_switch
```

---

## ⚠️ 风险清单 + 应对措施

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| **ROCm 6.0 不支持 RDNA 3.5** | 中 | 高 | 尝试 ROCm 6.1+ 或等待官方支持 |
| **WSL2 GPU 直通失败** | 低 | 高 | 使用双系统 Linux |
| **训练 OOM** | 中 | 中 | 降低 batch_size，增加梯度累积 |
| **训练中断** | 中 | 中 | Checkpoint 每 500 步保存，自动恢复 |
| **llama.cpp ROCm 支持问题** | 中 | 中 | 使用 CPU 推理（慢但可用） |
| **Claw 集成失败** | 低 | 高 | 准备独立 CLI 工具作为备选 |

---

## 📊 完整实施时间表

| 步骤 | 任务 | 预计时间 | 状态 |
|------|------|----------|------|
| **1** | WSL2 安装 | 10 分钟 | ⏳ 待执行 |
| **2** | ROCm 6.0 安装 | 30 分钟 | ⏳ 待执行 |
| **3** | Python + LLaMA-Factory | 20 分钟 | ⏳ 待执行 |
| **4** | 创建训练脚本 | 15 分钟 | ⏳ 待执行 |
| **5** | 资源监控配置 | 10 分钟 | ⏳ 待执行 |
| **6** | 模型导出 + Claw 集成 | 30 分钟 | ⏳ 待执行 |
| **总计** | | **~2 小时** | |

---

## 🚀 快速启动命令清单

```bash
# === Windows 端（管理员 PowerShell） ===
wsl --install -d Ubuntu-22.04
wsl --set-default-version 2

# === WSL2 端（Ubuntu 终端） ===
# 1. 安装 ROCm
sudo apt update && sudo apt upgrade -y
sudo apt install -y wget gnupg2 software-properties-common
wget https://repo.radeon.com/rocm/rocm.gpg.key
gpg --dearmor rocm.gpg.key
sudo mv rocm.gpg.key /etc/apt/trusted.gpg.d/
sudo add-apt-repository 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/6.0 jammy main'
sudo apt update
sudo apt install -y rocm-dkms rocm-smi-lib rocm-opencl-runtime
sudo usermod -aG video $USER
sudo usermod -aG render $USER
echo 'export PATH=/opt/rocm/bin:$PATH' >> ~/.bashrc
echo 'export HSA_OVERRIDE_GFX_VERSION=11.0.0' >> ~/.bashrc
source ~/.bashrc

# 2. 安装 Python + LLaMA-Factory
sudo apt install -y python3 python3-pip python3-venv
mkdir -p ~/amd-rocm-training && cd ~/amd-rocm-training
python3 -m venv .venv
source .venv/bin/activate
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.0
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e .[torch,metrics]

# 3. 创建脚本（复制上面的脚本内容）
cd ~/amd-rocm-training
mkdir -p scripts config checkpoints logs
# ... 创建 training_config.yaml, start_training.sh, stop_training.sh, status.sh, monitor.sh

# 4. 启动训练
./scripts/start_training.sh

# 5. 查看状态
./scripts/status.sh

# 6. 停止训练
./scripts/stop_training.sh
```

---

## ✅ 核心功能验证

### 1. 有空时启动训练
```bash
# 进入 WSL2
wsl -d Ubuntu-22.04

# 启动训练
cd ~/amd-rocm-training
./scripts/start_training.sh
```

### 2. 没空时停止训练
```bash
# 优雅停止（自动保存 checkpoint）
./scripts/stop_training.sh
```

### 3. 查看训练状态
```bash
# 查看运行状态 + GPU 状态 + 最新 checkpoint
./scripts/status.sh
```

### 4. 恢复训练
```bash
# 再次启动会自动从最新 checkpoint 恢复
./scripts/start_training.sh
```

---

## 📝 下一步行动

1. **确认 M1A Pro+ 已到手并可访问**
2. **执行上述 6 步安装流程**
3. **准备训练数据**（alpaca 格式或自定义）
4. **测试小规模蒸馏**（先用小数据集验证流程）
5. **正式训练**（有空时启动，没空时停止）
6. **模型导出 + Claw 集成测试**

---

**🎉 完整方案已完成！随时可以开始实施！** ⚡

**有任何问题随时问我！** 🚀

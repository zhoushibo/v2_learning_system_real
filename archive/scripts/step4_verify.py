import time
start = time.time()

with open('C:/Users/10952/.openclaw/workspace/MEMORY.md', 'r', encoding='utf-8') as f:
    c = f.read()

elapsed = time.time() - start
print(f'✅ 步骤 4 完成：验证耗时 {elapsed:.2f}秒')
print(f'📄 文件大小：{len(c):,} 字符')
print(f'✅ 规则 5 存在：{"规则 5" in c}')
print(f'✅ 规则 6 存在：{"规则 6" in c}')
print(f'📍 规则 5 位置：{c.find("规则 5"):,}')
print(f'📍 规则 6 位置：{c.find("规则 6"):,}')

# 显示规则 6 的开头
idx = c.find('### 🚨 **规则 6')
if idx > 0:
    print(f'\n📄 规则 6 开头 100 字符：{repr(c[idx:idx+100])}')

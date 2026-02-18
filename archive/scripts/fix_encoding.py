"""Fix encoding issues in learning_engine.py"""
import re

# Read the broken file
with open('v2_learning_system_real/learning_engine.py.broken', 'rb') as f:
    content = f.read()

# Remove all invalid/private Unicode characters
# U+E000-U+F8FF: Private Use Area
# U+FE00-U+FEFF: Variation Selectors
patterns_to_remove = [
    b'[\ue000-\uf8ff]'.decode('unicode_escape').encode('utf-8', errors='ignore'),
    b'\xef\xb8\xbf',  # U+FE3F
]

# Simple approach: decode with errors='ignore' and re-encode
try:
    text = content.decode('utf-8', errors='ignore')
    # Remove suspicious characters
    cleaned_text = ''
    for char in text:
        code = ord(char)
        # Skip private use area and other problematic ranges
        if 0xE000 <= code <= 0xF8FF:  # Private Use
            continue
        if 0xFE00 <= code <= 0xFEFF:  # Variation Selectors
            continue
        cleaned_text += char
    
    with open('v2_learning_system_real/learning_engine.py', 'w', encoding='utf-8') as f:
        f.write(cleaned_text)
    
    print(f'✅ Fixed! Original: {len(content)} bytes, Cleaned: {len(cleaned_text)} chars')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

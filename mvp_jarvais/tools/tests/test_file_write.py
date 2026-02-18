"""
file_write 工具单元测试

测试用例：
1. 正常写入（覆盖模式）
2. 正常写入（追加模式）
3. 自动创建父目录
4. 权限不足错误
5. 路径无效错误
6. 编码错误
7. 大文件写入
8. 空内容写入
"""

import pytest
import tempfile
import os
from pathlib import Path

from mvp_jarvais.tools.file_write import file_write


class TestFileWriteNormal:
    """正常写入测试"""
    
    @pytest.mark.asyncio
    async def test_write_overwrite(self):
        """测试 1：覆盖写入"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Old content\n")
            temp_path = f.name
        
        try:
            result = await file_write(temp_path, "New content")
            
            assert result["success"] is True
            assert result["bytes_written"] > 0
            assert result["path"] == os.path.abspath(temp_path)
            assert result["mode"] == "w"
            
            # 验证文件内容
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert content == "New content"
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_write_append(self):
        """测试 2：追加写入"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Line 1\n")
            temp_path = f.name
        
        try:
            result = await file_write(temp_path, "Line 2\n", mode="a")
            
            assert result["success"] is True
            
            # 验证文件内容
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert content == "Line 1\nLine 2\n"
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_write_create_dirs(self):
        """测试 3：自动创建父目录"""
        temp_dir = tempfile.mkdtemp()
        new_path = os.path.join(temp_dir, "new_dir", "sub_dir", "file.txt")
        
        try:
            result = await file_write(new_path, "Content", create_dirs=True)
            
            assert result["success"] is True
            assert os.path.exists(new_path)
            
            with open(new_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert content == "Content"
        finally:
            # 清理
            import shutil
            shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_write_empty_content(self):
        """测试 4：空内容写入"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            result = await file_write(temp_path, "")
            
            assert result["success"] is True
            assert result["bytes_written"] == 0
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert content == ""
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_write_unicode(self):
        """测试 5：Unicode 内容写入"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            temp_path = f.name
        
        try:
            result = await file_write(temp_path, "Hello 世界 🌍")
            
            assert result["success"] is True
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert content == "Hello 世界 🌍"
        finally:
            os.unlink(temp_path)


class TestFileWriteErrors:
    """错误处理测试"""
    
    @pytest.mark.asyncio
    async def test_write_empty_path(self):
        """测试 6：空路径"""
        result = await file_write("", "Content")
        
        assert result["success"] is False
        assert "文件路径不能为空" in result["error"]
    
    @pytest.mark.asyncio
    async def test_write_none_content(self):
        """测试 7：None 内容"""
        result = await file_write("file.txt", None)
        
        assert result["success"] is False
        assert "写入内容不能为 None" in result["error"]
    
    @pytest.mark.asyncio
    async def test_write_invalid_mode(self):
        """测试 8：无效的 mode"""
        result = await file_write("file.txt", "Content", mode="x")
        
        assert result["success"] is False
        assert "mode 必须是 'w' 或 'a'" in result["error"]
    
    @pytest.mark.asyncio
    async def test_write_to_directory(self):
        """测试 9：写入到目录而不是文件"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            result = await file_write(temp_dir, "Content")
            
            assert result["success"] is False
            assert "路径是目录，不是文件" in result["error"]
        finally:
            os.rmdir(temp_dir)
    
    @pytest.mark.asyncio
    async def test_write_encoding_error(self):
        """测试 10：编码错误"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            # 尝试用 ASCII 编码写入中文
            result = await file_write(temp_path, "中文内容", encoding="ascii")
            
            assert result["success"] is False
            assert "编码错误" in result["error"]
        finally:
            os.unlink(temp_path)


class TestFileWriteLarge:
    """大文件写入测试"""
    
    @pytest.mark.asyncio
    async def test_write_large_file(self):
        """测试 11：大文件写入"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            # 写入 10000 行
            large_content = "\n".join([f"Line {i}" for i in range(1, 10001)])
            
            result = await file_write(temp_path, large_content)
            
            assert result["success"] is True
            assert result["bytes_written"] > 0
            
            # 验证行数
            with open(temp_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            assert len(lines) == 10000
        finally:
            os.unlink(temp_path)


class TestFileWriteEncoding:
    """编码测试"""
    
    @pytest.mark.asyncio
    async def test_write_utf8(self):
        """测试 12：UTF-8 编码"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            result = await file_write(temp_path, "Hello 世界", encoding="utf-8")
            
            assert result["success"] is True
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert content == "Hello 世界"
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_write_gbk(self):
        """测试 13：GBK 编码"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            result = await file_write(temp_path, "中文测试", encoding="gbk")
            
            assert result["success"] is True
            
            with open(temp_path, 'r', encoding='gbk') as f:
                content = f.read()
            assert content == "中文测试"
        finally:
            os.unlink(temp_path)


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

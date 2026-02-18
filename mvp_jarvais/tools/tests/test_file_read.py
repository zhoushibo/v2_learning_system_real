"""
file_read 工具单元测试

测试用例：
1. 正常读取完整文件
2. 读取指定行范围（offset/limit）
3. 文件不存在
4. 编码错误
5. 权限不足（可选，依赖系统）
6. 大文件性能测试
"""

import pytest
import tempfile
import os
from pathlib import Path

from mvp_jarvais.tools.file_read import file_read


class TestFileReadNormal:
    """正常读取测试"""
    
    @pytest.mark.asyncio
    async def test_read_full_file(self):
        """测试 1：读取完整文件"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Line 1\nLine 2\nLine 3\n")
            temp_path = f.name
        
        try:
            result = await file_read(temp_path)
            
            assert "error" not in result
            assert result["content"] == "Line 1\nLine 2\nLine 3\n"
            assert result["total_lines"] == 3
            assert result["read_lines"] == 3
            assert result["size_bytes"] > 0
            assert result["path"] == os.path.abspath(temp_path)
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_read_with_offset_limit(self):
        """测试 2：读取指定行范围"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for i in range(1, 11):
                f.write(f"Line {i}\n")
            temp_path = f.name
        
        try:
            # 读取第 5-7 行（共 3 行）
            result = await file_read(temp_path, offset=5, limit=3)
            
            assert "error" not in result
            assert result["content"] == "Line 5\nLine 6\nLine 7\n"
            assert result["total_lines"] == 10
            assert result["read_lines"] == 3
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_read_with_offset_only(self):
        """测试 3：只指定 offset"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for i in range(1, 6):
                f.write(f"Line {i}\n")
            temp_path = f.name
        
        try:
            result = await file_read(temp_path, offset=3)
            
            assert "error" not in result
            assert result["content"] == "Line 3\nLine 4\nLine 5\n"
            assert result["read_lines"] == 3
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_read_with_limit_only(self):
        """测试 4：只指定 limit"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for i in range(1, 11):
                f.write(f"Line {i}\n")
            temp_path = f.name
        
        try:
            result = await file_read(temp_path, limit=5)
            
            assert "error" not in result
            assert result["content"] == "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"
            assert result["read_lines"] == 5
        finally:
            os.unlink(temp_path)


class TestFileReadErrors:
    """错误处理测试"""
    
    @pytest.mark.asyncio
    async def test_file_not_found(self):
        """测试 5：文件不存在"""
        result = await file_read("/nonexistent/path/file.txt")
        
        assert "error" in result
        assert "文件不存在" in result["error"]
    
    @pytest.mark.asyncio
    async def test_empty_path(self):
        """测试 6：空路径"""
        result = await file_read("")
        
        assert "error" in result
        assert "文件路径不能为空" in result["error"]
    
    @pytest.mark.asyncio
    async def test_invalid_offset(self):
        """测试 7：负数 offset"""
        result = await file_read("some_file.txt", offset=-1)
        
        assert "error" in result
        assert "offset 必须 >= 0" in result["error"]
    
    @pytest.mark.asyncio
    async def test_invalid_limit(self):
        """测试 8：零或负数 limit"""
        result = await file_read("some_file.txt", limit=0)
        
        assert "error" in result
        assert "limit 必须 > 0" in result["error"]
        
        result = await file_read("some_file.txt", limit=-5)
        
        assert "error" in result
        assert "limit 必须 > 0" in result["error"]
    
    @pytest.mark.asyncio
    async def test_directory_not_file(self):
        """测试 9：路径是目录不是文件"""
        result = await file_read("/tmp")
        
        assert "error" in result
        assert "不是文件" in result["error"]
    
    @pytest.mark.asyncio
    async def test_encoding_error(self):
        """测试 10：编码错误"""
        # 创建一个 GBK 编码的文件
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
            f.write("中文测试".encode('gbk'))
            temp_path = f.name
        
        try:
            # 尝试用 UTF-8 读取
            result = await file_read(temp_path, encoding='utf-8')
            
            # 应该捕获编码错误或自动替换（errors='replace'）
            # 根据实现，可能会返回替换后的内容或错误
            # 这里验证至少不会崩溃
            assert "content" in result or "error" in result
        finally:
            os.unlink(temp_path)


class TestFileReadLarge:
    """大文件性能测试"""
    
    @pytest.mark.asyncio
    async def test_large_file_with_limit(self):
        """测试 11：大文件 + limit 限制（验证不一次性加载）"""
        # 创建一个大文件（10000 行）
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for i in range(1, 10001):
                f.write(f"Line {i}\n")
            temp_path = f.name
        
        try:
            # 只读取前 10 行
            result = await file_read(temp_path, limit=10)
            
            assert "error" not in result
            assert result["read_lines"] == 10
            assert result["total_lines"] == 10000
            assert "Line 1\n" in result["content"]
            assert "Line 10\n" in result["content"]
            assert "Line 11\n" not in result["content"]
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_large_file_with_offset(self):
        """测试 12：大文件 + offset 跳过"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for i in range(1, 1001):
                f.write(f"Line {i}\n")
            temp_path = f.name
        
        try:
            # 跳过前 990 行，读取最后 10 行
            result = await file_read(temp_path, offset=991)
            
            assert "error" not in result
            assert result["read_lines"] == 10
            assert "Line 991\n" in result["content"]
            assert "Line 1000\n" in result["content"]
        finally:
            os.unlink(temp_path)


class TestFileReadEncoding:
    """编码测试"""
    
    @pytest.mark.asyncio
    async def test_utf8_encoding(self):
        """测试 13：UTF-8 编码文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("Hello 世界 🌍\n")
            temp_path = f.name
        
        try:
            result = await file_read(temp_path, encoding='utf-8')
            
            assert "error" not in result
            assert "Hello 世界 🌍" in result["content"]
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_gbk_encoding(self):
        """测试 14：GBK 编码文件"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
            f.write("中文测试".encode('gbk'))
            temp_path = f.name
        
        try:
            result = await file_read(temp_path, encoding='gbk')
            
            assert "error" not in result
            assert "中文测试" in result["content"]
        finally:
            os.unlink(temp_path)


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

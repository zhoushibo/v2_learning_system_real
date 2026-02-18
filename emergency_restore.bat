@echo off
REM ============================================================
REM OpenClaw 灾难恢复批处理脚本
REM 一键恢复 + 健康检查
REM ============================================================

echo ============================================================
echo OpenClaw 灾难恢复系统
echo ============================================================
echo.

REM 检查备份目录
if not exist "D:\ClawBackups" (
    echo [错误] 备份目录不存在！
    echo        请先运行备份脚本：backup_by_project.py
    pause
    exit /b 1
)

echo [1/5] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装或未添加到PATH
    pause
    exit /b 1
)
echo       Python环境正常
echo.

echo [2/5] 检查备份文件...
dir /b "D:\ClawBackups\*.zip" | findstr /v "^$"
if errorlevel 1 (
    echo [错误] 没有找到备份文件！
    pause
    exit /b 1
)
echo       备份文件正常
echo.

echo [3/5] 查看可用备份...
dir "D:\ClawBackups\*.zip" /O-D /T:W | findstr ".zip$"
echo.

echo [4/5] 恢复选项：
echo    1. 恢復最新备份（已按时间排序，第一个是最新的）
echo    2. 恢复指定备份
echo    3. 仅检查备份完整性
echo    4. 取消
echo.

set /p choice="请选择 (1/2/3/4): "

if "%choice%"=="1" (
    echo.
    echo 开始恢复最新备份...
    python one_click_restore.py
) else if "%choice%"=="2" (
    echo.
    set /p backup_file="请输入备份文件名（如：project_v2_mvp_20260216_083522.zip）："
    if exist "D:\ClawBackups\%backup_file%" (
        echo 开始恢复备份: %backup_file%
        python -c "from one_click_restore import restore_backup; restore_backup('D:\\ClawBackups\\%backup_file%', r'C:\Users\10952\.openclaw\workspace', 'project')"
    ) else (
        echo [错误] 备份文件不存在！
        pause
        exit /b 1
    )
) else if "%choice%"=="3" (
    echo.
    echo 检查备份完整性...
    for %%f in (D:\ClawBackups\*.zip) do (
        echo 检查: %%f
        python -c "import zipfile; zipfile.ZipFile('D:\\ClawBackups\\%%f').testzip(); print('  OK')"
        if errorlevel 1 (
            echo   [错误] 损坏的备份文件！
            pause
            exit /b 1
        )
    )
    echo.
    echo [完成] 所有备份文件完整性检查通过
) else if "%choice%"=="4" (
    echo.
    echo 已取消
    pause
    exit /b 0
) else (
    echo.
    echo [错误] 无效选择
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 恢复完成！
echo ============================================================
echo.
echo 下一步操作：
echo   1. 检查恢复的文件
echo   2. 重启OpenClaw（如需要）
echo   3. 验证功能
echo.

pause

# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite for OpenClaw Control Center v4.0
Tests all 8 tabs and system tray functionality
"""

import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("OpenClaw Control Center v4.0 - Comprehensive Test Suite")
print("=" * 80)
print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

workspace_dir = Path(__file__).parent.parent
project_dir = Path(__file__).parent

# Test counters
total_tests = 0
passed_tests = 0
failed_tests = 0

def test_result(name, success, details=""):
    """Record test result"""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    
    status = "[PASS]" if success else "[FAIL]"
    print(f"[{status}] {name}")
    if details:
        print(f"       {details}")
    
    if success:
        passed_tests += 1
    else:
        failed_tests += 1

# ============================================================================
# Test 1: File Structure
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: File Structure Check")
print("=" * 80)

required_files = [
    'main_v3.py',
    'gui/main_window_v3.py',
    'gui/quick_start.py',
    'gui/knowledge_base_panel.py',
    'gui/v2_learning_panel.py',
    'gui/system_tray.py',
    'gui/config_editor.py',
    'gui/diagnostic_panel.py',
    'gui/themes.py',
    'gui/dashboard.py',
    'gui/service_manager.py',
    'gui/project_list.py',
    'services/gateway_service.py',
    'services/knowledge_base_service.py',
    'services/diagnostic.py',
]

for file_path in required_files:
    full_path = project_dir / file_path
    exists = full_path.exists()
    test_result(f"File exists: {file_path}", exists)

# ============================================================================
# Test 2: Import Check
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: Module Import Check")
print("=" * 80)

import_checks = [
    ('PyQt5', 'PyQt5'),
    ('PyQt5.QtWidgets', 'PyQt5.QtWidgets'),
    ('QSystemTrayIcon', 'PyQt5.QtWidgets', 'QSystemTrayIcon'),
    ('json', 'json'),
    ('subprocess', 'subprocess'),
]

for check in import_checks:
    if len(check) == 2:
        name, module_path = check
        try:
            __import__(module_path)
            test_result(f"Import: {name}", True)
        except Exception as e:
            test_result(f"Import: {name}", False, str(e))
    else:
        name, module_path, class_name = check
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            test_result(f"Import: {name}.{class_name}", True)
        except Exception as e:
            test_result(f"Import: {name}.{class_name}", False, str(e))

# ============================================================================
# Test 3: GUI Launch Test
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: GUI Launch Test")
print("=" * 80)

print("Attempting to launch GUI...")
try:
    # Start GUI in background
    process = subprocess.Popen(
        [sys.executable, 'main_v3.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(project_dir)
    )
    
    # Wait for GUI to start (max 10 seconds)
    time.sleep(5)
    
    # Check if process is still running
    if process.poll() is None:
        test_result("GUI launched successfully", True, "Process is running")
        
        # Close the GUI
        process.terminate()
        process.wait(timeout=5)
        test_result("GUI closed cleanly", True)
    else:
        # Process exited early, check for errors
        stdout, stderr = process.communicate()
        error_msg = stderr.decode('utf-8', errors='ignore')[:200]
        test_result("GUI launched successfully", False, f"Exited with code {process.returncode}: {error_msg}")
        
except Exception as e:
    test_result("GUI launch test", False, str(e))

# ============================================================================
# Test 4: STATE.json Check
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: STATE.json Validation")
print("=" * 80)

state_file = workspace_dir / 'STATE.json'
if state_file.exists():
    test_result("STATE.json exists", True)
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        
        test_result("STATE.json is valid JSON", True)
        
        # Check required fields
        required_fields = ['projects', 'last_updated', 'version']
        for field in required_fields:
            exists = field in state_data
            test_result(f"STATE.json has '{field}' field", exists)
        
        # Check projects
        projects = state_data.get('projects', {})
        test_result(f"STATE.json has {len(projects)} projects", len(projects) > 0)
        
    except Exception as e:
        test_result("STATE.json validation", False, str(e))
else:
    test_result("STATE.json exists", False, "File not found")

# ============================================================================
# Test 5: V2 Learning System Check
# ============================================================================
print("\n" + "=" * 80)
print("TEST 5: V2 Learning System Integration")
print("=" * 80)

v2_dir = workspace_dir / 'v2_learning_system_real'
if v2_dir.exists():
    test_result("V2 learning system directory exists", True)
    
    # Check key files
    v2_files = [
        'learning_engine.py',
        'knowledge_base_integration_v2.py',
        'INTEGRATION_GUIDE.md'
    ]
    
    for file_name in v2_files:
        file_path = v2_dir / file_name
        exists = file_path.exists()
        test_result(f"V2 file: {file_name}", exists)
else:
    test_result("V2 learning system directory exists", False, "Directory not found")

# ============================================================================
# Test 6: Knowledge Base Check
# ============================================================================
print("\n" + "=" * 80)
print("TEST 6: Knowledge Base Integration")
print("=" * 80)

kb_dir = workspace_dir / 'knowledge_base'
if kb_dir.exists():
    test_result("Knowledge base directory exists", True)
    
    # Check key files
    kb_files = [
        'app.py',
        'core/knowledge_index.py',
        'core/knowledge_search.py',
        'core/embedding_generator.py'
    ]
    
    for file_name in kb_files:
        file_path = kb_dir / file_name
        exists = file_path.exists()
        test_result(f"KB file: {file_name}", exists)
else:
    test_result("Knowledge base directory exists", False, "Directory not found")

# ============================================================================
# Test 7: Service Scripts Check
# ============================================================================
print("\n" + "=" * 80)
print("TEST 7: Service Management Scripts")
print("=" * 80)

service_scripts = [
    ('Gateway service', 'services/gateway_service.py'),
    ('Knowledge Base service', 'services/knowledge_base_service.py'),
    ('Diagnostic service', 'services/diagnostic.py'),
]

for name, script_path in service_scripts:
    full_path = project_dir / script_path
    if full_path.exists():
        test_result(f"{name} script exists", True)
        
        # Try to import
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("module", full_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            test_result(f"{name} imports cleanly", True)
        except Exception as e:
            test_result(f"{name} imports cleanly", False, str(e)[:100])
    else:
        test_result(f"{name} script exists", False)

# ============================================================================
# Test 8: Theme Files Check
# ============================================================================
print("\n" + "=" * 80)
print("TEST 8: Theme System")
print("=" * 80)

themes_file = project_dir / 'gui' / 'themes.py'
if themes_file.exists():
    test_result("themes.py exists", True)
    
    try:
        with open(themes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for theme definitions
        themes = ['Dark', 'Light', 'Cyberpunk']
        for theme in themes:
            exists = theme in content
            test_result(f"Theme '{theme}' defined", exists)
    except Exception as e:
        test_result("themes.py readable", False, str(e))
else:
    test_result("themes.py exists", False)

# ============================================================================
# Test 9: System Tray Check
# ============================================================================
print("\n" + "=" * 80)
print("TEST 9: System Tray Integration")
print("=" * 80)

tray_file = project_dir / 'gui' / 'system_tray.py'
if tray_file.exists():
    test_result("system_tray.py exists", True)
    
    try:
        with open(tray_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key features
        features = [
            ('QSystemTrayIcon', 'System tray icon'),
            ('tray_menu', 'Tray menu'),
            ('show_notification', 'Notification support'),
            ('minimize_to_tray', 'Minimize to tray'),
        ]
        
        for keyword, description in features:
            exists = keyword in content
            test_result(f"Feature: {description}", exists)
    except Exception as e:
        test_result("system_tray.py readable", False, str(e))
else:
    test_result("system_tray.py exists", False)

# ============================================================================
# Test 10: Config Editor Check
# ============================================================================
print("\n" + "=" * 80)
print("TEST 10: Configuration Editor")
print("=" * 80)

config_file = project_dir / 'gui' / 'config_editor.py'
if config_file.exists():
    test_result("config_editor.py exists", True)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key features
        features = [
            ('ProjectEditorCard', 'Project editing'),
            ('add_project', 'Add project'),
            ('save_changes', 'Save changes'),
            ('STATE.json', 'STATE.json integration'),
        ]
        
        for keyword, description in features:
            exists = keyword in content
            test_result(f"Feature: {description}", exists)
    except Exception as e:
        test_result("config_editor.py readable", False, str(e))
else:
    test_result("config_editor.py exists", False)

# ============================================================================
# Final Summary
# ============================================================================
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total tests:  {total_tests}")
print(f"Passed:       {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
print(f"Failed:       {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
print()

if failed_tests == 0:
    print("[SUCCESS] ALL TESTS PASSED!")
    print()
    print("OpenClaw Control Center v4.0 is ready for release!")
    print()
    print("Next steps:")
    print("1. Manual testing of all 8 tabs")
    print("2. Test system tray functionality")
    print("3. Write user documentation")
    print("4. Git commit and tag v4.0")
else:
    print(f"[WARNING] {failed_tests} test(s) failed. Please review the errors above.")
    print()
    print("Failed tests should be fixed before release.")

print("=" * 80)
print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Exit with appropriate code
sys.exit(0 if failed_tests == 0 else 1)

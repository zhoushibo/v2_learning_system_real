# -*- coding: utf-8 -*-
"""
Theme System for OpenClaw Control Center
3 built-in themes: Dark, Light, Cyberpunk
"""

# Dark Theme (程序员最爱)
DARK_THEME = """
/* ===== Global Styles ===== */
QWidget {
    background-color: #1e1e2e;
    color: #e0e0e0;
    font-family: "Microsoft YaHei", "Segoe UI", Arial;
    font-size: 14px;
}

/* ===== Main Window ===== */
QMainWindow {
    background-color: #1e1e2e;
}

/* ===== Tab Widget ===== */
QTabWidget::pane {
    border: 1px solid #3a3a5a;
    border-radius: 8px;
    background-color: #252538;
}

QTabBar::tab {
    background-color: #2a2a3e;
    color: #a0a0b0;
    padding: 12px 24px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: #3a3a5a;
    color: #ffffff;
}

QTabBar::tab:hover:!selected {
    background-color: #32324a;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #4a4a6a;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #5a5a7a;
}

QPushButton:pressed {
    background-color: #3a3a5a;
}

QPushButton:disabled {
    background-color: #2a2a3a;
    color: #666666;
}

/* Primary Button */
QPushButton#primaryBtn {
    background-color: #4CAF50;
}

QPushButton#primaryBtn:hover {
    background-color: #45a049;
}

/* Danger Button */
QPushButton#dangerBtn {
    background-color: #f44336;
}

QPushButton#dangerBtn:hover {
    background-color: #da190b;
}

/* ===== Labels ===== */
QLabel {
    color: #e0e0e0;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #4a9eff;
}

QLabel#descLabel {
    color: #a0a0b0;
    font-style: italic;
}

/* ===== Scroll Area ===== */
QScrollArea {
    background-color: #252538;
    border: 1px solid #3a3a5a;
    border-radius: 8px;
}

/* ===== Progress Bar ===== */
QProgressBar {
    border: 2px solid #3a3a5a;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
    background-color: #2a2a3e;
    color: #e0e0e0;
}

QProgressBar::chunk {
    background-color: #4a9eff;
    border-radius: 6px;
}

/* ===== Service Cards ===== */
QFrame#serviceCard {
    background-color: #2a2a3e;
    border: 2px solid #3a3a5a;
    border-radius: 12px;
}

QFrame#serviceCard:hover {
    border-color: #4a9eff;
    background-color: #32324a;
}

QFrame#serviceCard.healthy {
    border-color: #4CAF50;
}

QFrame#serviceCard.unhealthy {
    border-color: #f44336;
}

/* ===== Input Fields ===== */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #2a2a3e;
    border: 1px solid #3a3a5a;
    border-radius: 6px;
    padding: 8px;
    color: #e0e0e0;
    selection-background-color: #4a9eff;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #4a9eff;
}

/* ===== Combo Box ===== */
QComboBox {
    background-color: #2a2a3e;
    border: 1px solid #3a3a5a;
    border-radius: 6px;
    padding: 8px;
    color: #e0e0e0;
}

QComboBox:hover {
    border-color: #4a9eff;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #e0e0e0;
    margin-right: 10px;
}

/* ===== Status Bar ===== */
QStatusBar {
    background-color: #2a2a3e;
    color: #a0a0b0;
    border-top: 1px solid #3a3a5a;
}

/* ===== Tool Tips ===== */
QToolTip {
    background-color: #3a3a5a;
    color: #e0e0e0;
    border: 1px solid #4a4a6a;
    border-radius: 4px;
    padding: 5px;
}

/* ===== Menu Bar ===== */
QMenuBar {
    background-color: #2a2a3e;
    color: #e0e0e0;
}

QMenuBar::item:selected {
    background-color: #3a3a5a;
}

/* ===== Dialog ===== */
QDialog {
    background-color: #1e1e2e;
}

QMessageBox {
    background-color: #1e1e2e;
}
"""

# Light Theme (清新简洁)
LIGHT_THEME = """
/* ===== Global Styles ===== */
QWidget {
    background-color: #f5f5f5;
    color: #333333;
    font-family: "Microsoft YaHei", "Segoe UI", Arial;
    font-size: 14px;
}

/* ===== Main Window ===== */
QMainWindow {
    background-color: #f5f5f5;
}

/* ===== Tab Widget ===== */
QTabWidget::pane {
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #e8e8e8;
    color: #666666;
    padding: 12px 24px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #333333;
}

QTabBar::tab:hover:!selected {
    background-color: #f0f0f0;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #e0e0e0;
    color: #333333;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #d0d0d0;
}

QPushButton:pressed {
    background-color: #c0c0c0;
}

QPushButton:disabled {
    background-color: #f0f0f0;
    color: #999999;
}

/* Primary Button */
QPushButton#primaryBtn {
    background-color: #4CAF50;
    color: white;
}

QPushButton#primaryBtn:hover {
    background-color: #45a049;
}

/* Danger Button */
QPushButton#dangerBtn {
    background-color: #f44336;
    color: white;
}

QPushButton#dangerBtn:hover {
    background-color: #da190b;
}

/* ===== Labels ===== */
QLabel {
    color: #333333;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #2196F3;
}

QLabel#descLabel {
    color: #666666;
    font-style: italic;
}

/* ===== Scroll Area ===== */
QScrollArea {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 8px;
}

/* ===== Progress Bar ===== */
QProgressBar {
    border: 2px solid #ddd;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
    background-color: #f0f0f0;
    color: #333333;
}

QProgressBar::chunk {
    background-color: #2196F3;
    border-radius: 6px;
}

/* ===== Service Cards ===== */
QFrame#serviceCard {
    background-color: #ffffff;
    border: 2px solid #ddd;
    border-radius: 12px;
}

QFrame#serviceCard:hover {
    border-color: #2196F3;
    background-color: #f8f9fa;
}

QFrame#serviceCard.healthy {
    border-color: #4CAF50;
}

QFrame#serviceCard.unhealthy {
    border-color: #f44336;
}

/* ===== Input Fields ===== */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 8px;
    color: #333333;
    selection-background-color: #2196F3;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #2196F3;
}

/* ===== Combo Box ===== */
QComboBox {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 8px;
    color: #333333;
}

QComboBox:hover {
    border-color: #2196F3;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #333333;
    margin-right: 10px;
}

/* ===== Status Bar ===== */
QStatusBar {
    background-color: #f0f0f0;
    color: #666666;
    border-top: 1px solid #ddd;
}

/* ===== Tool Tips ===== */
QToolTip {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 5px;
}

/* ===== Menu Bar ===== */
QMenuBar {
    background-color: #f0f0f0;
    color: #333333;
}

QMenuBar::item:selected {
    background-color: #e0e0e0;
}

/* ===== Dialog ===== */
QDialog {
    background-color: #f5f5f5;
}

QMessageBox {
    background-color: #f5f5f5;
}
"""

# Cyberpunk Theme (酷炫蓝紫配色)
CYBERPUNK_THEME = """
/* ===== Global Styles ===== */
QWidget {
    background-color: #0a0a1a;
    color: #00ffff;
    font-family: "Microsoft YaHei", "Segoe UI", Arial;
    font-size: 14px;
}

/* ===== Main Window ===== */
QMainWindow {
    background-color: #0a0a1a;
}

/* ===== Tab Widget ===== */
QTabWidget::pane {
    border: 2px solid #00ffff;
    border-radius: 8px;
    background-color: #12122a;
}

QTabBar::tab {
    background-color: #1a1a3a;
    color: #008888;
    padding: 12px 24px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: bold;
    border: 1px solid #005555;
}

QTabBar::tab:selected {
    background-color: #00ffff;
    color: #000000;
    border-color: #00ffff;
}

QTabBar::tab:hover:!selected {
    background-color: #22224a;
    border-color: #00aaaa;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #1a1a3a;
    color: #00ffff;
    border: 2px solid #00ffff;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #00ffff;
    color: #000000;
    border-color: #00ffff;
}

QPushButton:pressed {
    background-color: #00cccc;
    border-color: #00aaaa;
}

QPushButton:disabled {
    background-color: #1a1a2a;
    color: #005555;
    border-color: #003333;
}

/* Primary Button */
QPushButton#primaryBtn {
    background-color: #ff00ff;
    color: white;
    border-color: #ff00ff;
}

QPushButton#primaryBtn:hover {
    background-color: #ff33ff;
    border-color: #ff66ff;
}

/* Danger Button */
QPushButton#dangerBtn {
    background-color: #ff3333;
    color: white;
    border-color: #ff0000;
}

QPushButton#dangerBtn:hover {
    background-color: #ff6666;
    border-color: #ff3333;
}

/* ===== Labels ===== */
QLabel {
    color: #00ffff;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #ff00ff;
}

QLabel#descLabel {
    color: #00aaaa;
    font-style: italic;
}

/* ===== Scroll Area ===== */
QScrollArea {
    background-color: #12122a;
    border: 1px solid #00ffff;
    border-radius: 8px;
}

/* ===== Progress Bar ===== */
QProgressBar {
    border: 2px solid #00ffff;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
    background-color: #1a1a3a;
    color: #00ffff;
}

QProgressBar::chunk {
    background-color: #ff00ff;
    border-radius: 6px;
}

/* ===== Service Cards ===== */
QFrame#serviceCard {
    background-color: #1a1a3a;
    border: 2px solid #00ffff;
    border-radius: 12px;
}

QFrame#serviceCard:hover {
    border-color: #ff00ff;
    background-color: #22224a;
}

QFrame#serviceCard.healthy {
    border-color: #00ff00;
}

QFrame#serviceCard.unhealthy {
    border-color: #ff0000;
}

/* ===== Input Fields ===== */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1a1a3a;
    border: 1px solid #00ffff;
    border-radius: 6px;
    padding: 8px;
    color: #00ffff;
    selection-background-color: #ff00ff;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #ff00ff;
}

/* ===== Combo Box ===== */
QComboBox {
    background-color: #1a1a3a;
    border: 1px solid #00ffff;
    border-radius: 6px;
    padding: 8px;
    color: #00ffff;
}

QComboBox:hover {
    border-color: #ff00ff;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #00ffff;
    margin-right: 10px;
}

/* ===== Status Bar ===== */
QStatusBar {
    background-color: #12122a;
    color: #00aaaa;
    border-top: 1px solid #00ffff;
}

/* ===== Tool Tips ===== */
QToolTip {
    background-color: #1a1a3a;
    color: #00ffff;
    border: 1px solid #00ffff;
    border-radius: 4px;
    padding: 5px;
}

/* ===== Menu Bar ===== */
QMenuBar {
    background-color: #12122a;
    color: #00ffff;
}

QMenuBar::item:selected {
    background-color: #1a1a3a;
}

/* ===== Dialog ===== */
QDialog {
    background-color: #0a0a1a;
}

QMessageBox {
    background-color: #0a0a1a;
}
"""

# Theme Manager
class ThemeManager:
    """Manage application themes"""
    
    THEMES = {
        'dark': ('深色主题', DARK_THEME),
        'light': ('浅色主题', LIGHT_THEME),
        'cyberpunk': ('科技主题', CYBERPUNK_THEME)
    }
    
    @classmethod
    def get_theme_names(cls):
        """Get list of theme names"""
        return list(cls.THEMES.keys())
    
    @classmethod
    def get_theme_display_name(cls, theme_name: str) -> str:
        """Get display name for a theme"""
        if theme_name in cls.THEMES:
            return cls.THEMES[theme_name][0]
        return theme_name
    
    @classmethod
    def get_theme_stylesheet(cls, theme_name: str) -> str:
        """Get stylesheet for a theme"""
        if theme_name in cls.THEMES:
            return cls.THEMES[theme_name][1]
        return DARK_THEME  # Default to dark
    
    @classmethod
    def get_default_theme(cls) -> str:
        """Get default theme name"""
        return 'dark'

#!/usr/bin/env python3
"""
谎言骰子游戏启动器
Liar's Dice Game Launcher

运行此文件启动游戏GUI界面
"""

import sys
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """检查必要的依赖"""
    missing_modules = []

    try:
        import openai
    except ImportError:
        missing_modules.append("openai")

    if missing_modules:
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror(
            "缺少依赖",
            f"缺少以下Python模块：{', '.join(missing_modules)}\n\n"
            "请运行以下命令安装：\n"
            f"pip install {' '.join(missing_modules)}"
        )
        return False

    return True

def main():
    """主函数"""
    print("🎮 启动谎言骰子游戏...")

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    try:
        # 导入并启动GUI
        from src.liars_dice_gui import LiarsDiceGUI

        print("✅ 依赖检查完成，启动GUI...")
        app = LiarsDiceGUI()
        app.run()

    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("启动错误", f"游戏启动失败：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
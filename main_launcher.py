#!/usr/bin/env python3
"""
谎言骰子游戏启动器
Liar's Dice Game Launcher

运行此文件启动游戏GUI界面
"""

import sys
import tkinter as tk
from tkinter import messagebox

def main():
    """主函数"""
    print("🎮 启动谎言骰子游戏...")

    try:
        # 导入并启动GUI
        from src.liars_dice_gui import LiarsDiceGUI

        print("启动GUI...")
        app = LiarsDiceGUI()
        app.run()

    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("启动错误", f"游戏启动失败：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
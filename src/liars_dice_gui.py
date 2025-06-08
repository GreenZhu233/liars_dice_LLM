import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import threading
import time
from typing import Dict, Any
from src.game import LiarsDiceGame
from src.players import Player

class LiarsDiceGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Liar's Dice Game")
        self.root.geometry("1600x900")
        self.root.configure(bg="#2c3e50")

        # 游戏状态
        self.game = None
        self.game_thread = None
        self.is_game_running = False
        self.human_action_event = None
        self.human_action_result = None

        # 创建主界面
        self.create_main_interface()

    def create_main_interface(self):
        """创建主界面"""
        # 清空界面
        for widget in self.root.winfo_children():
            widget.destroy()

        # 标题
        title_label = tk.Label(
            self.root,
            text="Liar's Dice Game",
            font=("Arial", 24, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50"
        )
        title_label.pack(pady=30)

        # 游戏模式选择框
        mode_frame = tk.Frame(self.root, bg="#2c3e50")
        mode_frame.pack(pady=20)

        tk.Label(
            mode_frame,
            text="选择游戏模式:",
            font=("Arial", 14),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack()

        self.game_mode = tk.StringVar(value="ai_only")

        mode_options = [
            ("4个AI对局", "ai_only"),
            ("人类玩家 vs 3个AI", "human_vs_ai")
        ]

        for text, value in mode_options:
            tk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.game_mode,
                value=value,
                font=("Arial", 12),
                fg="#ecf0f1",
                bg="#2c3e50",
                selectcolor="#34495e",
                activebackground="#34495e",
                activeforeground="#ecf0f1"
            ).pack(anchor="w", padx=20)

        # API设置按钮
        api_button = tk.Button(
            self.root,
            text="设置API Keys",
            command=self.show_api_settings,
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=10,
            relief="flat",
            cursor="hand2"
        )
        api_button.pack(pady=20)

        # 开始游戏按钮
        start_button = tk.Button(
            self.root,
            text="开始游戏",
            command=self.start_game,
            font=("Arial", 14, "bold"),
            bg="#27ae60",
            fg="white",
            padx=30,
            pady=15,
            relief="flat",
            cursor="hand2"
        )
        start_button.pack(pady=30)

    def show_api_settings(self):
        """显示API设置窗口"""
        api_window = tk.Toplevel(self.root)
        api_window.title("API Keys 设置")
        api_window.geometry("500x400")
        api_window.configure(bg="#2c3e50")
        api_window.grab_set()  # 模态窗口

        # 读取现有配置
        config = self.load_config()

        tk.Label(
            api_window,
            text="API Keys 配置",
            font=("Arial", 16, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(pady=20)

        # DeepSeek API Key
        deepseek_frame = tk.Frame(api_window, bg="#2c3e50")
        deepseek_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(
            deepseek_frame,
            text="DeepSeek API Key:",
            font=("Arial", 12),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(anchor="w")

        deepseek_entry = tk.Entry(
            deepseek_frame,
            font=("Arial", 11),
            width=50,
            show="*"
        )
        deepseek_entry.pack(pady=5, fill="x")
        deepseek_entry.insert(0, config.get("DEEPSEEK_API_KEY", ""))

        # Doubao API Key
        doubao_frame = tk.Frame(api_window, bg="#2c3e50")
        doubao_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(
            doubao_frame,
            text="Doubao API Key:",
            font=("Arial", 12),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(anchor="w")

        doubao_entry = tk.Entry(
            doubao_frame,
            font=("Arial", 11),
            width=50,
            show="*"
        )
        doubao_entry.pack(pady=5, fill="x")
        doubao_entry.insert(0, config.get("DOUBAO_API_KEY", ""))

        # 按钮框架
        button_frame = tk.Frame(api_window, bg="#2c3e50")
        button_frame.pack(pady=30)

        def save_config():
            config = {
                "DEEPSEEK_API_KEY": deepseek_entry.get().strip(),
                "DOUBAO_API_KEY": doubao_entry.get().strip()
            }

            # 确保config目录存在
            os.makedirs("config", exist_ok=True)

            try:
                with open("config/keys.json", "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2)
                messagebox.showinfo("成功", "API Keys 保存成功！")
                api_window.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")

        tk.Button(
            button_frame,
            text="保存",
            command=save_config,
            font=("Arial", 12),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=10)

        tk.Button(
            button_frame,
            text="取消",
            command=api_window.destroy,
            font=("Arial", 12),
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=10)

    def load_config(self):
        """加载配置文件"""
        try:
            with open("config/keys.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def start_game(self):
        """开始游戏"""
        # 检查API keys
        config = self.load_config()
        if not config.get("DEEPSEEK_API_KEY"):
            messagebox.showerror("错误", "请先设置DeepSeek API Key！")
            return

        # 创建游戏界面
        self.create_game_interface()

        # 创建玩家
        if self.game_mode.get() == "ai_only":
            players = [
                Player(name="Alice", is_human=False, model="deepseek-chat"),
                Player(name="Bob", is_human=False, model="deepseek-chat"),
                Player(name="Charlie", is_human=False, model="deepseek-chat"),
                Player(name="David", is_human=False, model="deepseek-chat")
            ]
        else:
            players = [
                Player(name="Alice", is_human=True, model=""),
                Player(name="Bob", is_human=False, model="deepseek-chat"),
                Player(name="Charlie", is_human=False, model="deepseek-chat"),
                Player(name="David", is_human=False, model="deepseek-chat")
            ]

        # 启动游戏线程
        self.game = LiarsDiceGame(players)
        self.game.set_gui(self)  # 设置GUI引用
        self.is_game_running = True
        self.game_thread = threading.Thread(target=self.run_game_thread)
        self.game_thread.daemon = True
        self.game_thread.start()

    def create_game_interface(self):
        """创建游戏界面"""
        # 清空界面
        for widget in self.root.winfo_children():
            widget.destroy()

        # 主框架
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 左侧信息面板
        left_frame = tk.Frame(main_frame, bg="#34495e", width=300)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)

        # 玩家信息
        tk.Label(
            left_frame,
            text="玩家状态",
            font=("Arial", 14, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        ).pack(pady=10)

        self.players_info = tk.Frame(left_frame, bg="#34495e")
        self.players_info.pack(fill="x", padx=10)

        # 当前骰子显示
        if self.game_mode.get() != 'ai_only':
            tk.Label(
                left_frame,
                text="你的骰子",
                font=("Arial", 12, "bold"),
                fg="#ecf0f1",
                bg="#34495e"
            ).pack(pady=(20, 5))

        self.dice_frame = tk.Frame(left_frame, bg="#34495e")
        self.dice_frame.pack(pady=10)

        # 右侧游戏区域
        right_frame = tk.Frame(main_frame, bg="#34495e")
        right_frame.pack(side="right", fill="both", expand=True)

        # 游戏日志
        tk.Label(
            right_frame,
            text="游戏日志",
            font=("Arial", 14, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        ).pack(pady=10)

        self.log_text = scrolledtext.ScrolledText(
            right_frame,
            height=20,
            font=("Consolas", 10),
            bg="#2c3e50",
            fg="#ecf0f1",
            insertbackground="#ecf0f1"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 人类玩家操作区域
        self.action_frame = tk.Frame(right_frame, bg="#34495e")
        self.action_frame.pack(fill="x", padx=10, pady=10)

        # 返回主菜单按钮
        tk.Button(
            right_frame,
            text="返回主菜单",
            command=self.return_to_main,
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=5,
            relief="flat",
            cursor="hand2"
        ).pack(pady=10)

    def update_players_info(self, players):
        """更新玩家信息显示"""
        # 清空现有信息
        for widget in self.players_info.winfo_children():
            widget.destroy()

        for player in players:
            player_frame = tk.Frame(self.players_info, bg="#2c3e50", relief="solid", bd=1)
            player_frame.pack(fill="x", pady=2)

            # 玩家名称和毒药数量
            info_text = f"{player.name}: {player.poison}瓶毒药"
            if not player.is_alive():
                info_text += " (已死亡)"

            tk.Label(
                player_frame,
                text=info_text,
                font=("Arial", 11),
                fg="#ecf0f1" if player.is_alive() else "#95a5a6",
                bg="#2c3e50"
            ).pack(pady=5)

    def update_dice_display(self, dice):
        """更新骰子显示"""
        # 清空现有骰子
        for widget in self.dice_frame.winfo_children():
            widget.destroy()

        if dice:
            for i, die in enumerate(dice):
                die_label = tk.Label(
                    self.dice_frame,
                    text=str(die),
                    font=("Arial", 16, "bold"),
                    fg="#ecf0f1",
                    bg="#e74c3c",
                    width=3,
                    height=1,
                    relief="solid",
                    bd=2
                )
                die_label.grid(row=0, column=i, padx=2)

    def log_message(self, message):
        """添加日志消息"""
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.root.update()

    def show_human_action_interface(self, is_first, current_bid_number, current_bid_value):
        """显示人类玩家操作界面"""
        # 清空操作区域
        for widget in self.action_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.action_frame,
            text="轮到你行动！",
            font=("Arial", 14, "bold"),
            fg="#f39c12",
            bg="#34495e"
        ).pack(pady=10)

        # 创建操作选项
        action_type = tk.StringVar(value="bid")

        # 如果不是第一个玩家，显示质疑选项
        if not is_first:
            tk.Radiobutton(
                self.action_frame,
                text="质疑上家",
                variable=action_type,
                value="challenge",
                font=("Arial", 12),
                fg="#ecf0f1",
                bg="#34495e",
                selectcolor="#2c3e50",
                activebackground="#34495e",
                activeforeground="#ecf0f1"
            ).pack(anchor="w")

        tk.Radiobutton(
            self.action_frame,
            text="叫点",
            variable=action_type,
            value="bid",
            font=("Arial", 12),
            fg="#ecf0f1",
            bg="#34495e",
            selectcolor="#2c3e50",
            activebackground="#34495e",
            activeforeground="#ecf0f1"
        ).pack(anchor="w")

        # 叫点输入
        bid_frame = tk.Frame(self.action_frame, bg="#34495e")
        bid_frame.pack(pady=10)

        tk.Label(bid_frame, text="数量:", font=("Arial", 12), fg="#ecf0f1", bg="#34495e").grid(row=0, column=0, padx=5)
        number_var = tk.StringVar(value=str(current_bid_number + 1))
        number_entry = tk.Spinbox(bid_frame, from_=1, to=20, textvariable=number_var, width=5, font=("Arial", 12))
        number_entry.grid(row=0, column=1, padx=5)

        tk.Label(bid_frame, text="点数:", font=("Arial", 12), fg="#ecf0f1", bg="#34495e").grid(row=0, column=2, padx=5)
        value_var = tk.StringVar(value=str(current_bid_value))
        value_spinbox = tk.Spinbox(bid_frame, from_=1, to=6, textvariable=value_var, width=5, font=("Arial", 12))
        value_spinbox.grid(row=0, column=3, padx=5)

        # 表现输入
        tk.Label(
            self.action_frame,
            text="表现/发言:",
            font=("Arial", 12),
            fg="#ecf0f1",
            bg="#34495e"
        ).pack(anchor="w", pady=(10, 5))

        behavior_text = tk.Text(
            self.action_frame,
            height=2,
            width=50,
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#ecf0f1",
            insertbackground="#ecf0f1"
        )
        behavior_text.pack(pady=5)

        def submit_action():
            try:
                is_challenge = action_type.get() == "challenge"
                number = 0 if is_challenge else int(number_var.get())
                value = 0 if is_challenge else int(value_var.get())
                # reason = reason_text.get("1.0", tk.END).strip()
                reason = ""
                behavior = behavior_text.get("1.0", tk.END).strip()

                self.human_action_result = {
                    "challenge": is_challenge,
                    "number": number,
                    "value": value,
                    "reason": reason,
                    "behaviour": behavior
                }

                # 清空操作界面
                for widget in self.action_frame.winfo_children():
                    widget.destroy()

                tk.Label(
                    self.action_frame,
                    text="等待其他玩家...",
                    font=("Arial", 12),
                    fg="#95a5a6",
                    bg="#34495e"
                ).pack(pady=20)

                # 设置事件
                if self.human_action_event:
                    self.human_action_event.set()

            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字！")

        tk.Button(
            self.action_frame,
            text="确认",
            command=submit_action,
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=10,
            relief="flat",
            cursor="hand2"
        ).pack(pady=20)

    def run_game_thread(self):
        """运行游戏线程"""
        try:
            winner = self.game.start_game()
            if self.is_game_running:
                self.root.after(0, lambda: self.show_game_result(winner))
        except Exception as e:
            if self.is_game_running:
                self.root.after(0, lambda: messagebox.showerror("游戏错误", f"游戏发生错误：{str(e)}"))

    def show_game_result(self, winner):
        """显示游戏结果"""
        result_msg = f"游戏结束！\n获胜者：{winner}"
        messagebox.showinfo("游戏结果", result_msg)
        self.log_message(f"\n🎉 游戏结束！获胜者：{winner} 🎉")
        self.is_game_running = False

    def return_to_main(self):
        """返回主菜单"""
        if self.is_game_running:
            if messagebox.askyesno("确认", "游戏正在进行中，确定要返回主菜单吗？"):
                self.is_game_running = False
                self.create_main_interface()
        else:
            self.create_main_interface()

    def run(self):
        """运行GUI"""
        self.root.mainloop()

# 为Player类添加GUI相关方法
def get_human_action(self):
    """获取人类玩家的操作"""
    if not hasattr(self, 'gui'):
        raise RuntimeError("Human player needs GUI reference")
    
    gui = self.gui
    
    # 创建事件
    gui.human_action_event = threading.Event()
    gui.human_action_result = None
    
    # 获取当前叫点信息
    current_bid_number = getattr(gui.game, 'dice_number', 0)
    current_bid_value = getattr(gui.game, 'dice_value', 0)
    
    # 更新骰子显示
    # gui.root.after(0, lambda: gui.update_dice_display(self.dice))
    
    # 显示操作界面
    is_first = current_bid_number == 0
    gui.root.after(0, lambda: gui.show_human_action_interface(is_first, current_bid_number, current_bid_value))
    
    # 等待用户操作
    gui.human_action_event.wait()
    
    return gui.human_action_result

# 修改Player类
Player.get_human_action = get_human_action

if __name__ == "__main__":
    app = LiarsDiceGUI()
    app.run()
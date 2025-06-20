import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import threading
from src.game import LiarsDiceGame
from src.players import Player
from src.snippets import *

class LiarsDiceGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Liar's Dice Game")
        self.root.iconbitmap("images/diceicon.ico")
        maxwide, maxheight = self.root.maxsize()
        self.root.geometry(f"{int(maxwide*0.9)}x{int(maxheight*0.9)}+{int(maxwide*0.05)}+{int(maxheight*0.05)}")
        self.root.configure(bg="#2c3e50")

        # 游戏状态
        self.game = None
        self.game_thread = None
        self.is_game_running = False
        self.human_action_event = None
        self.human_action_result = None

        # 加载角色配置
        os.makedirs("config", exist_ok=True)
        try:
            with open("config/players.json", "r", encoding="utf-8") as f:
                self.role_config = json.load(f)
        except:
            self.role_config = [
                {"name": "Alice", "model": "deepseek-chat"},
                {"name": "Bob", "model": "deepseek-chat"},
                {"name": "Charlie", "model": "deepseek-chat"},
                {"name": "David", "model": "deepseek-chat"}
            ]

        # 加载骰子图片
        self.dice_images = []
        for i in range(1,7):
            img_path = os.path.join("images", f"dice{i}.png")
            img = tk.PhotoImage(file=img_path)
            self.dice_images.append(img)

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
            text="谎 言 骰 子",
            font=("Heiti", 32, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50"
        )
        title_label.pack(pady=60)

        # 游戏模式选择框
        mode_frame = tk.Frame(self.root, bg="#2c3e50")
        mode_frame.pack(pady=20)

        tk.Label(
            mode_frame,
            text="选择游戏模式:",
            font=("Heiti", 14),
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
                font=("Heiti", 12),
                fg="#ecf0f1",
                bg="#2c3e50",
                selectcolor="#34495e",
                activebackground="#34495e",
                activeforeground="#ecf0f1"
            ).pack(anchor="w", padx=20)

        # API设置按钮
        api_button = tk.Button(
            self.root,
            text="API Keys",
            command=self.show_api_settings,
            font=("Heiti", 12),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=10,
            relief="flat",
            cursor="hand2"
        )
        api_button.pack(pady=15)

        # 角色配置按钮
        role_button = tk.Button(
            self.root,
            text="角色配置",
            command=self.show_role_settings,
            font=("Heiti", 12),
            bg="#9b59b6",
            fg="white",
            padx=20,
            pady=10,
            relief="flat",
            cursor="hand2"
        )
        role_button.pack(pady=15)

        # 开始游戏按钮
        start_button = tk.Button(
            self.root,
            text="开始游戏",
            command=self.start_game,
            font=("Heiti", 14,),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=10,
            relief="flat",
            cursor="hand2"
        )
        start_button.pack(pady=15)

    def show_api_settings(self):
        """显示API设置窗口"""
        api_window = tk.Toplevel(self.root)
        api_window.title("API Keys 设置")
        api_window.geometry("500x700")
        api_window.configure(bg="#2c3e50")
        api_window.grab_set()  # 模态窗口

        # 读取现有配置
        config = self.load_api_config()

        tk.Label(
            api_window,
            text="API Keys 配置",
            font=("Heiti", 16, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(pady=20)

        # DeepSeek API Key
        deepseek_frame = tk.Frame(api_window, bg="#2c3e50")
        deepseek_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(
            deepseek_frame,
            text="DeepSeek API Key:",
            font=("Heiti", 12),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(anchor="w")

        deepseek_entry = tk.Entry(
            deepseek_frame,
            font=("Heiti", 11),
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
            text="Doubao（豆包） API Key:",
            font=("Heiti", 12),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(anchor="w")

        doubao_entry = tk.Entry(
            doubao_frame,
            font=("Heiti", 11),
            width=50,
            show="*"
        )
        doubao_entry.pack(pady=5, fill="x")
        doubao_entry.insert(0, config.get("DOUBAO_API_KEY", ""))

        # gemini API Key
        gemini_frame = tk.Frame(api_window, bg="#2c3e50")
        gemini_frame.pack(pady=10, padx=20, fill='x')

        tk.Label(
            gemini_frame,
            text="Gemini API Key:",
            font=("Heiti", 12),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(anchor="w")

        gemini_entry = tk.Entry(
            gemini_frame,
            font=("Heiti", 11),
            width=50,
            show="*"
        )
        gemini_entry.pack(pady=5, fill="x")
        gemini_entry.insert(0, config.get("GEMINI_API_KEY", ""))

        # 质谱API Key
        zhipu_frame = tk.Frame(api_window, bg="#2c3e50")
        zhipu_frame.pack(pady=10, padx=20, fill='x')

        tk.Label(
            zhipu_frame,
            text="ZhiPu（智谱） API Key:",
            font=("Heiti", 12),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(anchor="w")

        zhipu_entry = tk.Entry(
            zhipu_frame,
            font=("Heiti", 11),
            width=50,
            show="*"
        )
        zhipu_entry.pack(pady=5, fill="x")
        zhipu_entry.insert(0, config.get("ZHIPU_API_KEY", ""))

        # 千问 API Key
        qwen_frame = tk.Frame(api_window, bg="#2c3e50")
        qwen_frame.pack(pady=10, padx=20, fill='x')

        tk.Label(
            qwen_frame,
            text="DashScope（千问） API Key:",
            font=("Heiti", 12),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(anchor="w")

        qwen_entry = tk.Entry(
            qwen_frame,
            font=("Heiti", 11),
            width=50,
            show="*"
        )
        qwen_entry.pack(pady=5, fill="x")
        qwen_entry.insert(0, config.get("DASHSCOPE_API_KEY", ""))

        # 混元 API Key
        hunyuan_frame = tk.Frame(api_window, bg="#2c3e50")
        hunyuan_frame.pack(pady=10, padx=20, fill='x')

        tk.Label(
            hunyuan_frame,
            text="HunYuan（混元） API Key:",
            font=("Heiti", 12),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(anchor="w")

        hunyuan_entry = tk.Entry(
            hunyuan_frame,
            font=("Heiti", 11),
            width=50,
            show="*"
        )
        hunyuan_entry.pack(pady=5, fill="x")
        hunyuan_entry.insert(0, config.get("HUNYUAN_API_KEY", ""))

        # 星火 API Key
        x1_frame = tk.Frame(api_window, bg="#2c3e50")
        x1_frame.pack(pady=10, padx=20, fill='x')

        tk.Label(
            x1_frame,
            text="Spark（星火） API Key:",
            font=("Heiti", 12),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(anchor="w")

        x1_entry = tk.Entry(
            x1_frame,
            font=("Heiti", 11),
            width=50,
            show="*"
        )
        x1_entry.pack(pady=5, fill="x")
        x1_entry.insert(0, config.get("SPARK_API_KEY", ""))

        # 按钮框架
        button_frame = tk.Frame(api_window, bg="#2c3e50")
        button_frame.pack(pady=30)

        def save_config():
            config = {
                "DEEPSEEK_API_KEY": deepseek_entry.get().strip(),
                "DOUBAO_API_KEY": doubao_entry.get().strip(),
                "GEMINI_API_KEY": gemini_entry.get().strip(),
                "ZHIPU_API_KEY": zhipu_entry.get().strip(),
                "DASHSCOPE_API_KEY": qwen_entry.get().strip(),
                "HUNYUAN_API_KEY": hunyuan_entry.get().strip(),
                "SPARK_API_KEY": x1_entry.get().strip()
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
            font=("Heiti", 12),
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
            font=("Heiti", 12),
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(side="left", padx=10)

    def show_role_settings(self):
        """显示角色配置窗口"""
        role_window = tk.Toplevel(self.root)
        role_window.title("角色配置")
        role_window.geometry("500x500")
        role_window.configure(bg="#2c3e50")
        role_window.grab_set()

        tk.Label(
            role_window,
            text="角色配置",
            font=("Heiti", 16, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(pady=20)

        # 创建滚动框架
        canvas = tk.Canvas(role_window, bg="#2c3e50")
        scrollbar = ttk.Scrollbar(role_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2c3e50")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 角色配置区域
        role_entries = []

        for i, role in enumerate(self.role_config):
            frame = tk.Frame(scrollable_frame, bg="#34495e", relief="solid", bd=1)
            frame.pack(fill="x", padx=20, pady=10)

            tk.Label(
                frame,
                text=f"玩家 {i+1}:(AI)" if i > 0 else "玩家 1:(AI或人类玩家)",
                font=("Heiti", 12, "bold"),
                fg="#ecf0f1",
                bg="#34495e"
            ).grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

            # 玩家名字
            tk.Label(frame, text="名字:", font=("Heiti", 10), fg="#ecf0f1", bg="#34495e").grid(row=2, column=0, sticky="w", padx=5)
            name_var = tk.StringVar(value=role["name"])
            name_entry = tk.Entry(frame, textvariable=name_var, width=30)
            name_entry.grid(row=2, column=1, padx=5, pady=2)

            # AI模型
            tk.Label(frame, text="AI模型:", font=("Heiti", 10), fg="#ecf0f1", bg="#34495e").grid(row=3, column=0, sticky="w", padx=5)
            model_var = tk.StringVar(value=role["model"])
            model_combo = ttk.Combobox(
                frame,
                textvariable=model_var,
                values=model_list,
                state="readonly",
                width=30
            )
            model_combo.grid(row=3, column=1, padx=5, pady=2)

            role_entries.append({
                "name": name_var,
                "model": model_var
            })

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 按钮框架
        button_frame = tk.Frame(role_window, bg="#2c3e50")
        button_frame.pack(pady=20)

        def save_roles():
            try:
                new_config = []

                for entry in role_entries:

                    new_config.append({
                        "name": entry["name"].get().strip() or f"Player{len(new_config)+1}",
                        "model": entry["model"].get(),
                    })

                self.role_config = new_config
                with open("config/players.json", "w", encoding="utf-8") as f:
                    json.dump(new_config, f, indent=2)
                messagebox.showinfo("成功", "角色配置保存成功！")
                role_window.destroy()

            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")

        tk.Button(
            button_frame,
            text="保存",
            command=save_roles,
            font=("Heiti", 12),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(side="top", padx=10, pady=30)

        tk.Button(
            button_frame,
            text="取消",
            command=role_window.destroy,
            font=("Heiti", 12),
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=8,
            relief="flat",
            cursor="hand2"
        ).pack(side="top", padx=10, pady=30)

    def load_api_config(self):
        """加载API配置文件"""
        try:
            with open("config/keys.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def start_game(self):
        """开始游戏"""
        # 检查API keys
        config = self.load_api_config()
        for role in self.role_config:
            if not config.get(model_to_key_name[role["model"]]):
                messagebox.showerror("错误", f"请先配置好 API Key: {role["model"]}")
                return

        # 创建游戏界面
        self.create_game_interface()

        # 根据角色配置创建玩家
        players = []
        if self.game_mode.get() == "ai_only":
            for role in self.role_config:
                players.append(Player(name=role["name"], is_human=False, model=role["model"]))
        else:
            for i, role in enumerate(self.role_config):
                players.append(Player(
                    name=role["name"],
                    is_human=False if i > 0 else True,
                    model=role["model"] if i > 0 else ""
                ))

        # 启动游戏线程
        self.game = LiarsDiceGame(players)
        self.game.set_gui(self)
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
        self.left_frame = tk.Frame(main_frame, bg="#34495e", width=300)
        self.left_frame.pack(side="left", fill="y", padx=(0, 10))
        self.left_frame.pack_propagate(False)

        # 玩家信息
        tk.Label(
            self.left_frame,
            text="玩家状态",
            font=("Heiti", 22, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        ).pack(pady=10)

        self.players_info = tk.Frame(self.left_frame, bg="#34495e")
        self.players_info.pack(fill="x", padx=10)

        self.dice_frames = []

        # 当前赌注显示
        tk.Label(
            self.left_frame,
            text="当前赌注",
            font=("Heiti", 22, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        ).pack(pady=(20, 5))

        self.bid_frame = tk.Frame(self.left_frame, bg="#34495e", height=60)
        self.bid_frame.pack(fill='x', padx=10)

        self.bid_label = tk.Label(
            self.bid_frame,
            bg="#34495e",
            fg="#ee3636",
            font=("Heiti", 22, "bold"),
            text=""
        )
        self.bid_label.place(relx=0.3, rely=0.2)

        self.bid_dice = tk.Label(
            self.bid_frame,
            bg="#34495e",
            width=48,
            height=48,
            bd=2,
            borderwidth=0,
            relief="flat"
        )
        self.bid_dice.place(relx=0.55, rely=0.1)

        # 右侧游戏区域
        right_frame = tk.Frame(main_frame, bg="#34495e")
        right_frame.pack(side="right", fill="both", expand=True)

        # 游戏日志
        tk.Label(
            right_frame,
            text="游戏日志",
            font=("Heiti", 14, "bold"),
            fg="#ecf0f1",
            bg="#34495e"
        ).pack(pady=10)

        self.log_text = scrolledtext.ScrolledText(
            right_frame,
            height=20,
            font=("Consolas", 14),
            bg="#2c3e50",
            fg="#ecf0f1",
            insertbackground="#ecf0f1"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.log_text.config(state='disabled')

        # 人类玩家操作区域
        self.action_frame = tk.Frame(right_frame, bg="#34495e")
        self.action_frame.pack(fill="x", padx=10, pady=10)

        # 返回主菜单按钮
        tk.Button(
            self.left_frame,
            text="返回主菜单",
            command=self.return_to_main,
            font=("Heiti", 10),
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=5,
            relief="flat",
            cursor="hand2"
        ).pack(side='bottom', pady=30)

        self.root.update()

    def update_players_info(self, players):
        """更新玩家信息显示"""
        # 清空现有信息
        for widget in self.players_info.winfo_children():
            widget.destroy()

        del self.dice_frames
        self.dice_frames = []

        for player in players:
            player_frame = tk.Frame(self.players_info, bg="#2c3e50", relief="solid", bd=1)
            player_frame.pack(fill="x", pady=2)

            # 玩家名称和毒药数量
            info_text = f"{player.name}: {player.poison}瓶毒药"

            tk.Label(
                player_frame,
                text=info_text,
                font=("Heiti", 12),
                fg="#ecf0f1" if player.is_alive() else "#95a5a6",
                bg="#2c3e50"
            ).pack(pady=5)

            dice_frame = tk.Frame(self.players_info, bg="#34495e", height=48)
            dice_frame.pack(fill='x', pady=10)
            self.dice_frames.append(dice_frame)
        self.root.update()

    def update_dice_display(self, dices):
        """更新在场玩家骰子显示"""
        # 清空现有骰子
        for dice_frame in self.dice_frames:
            for widget in dice_frame.winfo_children():
                widget.destroy()

        for p, dice in enumerate(dices):
            for i, die in enumerate(dice):
                die_label = tk.Label(
                    self.dice_frames[p],
                    image=self.dice_images[die-1],
                    bg="#34495e",
                    width=48,
                    height=48,
                    bd=2,
                    borderwidth=0,
                    relief="flat"
                )
                die_label.grid(row=0, column=i, padx=2)
        self.root.update()

    def update_bid_display(self, number, value):
        """更新赌注显示"""
        if number:
            self.bid_label.configure(text = f"{number} X ")
            self.bid_dice.configure(image=self.dice_images[value-1])
        else:
            self.bid_label.configure(text = "")
            self.bid_dice.configure(image = "")

    def log_message(self, message):
        """添加日志消息"""
        if hasattr(self, 'log_text'):
            try:
                self.log_text.config(state='normal')
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state='disabled')
                self.root.update()
            except tk.TclError:
                # 忽略日志
                pass

    def show_human_action_interface(self, is_first, current_bid_number, current_bid_value):
        """显示人类玩家操作界面"""
        # 清空操作区域
        for widget in self.action_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.action_frame,
            text="轮到你行动！",
            font=("Heiti", 14, "bold"),
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
                font=("Heiti", 12),
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
            font=("Heiti", 12),
            fg="#ecf0f1",
            bg="#34495e",
            selectcolor="#2c3e50",
            activebackground="#34495e",
            activeforeground="#ecf0f1"
        ).pack(anchor="w")

        # 叫点输入
        bid_frame = tk.Frame(self.action_frame, bg="#34495e")
        bid_frame.pack(pady=10)

        tk.Label(bid_frame, text="数量:", font=("Heiti", 12), fg="#ecf0f1", bg="#34495e").grid(row=0, column=0, padx=5)
        number_var = tk.StringVar(value=str(current_bid_number + 1))
        number_entry = tk.Spinbox(bid_frame, from_=1, to=20, textvariable=number_var, width=5, font=("Heiti", 12))
        number_entry.grid(row=0, column=1, padx=5)

        tk.Label(bid_frame, text="点数:", font=("Heiti", 12), fg="#ecf0f1", bg="#34495e").grid(row=0, column=2, padx=5)
        value_var = tk.StringVar(value=str(current_bid_value))
        value_spinbox = tk.Spinbox(bid_frame, from_=1, to=6, textvariable=value_var, width=5, font=("Heiti", 12))
        value_spinbox.grid(row=0, column=3, padx=5)

        # 表现输入
        tk.Label(
            self.action_frame,
            text="表现/发言:",
            font=("Heiti", 12),
            fg="#ecf0f1",
            bg="#34495e"
        ).pack(anchor="w", pady=(10, 5))

        behavior_text = tk.Text(
            self.action_frame,
            height=2,
            width=200,
            font=("Heiti", 10),
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
                    font=("Heiti", 12),
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
            font=("Heiti", 12, "bold"),
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
            if self.is_game_running and winner:
                self.root.after(0, lambda: self.show_game_result(winner))
        except Exception as e:
            if self.is_game_running:
                self.root.after(0, lambda err=e: messagebox.showerror("游戏错误", f"游戏发生错误：{str(err)}"))

    def show_game_result(self, winner):
        """显示游戏结果"""
        result_msg = f"游戏结束！\n获胜者：{winner}"
        self.log_message(f"\n🎉 游戏结束！获胜者：{winner} 🎉")
        for widget in self.action_frame.winfo_children():
            widget.destroy()
        self.is_game_running = False
        messagebox.showinfo("游戏结果", result_msg)

    def return_to_main(self):
        """返回主菜单"""
        if self.is_game_running:
            if messagebox.askyesno("确认", "游戏正在进行中，确定要返回主菜单吗？"):
                self.game.logger.warning("游戏已被迫终止！")
                self.is_game_running = False
                self.game.is_running = False
                if self.human_action_event:
                    self.human_action_event.set()       # 防止游戏线程卡死
                self.game.logger.handlers.clear()
                # self.game_thread.join()
                self.create_main_interface()
        else:
            self.create_main_interface()

    def run(self):
        """运行GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = LiarsDiceGUI()
    app.run()
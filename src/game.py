from src.players import Player
import logging
import time
import random
import os
from typing import List, Dict, Any
import uuid
import threading
from tkinter import messagebox
from src.snippets import InvalidAction

class LiarsDiceGame():
    def __init__(self, players: List[Player], console_output = True, reflect_each_round = True):
        self.players = players
        self.game_mode = 'ai_only'
        self.human_player = None
        for player in players:
            if player.is_human:
                self.human_player = player
                self.game_mode = 'human_vs_ai'
            else:
                player.init_opinions(players)
        self.is_running = True
        self.round = 0
        self.active_players = []
        self.first_player = self.players[random.randint(0, len(self.players) - 1)]  # 随机选择第一个玩家
        self.current_player_index = 0
        self.gui = None  # GUI引用
        self.logger = self.create_logger(console_output)
        self.reflect_each_round = reflect_each_round

        # 轮次信息
        self.round_base_info = ""
        self.round_action_info = ""
        self.extra_hint = ""

    def set_gui(self, gui):
        """设置GUI引用"""
        self.gui = gui
        # 为人类玩家设置GUI引用
        for player in self.players:
            if player.is_human:
                player.gui = gui

    def create_logger(self, console_output):
        """创建日志记录器"""
        os.makedirs('logs', exist_ok=True)
        uuid4 = str(uuid.uuid4())
        logger = logging.getLogger(uuid4)
        logger.setLevel(logging.INFO)
        self.log_path = f"logs/{time.strftime('%Y%m%d_%H%M%S')}_{uuid4}.log"
        file_handler = logging.FileHandler(self.log_path, encoding="utf-8")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        return logger

    def log_to_gui(self, message):
        """向GUI发送日志消息"""
        if self.gui and self.is_running:
            self.gui.root.after(0, lambda: self.gui.log_message(message))

    def handle_bid(self, player: Player, action: Dict[str, Any]) -> bool:
        """处理玩家的叫点行为"""
        # 打印日志
        log_msg = f"{player.name} 叫点：{action['number']}个{action['value']}点。\n理由：{action['reason']}\n行为：{action['behaviour']}"
        self.logger.info(log_msg)
        self.log_to_gui(f"🎲 {player.name} 叫点：{action['number']}个{action['value']}点")
        if self.game_mode == "ai_only":
            self.log_to_gui(f"💭 理由：{action['reason']}")
        self.log_to_gui(f"🎭 {action['behaviour']}")
        self.log_to_gui("-" * 50)

        # 判断合法性
        if action['value'] < 1 or action['value'] > 6:
            self.logger.error(f"{player.name} 叫点不合法。")
            self.log_to_gui(f"❌ {player.name} 叫点不合法！")
            self.extra_hint = "骰子点数只能取[1,2,3,4,5,6]中的值。"
            return False
        if action['number'] > self.dice_number or (action['number'] == self.dice_number and action['value'] > self.dice_value):
            self.dice_number = action['number']
            self.dice_value = action['value']
            if action['behaviour']:
                self.round_action_info += f"{player.name}: {action['behaviour']}\n"
            self.round_action_info += f"{player.name} 叫点：{action['number']}个{action['value']}点。\n"
            self.extra_hint = ""
            self.current_player_index = (self.current_player_index + 1) % len(self.active_players)      # 切换下一个玩家行动
            if self.gui and self.is_running:
                self.gui.update_bid_display(action['number'], action['value'])
            return True
        else:
            self.logger.error(f"{player.name} 叫点不合法。")
            self.log_to_gui(f"❌ {player.name} 叫点不合法！")
            self.extra_hint = f"你的赌注要么数量大于{self.dice_number}，要么数量等于{self.dice_number}但点数大于{self.dice_value}。"
            return False

    def handle_challenge(self, player: Player, action: Dict[str, Any]):
        """处理玩家的质疑行为"""
        # 打印日志
        log_msg = f"{player.name} 质疑上家。\n理由：{action['reason']}\n行为：{action['behaviour']}"
        self.logger.info(log_msg)
        self.log_to_gui(f"⚔️ {player.name} 质疑上家！")
        if self.game_mode == "ai_only":
            self.log_to_gui(f"💭 理由：{action['reason']}")
        self.log_to_gui(f"🎭 {action['behaviour']}")
        self.log_to_gui("-" * 50)
        if action['behaviour']:
            self.round_action_info += f"{player.name}: {action['behaviour']}\n"
        self.round_action_info += f"{player.name} 质疑上家。"

        # 计算骰子总数
        total_dice = sum(player.count_dice(self.dice_value) for player in self.active_players)

        # 显示所有玩家的骰子（用于验证）
        dice_info = "🎲 验证结果 - 所有玩家的骰子："
        for p in self.active_players:
            dice_info += f"\n{p.name}: {p.dice} (有{p.count_dice(self.dice_value)}个{self.dice_value}点)"
        dice_info += f"\n总共有 {total_dice} 个 {self.dice_value} 点，赌注是 {self.dice_number} 个"
        self.log_to_gui(dice_info)
        self.round_action_info += dice_info + '\n'

        # 获取上家和下家
        previous_player = self.active_players[(self.current_player_index - 1)]
        next_player = self.active_players[(self.current_player_index + 1) % len(self.active_players)]

        # 比较赌注和实际骰子数量
        if self.dice_number > total_dice:
            # 质疑成功
            previous_player.drink_poison()
            result_msg = f"✅ {player.name} 质疑成功！{previous_player.name} 喝了一瓶毒药。"
            self.round_action_info += f"{player.name} 质疑成功！{previous_player.name} 喝了一瓶毒药。\n"
            self.logger.info(result_msg)
            self.log_to_gui(result_msg)

            # 判断上家是否死亡
            if previous_player.is_alive():
                self.first_player = previous_player  # 败者成为下一轮的第一个玩家
                self.log_to_gui(f"💊 {previous_player.name} 还剩 {previous_player.poison} 瓶毒药")
                self.round_action_info += f"{previous_player.name} 还剩 {previous_player.poison} 瓶毒药"
            else:
                death_msg = f"💀 {previous_player.name} 已经死亡。"
                self.logger.info(death_msg)
                self.log_to_gui(death_msg)
                self.round_action_info += f"{previous_player.name} 已经死亡。"
                self.active_players.remove(previous_player)
                self.first_player = next_player      # 质疑者下家成为下一轮的第一个玩家
        else:
            # 质疑失败
            player.drink_poison()
            self.round_action_info += f"{player.name} 质疑失败！{player.name} 喝了一瓶毒药。\n"
            result_msg = f"❌ {player.name} 质疑失败！{player.name} 喝了一瓶毒药。"
            self.logger.info(result_msg)
            self.log_to_gui(result_msg)

            # 判断质疑者是否死亡
            if player.is_alive():
                self.first_player = player      # 败者成为下一轮的第一个玩家
                self.log_to_gui(f"💊 {player.name} 还剩 {player.poison} 瓶毒药")
                self.round_action_info += f"{player.name} 还剩 {player.poison} 瓶毒药"
            else:
                death_msg = f"💀 {player.name} 已经死亡。"
                self.logger.info(death_msg)
                self.log_to_gui(death_msg)
                self.round_action_info += f"{player.name} 已经死亡。"
                self.active_players.remove(player)
                self.first_player = next_player     # 质疑者下家成为下一轮的第一个玩家

        # 更新GUI玩家信息
        if self.gui and self.is_running:
            self.gui.update_players_info(self.active_players)
            self.gui.update_bid_display(0, 0)

    def start_round(self):
        """开始一轮游戏"""
        self.round += 1
        self.round_base_info = f"第{self.round}轮，{len(self.active_players)}名存活玩家的名字和毒药数量分别为：\n"
        for player in self.active_players:
            self.round_base_info += f"{player.name}: 还剩{player.poison}瓶\n"
        self.round_base_info += f"本轮从{self.first_player.name}开始\n"
        self.round_action_info = ""
        self.extra_hint = ""

        # GUI显示轮次信息
        round_msg = f"🚀 第{self.round}轮开始！从 {self.first_player.name} 开始"
        self.log_to_gui("=" * 50)
        self.log_to_gui(round_msg)
        self.log_to_gui("=" * 50)
        if not self.first_player.is_human:
            self.log_to_gui(f"⏳ 等待 {self.first_player.name} 行动...")

        # 更新GUI玩家信息
        if self.gui and self.is_running:
            self.gui.update_players_info(self.active_players)

        # 重置当前的赌注
        self.dice_value = 0
        self.dice_number = 0

        # 摇盅
        for player in self.active_players:
            player.roll_dice(5)

        if self.gui and self.is_running:
            if self.human_player and self.human_player.is_alive():
                self.gui.update_dice_display([self.human_player.dice])    # 更新人类玩家的骰子显示
            else:
                dices = [player.dice for player in self.players if player.is_alive()]
                self.gui.update_dice_display(dices)                     # 更新所有玩家的骰子显示

        # 日志
        log_msg = f"第{self.round}轮开始"
        for player in self.active_players:
            log_msg += f"\n玩家：{player.name} 骰子：{player.dice} 毒药: {player.poison}瓶"
        self.logger.info(log_msg)

        # 玩家开始行动
        self.current_player_index = self.active_players.index(self.first_player)
        is_first = True
        invalid_actions = 0
        self.logger.info(f"本轮从{self.first_player.name}开始")

        while(1):
            if invalid_actions >= 2:
                self.logger.error("连续两次叫点不合法，游戏被迫终止")
                raise InvalidAction("连续两次叫点不合法，游戏被迫终止")

            # 获取玩家行动
            player = self.active_players[self.current_player_index]

            # 等待一下，让界面更新
            if self.gui:
                time.sleep(0.5)

            if not player.is_human:
                action, reasoning = player.get_ai_action(
                    is_first=is_first,
                    active_players=self.active_players,
                    round_base_info=self.round_base_info,
                    round_action_info=self.round_action_info,
                    extra_hint=self.extra_hint
                )
                # 处理退出逻辑
                if self.gui and (not self.is_running):
                    return
            else:
                action = player.get_human_action()
                reasoning = ""

            # 分析处理玩家行动
            if reasoning:
                self.logger.info(f"🤔 {player.name} 思考：{reasoning}")
            if not action:
                self.logger.error(f"{player.name} 行动为空。")
                raise ValueError(f"{player.name} 行动为空。")
            if action['challenge']:
                self.handle_challenge(player, action)
                break
            else:
                if self.handle_bid(player, action):
                    is_first = False
                    # 如果还有下一个玩家，显示提示
                    next_player = self.active_players[self.current_player_index]
                    if not next_player.is_human:
                        self.log_to_gui(f"⏳ 等待 {next_player.name} 行动...")
                else:
                    if player.is_human:
                        messagebox.showerror("叫点不合法", self.extra_hint)
                    else:
                        invalid_actions += 1
            # 处理退出逻辑
            if self.gui and (not self.is_running):
                return

    def round_reflect(self):
        """多线程处理所有AI玩家对局面的反思"""
        logger_lock = threading.Lock()
        def reflect_thread(subject_player: Player, other_players: List[Player]):
            """更新观点"""
            success, content, reasoning = subject_player.reflect(
                other_players,
                self.round_base_info,
                self.round_action_info
            )
            with logger_lock:
                if success:
                    if reasoning:
                        self.logger.info(f"{subject_player.name} 思考：{reasoning}")
                    self.logger.info(f"{subject_player.name}: {content}")
                else:
                    self.logger.error(content)

        self.logger.info("所有玩家正在进行反思……")
        self.log_to_gui("⏳ 所有玩家正在进行反思……")

        # 创建线程
        threads: List[threading.Thread] = []
        for player in self.active_players:
            if player.is_human:
                continue
            # 处理退出逻辑
            if not self.is_running:
                return
            other_players = [p for p in self.active_players if p is not player]
            thread = threading.Thread(target=reflect_thread, daemon=True, args=(player, other_players))
            threads.append(thread)
            thread.start()
            time.sleep(1)

        # 等待线程执行完毕
        for thread in threads:
            thread.join()
        self.log_to_gui("✅ 反思完毕！")

    def start_game(self) -> str:
        """开始游戏"""
        self.logger.info("游戏开始")
        self.log_to_gui("🎮 欢迎来到谎言骰子游戏！")
        self.log_to_gui("📋 游戏规则：每人有5个骰子和2瓶毒药，轮流叫点或质疑，败者喝毒药")
        for player in self.players:
            self.logger.info(f"玩家：{player.name}，模型：{'人类' if player.is_human else player.model}")
            self.log_to_gui(f"玩家：{player.name}，模型：{'人类' if player.is_human else player.model}")

        self.active_players = self.players.copy()

        while len(self.active_players) > 1:
            self.start_round()
            # 处理退出逻辑
            if self.gui and (not self.is_running):
                return ""
            if len(self.active_players) > 1:
                self.log_to_gui(f"📊 本轮结束，还有 {len(self.active_players)} 名玩家存活")
                if self.reflect_each_round:
                    self.round_reflect()

        winner = self.active_players[0]
        self.logger.info(f"游戏结束，{winner.name} 获胜！")
        return winner.name

if __name__ == "__main__":
    # 示例
    players = [
        Player(name="Alice", is_human=False, model = "deepseek-chat"),
        Player(name="Bob", is_human=False, model = "deepseek-chat"),
        Player(name="Charlie", is_human=False, model = "deepseek-chat"),
        Player(name="David", is_human=False, model = "deepseek-chat")
    ]
    game = LiarsDiceGame(players)
    winner = game.start_game()
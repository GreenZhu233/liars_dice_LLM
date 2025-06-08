from players import Player
import logging
import time
import random
import os
from typing import List, Dict, Any

class LiarsDiceGame():
    def __init__(self, players: List[Player]):
        self.players = players
        self.logger = self.create_logger()
        self.round = 0
        self.active_players = []
        self.first_player = self.players[random.randint(0, len(self.players) - 1)]  # 随机选择第一个玩家
        self.current_player_index = 0

        # 轮次信息
        self.round_base_info = ""
        self.round_action_info = ""
        self.extra_hint = ""

    def create_logger(self):
        """创建日志记录器"""
        os.makedirs('logs', exist_ok=True)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(f"logs/game_log_{time.strftime('%Y%m%d_%H%M%S')}.log", encoding="utf-8")
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger

    def handle_bid(self, player: Player, action: Dict[str, Any]) -> bool:
        """处理玩家的叫点行为"""
        # 打印日志
        log_msg = f"{player.name} 叫点：{action['number']}个{action['value']}点。\n理由：{action['reason']}\n行为：{action['behaviour']}"
        self.logger.info(log_msg)

        # 判断合法性
        if action['number'] > self.dice_number or (action['number'] == self.dice_number and action['value'] > self.dice_value):
            self.dice_number = action['number']
            self.dice_value = action['value']
            self.round_action_info += f"{player.name}: {action['behaviour']}\n"
            self.round_action_info += f"{player.name} 叫点：{action['number']}个{action['value']}点。\n"
            self.extra_hint = ""
            self.current_player_index = (self.current_player_index + 1) % len(self.active_players)      # 切换下一个玩家行动
            return True
        else:
            self.logger.error(f"{player.name} 叫点不合法。")
            self.extra_hint = f"你的赌注要么数量大于{self.dice_number}，要么数量等于{self.dice_number}但点数大于{self.dice_value}。"
            return False

    def handle_challenge(self, player: Player, action: Dict[str, Any]):
        """处理玩家的质疑行为"""
        # 打印日志
        log_msg = f"{player.name} 质疑上家。\n理由：{action['reason']}\n行为：{action['behaviour']}"
        self.logger.info(log_msg)

        # 计算骰子总数
        total_dice = sum(player.count_dice(self.dice_value) for player in self.active_players)

        # 获取上家和下家
        previous_player = self.active_players[(self.current_player_index - 1)]
        next_player = self.active_players[(self.current_player_index + 1) % len(self.active_players)]

        # 比较赌注和实际骰子数量
        if self.dice_number > total_dice:
            # 质疑成功
            previous_player.drink_poison()
            self.round_action_info += f"{player.name} 质疑成功！{previous_player.name} 喝了一瓶毒药。\n"
            self.logger.info(f"{player.name} 质疑成功！{previous_player.name} 喝了一瓶毒药。")
            # 判断上家是否死亡
            if previous_player.is_alive():
                self.first_player = previous_player  # 败者成为下一轮的第一个玩家
            else:
                self.logger.info(f"{previous_player.name} 已经死亡。")
                self.active_players.remove(previous_player)
                self.first_player = next_player      # 质疑者下家成为下一轮的第一个玩家
        else:
            # 质疑失败
            player.drink_poison()
            self.round_action_info += f"{player.name} 质疑失败！{player.name} 喝了一瓶毒药。\n"
            self.logger.info(f"{player.name} 质疑失败！{player.name} 喝了一瓶毒药。")
            # 判断质疑者是否死亡
            if player.is_alive():
                self.first_player = player      # 败者成为下一轮的第一个玩家
            else:
                self.logger.info(f"{player.name} 已经死亡。")
                self.active_players.remove(player)
                self.first_player = next_player     # 质疑者下家成为下一轮的第一个玩家

    def start_round(self):
        """开始一轮游戏"""
        self.round += 1
        self.round_base_info = f"第{self.round}轮，存活的玩家（按活动顺序）及其剩余的毒药数量为：\n"
        for player in self.active_players:
            self.round_base_info += f"{player.name}: {player.poison}瓶\n"
        self.round_base_info += f"本轮从{self.first_player.name}开始\n"
        self.round_action_info = ""
        self.extra_hint = ""

        # 重置当前的赌注
        self.dice_value = 0
        self.dice_number = 0

        # 摇盅
        for player in self.active_players:
            player.roll_dice(5)

        # 日志
        log_msg = f"第{self.round}轮开始\n"
        for player in self.active_players:
            log_msg += f"玩家：{player.name} 骰子：{player.dice} 毒药: {player.poison}瓶\n"
        self.logger.info(log_msg)

        # 玩家开始行动
        self.current_player_index = self.active_players.index(self.first_player)
        is_first = True
        error_times = 0
        self.logger.info(f"本轮从{self.first_player.name}开始")
        while(1):
            if error_times >= 2:
                self.logger.error("连续两次错误，退出程序。")
                raise ValueError("连续两次错误，退出程序。")

            # 获取玩家行动
            player = self.active_players[self.current_player_index]
            if not player.is_human:
                action, reasoning = player.get_ai_action(
                    is_first=is_first,
                    round_base_info=self.round_base_info,
                    round_action_info=self.round_action_info,
                    extra_hint=self.extra_hint
                )
            else:
                action = player.get_human_action()
                reasoning = ""

            # 分析处理玩家行动
            if reasoning:
                self.logger.info(f"{player.name} 思考：{reasoning}")
            if not action:
                self.logger.error(f"{player.name} 行动为空。")
                raise ValueError(f"{player.name} 行动为空。")
            if action['challenge']:
                self.handle_challenge(player, action)
                break
            else:
                if self.handle_bid(player, action):
                    is_first = False
                else:
                    error_times += 1

    def start_game(self) -> str:
        """开始游戏"""
        self.logger.info("游戏开始")
        self.active_players = self.players.copy()
        while len(self.active_players) > 1:
            self.start_round()

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
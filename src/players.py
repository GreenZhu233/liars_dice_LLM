import random
import re
import json
import threading
from src.llm_client import OpenAILLMClient, GoogleLLMClient
from typing import List, Dict, Any
from src.snippets import *
from src.json_parser import *

RULE_PATH = "template/rule.txt"
ACTION_PROMPT_TEMPLATE_PATH = "template/action_prompt_template.txt"
FIRST_PLAYER_ACTION_PROMPT_TEMPLATE_PATH = "template/first_player_action_prompt_template.txt"
REFLECT_PROMPT_TEMPLATE_PATH = "template/reflect_prompt_template.txt"

class Player():
    def __init__(self, name = "", is_human = False, model: str = ""):
        """
        初始化玩家属性
            name: 玩家名称
            is_human: 是否为人类玩家
            model: AI模型，如"deepseek-chat"
        """
        self.name = name
        self.is_human = is_human
        self.model = model
        self.dice = []      # 骰子列表
        self.poison = 2     # 毒药数量
        if is_human:
            self.llm_client = None
        else:
            match model_to_API[model]:
                case "OpenAI":
                    self.llm_client = OpenAILLMClient(self.model)
                case "Google":
                    self.llm_client = GoogleLLMClient(self.model)
                case _:
                    raise ValueError(f"不支持的模型: {self.model}")
        self.gui = None     # GUI引用，用于人类玩家交互
        self.opinions = {}  # 对其他玩家的看法

    def roll_dice(self, count):
        self.dice = [random.randint(1, 6) for _ in range(count)]
        return self.dice.sort()

    def count_dice(self, value):
        return self.dice.count(value)

    def is_alive(self):
        return self.poison > 0

    def drink_poison(self):
        """喝下一瓶毒药"""
        if self.poison > 0:
            self.poison -= 1
            return True
        return False

    def _read_file(self, filepath: str):
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"读取文件 {filepath} 失败: {str(e)}")
            return ""

    def get_ai_action(self, is_first: bool, active_players: List["Player"], round_base_info: str, round_action_info: str, extra_hint: str = "") -> tuple[Dict[str, Any], str]:
        """
        获取AI玩家的动作
        Args:
            is_first: bool, 是否为本轮的第一个玩家（第一个玩家不能质疑）。
            round_base_info: 本轮的基本信息，包含玩家数量、玩家名称、玩家顺序和毒药数量等。
            round_action_info: 本轮游戏中已经发生的动作记录。
            extra_hint: 额外提示信息。

        Returns:
            返回一个二元组，包含以下两部分：
            1. 一个字典，包含以下键值对：
                - challenge: bool, 是否质疑上家
                - value: int, 所叫的骰子点数(1~6，若选择质疑，填入0)
                - number: int, 所叫的骰子数量(>=1，若选择质疑，填入0)
                - reason: str, 选择这么决策(质疑/叫点)的理由
                - behaviour: str, 一段没有主语的行为/表情/发言等描写，能被其他玩家观察。
            2. 大模型推理文本
        """
        # 读取规则和模板
        rules = self._read_file(RULE_PATH)
        template = self._read_file(ACTION_PROMPT_TEMPLATE_PATH)
        first_template = self._read_file(FIRST_PLAYER_ACTION_PROMPT_TEMPLATE_PATH)

        # 准备当前手牌信息
        current_dice = ", ".join([str(dice) for dice in self.dice])

        # 获取对其他玩家的印象
        opinions = "你对其他玩家的了解：\n" + '\n'.join(
            [f"{p.name}: {self.opinions[p.name]}" for p in active_players if p is not self]
        )

        # 添加玩家顺序信息
        if (l := len(active_players)) > 2:
            self_index = active_players.index(self)
            previous = active_players[self_index - 1]
            next = active_players[(self_index + 1) % l]
            round_base_info += f"你的上家是{previous.name}，你的下家是{next.name}"

        # 填充模板
        if is_first:
            prompt = first_template.format(
                player_name = self.name,
                round_base_info = round_base_info,
                round_action_info = round_action_info,
                opinions=opinions,
                dices = current_dice,
                extra_hint = extra_hint,
            )
        else:
            prompt = template.format(
                player_name = self.name,
                round_base_info = round_base_info,
                round_action_info = round_action_info,
                opinions=opinions,
                dices = current_dice,
                extra_hint = extra_hint,
            )

        # 尝试获取有效的JSON响应。最多重复两次
        for attempt in range(2):
            # 每次都发送相同的原始prompt
            messages = [{"role": "system", "content": rules},
            {"role": "user", "content": prompt}]

            try:
                content, reasoning_content = self.llm_client.chat(messages)

                # 尝试从响应中提取JSON
                _, result = try_parse_json_object(content)

                # 验证JSON格式是否符合要求
                if all(key in result for key in ["challenge", "value", "number", "reason", "behaviour"]):
                    return result, reasoning_content
                else:
                    raise Exception("json格式不符合要求")

            except Exception as e:
                # 仅记录错误，不修改重试请求
                print(f"尝试 {attempt+1} 解析失败: {str(e)}")
        raise RuntimeError(f"玩家 {self.name} 的get_ai_action方法在多次尝试后失败")

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

        # 显示操作界面
        is_first = current_bid_number == 0
        gui.root.after(0, lambda: gui.show_human_action_interface(is_first, current_bid_number, current_bid_value))

        # 等待用户操作
        gui.human_action_event.wait()

        return gui.human_action_result

    def init_opinions(self, players: List["Player"]):
        """初始化对其他玩家的看法"""
        self.opinions = {player.name: "还不了解这个玩家" for player in players if player is not self}

    def reflect(self, other_players: List["Player"], round_base_info: str, round_action_info: str) -> tuple[bool, str, str]:
        """更新对其他玩家的看法"""
        template = self._read_file(REFLECT_PROMPT_TEMPLATE_PATH)
        rules = self._read_file(RULE_PATH)

        # 填充模板
        previous_opinions = '\n'.join(
            [f'{p.name}: {self.opinions.get(p.name, "还不了解这个玩家")}' for p in other_players]
        )
        output_format = '\n'.join(
            [f'"{p.name}": str' for p in other_players]
        )

        prompt = template.format(
            self_name=self.name,
            round_base_info=round_base_info,
            round_action_info=round_action_info,
            previous_opinions=previous_opinions,
            output_format=output_format
        )

        messages = [{"role": "system", "content": rules},
        {"role": "user", "content": prompt}]

        # 向LLM发送请求
        try:
            content, reasoning_content = self.llm_client.reflect(messages, other_players)
            _, result = try_parse_json_object(content)

            # 更新 opinions
            for key, value in result.items():
                if key in self.opinions.keys():
                    self.opinions[key] = value
                else:
                    raise Exception(f"不存在的玩家名: {key}")

            return True, content, reasoning_content

        except Exception as e:
            return False, f"{self.name} 反思过程出错: {str(e)}", ""
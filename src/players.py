import random

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

    def roll_dice(self, count):
        self.dice = [random.randint(1, 6) for _ in range(count)]
        return self.dice

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

    def get_ai_action(self, is_first: bool, round_base_info: str, round_action_info: str, extra_hint: str = ""):
        """
        获取AI玩家的动作
        Args:
            is_first: bool, 是否为本轮的第一个玩家（第一个玩家不能质疑）。
            round_base_info: 本轮的基本信息，包含玩家数量、玩家名称、玩家顺序和毒药数量等。
            round_action_info: 本轮游戏中已经发生的动作记录。
            extra_hint: 额外提示信息。

        Rets:
            返回一个字典，包含以下键值对
            - challenge: bool, 是否质疑上家
            - point: int, 所叫的骰子点数(1~6，若选择质疑，填入0)
            - count: int, 所叫的骰子数量(>=1，若选择质疑，填入0)
            - reason: str, 选择这么决策(质疑/叫点)的理由
            - behaviour: str, 一段没有主语的行为/表情/发言等描写，能被其他玩家观察。
        """
        pass

    def get_human_action(self):
        pass
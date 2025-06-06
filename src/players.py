import random

class Player():
    def __init__(self, name = "", is_human = False, model: str = ""):
        '''
        初始化玩家属性
            name: 玩家名称
            is_human: 是否为人类玩家
            model: AI模型，如"deepseek-chat"
        '''
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

    def get_ai_action(self, historical_message: str):
        pass

    def get_human_action(self):
        pass
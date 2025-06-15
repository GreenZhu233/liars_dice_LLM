# 谎言骰子（Liar's Dice）多智能体对战平台

## 项目简介
谎言骰子（Liar's dice）是《骗子酒馆（Liar's Bar）》中的一个游戏模式。
本项目基于游戏中的规则，实现了一个多智能体对战平台，支持两种游戏模式：4xAI 或 1x人类+3xAI。

## 游戏规则
游戏由4名玩家参与，每人拥有5个骰子和2瓶毒药，游戏以轮次进行。
每轮开始时，每位玩家各自摇骰子，结果仅自己可见。
玩家依次轮流叫点。首位玩家可以宣称场上所有玩家手中，某个点数的骰子达到或超过指定数量。
宣称的点数需要在1到6点之间。在此游戏中，1点不是万能骰子。
轮到下家时，可以选择“质疑”或“加注”。加注时，必须使数量大于上家，或在数量相同的情况下点数更大。
（例如，上家：“4个5点”，你可以加注“5个2点”或“4个6点”，但不能是“3个5点”或“4个4点”，也不能重复上家的“4个5点”）
若有人选择质疑，则所有玩家亮出骰子，统计被叫点数的总数。若实际数量小于上家宣称，则质疑成功，被质疑者失败；反之，质疑者失败。失败者需喝下一瓶毒药。
喝完两瓶毒药的玩家死亡出局。
每当有人质疑后，本轮结束，存活玩家进入下一轮，并重新摇骰子。
当场上仅剩一名玩家存活时，游戏结束。

## 目录结构
- main_launcher.py：启动游戏的 GUI 界面
- multi_game_runner.py：批量自动对战脚本，支持多线程
- src：核心代码（如游戏逻辑、玩家实现等）
- config：配置文件（如玩家、密钥等）
- images：骰子图片资源
- logs：对局日志
- template：规则等文本模板

## 安装与依赖
1. Python >= 3.10
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 快速开始

### 启动 GUI 版
```bash
python main_launcher.py
```

### 批量自动对战
```bash
python multi_game_runner.py <总对局数> -t [线程数] [玩家参数]
```
示例：
```bash
python multi_game_runner.py 4 -t 2 --name1 Alice --model1 doubao-1-5-lite-32k-250115 --name2 Bob --model2 deepseek-chat --name3 Charlie --model3 doubao-1-5-lite-32k-250115 --name4 David --model4 gemini-2.5-flash-preview-05-20
```
在启动批量自动对战前，请确保需要的模型API秘钥已在 `config/keys.json` 中配置完成。

## 其他说明
- 所有对局日志保存在 `logs` 目录。
- deepseek-reasoner 模型的响应速度非常慢，且输出的思考内容特别长，建议不要使用这个模型。
from src.game import LiarsDiceGame
from src.players import Player
from src.snippets import *
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_game(thread_id: int):
    players = [Player(name=config['name'], is_human=False, model=config['model']) for config in role_config]
    game = LiarsDiceGame(players, console_output=False)
    try:
        winner = game.start_game()
        print(f"({thread_id})winner: {winner}\tlogfile: {game.log_path}\n", end='')
        wins[player_id[winner]] += 1
    except Exception as e:
        print(f"{str(e)}\nlogfile: {game.log_path}\n", end='')
        raise e

# 设置参数
parser = argparse.ArgumentParser()
parser.add_argument('total_runs', type=int, help='游戏运行次数')
parser.add_argument('-t', '--threads', type=int, help='同时运行的线程数', default=1)
group = parser.add_argument_group("玩家设定")
group.add_argument('--name1', type=str, help='第1个玩家的名字', default='Alice')
group.add_argument('--model1', type=str, help='第1个玩家的模型', default='doubao-1-5-lite-32k-250115')
group.add_argument('--name2', type=str, help='第2个玩家的名字', default='Bob')
group.add_argument('--model2', type=str, help='第2个玩家的模型', default='doubao-1-5-lite-32k-250115')
group.add_argument('--name3', type=str, help='第3个玩家的名字', default='Charlie')
group.add_argument('--model3', type=str, help='第3个玩家的模型', default='doubao-1-5-lite-32k-250115')
group.add_argument('--name4', type=str, help='第4个玩家的名字', default='David')
group.add_argument('--model4', type=str, help='第4个玩家的模型', default='doubao-1-5-lite-32k-250115')

# 读取参数
args = parser.parse_args()
role_config = [
    {'name': args.name1, 'model': args.model1},
    {'name': args.name2, 'model': args.model2},
    {'name': args.name3, 'model': args.model3},
    {'name': args.name4, 'model': args.model4}
]
threads = args.threads
player_id = {args.name1: 0, args.name2: 1, args.name3: 2, args.name4: 3}
total_runs = args.total_runs

# 检查名字合法性
names = [p['name'] for p in role_config if p['name']]
if len(set(names)) != 4:
    raise ValueError("玩家名字不能重复、不能为空！")

# 检查模型合法性
for p in role_config:
    model = p['model']
    if model not in model_list:
        raise ValueError(f"不支持的模型：{model}")

# 打印玩家信息
for p in role_config:
    print(p['name'], ':', p['model'])

# 执行线程任务
wins = [0,0,0,0]
with ThreadPoolExecutor(max_workers=threads) as executor:
    futures = [executor.submit(run_game, i) for i in range(total_runs)]
    id = 1
    try:
        for future in as_completed(futures):
            id += 1
            future.result()
    except Exception:
        print(f"第{id}局游戏中检测到异常，终止所有任务。")
        executor.shutdown(cancel_futures=True)

success = wins[0] + wins[1] + wins[2] + wins[3]
print(f"成功运行{success}次游戏，胜利次数统计：")
for i in range(4):
    print(f'{role_config[i]['name']}({role_config[i]['model']}): {wins[i]}')
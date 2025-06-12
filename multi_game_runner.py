from src.game import LiarsDiceGame
from src.players import Player
import argparse
import threading

def run_game(thread_runs: int):
    for _ in range(thread_runs):
        players = [Player(name=config['name'], is_human=False, model=config['model']) for config in role_config]
        game = LiarsDiceGame(players, stream_output=False)
        winner = game.start_game()
        if winner:
            print(f"winner: {winner}\tlogfile: {game.log_path}\n", end='')
            wins[player_id[winner]] += 1
        else:
            print(f"winner: None\tlogfile: {game.log_path}\n", end='')

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

# 线程分配
wins = [0,0,0,0]
thread_runs_list = [total_runs // threads for _ in range(threads)]
for i in range(total_runs % threads):
    thread_runs_list[i] += 1

# 开始运行游戏
thread_list = [threading.Thread(target=run_game, args=(thread_runs_list[t],), daemon=True) for t in range(threads)]
for t in range(threads):
    thread_list[t].start()
for t in range(threads):
    thread_list[t].join()

print("胜利次数统计：")
for i in range(4):
    print(f'{role_config[i]['name']}: {wins[i]}')
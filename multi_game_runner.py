from src.game import LiarsDiceGame
from src.players import Player
import sys

player_id = {"Alice": 0, "Bob": 1, "Charlie": 2, "David": 3}
try:
    number_of_runs = sys.argv[1]
except:
    number_of_runs = 1

wins = [0,0,0,0]

for _ in range(number_of_runs):
    players = [
        Player(name="Alice", is_human=False, model = "deepseek-chat"),
        Player(name="Bob", is_human=False, model = "deepseek-chat"),
        Player(name="Charlie", is_human=False, model = "deepseek-chat"),
        Player(name="David", is_human=False, model = "deepseek-chat")
    ]
    game = LiarsDiceGame(players)
    winner = game.start_game()
    wins[player_id[winner]] += 1

print("胜利次数统计：")
print("Alice: " + str(wins[0]))
print("Bob: " + str(wins[1]))
print("Charlie: " + str(wins[2]))
print("David: " + str(wins[3]))
import time
import os
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.animation import FuncAnimation
from witcher import Witcher
from demon import Demon
from board import Board
from position import Position, Direction

raw_board = """
%%%%%%%%%%
%      %!%
%   D  %%%
%        %
%        %
%        %
%   W    %
%        %
%        %
%%%%%%%%%%
"""

board = Board(raw_board)
print(board)

witcher = Witcher(board, learning_rate=0.1, discount_factor=0.1, experiment_rate=0.1)
demon = Demon(board, True)

board.witcher = witcher
board.demon = demon

fig, axes = plt.subplots(3)
xs = [[] for _ in range(3)]
ys = [[] for _ in range(3)]
lines = [axes[i].plot([], [], 'r')[0] for i in range(3)]

AVG_WINDOW = 100
ITERS = 10000


def init():
    for i in range(3):
        axes[i].set_xlim(1, ITERS)
    axes[0].set_ylim(0, 2000)
    axes[1].set_ylim(0, 30)
    axes[2].set_ylim(-200, 1000)
    return lines


def update(frame):
    while not board.game_over:
        os.system("clear")
        demon.make_action()
        if not board.game_over:
            witcher.make_action()
        # print(board)
    board.reset()

    for i in range(3):
        xs[i].append(frame)

    if frame < AVG_WINDOW:
        ys[0].append(np.average(witcher.lifespan_history))
        ys[1].append(np.average(witcher.hits_history))
        ys[2].append(np.average(witcher.reward_history))
    else:
        ys[0].append(np.average(witcher.lifespan_history[-AVG_WINDOW:]))
        ys[1].append(np.average(witcher.hits_history[-AVG_WINDOW:]))
        ys[2].append(np.average(witcher.reward_history[-AVG_WINDOW:]))

    for i in range(3):
        lines[i].set_data(xs[i], ys[i])

    return lines


ani = FuncAnimation(fig, update, frames=ITERS, init_func=init, blit=True, interval=0)
plt.show()

# for i in range(10000):
#     os.system("clear")
#     demon.make_action()
#     if not board.game_over:
#         witcher.make_action()
#     print(board)
#     time.sleep(0.001)
#     if board.game_over:
#         board.reset()

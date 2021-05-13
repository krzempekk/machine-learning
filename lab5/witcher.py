import numpy as np

from position import Position, Direction
from board import BoardItem
from enum import Enum
from collections import defaultdict


def get_position(action):
    if action == WitcherAction.MOVE_UP:
        return Direction.UP.value
    elif action == WitcherAction.MOVE_RIGHT:
        return Direction.RIGHT.value
    elif action == WitcherAction.MOVE_DOWN:
        return Direction.DOWN.value
    elif action == WitcherAction.MOVE_LEFT:
        return Direction.LEFT.value
    return None


class WitcherAction(Enum):
    MOVE_UP = 0
    MOVE_RIGHT = 1
    MOVE_DOWN = 2
    MOVE_LEFT = 3
    ATTACK = 4


HIT_REWARD = 50
DAMAGE_REWARD = -100
DISTANCE_REWARD = 0.5


class Witcher:
    def __init__(self, board, learning_rate, discount_factor, experiment_rate):
        self.board = board
        self.initial_position = board.get_position(BoardItem.WITCHER)
        self.position = self.initial_position
        self.health_points = 1
        self.Q = defaultdict(lambda: np.zeros(len(list(WitcherAction))))
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.experiment_rate = experiment_rate
        self.state = self.board.get_state()
        self.action = self.get_action(self.state)
        self.current_reward = 0
        self.reward_history = [0]
        self.current_lifespan = 0
        self.lifespan_history = []
        self.current_hits = 0
        self.hits_history = []

    def clear_history(self):
        self.reward_history = [0]
        self.lifespan_history = []
        self.hits_history = []

    def reset(self):
        self.board.move(self.position, self.initial_position, BoardItem.WITCHER)
        self.position = self.initial_position
        self.health_points = 1

    def receive_damage(self):
        self.current_reward += DAMAGE_REWARD
        self.lifespan_history.append(self.current_lifespan)
        self.current_lifespan = 0
        self.hits_history.append(self.current_hits)
        self.current_hits = 0
        self.finish_move()
        self.reward_history.append(0)
        return True

    def make_action(self):
        if self.action == WitcherAction.ATTACK:
            attacked_positions = list(map(lambda direction: self.position + direction.value, list(Direction)))
            if self.board.attack(attacked_positions):
                self.current_reward += HIT_REWARD
                self.current_hits += 1
        else:
            old_position = self.position
            new_position = self.position + get_position(self.action)
            if self.board.can_move_to(new_position):
                self.board.move(self.position, new_position, BoardItem.WITCHER)
                self.position = new_position
            demon_position = self.board.get_position(BoardItem.DEMON)
            if old_position.distance_from(demon_position) > new_position.distance_from(demon_position):
                self.current_reward += DISTANCE_REWARD
        self.current_lifespan += 1
        self.finish_move()

    def finish_move(self):
        next_state = self.board.get_state()
        next_action = self.get_action(next_state)
        self.learn(self.state, self.action, self.current_reward, next_state, next_action)
        self.state, self.action = next_state, next_action
        self.reward_history[-1] += self.current_reward
        self.current_reward = 0

    def get_action(self, state):
        values = self.Q[state]
        actions = list(WitcherAction)
        if np.sum(values) == 0 or np.random.random() < self.experiment_rate:
            return np.random.choice(actions)
        return actions[np.argmax(values)]

    def learn(self, state_1, action_1, reward, state_2, action_2):
        old_value = self.Q[state_1][action_1.value]
        new_value = reward + self.discount_factor * self.Q[state_2][action_2.value]
        # new_value = reward + self.discount_factor * np.max(self.Q[state_2])
        self.Q[state_1][action_1.value] = old_value + self.learning_rate * (new_value - old_value)

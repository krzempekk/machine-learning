import copy
import numpy as np

from board import BoardItem
from position import Direction, get_random_direction


class Demon:
    def __init__(self, board, is_deterministic):
        self.board = board
        self.initial_position = board.get_position(BoardItem.DEMON)
        self.position = self.initial_position
        self.is_deterministic = is_deterministic
        self.health_points = 3
        self.initial_state = {
            "curse_interval": 1000,
            "curse_countdown": 1000,
            "hideout_countdown": 0
        }
        if is_deterministic:
            self.initial_state = {
                **self.initial_state,
                "direction": Direction.UP,
                "attack_interval": 5,
                "attack_countdown": 5,
            }
        self.state = copy.copy(self.initial_state)

    def reset(self):
        self.board.move(self.position, self.initial_position, BoardItem.DEMON)
        self.position = self.initial_position
        self.health_points = 3
        if self.is_deterministic:
            self.state = copy.copy(self.initial_state)

    def receive_damage(self):
        self.health_points -= 1
        if self.health_points == 0:
            return True
        self.board.enter_hideout(BoardItem.DEMON)
        self.state['hideout_countdown'] = 3
        return False

    def move(self):
        if self.is_deterministic:
            direction = self.state['direction']
            while not self.board.can_move_to(self.position.get_adjacent(direction)):
                direction = direction.rotate(2)
            new_position = self.position.get_adjacent(direction)
            self.board.move(self.position, new_position, BoardItem.DEMON)
            self.position = new_position
            self.state['direction'] = direction
        else:
            direction = get_random_direction()
            while not self.board.can_move_to(self.position.get_adjacent(direction)):
                direction = get_random_direction()
            new_position = self.position.get_adjacent(direction)
            self.board.move(self.position, new_position, BoardItem.DEMON)
            self.position = new_position

    def attack(self):
        if self.is_deterministic:
            direction = self.state['direction']
            attacked_positions = [
                self.position.get_adjacent(direction.rotate(-2)),
                self.position.get_adjacent(direction),
                self.position.get_adjacent(direction.rotate(2))
            ]
            self.board.attack(attacked_positions)
            self.state['attack_countdown'] = self.state['attack_interval']
        else:
            direction = get_random_direction()
            attacked_positions = [
                self.position.get_adjacent(direction.rotate(-2)),
                self.position.get_adjacent(direction),
                self.position.get_adjacent(direction.rotate(2))
            ]
            self.board.attack(attacked_positions)

    def make_action(self):
        # curse
        self.state['curse_countdown'] -= 1
        if self.state['curse_countdown'] == 0:
            self.board.cast_curse()
            return

        # stay in hideout
        if self.state['hideout_countdown'] == 1:
            self.position = self.initial_position
            self.board.leave_hideout(BoardItem.DEMON, self.position)
            self.state = copy.copy(self.initial_state)
            for i in range(np.random.randint(1, 5)):
                self.move()
            return
        elif self.state['hideout_countdown'] > 0:
            self.state['hideout_countdown'] -= 1
            return

        # normal action
        if self.is_deterministic:
            if self.state['attack_countdown'] > 0:
                self.move()
                self.state['attack_countdown'] -= 1
            else:
                self.attack()
        else:
            if np.random.random() < 0.2:
                self.attack()
            else:
                self.move()

from enum import Enum
from position import Position


def parse_board(board):
    return list(map(lambda row: list(map(lambda char: get_board_item(char), row)), board.split("\n")[1:-1]))


def get_board_item(char):
    items = list(BoardItem)
    index = list(map(lambda item: item.value, items)).index(char)
    return items[index]


class BoardItem(Enum):
    WALL = "%"
    EMPTY = " "
    WITCHER = "W"
    DEMON = "D"
    HIDEOUT = "!"
    HIDEOUT_FULL = "$"


class Board:
    def __init__(self, raw_board):
        self.fields = parse_board(raw_board)
        self._str_attacked_positions = []
        self.witcher = None
        self.demon = None
        self.hideout_position = self.get_position(BoardItem.HIDEOUT)
        self.game_over = False

    def __str__(self):
        rows = list(map(lambda row: "".join(list(map(lambda item: item.value, row))), self.fields))
        for position in self._str_attacked_positions:
            row = list(rows[position.y])
            row[position.x] = '*'
            rows[position.y] = "".join(row)
        self._str_attacked_positions = []
        return "\n".join(rows)

    def get(self, position):
        return self.fields[position.y][position.x]

    def set(self, position, board_item):
        self.fields[position.y][position.x] = board_item

    def get_position(self, board_item):
        for y, row in enumerate(self.fields):
            for x, item in enumerate(row):
                if item == board_item:
                    return Position(x, y)
        return Position(0, 0)

    def get_state(self):
        return str(self.get_position(BoardItem.WITCHER)) + str(self.get_position(BoardItem.DEMON))

    def can_move_to(self, position):
        return self.get(position) == BoardItem.EMPTY

    def move(self, old_position, new_position, item, leave_item=BoardItem.EMPTY):
        self.fields[old_position.y][old_position.x] = leave_item
        self.fields[new_position.y][new_position.x] = item

    def enter_hideout(self, board_item):
        self.move(self.get_position(board_item), self.hideout_position, board_item)

    def leave_hideout(self, board_item, position):
        self.move(self.hideout_position, position, board_item, BoardItem.HIDEOUT)

    def attack(self, positions):
        self._str_attacked_positions = positions
        for position in positions:
            item = self.get(position)
            if item == BoardItem.WITCHER:
                if self.witcher.receive_damage():
                    self.game_over = True
                    return True
            elif item == BoardItem.DEMON:
                if self.demon.receive_damage():
                    self.game_over = True
                    return True
        return False

    def cast_curse(self):
        print("CURSE")
        self.witcher.receive_damage()
        self.game_over = True

    def reset(self):
        self.witcher.reset()
        self.demon.reset()
        self.game_over = False

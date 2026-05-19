import sys
import types
import math
import pytest

if "tkinter" not in sys.modules:
    _tk_stub = types.ModuleType("tkinter")
    _tk_stub.LAST = "last"
    sys.modules["tkinter"] = _tk_stub

from caro_ai.logic import Game_Caro
from caro_ai.ai.minimax_lv2 import agent

@pytest.fixture
def ai():
    # AI default: depth 3, đóng vai O
    return agent(depth=3, ai_player='O')

@pytest.fixture
def ai_shallow():
    # AI độ sâu 2 cho các test cần chạy nhanh
    return agent(depth=2, ai_player='O')


@pytest.fixture
def game():
    # Bàn cờ 9x9 mới hoàn toàn, lượt X đi trước
    return Game_Caro(9)


def _place(game, cells_x, cells_o):
    # Đặt quân trực tiếp lên bàn không qua make_move (tránh kích logic thắng/thua)
    for r, c in cells_x:
        game.board[r][c] = 'X'
    for r, c in cells_o:
        game.board[r][c] = 'O'


# Tạo agent

class TestInit:
    def test_depth_default(self):
        # Độ sâu mặc định phải là 3
        a = agent()
        assert a.depth == 3

    def test_depth_custom(self):
        # Độ sâu tuỳ chỉnh phải được lưu đúng
        a = agent(depth=5)
        assert a.depth == 5

    def test_ai_player_default(self):
        # Người chơi AI mặc định là O
        a = agent()
        assert a.ai_player == 'O'

    def test_ai_player_custom(self):
        # Có thể khởi tạo AI đóng vai X
        a = agent(ai_player='X')
        assert a.ai_player == 'X'

    def test_node_visited_starts_at_zero(self):
        # Bộ đếm node bắt đầu từ 0
        a = agent()
        assert a.node_visted == 0

# _test_move và _undo_move
class TestTestMoveAndUndo:
    def _init_board(self, ai, game):
        # Sao chép bàn cờ từ game vào agent như _execute_search làm
        ai.board = [row.copy() for row in game.board]
        ai.player = game.current_player

    def test_test_move_places_current_player(self, ai, game):
        # _test_move đặt ký hiệu của người chơi hiện tại vào ô
        self._init_board(ai, game)
        ai._test_move(4, 4)
        assert ai.board[4][4] == 'X'

    def test_test_move_switches_player(self, ai, game):
        # Sau _test_move -> lượt chuyển sang người kia
        self._init_board(ai, game)
        ai._test_move(4, 4)
        assert ai.player == 'O'

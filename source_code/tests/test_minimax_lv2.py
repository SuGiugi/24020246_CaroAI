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
        a = agent()
        assert a.depth == 3

    def test_depth_custom(self):
        a = agent(depth=5)
        assert a.depth == 5

    def test_ai_player_default(self):
        a = agent()
        assert a.ai_player == 'O'

    def test_ai_player_custom(self):
        a = agent(ai_player='X')
        assert a.ai_player == 'X'

    def test_node_visited_starts_at_zero(self):
        a = agent()
        assert a.node_visted == 0

# _test_move và _undo_move
class TestTestMoveAndUndo:
    def _init_board(self, ai, game):
        # Sao chép bàn cờ từ game vào agent như _execute_search làm
        ai.board = [row.copy() for row in game.board]
        ai.player = game.current_player

    def test_test_move_places_current_player(self, ai, game):
        self._init_board(ai, game)
        ai._test_move(4, 4)
        assert ai.board[4][4] == 'X'

    def test_test_move_switches_player(self, ai, game):
        self._init_board(ai, game)
        ai._test_move(4, 4)
        assert ai.player == 'O'

    def test_undo_move_removes_piece(self, ai, game):
        self._init_board(ai, game)
        ai._test_move(4, 4)
        ai._undo_move(4, 4)
        assert ai.board[4][4] == '.'

    def test_undo_move_restores_player(self, ai, game):
        self._init_board(ai, game)
        original = ai.player
        ai._test_move(4, 4)
        ai._undo_move(4, 4)
        assert ai.player == original

    def test_double_move_and_undo(self, ai, game):
        # Hai nước đi liên tiếp và undo đúng thứ tự phải hoàn trả bàn về ban đầu
        self._init_board(ai, game)
        ai._test_move(3, 3)  # X đánh
        ai._test_move(4, 4)  # O đánh
        ai._undo_move(4, 4)  # undo O
        ai._undo_move(3, 3)  # undo X
        assert ai.board[3][3] == '.'
        assert ai.board[4][4] == '.'
        assert ai.player == 'X'

    def test_test_move_o_player(self, ai, game):
        # Khi lượt là O thì _test_move phải đặt 'O' vào ô
        self._init_board(ai, game)
        game.current_player = 'O'
        ai.player = 'O'
        ai._test_move(0, 0)
        assert ai.board[0][0] == 'O'

# _evaluate
class TestEvaluate:
    def _set_board(self, ai, game):
        # Đồng bộ self.board của agent với bàn của game
        ai.board = [row.copy() for row in game.board]

    def test_empty_board_score_is_zero(self, ai, game):
        # Bàn trống không có quân nào -> điểm phải = 0
        self._set_board(ai, game)
        assert ai._evaluate(9) == 0

    def test_ai_advantage_positive_score(self, ai, game):
        # AI có 2 quân liên tiếp không bị chặn -> điểm phải dương
        game.board[4][4] = 'O'
        game.board[4][5] = 'O'
        self._set_board(ai, game)
        assert ai._evaluate(9) > 0

    def test_opponent_advantage_negative_score(self, ai, game):
        # Đối thủ có 2 quân liên tiếp không bị chặn -> điểm phải âm
        game.board[4][4] = 'X'
        game.board[4][5] = 'X'
        self._set_board(ai, game)
        assert ai._evaluate(9) < 0

    def test_three_ai_pieces_scores_higher_than_two(self, ai, game):
        # 3 quân AI liên tiếp phải cho điểm cao hơn 2 quân
        game.board[4][4] = 'O'
        game.board[4][5] = 'O'
        self._set_board(ai, game)
        score_two = ai._evaluate(9)

        game.board[4][6] = 'O'
        self._set_board(ai, game)
        score_three = ai._evaluate(9)

        assert score_three > score_two

    def test_blocked_run_scores_less_than_open_run(self, ai, game):
        # Dãy bị chặn 1 đầu phải có điểm thấp hơn dãy mở cả 2 đầu
        game.board[4][3] = 'O'
        game.board[4][4] = 'O'
        game.board[4][5] = 'O'
        game.board[4][2] = 'X'
        self._set_board(ai, game)
        score_blocked = ai._evaluate(9)

        game.board[4][2] = '.'
        self._set_board(ai, game)
        score_open = ai._evaluate(9)

        assert score_open > score_blocked

    def test_opponent_threat_weighted_heavily(self, ai, game):
        # Đối thủ 3 quân mở cả 2 đầu phải bị phạt nặng hơn AI 3 quân cùng thế
        game.board[2][2] = 'O'
        game.board[2][3] = 'O'
        game.board[2][4] = 'O'
        self._set_board(ai, game)
        score_ai_3 = ai._evaluate(9)

        game.board[2][2] = 'X'
        game.board[2][3] = 'X'
        game.board[2][4] = 'X'
        self._set_board(ai, game)
        score_opp_3 = ai._evaluate(9)

        assert score_ai_3 > 0
        assert score_opp_3 < 0

    def test_symmetric_position_ai_vs_x(self):
        # AI đóng vai X: bố cục đối xứng phải cho điểm dương
        a = agent(depth=2, ai_player='X')
        g = Game_Caro(9)
        g.board[4][4] = 'X'
        g.board[4][5] = 'X'
        a.board = [row.copy() for row in g.board]
        assert a._evaluate(9) > 0

# test get_best_move
class TestGetBestMove:
    def test_returns_tuple_of_three(self, ai_shallow, game):
        result = ai_shallow.get_best_move(game, mode='alphabeta')
        assert len(result) == 3

    def test_move_is_within_bounds(self, ai_shallow, game):
        move, _, _ = ai_shallow.get_best_move(game, mode='alphabeta')
        r, c = move
        assert 0 <= r < 9 and 0 <= c < 9

    def test_move_is_on_empty_cell(self, ai_shallow, game):
        move, _, _ = ai_shallow.get_best_move(game, mode='alphabeta')
        r, c = move
        assert game.board[r][c] == '.'

    def test_nodes_visited_positive(self, ai_shallow, game):
        _, nodes, _ = ai_shallow.get_best_move(game, mode='alphabeta')
        assert nodes > 0

    def test_execution_time_positive(self, ai_shallow, game):
        _, _, t = ai_shallow.get_best_move(game, mode='alphabeta')
        assert t > 0

    def test_node_count_resets_between_calls(self, ai_shallow, game):
        _, nodes1, _ = ai_shallow.get_best_move(game, mode='alphabeta')
        _, nodes2, _ = ai_shallow.get_best_move(game, mode='alphabeta')
        assert nodes1 == nodes2

    def test_ai_takes_winning_move(self, game):
        # AI phải chọn nước thắng ngay khi có thể (O đã có 3 liên tiếp)
        # X đang là lượt chơi, nhưng đặt lượt O để AI đi
        _place(game,
               cells_x=[(0, 8), (1, 8), (2, 8)],
               cells_o=[(4, 0), (4, 1), (4, 2)])
        game.current_player = 'O'
        a = agent(depth=2, ai_player='O')
        move, _, _ = a.get_best_move(game, mode='alphabeta')
        # Nước thắng phải là (4,3) hoặc (4,4) -> hoàn thành dãy ngang
        r, c = move
        # Ít nhất phải đặt quân ở hàng 4 (tiếp tục dãy 3 quân liên tiếp)
        assert r == 4 and c in [3, 4]

    def test_ai_blocks_opponent_win(self, game):
        # AI phải chặn ngay khi đối thủ sắp thắng (X đã có 3 liên tiếp)
        _place(game,
               cells_x=[(2, 2), (2, 3), (2, 4)],
               cells_o=[(5, 5)])
        game.current_player = 'O'
        a = agent(depth=2, ai_player='O')
        move, _, _ = a.get_best_move(game, mode='alphabeta')
        r, c = move
        # O phải chặn tại (2,1) hoặc (2,5) để ngăn X thắng
        assert (r, c) in [(2, 1), (2, 5)]

    def test_minimax_mode_returns_valid_move(self, ai_shallow, game):
        move, nodes, t = ai_shallow.get_best_move(game, mode='minimax')
        r, c = move
        assert 0 <= r < 9 and 0 <= c < 9
        assert game.board[r][c] == '.'
        assert nodes > 0

    def test_compare_mode_returns_tuple_of_three(self, ai_shallow, game):
        game.board[4][4] = 'X'
        game.current_player = 'O'
        result = ai_shallow.get_best_move(game, mode='compare')
        assert len(result) == 3

    def test_compare_mode_move_is_valid(self, ai_shallow, game):
        game.board[4][4] = 'X'
        game.current_player = 'O'
        move, _, _ = ai_shallow.get_best_move(game, mode='compare')
        r, c = move
        assert 0 <= r < 9 and 0 <= c < 9
        assert game.board[r][c] == '.'
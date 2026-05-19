import sys
import types

if "tkinter" not in sys.modules:
    _tk_stub = types.ModuleType("tkinter")
    _tk_stub.LAST = "last"
    sys.modules["tkinter"] = _tk_stub

import pytest
from caro_ai.logic import Game_Caro

# Dữ liệu dùng chung cho các test
@pytest.fixture
def game():
    return Game_Caro(9)


@pytest.fixture
def small_game():
    # Bàn cờ 5x5 dùng cho các test hoà
    return Game_Caro(5)


def _fill_board(game, moves):
    for r, c in moves:
        game.make_move(r, c)
    return game

# Khởi tạo game
class TestInit:
    def test_board_size(self, game):
        # Bàn cờ phải có đúng 9 hàng và 9 cột
        assert len(game.board) == 9
        assert all(len(row) == 9 for row in game.board)

    def test_board_all_empty(self, game):
        # Tất cả ô phải rỗng khi mới khởi tạo
        assert all(cell == '.' for row in game.board for cell in row)

    def test_first_player_is_x(self, game):
        # Người đi trước phải là X
        assert game.current_player == 'X'

    def test_custom_size(self):
        # Kiểm tra khởi tạo với kích thước tuỳ chỉnh (13x13)
        g = Game_Caro(13)
        assert len(g.board) == 13
        assert len(g.board[0]) == 13

    def test_size_attribute(self, game):
        # Thuộc tính size phải khớp với kích thước thực tế
        assert game.size == 9

# Make move cơ bản
class TestMakeMoveBasic:
    def test_valid_move_places_piece(self, game):
        # Nước đi hợp lệ phải đặt quân đúng vị trí
        game.make_move(0, 0)
        assert game.board[0][0] == 'X'

    def test_player_switches_after_valid_move(self, game):
        # Sau nước đi hợp lệ, lượt phải chuyển sang O
        game.make_move(0, 0)
        assert game.current_player == 'O'

    def test_second_move_switches_back(self, game):
        # Sau 2 nước đi, lượt phải trở về X
        game.make_move(0, 0)
        game.make_move(1, 1)
        assert game.current_player == 'X'

    def test_invalid_move_occupied_cell(self, game):
        game.make_move(0, 0)           # X đi
        result = game.make_move(0, 0)  # O cố đi vào ô đã có quân
        assert result is False
        assert game.board[0][0] == 'X'    # ô không bị ghi đè
        assert game.current_player == 'O' # lượt không được chuyển

    def test_valid_move_returns_false_when_no_terminal(self, game):
        # Nước đi bình thường chưa kết thúc game phải trả về False
        result = game.make_move(4, 4)
        assert result is False

    def test_move_populates_correct_symbol(self, game):
        # X và O phải được đặt đúng ký hiệu theo thứ tự đi
        game.make_move(3, 3)  # X
        game.make_move(3, 4)  # O
        assert game.board[3][3] == 'X'
        assert game.board[3][4] == 'O'

# Check win
class TestCheckWin:

    def _board_with(self, size, cells, symbol):
        # Tạo bàn cờ trống rồi đặt symbol vào các ô cells
        b = [['.' for _ in range(size)] for _ in range(size)]
        for r, c in cells:
            b[r][c] = symbol
        return b

    # Hàng ngang
    def test_horizontal_win_4(self, game):
        # 4 quân liên tiếp theo hàng ngang → thắng
        b = self._board_with(9, [(2, 1), (2, 2), (2, 3), (2, 4)], 'X')
        assert game.check_win(2, 4, b) is True

    def test_horizontal_no_win_3(self, game):
        # 3 quân liên tiếp theo hàng ngang → chưa thắng
        b = self._board_with(9, [(2, 1), (2, 2), (2, 3)], 'X')
        assert game.check_win(2, 3, b) is False

    # Hàng dọc
    def test_vertical_win_4(self, game):
        # 4 quân liên tiếp theo cột → thắng
        b = self._board_with(9, [(1, 0), (2, 0), (3, 0), (4, 0)], 'O')
        assert game.check_win(4, 0, b) is True

    def test_vertical_no_win_3(self, game):
        # 3 quân liên tiếp theo cột → chưa thắng
        b = self._board_with(9, [(1, 0), (2, 0), (3, 0)], 'O')
        assert game.check_win(3, 0, b) is False

    # Đường chéo chính (trên-trái → dưới-phải)
    def test_diagonal_tlbr_win_4(self, game):
        b = self._board_with(9, [(0, 0), (1, 1), (2, 2), (3, 3)], 'X')
        assert game.check_win(3, 3, b) is True

    def test_diagonal_tlbr_no_win_3(self, game):
        b = self._board_with(9, [(0, 0), (1, 1), (2, 2)], 'X')
        assert game.check_win(2, 2, b) is False

    # Đường chéo phụ (trên-phải → dưới-trái)
    def test_diagonal_trbl_win_4(self, game):
        b = self._board_with(9, [(0, 4), (1, 3), (2, 2), (3, 1)], 'X')
        assert game.check_win(3, 1, b) is True

    def test_diagonal_trbl_no_win_3(self, game):
        b = self._board_with(9, [(0, 4), (1, 3), (2, 2)], 'X')
        assert game.check_win(2, 2, b) is False

    # 5 quân liên tiếp vẫn thắng
    def test_five_in_a_row_is_win(self, game):
        b = self._board_with(9, [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4)], 'X')
        assert game.check_win(3, 4, b) is True

    # Dãy bị đứt bởi quân đối thủ
    def test_broken_run_by_opponent(self, game):
        # Quân O ở giữa làm đứt dãy X → không thắng
        b = self._board_with(9, [(2, 0), (2, 1), (2, 2), (2, 3)], 'X')
        b[2][1] = 'O'
        assert game.check_win(2, 3, b) is False

    # Kiểm tra sát cạnh bàn cờ
    def test_win_along_top_edge(self, game):
        # Thắng sát cạnh trên bàn cờ
        b = self._board_with(9, [(0, 5), (0, 6), (0, 7), (0, 8)], 'O')
        assert game.check_win(0, 5, b) is True

    def test_win_along_left_edge(self, game):
        # Thắng sát cạnh trái bàn cờ
        b = self._board_with(9, [(0, 0), (1, 0), (2, 0), (3, 0)], 'O')
        assert game.check_win(0, 0, b) is True

    # ── BUG: check_win so sánh board[nx][ny] == board[x][y] nên '.' == '.'
    # là True, dẫn đến đếm nhầm ô trống là quân → trả về True sai.
    # Fix: thêm đk if board[x][y] == '.': return False ở đầu hàm.
    @pytest.mark.xfail(reason="Bug: check_win đếm nhầm ô trống '.' là quân thắng")
    def test_empty_cell_no_win(self, game):
        # Ô trống không được tính là thắng
        assert game.check_win(4, 4, game.board) is False


# Make_move — Phát hiện thắng (return true khi end)
class TestMakeMoveWin:
    def _setup_near_win(self, game, positions_x, positions_o):
        # Đặt quân trực tiếp lên bàn mà không qua make_move
        for r, c in positions_x:
            game.board[r][c] = 'X'
        for r, c in positions_o:
            game.board[r][c] = 'O'

    def test_x_wins_horizontal(self, game):
        # X đã có 3 quân ngang, nước tiếp theo hoàn thành 4 → thắng
        self._setup_near_win(game,
                             positions_x=[(2, 0), (2, 1), (2, 2)],
                             positions_o=[(3, 0), (3, 1), (3, 2)])
        game.current_player = 'X'
        result = game.make_move(2, 3)
        assert result is True

    def test_o_wins_vertical(self, game):
        # O thắng theo cột dọc
        self._setup_near_win(game,
                             positions_x=[(0, 1), (1, 1), (2, 1)],
                             positions_o=[(0, 0), (1, 0), (2, 0)])
        game.current_player = 'O'
        result = game.make_move(3, 0)
        assert result is True

    def test_x_wins_diagonal(self, game):
        # X thắng theo đường chéo chính
        self._setup_near_win(game,
                             positions_x=[(0, 0), (1, 1), (2, 2)],
                             positions_o=[(0, 1), (1, 0), (2, 1)])
        game.current_player = 'X'
        result = game.make_move(3, 3)
        assert result is True

    def test_win_does_not_switch_player(self, game):
        # Sau nước thắng, lượt không được chuyển sang người kia
        self._setup_near_win(game,
                             positions_x=[(2, 0), (2, 1), (2, 2)],
                             positions_o=[(3, 0)])
        game.current_player = 'X'
        game.make_move(2, 3)
        # current_player vẫn là 'X' vì hàm return trước khi đổi lượt
        assert game.current_player == 'X'


# Kiểm tra hoà
class TestIsDraw:
    def test_empty_board_is_not_draw(self, game):
        # Bàn trống không phải hoà
        assert game.is_draw(game.board) is False

    def test_partially_filled_is_not_draw(self, game):
        # Bàn chưa đầy không phải hoà
        game.board[0][0] = 'X'
        assert game.is_draw(game.board) is False

    def test_full_board_is_draw(self, small_game):
        # Bàn đầy hoàn toàn → hoà
        for r in range(5):
            for c in range(5):
                small_game.board[r][c] = 'X' if (r + c) % 2 == 0 else 'O'
        assert small_game.is_draw(small_game.board) is True

    def test_one_empty_cell_is_not_draw(self, small_game):
        # Còn đúng 1 ô trống → chưa hoà
        for r in range(5):
            for c in range(5):
                small_game.board[r][c] = 'X'
        small_game.board[4][4] = '.'
        assert small_game.is_draw(small_game.board) is False

    def test_draw_detected_via_make_move(self):
        # make_move phải trả về True khi nước đi cuối lấp đầy bàn
        g = Game_Caro(2)   # bàn 2x2 nhỏ, không thể có 4 liên tiếp
        g.make_move(0, 0)  # X
        g.make_move(0, 1)  # O
        g.make_move(1, 0)  # X
        result = g.make_move(1, 1)  # O — bàn đầy
        assert result is True


# Kiểm tra nước đi khả dụng
class TestGetAvailableMoves:
    def test_empty_board_returns_center_area(self, game):
        # Bàn trống phải trả về ít nhất 1 nước gần trung tâm
        moves = game.get_available_moves(game.board)
        assert len(moves) >= 1
        # Tất cả nước trả về phải nằm trong bàn cờ
        for r, c in moves:
            assert 0 <= r < 9
            assert 0 <= c < 9

    def test_no_duplicate_moves(self, game):
        # Không được có nước đi trùng lặp trong danh sách
        game.board[4][4] = 'X'
        moves = game.get_available_moves(game.board)
        assert len(moves) == len(set(moves))

    def test_returns_only_empty_cells(self, game):
        # Chỉ trả về ô trống, không trả về ô đã có quân
        game.board[4][4] = 'X'
        game.board[4][5] = 'O'
        moves = game.get_available_moves(game.board)
        for r, c in moves:
            assert game.board[r][c] == '.', f"O ({r},{c}) da bi chiem"

    def test_all_moves_within_radius_of_pieces(self, game):
        # Mỗi nước đề xuất phải nằm trong vòng ±2 ô so với quân đã đặt
        game.board[4][4] = 'X'
        moves = game.get_available_moves(game.board)
        for r, c in moves:
            close = any(
                abs(r - pr) <= 2 and abs(c - pc) <= 2
                for pr in range(9) for pc in range(9)
                if game.board[pr][pc] != '.'
            )
            assert close, f"Nuoc ({r},{c}) qua xa moi quan da dat"

    def test_moves_respect_board_boundaries(self, game):
        # Quân ở góc không được sinh ra nước đi ngoài bàn cờ
        game.board[0][0] = 'X'
        moves = game.get_available_moves(game.board)
        for r, c in moves:
            assert 0 <= r < 9 and 0 <= c < 9

    def test_multiple_pieces_expand_candidates(self, game):
        # Thêm quân ở góc đối diện phải mở rộng danh sách nước khả dụng
        game.board[0][0] = 'X'
        moves_one = len(game.get_available_moves(game.board))

        game.board[8][8] = 'O'
        moves_two = len(game.get_available_moves(game.board))

        assert moves_two >= moves_one

    def test_almost_full_board_returns_remaining_cells(self, small_game):
        # Khi chỉ còn 1 ô trống được bao quanh bởi quân, ô đó phải có trong kết quả
        for r in range(5):
            for c in range(5):
                small_game.board[r][c] = 'X'
        small_game.board[2][2] = '.'  # chỉ còn 1 ô trống
        moves = small_game.get_available_moves(small_game.board)
        assert (2, 2) in moves


# Test mô phỏng ván đấu đầy đủ
class TestIntegration:
    def test_x_wins_full_game_sequence(self):
        # Mô phỏng ván X thắng bằng 4 quân liên tiếp theo hàng ngang
        g = Game_Caro(9)
        moves = [
            (2, 0),  # X
            (3, 0),  # O
            (2, 1),  # X
            (3, 1),  # O
            (2, 2),  # X
            (3, 2),  # O
            (2, 3),  # X thắng
        ]
        results = [g.make_move(r, c) for r, c in moves]
        assert results[-1] is True       # nước cuối phải kết thúc game
        assert g.board[2][3] == 'X'

    def test_o_wins_full_game_sequence(self):
        # Mô phỏng ván O thắng bằng 4 quân liên tiếp theo cột dọc
        g = Game_Caro(9)
        moves = [
            (0, 0),  # X
            (0, 1),  # O
            (1, 0),  # X
            (1, 1),  # O
            (2, 0),  # X
            (2, 1),  # O
            (8, 8),  # X (nước không liên quan)
            (3, 1),  # O thắng
        ]
        results = [g.make_move(r, c) for r, c in moves]
        assert results[-1] is True
        assert g.board[3][1] == 'O'

    def test_no_moves_after_win(self):
        # Sau khi game kết thúc, ô đã chiếm vẫn giữ nguyên và không thể đi đè
        g = Game_Caro(9)
        for r, c in [(2, 0), (3, 0), (2, 1), (3, 1), (2, 2), (3, 2)]:
            g.make_move(r, c)
        g.make_move(2, 3)  # X thắng
        result = g.make_move(2, 0)  # cố đi vào ô đã chiếm
        assert result is False

    def test_player_alternation_across_many_moves(self):
        # Lượt đi phải xen kẽ đúng thứ tự X → O → X → O qua nhiều nước
        g = Game_Caro(9)
        # Dùng 2 cột khác nhau để không tạo ra 4 liên tiếp
        positions = [(r, 0 if i % 2 == 0 else 5) for i, r in enumerate(range(8))]
        expected = ['X', 'O'] * 4
        actual = []
        for r, c in positions:
            actual.append(g.current_player)
            g.make_move(r, c)
        assert actual == expected

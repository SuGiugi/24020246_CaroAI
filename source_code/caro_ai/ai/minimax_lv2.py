import time
import math


class agent:
    def __init__(self, depth: int = 3, ai_player: str = 'O'):
        self.depth = depth
        self.ai_player = ai_player
        self.node_visted = 0

    # Hàm đánh giá
    def _evaluate(self, size):
        score = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for x in range(size):
            for y in range(size):
                if self.board[x][y] != '.':
                    player = self.board[x][y]
                    for dx, dy in directions:
                        close = 0
                        count = 1
                        nx, ny = x - dx, y - dy
                        if 0 <= nx < size and 0 <= ny < size:
                            if self.board[nx][ny] == player:
                                continue
                            elif self.board[nx][ny] == '.':
                                pass
                            else:
                                close += 1
                        else:
                            close += 1
                        for d in range(1, 4):
                            nx, ny = x + d * dx, y + d * dy
                            if 0 <= nx < size and 0 <= ny < size:
                                if self.board[nx][ny] == player:
                                    count += 1
                                elif self.board[nx][ny] == '.':
                                    break
                                else:
                                    close += 1
                                    break
                            else:
                                close += 1
                                break
                        point = 0
                        if close == 2:
                            continue
                        elif count == 3 and close == 1:
                            point = 1000
                        elif count == 3 and close == 0:
                            point = 4000
                        elif count == 2 and close == 1:
                            point = 10
                        elif count == 2 and close == 0:
                            point = 1000


                        if player == self.ai_player:
                            score += point
                        else:
                            score -= point * 5
        return score
    def _get_optimized_moves(self, game, board, use_optimization):
        available_moves = game.get_available_moves(board)
        if not use_optimization:
            return available_moves

        size = game.size
        has_pieces = any(board[r][c] != '.' for r in range(size) for c in range(size))

        # Nếu bàn cờ trống, ưu tiên đánh vào chính giữa
        if not has_pieces:
            center = size // 2
            if (center, center) in available_moves:
                return [(center, center)]
            return available_moves[:1]

        smart_moves = []
        center_pos = size / 2

        for move in available_moves:
            x, y = move
            is_near = False
            # Quét bán kính 2 ô xung quanh để tìm quân cờ đã đánh
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < size and 0 <= ny < size and board[nx][ny] != '.':
                        is_near = True
                        break
                if is_near: break

            if is_near:
                # Trọng số phụ: Khoảng cách tới tâm (càng gần tâm càng tốt)
                dist_to_center = (x - center_pos) ** 2 + (y - center_pos) ** 2
                smart_moves.append((move, dist_to_center))

        # Sắp xếp các nước đi ưu tiên gần tâm trước
        smart_moves.sort(key=lambda item: item[1])
        return [move for move, _ in smart_moves]

    # Minimax (Level 1) ---
    def _minimax(self, game, depth, maximizing, x, y, use_optimization):
        self.node_visted += 1
        if game.check_win(x, y, self.board):
            return -(500000 + depth) if maximizing else 500000 + depth
        if depth == 0 or game.is_draw(self.board):
            return self._evaluate(game.size)

        moves = self._get_optimized_moves(game, self.board, use_optimization)

        if maximizing:
            max_eval = -math.inf
            for move in moves:
                x, y = move
                self._test_move(x, y)
                eval = self._minimax(game, depth - 1, False, x, y, use_optimization)
                self._undo_move(x, y)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = math.inf
            for move in moves:
                x, y = move
                self._test_move(x, y)
                eval = self._minimax(game, depth - 1, True, x, y, use_optimization)
                self._undo_move(x, y)
                min_eval = min(min_eval, eval)
            return min_eval

    def _alphabeta(self, game, depth, alpha, beta, maximizing, x, y, use_optimization):
        self.node_visted += 1
        if game.check_win(x, y, self.board):
            return -(500000 + depth) if maximizing else 500000 + depth
        if depth == 0 or game.is_draw(self.board):
           return self._evaluate(game.size)

        moves = self._get_optimized_moves(game, self.board, use_optimization)

        if maximizing:
            max_eval = -math.inf
            for move in moves:
                x, y = move
                self._test_move(x, y)
                eval = self._alphabeta(game, depth - 1, alpha, beta, False, x, y, use_optimization)
                self._undo_move(x, y)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, max_eval)
                if beta <= alpha:  # Cắt nhánh Beta
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in moves:
                x, y = move
                self._test_move(x, y)
                eval = self._alphabeta(game, depth - 1, alpha, beta, True, x, y, use_optimization)
                self._undo_move(x, y)
                min_eval = min(min_eval, eval)
                beta = min(beta, min_eval)
                if beta <= alpha:  # Cắt nhánh Alpha
                    break
            return min_eval

    # --- Hàm chạy điều phối & So sánh hiệu năng ---
    def get_best_move(self, game, mode='alphabeta', use_optimization=True):
        if mode == 'compare':
            print(f"\n--- ĐỐI SÁNH HIỆU NĂNG TẠI ĐỘ SÂU {self.depth} ---")
            # Chạy thử nghiệm Minimax
            move_m, score_m, nodes_m, time_m = self._execute_search(game, 'minimax', use_optimization)
            print(
                f"[Minimax]    Nước đi: {move_m} | Điểm: {score_m} | Số node xét: {nodes_m} | Thời gian: {time_m:.4f}s")

            # Chạy thử nghiệm Alpha-Beta
            move_a, score_a, nodes_a, time_a = self._execute_search(game, 'alphabeta', use_optimization)
            print(
                f"[Alpha-Beta] Nước đi: {move_a} | Điểm: {score_a} | Số node xét: {nodes_a} | Thời gian: {time_a:.4f}s")
            print(
                f"-> Giảm tải được: {((nodes_m - nodes_a) / max(1, nodes_m)) * 100:.2f}% số lượng trạng thái phải duyệt.")
            print("-" * 40)
            return move_a, nodes_a, time_a

        # Chạy đơn lẻ theo chế độ được chọn
        move, _, nodes, execution_time = self._execute_search(game, mode, use_optimization)
        return move, nodes, execution_time

    def _execute_search(self, game, mode, use_optimization):
        self.node_visted = 0
        start_time = time.time()

        self.board = [row.copy() for row in game.board]
        self.player = game.current_player
        best_score = -math.inf
        move_to_make = None
        best_local = -math.inf

        moves = self._get_optimized_moves(game, self.board, use_optimization)
        alpha = -math.inf
        beta = math.inf

        for move in moves:
            x, y = move
            self._test_move(x, y)

            if mode == 'minimax':
                score = self._minimax(game, self.depth - 1, False, x, y, use_optimization)
            else:  # alphabeta
                score = self._alphabeta(game, self.depth - 1, alpha, beta, False, x, y, use_optimization)

            local = self._evaluate(game.size)
            self._undo_move(x, y)

            if score > best_score:
                print(f"New best move: {(x, y)} with score {score} (previous best: {best_score})")
                best_score = score
                move_to_make = (x, y)
                best_local = local
            elif score == best_score and local > best_local:
                print(f"Tie in score {score}, but new move {(x, y)} has better local evaluation {local} (previous local: {best_local})")
                move_to_make = (x, y)
                best_local = local

            if mode == 'alphabeta':
                alpha = max(alpha, best_score)

        return move_to_make, best_score, self.node_visted, time.time() - start_time

    def _test_move(self, x, y):
        self.board[x][y] = self.player
        self.player = 'O' if self.player == 'X' else 'X'

    def _undo_move(self, x, y):
        self.board[x][y] = '.'
        self.player = 'O' if self.player == 'X' else 'X'
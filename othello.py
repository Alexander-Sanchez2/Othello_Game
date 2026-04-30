import copy

# ── Board constants ──────────────────────────────────────────────────────────
SIZE = 8
EMPTY = '.'
BLACK = 'B'
WHITE = 'W'

DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

# ── Board helpers ───────────────────────────────────────────────────────────
def make_board():
    board = [[EMPTY]*SIZE for _ in range(SIZE)]
    mid = SIZE // 2
    board[mid-1][mid-1] = WHITE
    board[mid][mid] = WHITE
    board[mid-1][mid] = BLACK
    board[mid][mid-1] = BLACK
    return board

def opponent(color):
    return WHITE if color == BLACK else BLACK

def in_bounds(r, c):
    return 0 <= r < SIZE and 0 <= c < SIZE

def flips_in_dir(board, r, c, dr, dc, color):
    opp = opponent(color)
    cells = []
    nr, nc = r + dr, c + dc

    while in_bounds(nr, nc) and board[nr][nc] == opp:
        cells.append((nr, nc))
        nr += dr
        nc += dc

    if cells and in_bounds(nr, nc) and board[nr][nc] == color:
        return cells
    return []

def get_flips(board, r, c, color):
    if board[r][c] != EMPTY:
        return []

    flips = []
    for dr, dc in DIRECTIONS:
        flips += flips_in_dir(board, r, c, dr, dc, color)
    return flips

def valid_moves(board, color):
    return [(r, c) for r in range(SIZE) for c in range(SIZE)
            if get_flips(board, r, c, color)]

def make_move(board, r, c, color):
    flips = get_flips(board, r, c, color)
    if not flips:
        return None

    nb = [row[:] for row in board]
    nb[r][c] = color

    for fr, fc in flips:
        nb[fr][fc] = color

    return nb

def count(board):
    b = sum(row.count(BLACK) for row in board)
    w = sum(row.count(WHITE) for row in board)
    return b, w

def is_game_over(board):
    return not valid_moves(board, BLACK) and not valid_moves(board, WHITE)

# ── AI EVALUATION ───────────────────────────────────────────────────────────
def evaluate_board(board, color):
    opp = opponent(color)
    black, white = count(board)

    score = (black - white) if color == BLACK else (white - black)

    # corner importance
    corners = [(0,0),(0,7),(7,0),(7,7)]
    corner_score = 0

    for r, c in corners:
        if board[r][c] == color:
            corner_score += 25
        elif board[r][c] == opp:
            corner_score -= 25

    return score + corner_score

# ── MINIMAX AI ──────────────────────────────────────────────────────────────
def minimax(board, depth, maximizing, color, alpha, beta):
    if depth == 0 or is_game_over(board):
        return evaluate_board(board, color), None

    moves = valid_moves(board, color if maximizing else opponent(color))

    if not moves:
        return evaluate_board(board, color), None

    best_move = None

    if maximizing:
        max_eval = float('-inf')

        for move in moves:
            new_board = make_move(board, move[0], move[1], color)
            eval_score, _ = minimax(new_board, depth-1, False, color, alpha, beta)

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break

        return max_eval, best_move

    else:
        min_eval = float('inf')

        for move in moves:
            new_board = make_move(board, move[0], move[1], opponent(color))
            eval_score, _ = minimax(new_board, depth-1, True, color, alpha, beta)

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move

            beta = min(beta, eval_score)
            if beta <= alpha:
                break

        return min_eval, best_move

def best_ai_move(board, color, depth=4):
    _, move = minimax(board, depth, True, color, float('-inf'), float('inf'))
    return move

# ── GAME LOOP ───────────────────────────────────────────────────────────────
def game_loop(vs_ai=True):
    board = make_board()
    current = BLACK

    while True:

        moves = valid_moves(board, current)

        if is_game_over(board):
            b, w = count(board)
            print("\nGame Over!")
            print(f"Black: {b}  White: {w}")
            return

        if not moves:
            current = opponent(current)
            continue

        # ── AI TURN ──
        if vs_ai and current == WHITE:
            print("\nAI thinking...\n")

            move = best_ai_move(board, WHITE, depth=4)

            if move:
                board = make_move(board, move[0], move[1], WHITE)

            current = opponent(current)
            continue

        # ── HUMAN TURN ──
        print_board(board, moves)

        while True:
            raw = input("Enter move (e.g. D3): ").strip().upper()

            pos = parse_move(raw)

            if pos and pos in moves:
                board = make_move(board, pos[0], pos[1], current)
                current = opponent(current)
                break

            print("Invalid move")

# ── DISPLAY ─────────────────────────────────────────────────────────────────
def print_board(board, moves):
    print("\n  A B C D E F G H")
    for r in range(SIZE):
        row = str(r+1) + " "
        for c in range(SIZE):
            if board[r][c] == BLACK:
                row += "B "
            elif board[r][c] == WHITE:
                row += "W "
            elif (r, c) in moves:
                row += "+ "
            else:
                row += ". "
        print(row)

def parse_move(text):
    if len(text) != 2:
        return None

    c = ord(text[0]) - ord('A')
    r = int(text[1]) - 1

    if in_bounds(r, c):
        return r, c
    return None

# ── RUN GAME ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    game_loop(vs_ai=True)
import copy
# ── Board constants ──────────────────────────────────────────────────────────
SIZE = 8
EMPTY = '.'
BLACK = 'B'
WHITE = 'W'

DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

# ── ANSI colours ─────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
BG_GREEN  = "\033[42m"
BG_BLACK  = "\033[40m"
BG_GRAY   = "\033[100m"

def clear_screen():
    # Fallback: print 50 newlines if os.system is not allowed
    print("\n" * 50)

# ── Board helpers ─────────────────────────────────────────────────────────────
def make_board():
    board = [[EMPTY]*SIZE for _ in range(SIZE)]
    mid = SIZE // 2
    board[mid-1][mid-1] = WHITE
    board[mid][mid]     = WHITE
    board[mid-1][mid]   = BLACK
    board[mid][mid-1]   = BLACK
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
    nb = copy.deepcopy(board)
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

# ── Display ───────────────────────────────────────────────────────────────────
DISC_B = f"{BG_BLACK}{BOLD} ● {RESET}"
DISC_W = f"{BG_GRAY}{BOLD} ○ {RESET}"
DISC_E = f"{BG_GREEN} · {RESET}"
DISC_H = f"{BG_GREEN}{YELLOW}{BOLD} + {RESET}"

def render_board(board, color=None):
    moves = set(valid_moves(board, color)) if color else set()
    col_labels = "    " + " ".join(f"{CYAN} {chr(65+c)} {RESET}" for c in range(SIZE))
    print(col_labels)
    print(f"   {DIM}┌{'───┬'*(SIZE-1)}───┐{RESET}")
    for r in range(SIZE):
        row_str = f" {CYAN}{r+1}{RESET} {DIM}│{RESET}"
        for c in range(SIZE):
            val = board[r][c]
            if val == BLACK:
                row_str += DISC_B
            elif val == WHITE:
                row_str += DISC_W
            elif (r, c) in moves:
                row_str += DISC_H
            else:
                row_str += DISC_E
            row_str += f"{DIM}│{RESET}"
        print(row_str)
        if r < SIZE - 1:
            print(f"   {DIM}├{'───┼'*(SIZE-1)}───┤{RESET}")
    print(f"   {DIM}└{'───┴'*(SIZE-1)}───┘{RESET}")

def render_status(board, current):
    b, w = count(board)
    sym_b = f"{BG_BLACK}{BOLD} ● {RESET}"
    sym_w = f"{BG_GRAY}{BOLD} ○ {RESET}"
    turn_marker = lambda c: f" {YELLOW}◀ to move{RESET}" if c == current else ""
    print(f"\n  {sym_b} Black: {BOLD}{b}{RESET}{turn_marker(BLACK)}   "
          f"{sym_w} White: {BOLD}{w}{RESET}{turn_marker(WHITE)}")
    label = 'Black (●)' if current == BLACK else 'White (○)'
    print(f"\n  {GREEN}» {label}'s turn{RESET}  {DIM}[type col+row e.g. D3, or 'quit']{RESET}\n")

# ── Input parsing ─────────────────────────────────────────────────────────────
def parse_move(text):
    text = text.strip().upper()
    if len(text) != 2:
        return None
    if text[0].isalpha() and text[1].isdigit():
        c = ord(text[0]) - ord('A')
        r = int(text[1]) - 1
    elif text[0].isdigit() and text[1].isalpha():
        r = int(text[0]) - 1
        c = ord(text[1]) - ord('A')
    else:
        return None
    if in_bounds(r, c):
        return r, c
    return None

# ── Game loop ─────────────────────────────────────────────────────────────────
def game_loop():
    board = make_board()
    current = BLACK

    while True:
        clear_screen()
        print(f"\n  {BOLD}{CYAN}╔══════════════════╗")
        print(f"  ║   O T H E L L O  ║")
        print(f"  ╚══════════════════╝{RESET}\n")
        render_board(board, current)
        render_status(board, current)

        moves = valid_moves(board, current)

        if is_game_over(board):
            b, w = count(board)
            print(f"\n  {BOLD}Game Over!{RESET}")
            if b > w:
                print(f"  {GREEN}Black (●) wins! {b}–{w}{RESET}")
            elif w > b:
                print(f"  {GREEN}White (○) wins! {w}–{b}{RESET}")
            else:
                print(f"  {YELLOW}It's a draw! {b}–{w}{RESET}")
            return

        if not moves:
            input(f"  {YELLOW}No moves for {current} — press Enter to pass.{RESET}")
            current = opponent(current)
            continue

        while True:
            raw = input(f"  {BOLD}>{RESET} ").strip().lower()
            if raw in ('q', 'quit', 'exit'):
                return False # Signal to stop completely
            
            pos = parse_move(raw)
            if pos and pos in moves:
                board = make_move(board, pos[0], pos[1], current)
                current = opponent(current)
                break
            print(f"  {YELLOW}Invalid or illegal move. Try again.{RESET}")

def main():
    while True:
        clear_screen()
        print(f"\n  {BOLD}{CYAN}╔══════════════════╗")
        print(f"  ║   O T H E L L O  ║")
        print(f"  ╚══════════════════╝{RESET}\n")
        print(f"\n  {BOLD}{CYAN}OTHELLO - Local Multiplayer{RESET}")
        print(f"\n  {GREEN}s{RESET} · Start Game")
        print(f"  {GREEN}q{RESET} · Quit")
        
        choice = input(f"\n  {BOLD}>{RESET} ").strip().lower()
        if choice == 's':
            if game_loop() is False:
                break
            input(f"\n  Press Enter to return to menu...")
        elif choice == 'q':
            break

if __name__ == '__main__':
    main()

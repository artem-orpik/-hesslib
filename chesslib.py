import tkinter as tk
from tkinter import simpledialog

class Piece:
    def __init__(self, color):
        self.color = color

    def get_moves(self, board, x, y):
        return []

    def __str__(self):
        return self.symbol

class Pawn(Piece):
    symbol = '♟'

    def get_moves(self, board, x, y):
        moves = []
        direction = -1 if self.color == 'black' else 1
        start_row = 6 if self.color == 'black' else 1
        if 0 <= y + direction < 8 and board[y + direction][x] is None:
            moves.append((x, y + direction))
            if y == start_row and board[y + 2 * direction][x] is None:
                moves.append((x, y + 2 * direction))
        for dx in [-1, 1]:
            nx, ny = x + dx, y + direction
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = board[ny][nx]
                if target and target.color != self.color:
                    moves.append((nx, ny))
                else:
                    last_move = Board.last_move
                    if last_move:
                        (fx, fy), (tx, ty), last_piece = last_move
                        if (isinstance(last_piece, Pawn) and
                            abs(fy - ty) == 2 and
                            tx == nx and ty == y and
                            last_piece.color != self.color):
                            moves.append((nx, ny))
        return moves

class Rook(Piece):
    symbol = '♜'

    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def get_moves(self, board, x, y):
        moves = []
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if board[ny][nx] is None:
                    moves.append((nx, ny))
                elif board[ny][nx].color != self.color:
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return moves

class Knight(Piece):
    symbol = '♞'

    def get_moves(self, board, x, y):
        moves = []
        for dx, dy in [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = board[ny][nx]
                if target is None or target.color != self.color:
                    moves.append((nx, ny))
        return moves

class Bishop(Piece):
    symbol = '♝'

    def get_moves(self, board, x, y):
        moves = []
        for dx, dy in [(1,1), (-1,1), (1,-1), (-1,-1)]:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if board[ny][nx] is None:
                    moves.append((nx, ny))
                elif board[ny][nx].color != self.color:
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return moves

class Queen(Piece):
    symbol = '♛'

    def get_moves(self, board, x, y):
        return Rook(self.color).get_moves(board, x, y) + Bishop(self.color).get_moves(board, x, y)

class King(Piece):
    symbol = '♚'

    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def get_moves(self, board, x, y):
        moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    target = board[ny][nx]
                    if target is None or target.color != self.color:
                        moves.append((nx, ny))
        if not self.has_moved:
            row = 7 if self.color == 'black' else 0
            if isinstance(board[row][7], Rook) and not board[row][7].has_moved:
                if board[row][5] is None and board[row][6] is None:
                    moves.append((6, row))
            if isinstance(board[row][0], Rook) and not board[row][0].has_moved:
                if board[row][1] is None and board[row][2] is None and board[row][3] is None:
                    moves.append((2, row))
        return moves

class Board:
    last_move = None

    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.turn = 'white'
        self.setup()

    def setup(self):
        for i in range(8):
            self.board[1][i] = Pawn('white')
            self.board[6][i] = Pawn('black')
        layout = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, cls in enumerate(layout):
            self.board[0][i] = cls('white')
            self.board[7][i] = cls('black')

    def promote_pawn(self, x, y):
        color = self.board[y][x].color
        piece_map = {'Q': Queen, 'R': Rook, 'B': Bishop, 'N': Knight}
        choice = simpledialog.askstring("Promotion", "Выберите фигуру для превращения (Q, R, B, N):")
        if choice and choice.upper() in piece_map:
            self.board[y][x] = piece_map[choice.upper()](color)
        else:
            self.board[y][x] = Queen(color)

    def get_legal_moves(self, x, y):
        piece = self.board[y][x]
        if not piece or piece.color != self.turn:
            return []
        raw_moves = piece.get_moves(self.board, x, y)
        legal_moves = []
        for mx, my in raw_moves:
            backup_from = self.board[y][x]
            backup_to = self.board[my][mx]
            self.board[my][mx] = backup_from
            self.board[y][x] = None
            if not self.in_check(backup_from.color):
                legal_moves.append((mx, my))
            self.board[y][x] = backup_from
            self.board[my][mx] = backup_to
        return legal_moves

    def move(self, from_pos, to_pos):
        fx, fy = from_pos
        tx, ty = to_pos
        piece = self.board[fy][fx]
        if not piece or piece.color != self.turn:
            return False

        # Получение допустимых ходов с учетом шаха
        legal_moves = []
        for mx, my in piece.get_moves(self.board, fx, fy):
            backup_from = self.board[fy][fx]
            backup_to = self.board[my][mx]
            self.board[fy][fx] = None
            self.board[my][mx] = backup_from
            king_in_check = self.in_check(self.turn)
            self.board[fy][fx] = backup_from
            self.board[my][mx] = backup_to
            if not king_in_check:
                legal_moves.append((mx, my))

        if (tx, ty) not in legal_moves:
            return False

        target = self.board[ty][tx]

        # Взятие на проходе
        if isinstance(piece, Pawn) and target is None and abs(fx - tx) == 1:
            last_move = Board.last_move
            if last_move:
                (lx, ly), (tx2, ty2), last_piece = last_move
                if (isinstance(last_piece, Pawn) and
                        abs(ly - ty2) == 2 and
                        tx2 == tx and
                        ty2 == fy):
                    self.board[ty2][tx2] = None  # Удаляем пешку, которую берём на проходе

        # Рокировка
        if isinstance(piece, King) and abs(tx - fx) == 2:
            row = fy
            if tx == 6:  # короткая рокировка
                self.board[row][5] = self.board[row][7]
                self.board[row][7] = None
                self.board[row][5].has_moved = True
            elif tx == 2:  # длинная рокировка
                self.board[row][3] = self.board[row][0]
                self.board[row][0] = None
                self.board[row][3].has_moved = True
            piece.has_moved = True

        if isinstance(piece, (King, Rook)):
            piece.has_moved = True

        self.board[ty][tx] = piece
        self.board[fy][fx] = None

        # Превращение пешки
        if isinstance(piece, Pawn) and (ty == 0 or ty == 7):
            self.promote_pawn(tx, ty)

        # Обновление последнего хода
        Board.last_move = ((fx, fy), (tx, ty), piece)

        # Смена хода
        self.turn = 'white' if self.turn == 'black' else 'black'
        return True

    def get_king_pos(self, color):
        for y in range(8):
            for x in range(8):
                p = self.board[y][x]
                if isinstance(p, King) and p.color == color:
                    return x, y
        return None

    def in_check(self, color):
        kx, ky = self.get_king_pos(color)
        for y in range(8):
            for x in range(8):
                p = self.board[y][x]
                if p and p.color != color:
                    if (kx, ky) in p.get_moves(self.board, x, y):
                        return True
        return False

class ChessGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chess")
        self.canvas = tk.Canvas(self.root, width=640, height=640)
        self.canvas.pack()
        self.board = Board()
        self.selected = None
        self.valid_moves = []
        self.canvas.bind("<Button-1>", self.click)
        self.mate = False
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        is_mate = self.is_mate(self.board.turn)
        self.mate = is_mate
        for y in range(8):
            for x in range(8):
                color = "#EEEED2" if (x + y) % 2 == 0 else "#769656"
                self.canvas.create_rectangle(x*80, y*80, x*80+80, y*80+80, fill=color)
                if self.selected == (x, y):
                    self.canvas.create_rectangle(x*80, y*80, x*80+80, y*80+80, outline="blue", width=4)
                if (x, y) in self.valid_moves:
                    self.canvas.create_oval(x*80+30, y*80+30, x*80+50, y*80+50, fill="green")
                piece = self.board.board[y][x]
                if piece:
                    text_color = "black" if piece.color == 'black' else "white"
                    self.canvas.create_text(x*80+40, y*80+40, text=str(piece), fill=text_color, font=("Arial", 32))
        for color in ["white", "black"]:
            if self.board.in_check(color):
                xk, yk = self.board.get_king_pos(color)
                self.canvas.create_rectangle(xk*80, yk*80, xk*80+80, yk*80+80,
                                             outline="yellow" if not self.is_mate(color) else "red", width=4)
                if self.is_mate(color):
                    self.canvas.create_text(320, 20, text=f"Победа {'белых' if color == 'black' else 'черных'}",
                                            fill="red", font=("Arial", 24))

    def is_mate(self, color):
        if not self.board.in_check(color):
            return False
        for y in range(8):
            for x in range(8):
                p = self.board.board[y][x]
                if p and p.color == color:
                    if self.board.get_legal_moves(x, y):
                        return False
        return True

    def click(self, event):
        if self.mate:
            return
        x, y = event.x // 80, event.y // 80
        if self.selected:
            if self.board.move(self.selected, (x, y)):
                self.selected = None
                self.valid_moves = []
            else:
                self.selected = None
                self.valid_moves = []
        else:
            piece = self.board.board[y][x]
            if piece and piece.color == self.board.turn:
                legal_moves = self.board.get_legal_moves(x, y)
                if legal_moves:
                    self.selected = (x, y)
                    self.valid_moves = legal_moves
                else:
                    self.selected = None
                    self.valid_moves = []
            else:
                self.selected = None
                self.valid_moves = []
        self.draw_board()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    ChessGUI().run()

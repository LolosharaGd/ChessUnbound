#
# ██╗███╗   ███╗██████╗  ██████╗ ██████╗ ████████╗ █████╗ ███╗   ██╗████████╗
# ██║████╗ ████║██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝██╔══██╗████╗  ██║╚══██╔══╝
# ██║██╔████╔██║██████╔╝██║   ██║██████╔╝   ██║   ███████║██╔██╗ ██║   ██║
# ██║██║╚██╔╝██║██╔═══╝ ██║   ██║██╔══██╗   ██║   ██╔══██║██║╚██╗██║   ██║
# ██║██║ ╚═╝ ██║██║     ╚██████╔╝██║  ██║   ██║   ██║  ██║██║ ╚████║   ██║
# ╚═╝╚═╝     ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝
#
# Hello, this is Chess Unbound, a chess game on PythonXPygame, made by LolosharaGd, it is open source, and you can add anything you want to the code,
# New pieces, new modes, anything and publish it. The only thing you need to do - credit me and original (this) project
#
# Here is the list where I will list mods for this project (where you added something)
# If you made a mod and I haven't listed it here (because I haven't saw it or for other reasons), send it in the comments
#
mods_list = ["It is empty right now, but you can fix it :>"]
#
# If you are making a mod, you can replace this line with "Chess Unbound mod <ModName> made by <YourUsername>" or something like that
#

import pygame as pg
import sys

pg.font.init()


class Game:
    def __init__(self, wid, hei, fps):
        self.wid = wid
        self.hei = hei
        self.fps = fps

        self.dis = pg.display.set_mode((wid, hei))

        self.clock = pg.time.Clock()

        # Set of pieces on the board, lowercase =  white, uppercase = black
        self.pieces = [
            ["R", "N", "B", "Q", "K", "B", "N", "R"],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["r", "n", "b", "q", "k", "b", "n", "r"],
        ]

        # A list that contains every move that happened
        self.moves_history = []

        # A list of cells that are attacked by selected piece, 0 = not attacked, 1 = attacked
        self.attacked_cells = [[0 for x in range(8)] for y in range(8)]

        # A lists of cells attacked by black/white pieces, 0 = not attacked, 1 = attacked
        self.attacked_cells_b_white = [[0 for x in range(8)] for y in range(8)]
        self.attacked_cells_b_black = [[0 for x in range(8)] for y in range(8)]

        self.free_spaces = ["", "ep", "EP"]  # Pieces that count as a free space, "ep" and "EP" are pieces made for En Passant and do not affect anything besides pawns
        self.selected_piece = [None, None]  # Selected piece coordinates (x, y)
        self.selected_piece_type = None  # Selected piece type, like "b" or "Q"
        self.white_pieces = ["p", "r", "n", "b", "q", "k", "ep"]  # List of every possible white piece
        self.black_pieces = ["P", "R", "N", "B", "Q", "K", "EP"]  # List of every possible black piece

        self.mouse_pos = [0, 0]

        self.white_turn = True
        self.take_turns = True
        self.checks_enabled = True
        self.castles = [True, True, True, True]  # Ability to castle [White kingside, white queenside, black kingside, black queenside]

        self.piece_to_promote = "q"
        self.promote_piece_cycle = {
            "q": "r",
            "r": "b",
            "b": "n",
            "n": "k",
            "k": "",
            "": "q"
        }
        self.promoting_piece_text = {
            "q": "Queen",
            "r": "Rook",
            "b": "Bishop",
            "n": "Knight",
            "k": "King",
            "": "Death"
        }

        self.see_en_passant = False
        self.en_passant_enabled = True

        self.main_font = pg.font.SysFont("bahnschrift", 100)
        self.main_font_s = pg.font.SysFont("bahnschrift", 50)

    def run(self):
        while True:
            self.dis.fill((255, 255, 255))

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    sys.exit()

                elif e.type == pg.MOUSEMOTION:
                    self.mouse_pos = e.pos

                elif e.type == pg.MOUSEBUTTONDOWN:
                    if e.button == 1:  # If click is right click
                        if 100 <= e.pos[0] <= 900 and 100 <= e.pos[1] <= 900:  # If click is in bounds of board
                            if self.selected_piece == [None, None]:  # If we have not yet selected a piece
                                this_piece = self.pieces[(e.pos[1] - 100) // 100][(e.pos[0] - 100) // 100]  # Variable for piece standing under the cursor

                                if this_piece not in self.free_spaces:  # If this is not an empty space or En Passant space
                                    if (self.white_turn and this_piece == this_piece.lower()) or \
                                            (not self.white_turn and this_piece != this_piece.lower()) or \
                                            not self.take_turns:  # If (white turn and this piece is white) or (black turn and this piece is black) or (we do not take turns)
                                        self.selected_piece = [(e.pos[0] - 100) // 100, (e.pos[1] - 100) // 100]
                                        self.selected_piece_type = this_piece  # Saving selected piece type and coordinates

                                        # When a piece is clicked, selecting attacked cells
                                        if self.selected_piece_type.lower() == "n":  # If a piece type is "n"
                                            # In the list of offsets, check if offset cell is valid, and if it is, set value in corresponding cell in attacked cells list to 1
                                            for offset in [[-1, -2], [1, -2], [2, -1], [2, 1], [1, 2], [-1, 2], [-2, 1], [-2, -1]]:
                                                is_in_bounds = self.is_in_matrix(self.selected_piece[0] + offset[0], self.selected_piece[1] + offset[1], 8, 8)

                                                if is_in_bounds:
                                                    offset_piece = self.pieces[self.selected_piece[1] + offset[1]][self.selected_piece[0] + offset[0]]

                                                    is_free_or_opposite_team = (offset_piece in self.free_spaces) or \
                                                                               (this_piece == this_piece.lower() and offset_piece != offset_piece.lower()) or \
                                                                               (this_piece != this_piece.lower() and offset_piece == offset_piece.lower())

                                                    if is_free_or_opposite_team:
                                                        self.attacked_cells[self.selected_piece[1] + offset[1]][self.selected_piece[0] + offset[0]] = 1
                                        # You can copy and paste this block with "elif" instead of "if" to make new pieces
                                        elif self.selected_piece_type.lower() == "p":  # If a piece type is "p"
                                            # In the lists of offsets for black and white versions
                                            # check if offset cell is valid, and if it is, set value in corresponding cell in attacked cells list to 1
                                            offsets = [[[-1, -1], [1, -1]], [[0, -1], [0, -2]]]

                                            if self.selected_piece_type != self.selected_piece_type.lower():
                                                offsets = [[[-1, 1], [1, 1]], [[0, 1], [0, 2]]]

                                            for offset in offsets[0]:  # Capturing moves
                                                is_in_bounds = self.is_in_matrix(self.selected_piece[0] + offset[0], self.selected_piece[1] + offset[1], 8, 8)
                                                if is_in_bounds:
                                                    offset_piece = self.pieces[self.selected_piece[1] + offset[1]][self.selected_piece[0] + offset[0]]

                                                    is_not_free_and_opposite_team = (this_piece == this_piece.lower() and offset_piece != offset_piece.lower()) or \
                                                                                    (this_piece != this_piece.lower() and offset_piece == offset_piece.lower()) and \
                                                                                    (offset_piece != "")
                                                    if is_not_free_and_opposite_team:
                                                        self.attacked_cells[self.selected_piece[1] + offset[1]][self.selected_piece[0] + offset[0]] = 1

                                            for offset in offsets[1]:  # Peaceful moves
                                                is_in_bounds = self.is_in_matrix(self.selected_piece[0] + offset[0], self.selected_piece[1] + offset[1], 8, 8)
                                                if is_in_bounds:
                                                    offset_piece = self.pieces[self.selected_piece[1] + offset[1]][self.selected_piece[0] + offset[0]]

                                                    is_free = offset_piece in self.free_spaces
                                                    # (Is move 1 square) or ({Is move 2 squares} and [Is one square move possible] and <Is this pawn on 2nd or 7th rank>)
                                                    is_available_double_move = ([offset[0], abs(offset[1])] == [0, 1]) or \
                                                                               ([offset[0], abs(offset[1])] == [0, 2] and
                                                                                self.pieces[self.selected_piece[1] + int(offset[1] * 0.5)][self.selected_piece[0]] in self.free_spaces and (
                                                                                        self.selected_piece[1] == 1 or
                                                                                        self.selected_piece[1] == 6
                                                                                ))
                                                    if is_free and is_available_double_move:
                                                        self.attacked_cells[self.selected_piece[1] + offset[1]][self.selected_piece[0] + offset[0]] = 1
                                        elif self.selected_piece_type.lower() == "k":  # If a piece type is "k"
                                            # Check for available castling
                                            if self.selected_piece_type == "k":  # If you selected white king
                                                if self.castles[0]:  # If w-k castle is available
                                                    if self.pieces[7][4] == "k" and \
                                                            self.pieces[7][5] == "" and \
                                                            self.pieces[7][6] == "" and \
                                                            self.pieces[7][7] == "r":  # If every piece is on its place
                                                        if not self.checks_enabled or \
                                                                (self.attacked_cells_b_black[7][4] + self.attacked_cells_b_black[7][5] == 0):  # If all rules of castling are observed
                                                            self.attacked_cells[7][6] = 1  # Select castling square
                                                if self.castles[1]:  # If w-q castle is available
                                                    if self.pieces[7][4] == "k" and \
                                                            self.pieces[7][3] == "" and \
                                                            self.pieces[7][2] == "" and \
                                                            self.pieces[7][1] == "" and \
                                                            self.pieces[7][0] == "r":  # If every piece is on its place
                                                        if not self.checks_enabled or \
                                                                (self.attacked_cells_b_black[7][4] + self.attacked_cells_b_black[7][3] == 0):  # If all rules of castling are observed
                                                            self.attacked_cells[7][2] = 1  # Select castling square
                                            else:  # If you selected black king
                                                if self.castles[2]:  # If b-k castle is available
                                                    if self.pieces[0][4] == "K" and \
                                                            self.pieces[0][5] == "" and \
                                                            self.pieces[0][6] == "" and \
                                                            self.pieces[0][7] == "R":  # If every piece is on its place
                                                        if not self.checks_enabled or \
                                                                (self.attacked_cells_b_white[0][4] + self.attacked_cells_b_white[0][5] == 0):  # If all rules of castling are observed
                                                            self.attacked_cells[0][6] = 1  # Select castling square
                                                if self.castles[3]:  # If b-q castle is available
                                                    if self.pieces[0][4] == "K" and \
                                                            self.pieces[0][3] == "" and \
                                                            self.pieces[0][2] == "" and \
                                                            self.pieces[0][1] == "" and \
                                                            self.pieces[0][0] == "R":  # If every piece is on its place
                                                        if not self.checks_enabled or \
                                                                (self.attacked_cells_b_white[0][4] + self.attacked_cells_b_white[0][3] == 0):  # If all rules of castling are observed
                                                            self.attacked_cells[0][2] = 1  # Select castling square
                                            # In the list of offsets, check if offset cell is valid, and if it is, set value in corresponding cell in attacked cells list to 1
                                            for offset in [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]:
                                                atk_x = self.selected_piece[0] + offset[0]
                                                atk_y = self.selected_piece[1] + offset[1]
                                                is_in_bounds = self.is_in_matrix(atk_x, atk_y, 8, 8)

                                                if is_in_bounds:
                                                    offset_piece = self.pieces[atk_y][atk_x]

                                                    is_free_or_opposite_team = (offset_piece in self.free_spaces) or \
                                                                               (this_piece == this_piece.lower() and offset_piece != offset_piece.lower()) or \
                                                                               (this_piece != this_piece.lower() and offset_piece == offset_piece.lower())

                                                    is_not_check = self.attacked_cells_b_black[atk_y][atk_x] == 0 or not self.checks_enabled \
                                                        if this_piece == this_piece.lower() \
                                                        else self.attacked_cells_b_white[atk_y][atk_x] == 0 or \
                                                             not self.checks_enabled

                                                    if is_free_or_opposite_team and is_not_check:
                                                        self.attacked_cells[atk_y][atk_x] = 1
                                        elif self.selected_piece_type.lower() == "r":  # If a piece type is "r"
                                            # In the list of offsets, check if offset cell is valid, and if it is, set value in corresponding cell in attacked cells list to 1
                                            for step in [[1, 0], [-1, 0], [0, 1], [0, -1]]:  # Go through list of directions
                                                # Renew iteration
                                                offset = step.copy()
                                                atk_x = self.selected_piece[0] + offset[0]
                                                atk_y = self.selected_piece[1] + offset[1]

                                                # Go in that direction until stopped by borders/piece
                                                while self.is_in_matrix(atk_x, atk_y, 8, 8) and \
                                                        (self.pieces[atk_y - step[1]][atk_x - step[0]] in self.free_spaces or
                                                         self.pieces[atk_y - step[1]][atk_x - step[0]] == self.selected_piece_type):
                                                    offset_piece = self.pieces[atk_y][atk_x]

                                                    is_free_or_opposite_team = (offset_piece in self.free_spaces) or \
                                                                               (this_piece == this_piece.lower() and offset_piece != offset_piece.lower()) or \
                                                                               (this_piece != this_piece.lower() and offset_piece == offset_piece.lower())

                                                    if is_free_or_opposite_team:
                                                        self.attacked_cells[atk_y][atk_x] = 1

                                                    # Prepare for next iteration
                                                    offset[0] += step[0]
                                                    offset[1] += step[1]
                                                    atk_x = self.selected_piece[0] + offset[0]
                                                    atk_y = self.selected_piece[1] + offset[1]
                                        elif self.selected_piece_type.lower() == "b":  # If a piece type is "b"
                                            # In the list of offsets, check if offset cell is valid, and if it is, set value in corresponding cell in attacked cells list to 1
                                            for step in [[1, 1], [-1, 1], [-1, -1], [1, -1]]:  # Go through list of directions
                                                # Renew iteration
                                                offset = step.copy()
                                                atk_x = self.selected_piece[0] + offset[0]
                                                atk_y = self.selected_piece[1] + offset[1]

                                                # Go in that direction until stopped by borders/piece
                                                while self.is_in_matrix(atk_x, atk_y, 8, 8) and \
                                                        (self.pieces[atk_y - step[1]][atk_x - step[0]] in self.free_spaces or
                                                         self.pieces[atk_y - step[1]][atk_x - step[0]] == self.selected_piece_type):
                                                    offset_piece = self.pieces[atk_y][atk_x]

                                                    is_free_or_opposite_team = (offset_piece in self.free_spaces) or \
                                                                               (this_piece == this_piece.lower() and offset_piece != offset_piece.lower()) or \
                                                                               (this_piece != this_piece.lower() and offset_piece == offset_piece.lower())

                                                    if is_free_or_opposite_team:
                                                        self.attacked_cells[atk_y][atk_x] = 1

                                                    # Prepare for next iteration
                                                    offset[0] += step[0]
                                                    offset[1] += step[1]
                                                    atk_x = self.selected_piece[0] + offset[0]
                                                    atk_y = self.selected_piece[1] + offset[1]
                                        elif self.selected_piece_type.lower() == "q":  # If a piece type is "q"
                                            # In the list of offsets, check if offset cell is valid, and if it is, set value in corresponding cell in attacked cells list to 1
                                            for step in [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]]:  # Go through list of directions
                                                # Renew iteration
                                                offset = step.copy()
                                                atk_x = self.selected_piece[0] + offset[0]
                                                atk_y = self.selected_piece[1] + offset[1]

                                                # Go in that direction until stopped by borders/piece
                                                while self.is_in_matrix(atk_x, atk_y, 8, 8) and \
                                                        (self.pieces[atk_y - step[1]][atk_x - step[0]] in self.free_spaces or
                                                         self.pieces[atk_y - step[1]][atk_x - step[0]] == self.selected_piece_type):
                                                    offset_piece = self.pieces[atk_y][atk_x]

                                                    is_free_or_opposite_team = (offset_piece in self.free_spaces) or \
                                                                               (this_piece == this_piece.lower() and offset_piece != offset_piece.lower()) or \
                                                                               (this_piece != this_piece.lower() and offset_piece == offset_piece.lower())

                                                    if is_free_or_opposite_team:
                                                        self.attacked_cells[atk_y][atk_x] = 1

                                                    # Prepare for next iteration
                                                    offset[0] += step[0]
                                                    offset[1] += step[1]
                                                    atk_x = self.selected_piece[0] + offset[0]
                                                    atk_y = self.selected_piece[1] + offset[1]

                            else:  # If there is a piece selected
                                clicked_cell = [(e.pos[0] - 100) // 100, (e.pos[1] - 100) // 100]  # Coordinates of the cell clicked
                                if self.attacked_cells[clicked_cell[1]][clicked_cell[0]]:  # If clicked cell is one of the attacked by selected piece

                                    # P.S. WHY ARE PAWNS SO COMPLICATED???????? I SPENT ENTIRE DAY TO JUST CODE THE PAWNS!!!!!!!
                                    if self.selected_piece_type.lower() == "p":  # If this is a pawn
                                        if self.selected_piece_type == "p":  # If this is a white pawn
                                            if self.selected_piece[0] != clicked_cell[0]:  # If you are performing a capture
                                                if clicked_cell[1] == 2:  # If you captured a piece on 3rd rank from black
                                                    if self.pieces[clicked_cell[1]][clicked_cell[0]] == "EP":  # If you are performing an En Passant
                                                        self.pieces[clicked_cell[1] + 1][clicked_cell[0]] = ""  # Remove pawn that was captured via En Passant

                                            # Delete unused En Passant pieces
                                            if "ep" in self.pieces[5]:
                                                for x in range(8):
                                                    if self.pieces[5][x] == "ep":
                                                        self.pieces[5][x] = ""
                                            if "EP" in self.pieces[2]:
                                                for x in range(8):
                                                    if self.pieces[2][x] == "EP":
                                                        self.pieces[2][x] = ""

                                            if self.selected_piece[1] == 6 and clicked_cell[1] == 4 and self.en_passant_enabled:  # If you are performing double move and En Passant is enabled
                                                self.pieces[5][self.selected_piece[0]] = "ep"  # Place an En Passant piece

                                        else:  # If this is a black pawn
                                            if self.selected_piece[0] != clicked_cell[0]:  # If you are performing a capture
                                                if clicked_cell[1] == 5:  # If you captured a piece on 3rd rank from black
                                                    if self.pieces[clicked_cell[1]][clicked_cell[0]] == "ep":  # If you are performing an En Passant
                                                        self.pieces[clicked_cell[1] - 1][clicked_cell[0]] = ""  # Remove pawn that was captured via En Passant

                                            # Delete unused En Passant pieces
                                            if "ep" in self.pieces[5]:
                                                for x in range(8):
                                                    if self.pieces[5][x] == "ep":
                                                        self.pieces[5][x] = ""
                                            if "EP" in self.pieces[2]:
                                                for x in range(8):
                                                    if self.pieces[2][x] == "EP":
                                                        self.pieces[2][x] = ""

                                            if self.selected_piece[1] == 1 and clicked_cell[1] == 3 and self.en_passant_enabled:  # If you are performing double move and En Passant is enabled
                                                self.pieces[2][self.selected_piece[0]] = "EP"  # Place an En Passant piece
                                    else:  # If you moved any other piece
                                        # Delete unused En Passant pieces
                                        if "ep" in self.pieces[5]:
                                            for x in range(8):
                                                if self.pieces[5][x] == "ep":
                                                    self.pieces[5][x] = ""
                                        if "EP" in self.pieces[2]:
                                            for x in range(8):
                                                if self.pieces[2][x] == "EP":
                                                    self.pieces[2][x] = ""

                                    # Checking if player castled
                                    castles_ = [False, False, False, False]
                                    if self.selected_piece_type.lower() == "k":  # If you moved a king
                                        if self.selected_piece_type == "k":  # If you moved white king
                                            if self.selected_piece[0] == 4 and clicked_cell[0] == 6:  # If this is a castle kingside
                                                castles_[0] = True
                                            elif self.selected_piece[0] == 4 and clicked_cell[0] == 2:  # If this is a castle queenside
                                                castles_[1] = True
                                        else:  # If you moved black king
                                            if self.selected_piece[0] == 4 and clicked_cell[0] == 6:  # If this is a castle kingside
                                                castles_[2] = True
                                            elif self.selected_piece[0] == 4 and clicked_cell[0] == 2:  # If this is a castle queenside
                                                castles_[3] = True

                                    self.moves_history.append([
                                        [self.pieces[i].copy() for i in range(8)],
                                        self.white_turn,
                                        self.castles.copy(),
                                        [self.attacked_cells_b_white[i].copy() for i in range(8)],
                                        [self.attacked_cells_b_black[i].copy() for i in range(8)]
                                    ])  # Write board to history of moves
                                    self.pieces[clicked_cell[1]][clicked_cell[0]] = self.pieces[self.selected_piece[1]][self.selected_piece[0]]
                                    self.pieces[self.selected_piece[1]][self.selected_piece[0]] = ""  # Transfer current piece and capture the piece that was on that square

                                    if castles_[0]:
                                        self.pieces[7][7] = ""
                                        self.pieces[7][5] = "r"
                                    if castles_[1]:
                                        self.pieces[7][0] = ""
                                        self.pieces[7][3] = "r"
                                    if castles_[2]:
                                        self.pieces[0][7] = ""
                                        self.pieces[0][5] = "R"
                                    if castles_[3]:
                                        self.pieces[0][0] = ""
                                        self.pieces[0][3] = "R"

                                    # Promoting a pawn
                                    if self.selected_piece_type.lower() == "p":
                                        if self.selected_piece_type == "p":
                                            if clicked_cell[1] == 0:
                                                self.pieces[clicked_cell[1]][clicked_cell[0]] = self.piece_to_promote
                                        elif self.selected_piece_type == "P":
                                            if clicked_cell[1] == 7:
                                                self.pieces[clicked_cell[1]][clicked_cell[0]] = self.piece_to_promote.upper()

                                    # Checking for lost castling options
                                    if self.selected_piece_type == "k":
                                        self.castles[:2] = [False, False]
                                    elif self.selected_piece_type == "K":
                                        self.castles[2:] = [False, False]
                                    elif self.selected_piece_type == "r":
                                        if self.selected_piece[0] == 0:
                                            self.castles[1] = False
                                        elif self.selected_piece[0] == 7:
                                            self.castles[0] = False
                                    elif self.selected_piece_type == "R":
                                        if self.selected_piece[0] == 0:
                                            self.castles[3] = False
                                        elif self.selected_piece[0] == 7:
                                            self.castles[2] = False

                                    # If players take turns, give a turn to opponent
                                    if self.take_turns:
                                        self.white_turn = not self.white_turn

                                # Reset selected piece
                                self.attacked_cells = [[0 for x in range(8)] for y in range(8)]
                                self.selected_piece = [None, None]
                                self.selected_piece_type = None

                                # Renew lists of attacked cells
                                self.attacked_cells_b_white = [[0 for x in range(8)] for y in range(8)]
                                self.attacked_cells_b_black = [[0 for x in range(8)] for y in range(8)]

                                for x in range(8):  # Check every square on the board to mark cells attacked by that square
                                    for y in range(8):
                                        if self.pieces[y][x] not in self.free_spaces:  # If this is not free space
                                            is_white = self.pieces[y][x] == self.pieces[y][x].lower()

                                            if self.pieces[y][x].lower() == "p":  # If this is a pawn
                                                if is_white:  # If this is a white pawn
                                                    if x > 0:
                                                        self.attacked_cells_b_white[y - 1][x - 1] = 1
                                                    if x < 7:
                                                        self.attacked_cells_b_white[y - 1][x + 1] = 1
                                                else:  # If this is a black pawn
                                                    if x > 0:
                                                        self.attacked_cells_b_black[y + 1][x - 1] = 1
                                                    if x < 7:
                                                        self.attacked_cells_b_black[y + 1][x + 1] = 1

                                            elif self.pieces[y][x].lower() == "n":  # If this is a knight, also, you can copy and paste this segment to make new pieces
                                                for offset in [[-2, -1], [-1, -2], [1, -2], [2, -1], [2, 1], [1, 2], [-1, 2], [-2, 1]]:
                                                    if self.is_in_matrix(x + offset[0], y + offset[1], 8, 8):
                                                        if is_white:
                                                            self.attacked_cells_b_white[y + offset[1]][x + offset[0]] = 1
                                                        else:
                                                            self.attacked_cells_b_black[y + offset[1]][x + offset[0]] = 1
                                            elif self.pieces[y][x].lower() == "k":  # If this is a king
                                                for offset in [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]:
                                                    if self.is_in_matrix(x + offset[0], y + offset[1], 8, 8):
                                                        if is_white:
                                                            self.attacked_cells_b_white[y + offset[1]][x + offset[0]] = 1
                                                        else:
                                                            self.attacked_cells_b_black[y + offset[1]][x + offset[0]] = 1
                                            elif self.pieces[y][x].lower() == "q":  # If this is a queen
                                                # In the list of offsets, check if offset cell is valid, and if it is, set value in corresponding cell in attacked cells list to 1
                                                for step in [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]]:  # Go through list of directions
                                                    # Renew iteration
                                                    offset = step.copy()
                                                    atk_x = x + offset[0]
                                                    atk_y = y + offset[1]

                                                    # Go in that direction until stopped by borders/piece
                                                    while self.is_in_matrix(atk_x, atk_y, 8, 8) and \
                                                            (self.pieces[atk_y - step[1]][atk_x - step[0]] in self.free_spaces or
                                                             self.pieces[atk_y - step[1]][atk_x - step[0]] == self.pieces[y][x] or
                                                             (self.pieces[atk_y - step[1]][atk_x - step[0]] == "k" and not is_white) or
                                                             (self.pieces[atk_y - step[1]][atk_x - step[0]] == "K" and is_white)):
                                                        offset_piece = self.pieces[atk_y][atk_x]

                                                        if is_white:
                                                            self.attacked_cells_b_white[y + offset[1]][x + offset[0]] = 1
                                                        else:
                                                            self.attacked_cells_b_black[y + offset[1]][x + offset[0]] = 1

                                                        # Prepare for next iteration
                                                        offset[0] += step[0]
                                                        offset[1] += step[1]
                                                        atk_x = x + offset[0]
                                                        atk_y = y + offset[1]
                                            elif self.pieces[y][x].lower() == "r":  # If this is a queen
                                                # In the list of offsets, check if offset cell is valid, and if it is, set value in corresponding cell in attacked cells list to 1
                                                for step in [[1, 0], [-1, 0], [0, 1], [0, -1]]:  # Go through list of directions
                                                    # Renew iteration
                                                    offset = step.copy()
                                                    atk_x = x + offset[0]
                                                    atk_y = y + offset[1]

                                                    # Go in that direction until stopped by borders/piece
                                                    while self.is_in_matrix(atk_x, atk_y, 8, 8) and \
                                                            (self.pieces[atk_y - step[1]][atk_x - step[0]] in self.free_spaces or
                                                             self.pieces[atk_y - step[1]][atk_x - step[0]] == self.pieces[y][x] or
                                                             (self.pieces[atk_y - step[1]][atk_x - step[0]] == "k" and not is_white) or
                                                             (self.pieces[atk_y - step[1]][atk_x - step[0]] == "K" and is_white)):
                                                        offset_piece = self.pieces[atk_y][atk_x]

                                                        if is_white:
                                                            self.attacked_cells_b_white[y + offset[1]][x + offset[0]] = 1
                                                        else:
                                                            self.attacked_cells_b_black[y + offset[1]][x + offset[0]] = 1

                                                        # Prepare for next iteration
                                                        offset[0] += step[0]
                                                        offset[1] += step[1]
                                                        atk_x = x + offset[0]
                                                        atk_y = y + offset[1]
                                            elif self.pieces[y][x].lower() == "b":  # If this is a queen
                                                # In the list of offsets, check if offset cell is valid, and if it is, set value in corresponding cell in attacked cells list to 1
                                                for step in [[1, 1], [-1, 1], [-1, -1], [1, -1]]:  # Go through list of directions
                                                    # Renew iteration
                                                    offset = step.copy()
                                                    atk_x = x + offset[0]
                                                    atk_y = y + offset[1]

                                                    # Go in that direction until stopped by borders/piece
                                                    while self.is_in_matrix(atk_x, atk_y, 8, 8) and \
                                                            (self.pieces[atk_y - step[1]][atk_x - step[0]] in self.free_spaces or
                                                             self.pieces[atk_y - step[1]][atk_x - step[0]] == self.pieces[y][x] or
                                                             (self.pieces[atk_y - step[1]][atk_x - step[0]] == "k" and not is_white) or
                                                             (self.pieces[atk_y - step[1]][atk_x - step[0]] == "K" and is_white)):
                                                        offset_piece = self.pieces[atk_y][atk_x]

                                                        if is_white:
                                                            self.attacked_cells_b_white[y + offset[1]][x + offset[0]] = 1
                                                        else:
                                                            self.attacked_cells_b_black[y + offset[1]][x + offset[0]] = 1

                                                        # Prepare for next iteration
                                                        offset[0] += step[0]
                                                        offset[1] += step[1]
                                                        atk_x = x + offset[0]
                                                        atk_y = y + offset[1]

                                # Check if this move puts you in check and checks are enabled, also if taking turns is enabled
                                if self.take_turns and self.checks_enabled:
                                    for x in range(8):
                                        for y in range(8):
                                            if self.pieces[y][x] == "K" and self.attacked_cells_b_white[y][x] and self.white_turn:  # If black made a turn that put them in check
                                                self.undo()

                                            if self.pieces[y][x] == "k" and self.attacked_cells_b_black[y][x] and not self.white_turn:  # If white made a turn that put them in check
                                                self.undo()

                        else:  # If click is out of board bounds
                            if self.is_in_matrix(e.pos[0] - 940, e.pos[1] - 90, 70, 70):  # If click in bounds of undo button
                                self.undo()
                            elif self.is_in_matrix(e.pos[0] - 950, e.pos[1] - 200, 50, 50):  # If click in bounds of turn switch button
                                self.white_turn = not self.white_turn
                            elif self.is_in_matrix(e.pos[0] - 950, e.pos[1] - 300, 50, 50):  # If click in bounds of take turns switch button
                                self.take_turns = not self.take_turns
                            elif self.is_in_matrix(e.pos[0] - 940, e.pos[1] - 390, 70, 70):  # If click in bounds of piece to promote switch button
                                self.piece_to_promote = self.promote_piece_cycle[self.piece_to_promote]
                            elif self.is_in_matrix(e.pos[0] - 950, e.pos[1] - 500, 50, 50):  # If click in bounds of En Passant visibility switch button
                                self.see_en_passant = not self.see_en_passant
                            elif self.is_in_matrix(e.pos[0] - 950, e.pos[1] - 600, 50, 50):  # If click in bounds of En Passant switch button
                                self.en_passant_enabled = not self.en_passant_enabled
                            elif self.is_in_matrix(e.pos[0] - 950, e.pos[1] - 700, 50, 50):  # If click in bounds of check switch button
                                self.checks_enabled = not self.checks_enabled
                            elif self.is_in_matrix(e.pos[0] - 940, e.pos[1] - 790, 70, 70):  # If click in bounds of reset button
                                self.pieces = [
                                    ["R", "N", "B", "Q", "K", "B", "N", "R"],
                                    ["P", "P", "P", "P", "P", "P", "P", "P"],
                                    ["", "", "", "", "", "", "", ""],
                                    ["", "", "", "", "", "", "", ""],
                                    ["", "", "", "", "", "", "", ""],
                                    ["", "", "", "", "", "", "", ""],
                                    ["p", "p", "p", "p", "p", "p", "p", "p"],
                                    ["r", "n", "b", "q", "k", "b", "n", "r"],
                                ]

                                # Reset selected piece
                                self.attacked_cells = [[0 for x in range(8)] for y in range(8)]
                                self.selected_piece = [None, None]
                                self.selected_piece_type = None
                                self.white_turn = True
                                self.castles = [True, True, True, True]

                                # Renew lists of attacked cells
                                self.attacked_cells_b_white = [[0 for x in range(8)] for y in range(8)]
                                self.attacked_cells_b_black = [[0 for x in range(8)] for y in range(8)]
                            elif self.is_in_matrix(e.pos[0] - 1450, e.pos[1], 50, 50):  # If click in bounds of quit button
                                sys.exit()

            # Board rectangle, then loop drawing black squares
            pg.draw.rect(self.dis, (200, 200, 200), (100, 100, 800, 800))
            if self.take_turns:
                pg.draw.rect(self.dis, (0, 0, 0), (80, 80, 840, 840), 20)
                pg.draw.rect(self.dis, (self.white_turn * 255, self.white_turn * 255, self.white_turn * 255), (90, 90, 820, 820), 10)
            else:
                pg.draw.rect(self.dis, (0, 0, 0), (90, 90, 820, 820), 10)

            for x in range(0, 800, 100):
                for y in range(0, 800, 100):
                    if (x / 100) % 2 != (y / 100) % 2:
                        pg.draw.rect(self.dis, (60, 60, 60), (x + 100, y + 100, 100, 100))

            # Drawing check effect
            for x in range(8):
                for y in range(8):
                    if self.pieces[y][x] == "K" and self.attacked_cells_b_white[y][x]:  # If black king is in check
                        pg.draw.rect(self.dis, (255, 0, 0), (100 + x * 100, 100 + y * 100, 100, 100))

                    if self.pieces[y][x] == "k" and self.attacked_cells_b_black[y][x]:  # If white king is in check
                        pg.draw.rect(self.dis, (255, 0, 0), (100 + x * 100, 100 + y * 100, 100, 100))

            # Drawing pieces
            for x in range(8):
                for y in range(8):
                    # Offsets to make piece stand in its place
                    x_offset = 100 + x * 100
                    y_offset = 100 + y * 100

                    # A debugging tool that draw available En Passants
                    if self.see_en_passant:
                        if self.pieces[y][x] == "ep":
                            pg.draw.polygon(self.dis, (255, 255, 255), ((50 + x_offset, 25 + y_offset), (75 + x_offset, 50 + y_offset),
                                                                        (50 + x_offset, 75 + y_offset), (25 + x_offset, 50 + y_offset)))
                        if self.pieces[y][x] == "EP":
                            pg.draw.polygon(self.dis, (0, 0, 0), ((50 + x_offset, 25 + y_offset), (75 + x_offset, 50 + y_offset),
                                                                  (50 + x_offset, 75 + y_offset), (25 + x_offset, 50 + y_offset)))
                    # {}

                    # Draw piece
                    if self.pieces[y][x].lower() == "p":  # If piece type = p (in this case, pawn)
                        if self.pieces[y][x] == "p":  # If this piece is white
                            # Entire drawing procedure
                            pg.draw.polygon(self.dis, (255, 255, 255), (
                                (20 + x_offset, 85 + y_offset), (80 + x_offset, 85 + y_offset), (50 + x_offset, 25 + y_offset)
                            ))
                            pg.draw.circle(self.dis, (255, 255, 255), (50 + x_offset, 30 + y_offset), 15)
                        else:  # If this piece is black
                            # Entire drawing procedure but with black color
                            pg.draw.polygon(self.dis, (0, 0, 0), (
                                (20 + x_offset, 85 + y_offset), (80 + x_offset, 85 + y_offset), (50 + x_offset, 25 + y_offset)
                            ))
                            pg.draw.circle(self.dis, (0, 0, 0), (50 + x_offset, 30 + y_offset), 15)
                    # Now, just copy and paste this with "elif" instead of "if", and new drawing procedure
                    elif self.pieces[y][x].lower() == "r":  # If piece type = r (in this case, rook)
                        if self.pieces[y][x] == "r":  # If this piece is white
                            # Entire drawing procedure
                            pg.draw.polygon(self.dis, (255, 255, 255), (
                                (30 + x_offset, 15 + y_offset),
                                (38 + x_offset, 15 + y_offset),
                                (38 + x_offset, 20 + y_offset),
                                (46 + x_offset, 20 + y_offset),
                                (46 + x_offset, 15 + y_offset),
                                (54 + x_offset, 15 + y_offset),
                                (54 + x_offset, 20 + y_offset),
                                (62 + x_offset, 20 + y_offset),
                                (62 + x_offset, 15 + y_offset),
                                (70 + x_offset, 15 + y_offset),
                                (70 + x_offset, 40 + y_offset),
                                (65 + x_offset, 40 + y_offset),
                                (70 + x_offset, 75 + y_offset),
                                (80 + x_offset, 85 + y_offset),
                                (20 + x_offset, 85 + y_offset),
                                (30 + x_offset, 75 + y_offset),
                                (35 + x_offset, 40 + y_offset),
                                (30 + x_offset, 40 + y_offset)
                            ))
                        else:  # If this piece is black
                            # Entire drawing procedure but with black color
                            pg.draw.polygon(self.dis, (0, 0, 0), (
                                (30 + x_offset, 15 + y_offset),
                                (38 + x_offset, 15 + y_offset),
                                (38 + x_offset, 20 + y_offset),
                                (46 + x_offset, 20 + y_offset),
                                (46 + x_offset, 15 + y_offset),
                                (54 + x_offset, 15 + y_offset),
                                (54 + x_offset, 20 + y_offset),
                                (62 + x_offset, 20 + y_offset),
                                (62 + x_offset, 15 + y_offset),
                                (70 + x_offset, 15 + y_offset),
                                (70 + x_offset, 40 + y_offset),
                                (65 + x_offset, 40 + y_offset),
                                (70 + x_offset, 75 + y_offset),
                                (80 + x_offset, 85 + y_offset),
                                (20 + x_offset, 85 + y_offset),
                                (30 + x_offset, 75 + y_offset),
                                (35 + x_offset, 40 + y_offset),
                                (30 + x_offset, 40 + y_offset)
                            ))
                    elif self.pieces[y][x].lower() == "b":  # If piece type = b (in this case, bishop)
                        if self.pieces[y][x] == "b":  # If this piece is white
                            # Entire drawing procedure, and also here I use "x % 2 == y % 2" to detect if piece stands on black square, False = black and True = white
                            pg.draw.polygon(self.dis, (255, 255, 255), (
                                (20 + x_offset, 85 + y_offset), (80 + x_offset, 85 + y_offset), (50 + x_offset, 25 + y_offset)
                            ))
                            pg.draw.circle(self.dis, (255, 255, 255), (50 + x_offset, 40 + y_offset), 20)

                            cell_color = 60 + 140 * (x % 2 == y % 2)
                            pg.draw.polygon(self.dis, (cell_color, cell_color, cell_color), (
                                (40 + x_offset, 20 + y_offset), (30 + x_offset, 30 + y_offset), (50 + x_offset, 40 + y_offset)
                            ))
                        else:  # If this piece is black
                            # Entire drawing procedure but with black color
                            pg.draw.polygon(self.dis, (0, 0, 0), (
                                (20 + x_offset, 85 + y_offset), (80 + x_offset, 85 + y_offset), (50 + x_offset, 25 + y_offset)
                            ))
                            pg.draw.circle(self.dis, (0, 0, 0), (50 + x_offset, 40 + y_offset), 20)

                            cell_color = 60 + 140 * (x % 2 == y % 2)
                            pg.draw.polygon(self.dis, (cell_color, cell_color, cell_color), (
                                (40 + x_offset, 20 + y_offset), (30 + x_offset, 30 + y_offset), (50 + x_offset, 40 + y_offset)
                            ))
                    elif self.pieces[y][x].lower() == "n":  # If piece type = n (in this case, knight)
                        quality = 25  # Just a quality of curves
                        if self.pieces[y][x] == "n":  # If this piece is white
                            # Entire drawing procedure, and also here I use Bézier curves to accurately make knights
                            c1 = [[self.tlerp(43, 70, 82, 79, i / quality) + x_offset, self.tlerp(17, 16, 35, 85, i / quality) + y_offset] for i in range(quality + 1)]  # Curve №1
                            c2 = [[self.tlerp(35, 35, 51, 52, i / quality) + x_offset, self.tlerp(85, 64, 58, 43, i / quality) + y_offset] for i in range(quality + 1)]  # Curve №2
                            c3 = [[self.tlerp(31, 8, 32, 43, i / quality) + x_offset, self.tlerp(56, 52, 26, 17, i / quality) + y_offset] for i in range(quality + 1)]  # Curve №3

                            pg.draw.polygon(self.dis, (255, 255, 255), c1 + c2 + [[34 + x_offset, 58 + y_offset]] + c3)
                            pg.draw.circle(self.dis, (255, 255, 255), (43 + x_offset, 17 + y_offset), 4)
                            pg.draw.circle(self.dis, (255, 255, 255), (51 + x_offset, 17 + y_offset), 4)

                            pg.draw.circle(self.dis, (0, 0, 0), (41 + x_offset, 29 + y_offset), 3)
                            pg.draw.circle(self.dis, (0, 0, 0), (25 + x_offset, 46 + y_offset), 2)
                        else:  # If this piece is black
                            # Entire drawing procedure but with black color
                            c1 = [[self.tlerp(43, 70, 82, 79, i / quality) + x_offset, self.tlerp(17, 16, 35, 83, i / quality) + y_offset] for i in range(quality + 1)]  # Curve №1
                            c2 = [[self.tlerp(35, 35, 51, 52, i / quality) + x_offset, self.tlerp(83, 64, 58, 43, i / quality) + y_offset] for i in range(quality + 1)]  # Curve №2
                            c3 = [[self.tlerp(31, 8, 32, 43, i / quality) + x_offset, self.tlerp(56, 52, 26, 17, i / quality) + y_offset] for i in range(quality + 1)]  # Curve №3

                            pg.draw.polygon(self.dis, (0, 0, 0), c1 + c2 + [[34 + x_offset, 58 + y_offset]] + c3)
                            pg.draw.circle(self.dis, (0, 0, 0), (43 + x_offset, 17 + y_offset), 4)
                            pg.draw.circle(self.dis, (0, 0, 0), (51 + x_offset, 17 + y_offset), 4)

                            pg.draw.circle(self.dis, (255, 255, 255), (41 + x_offset, 29 + y_offset), 3)
                            pg.draw.circle(self.dis, (255, 255, 255), (25 + x_offset, 46 + y_offset), 2)
                    elif self.pieces[y][x].lower() == "q":  # If piece type = q (in this case, queen)
                        if self.pieces[y][x] == "q":  # If this piece is white
                            # Entire drawing procedure
                            pg.draw.polygon(self.dis, (255, 255, 255), (
                                [20 + x_offset, 85 + y_offset],
                                [80 + x_offset, 85 + y_offset],
                                [90 + x_offset, 30 + y_offset],
                                [75 + x_offset, 63 + y_offset],
                                [70 + x_offset, 22 + y_offset],
                                [60 + x_offset, 60 + y_offset],
                                [50 + x_offset, 20 + y_offset],
                                [40 + x_offset, 60 + y_offset],
                                [30 + x_offset, 22 + y_offset],
                                [25 + x_offset, 63 + y_offset],
                                [10 + x_offset, 30 + y_offset]
                            ))
                            pg.draw.circle(self.dis, (255, 255, 255), [90 + x_offset, 30 + y_offset], 4)
                            pg.draw.circle(self.dis, (255, 255, 255), [70 + x_offset, 22 + y_offset], 4)
                            pg.draw.circle(self.dis, (255, 255, 255), [50 + x_offset, 20 + y_offset], 4)
                            pg.draw.circle(self.dis, (255, 255, 255), [30 + x_offset, 22 + y_offset], 4)
                            pg.draw.circle(self.dis, (255, 255, 255), [10 + x_offset, 30 + y_offset], 4)
                        else:  # If this piece is black
                            # Entire drawing procedure but with black color
                            pg.draw.polygon(self.dis, (0, 0, 0), (
                                [20 + x_offset, 85 + y_offset],
                                [80 + x_offset, 85 + y_offset],
                                [90 + x_offset, 30 + y_offset],
                                [75 + x_offset, 63 + y_offset],
                                [70 + x_offset, 22 + y_offset],
                                [60 + x_offset, 60 + y_offset],
                                [50 + x_offset, 20 + y_offset],
                                [40 + x_offset, 60 + y_offset],
                                [30 + x_offset, 22 + y_offset],
                                [25 + x_offset, 63 + y_offset],
                                [10 + x_offset, 30 + y_offset]
                            ))
                            pg.draw.circle(self.dis, (0, 0, 0), [90 + x_offset, 30 + y_offset], 4)
                            pg.draw.circle(self.dis, (0, 0, 0), [70 + x_offset, 22 + y_offset], 4)
                            pg.draw.circle(self.dis, (0, 0, 0), [50 + x_offset, 20 + y_offset], 4)
                            pg.draw.circle(self.dis, (0, 0, 0), [30 + x_offset, 22 + y_offset], 4)
                            pg.draw.circle(self.dis, (0, 0, 0), [10 + x_offset, 30 + y_offset], 4)
                    elif self.pieces[y][x].lower() == "k":  # If piece type = k (in this case, king)
                        if self.pieces[y][x] == "k":  # If this piece is white
                            # Entire drawing procedure
                            pg.draw.polygon(self.dis, (255, 255, 255), (
                                (20 + x_offset, 85 + y_offset), (80 + x_offset, 85 + y_offset), (70 + x_offset, 50 + y_offset), (30 + x_offset, 50 + y_offset)
                            ))
                            pg.draw.circle(self.dis, (255, 255, 255), (70 + x_offset, 50 + y_offset), 20)
                            pg.draw.circle(self.dis, (255, 255, 255), (30 + x_offset, 50 + y_offset), 20)
                            pg.draw.circle(self.dis, (255, 255, 255), (50 + x_offset, 40 + y_offset), 20)
                            pg.draw.line(self.dis, (255, 255, 255), (50 + x_offset, 50 + y_offset), (50 + x_offset, 10 + y_offset), 3)
                            pg.draw.line(self.dis, (255, 255, 255), (45 + x_offset, 15 + y_offset), (55 + x_offset, 15 + y_offset), 3)
                        else:  # If this piece is black
                            # Entire drawing procedure but with black color
                            pg.draw.polygon(self.dis, (0, 0, 0), (
                                (20 + x_offset, 85 + y_offset), (80 + x_offset, 85 + y_offset), (70 + x_offset, 50 + y_offset), (30 + x_offset, 50 + y_offset)
                            ))
                            pg.draw.circle(self.dis, (0, 0, 0), (70 + x_offset, 50 + y_offset), 20)
                            pg.draw.circle(self.dis, (0, 0, 0), (30 + x_offset, 50 + y_offset), 20)
                            pg.draw.circle(self.dis, (0, 0, 0), (50 + x_offset, 40 + y_offset), 20)
                            pg.draw.line(self.dis, (0, 0, 0), (50 + x_offset, 50 + y_offset), (50 + x_offset, 10 + y_offset), 3)
                            pg.draw.line(self.dis, (0, 0, 0), (45 + x_offset, 15 + y_offset), (55 + x_offset, 15 + y_offset), 3)

            # Draw a circle that shows what piece is selected
            if self.selected_piece != [None, None]:
                pg.draw.circle(self.dis, (100, 100, 255), (150 + self.selected_piece[0] * 100, 150 + self.selected_piece[1] * 100), 40, 5)

            # Draw circles that show which cells are attacked by selected piece
            for x in range(8):
                for y in range(8):
                    if self.attacked_cells[y][x]:
                        pg.draw.circle(self.dis, (150, 150, 255), (150 + x * 100, 150 + y * 100), 25, 4)

            # Draw extra tools

            # Undo button
            pg.draw.rect(self.dis, (0, 0, 0), (940, 90, 70, 70))
            pg.draw.rect(self.dis, (255, 255, 255), (960, 110, 30, 30))
            self.dis.blit(self.main_font.render("Undo", False, (0, 0, 0)), (1025, 80))
            #

            # Turn switcher
            if self.take_turns:
                pg.draw.rect(self.dis, (0, 0, 0), (940, 190, 70, 70))
                pg.draw.rect(self.dis, (self.white_turn * 255, self.white_turn * 255, self.white_turn * 255), (950, 200, 50, 50))
            else:
                pg.draw.rect(self.dis, (0, 0, 0), (950, 200, 50, 50))
            self.dis.blit(self.main_font.render("Turn", False, (0, 0, 0)), (1025, 180))
            #

            # Taking turns switcher
            pg.draw.rect(self.dis, (0, 0, 0), (940, 290, 70, 70))
            pg.draw.rect(self.dis, (255 - self.take_turns * 255, 255 - self.take_turns * 255, 255 - self.take_turns * 255), (950, 300, 50, 50))
            if self.take_turns:
                pg.draw.polygon(self.dis, (255, 255, 255), self.checkmark_at_pos(975, 325))
            self.dis.blit(self.main_font.render("Take turns", False, (0, 0, 0)), (1025, 280))
            #

            # Promoting piece switch
            pg.draw.rect(self.dis, (0, 0, 0), (940, 390, 70, 70))
            pg.draw.rect(self.dis, (255, 255, 255), (960, 410, 30, 30))
            self.dis.blit(self.main_font_s.render("Pawns promote to", False, (0, 0, 0)), (1025, 380))
            self.dis.blit(self.main_font_s.render(self.promoting_piece_text[self.piece_to_promote], False, (0, 0, 0)), (1025, 430))
            #

            # En Passant visibility switch
            if self.en_passant_enabled:
                pg.draw.rect(self.dis, (0, 0, 0), (940, 490, 70, 70))
                pg.draw.rect(self.dis, (255 - self.see_en_passant * 255, 255 - self.see_en_passant * 255, 255 - self.see_en_passant * 255), (950, 500, 50, 50))
                pg.draw.polygon(self.dis, (255, 255, 255), self.checkmark_at_pos(975, 525))
            else:
                pg.draw.rect(self.dis, (0, 0, 0), (950, 500, 50, 50))
            self.dis.blit(self.main_font_s.render("En Passant visible", False, (0, 0, 0)), (1025, 505))
            #

            # En Passant switch
            pg.draw.rect(self.dis, (0, 0, 0), (940, 590, 70, 70))
            pg.draw.rect(self.dis, (255 - self.en_passant_enabled * 255, 255 - self.en_passant_enabled * 255, 255 - self.en_passant_enabled * 255), (950, 600, 50, 50))
            if self.en_passant_enabled:
                pg.draw.polygon(self.dis, (255, 255, 255), self.checkmark_at_pos(975, 625))
            self.dis.blit(self.main_font_s.render("En Passant enabled", False, (0, 0, 0)), (1025, 605))
            #

            # Checks switch
            pg.draw.rect(self.dis, (0, 0, 0), (940, 690, 70, 70))
            pg.draw.rect(self.dis, (255 - self.checks_enabled * 255, 255 - self.checks_enabled * 255, 255 - self.checks_enabled * 255), (950, 700, 50, 50))
            if self.checks_enabled:
                pg.draw.polygon(self.dis, (255, 255, 255), self.checkmark_at_pos(975, 725))
            self.dis.blit(self.main_font.render("Checks", False, (0, 0, 0)), (1025, 680))
            #

            # Reset button
            pg.draw.rect(self.dis, (0, 0, 0), (940, 790, 70, 70))
            pg.draw.rect(self.dis, (255, 255, 255), (960, 810, 30, 30))
            self.dis.blit(self.main_font.render("Reset", False, (0, 0, 0)), (1025, 780))
            #

            # Quit button
            pg.draw.rect(self.dis, (255, 0, 0), (1450, 0, 50, 50))
            pg.draw.line(self.dis, (0, 0, 0), (1465, 10), (1485, 40), 15)
            pg.draw.line(self.dis, (0, 0, 0), (1485, 10), (1465, 40), 15)
            #

            self.clock.tick(self.fps)
            pg.display.set_caption(f"Chess Unbound | FPS:{self.clock.get_fps():.2f}")
            pg.display.flip()

    # Lerp function
    def lerp(self, x, y, t):
        return (1 - t) * x + t * y

    # Double lerp function (can be used to make Quadratic Bézier curves)
    def dlerp(self, x, y, z, t):
        return self.lerp(self.lerp(x, y, t), self.lerp(y, z, t), t)

    # Triple lerp function (can be used to make Qubic Bézier curves)
    def tlerp(self, x, y, z, w, t):
        return self.lerp(self.dlerp(x, y, z, t), self.dlerp(y, z, w, t), t)

    # Function that checks if the X and Y coordinates are in box of width of W and height of H
    def is_in_matrix(self, x, y, w, h):
        return 0 <= x < w and 0 <= y < h

    def checkmark_at_pos(self, x, y):
        return [[x, y - 5], [x + 10, y - 15], [x + 20, y - 5], [x, y + 15], [x - 20, y - 5], [x - 10, y - 15]]

    def undo(self):
        if self.moves_history:
            self.pieces = self.moves_history[-1][0].copy()
            self.white_turn = self.moves_history[-1][1]
            self.castles = self.moves_history[-1][2].copy()
            self.attacked_cells_b_white = self.moves_history[-1][3].copy()
            self.attacked_cells_b_black = self.moves_history[-1][4].copy()
            self.moves_history.pop()


game = Game(1500, 1000, 60)
game.run()

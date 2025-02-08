class DejarikPiece:
    def __init__(self, name, attack, health, move_range, player):
        self.name = name
        self.attack = attack
        self.health = health
        self.move_range = move_range
        self.player = player

class DejarikBoard:
    def __init__(self):
        # 25 positions: A1 (center) + B1-B12 (middle ring) + C1-C12 (outer ring)
        self.spaces = [None] * 25
        self.setup_pieces()

    def setup_pieces(self):
        # Player 1 pieces (B positions)
        self.spaces[1] = DejarikPiece("Savrip", 6, 6, 2, 1)
        self.spaces[3] = DejarikPiece("Monnok", 6, 5, 3, 1)
        self.spaces[5] = DejarikPiece("Ghhhk", 4, 3, 2, 1)
        self.spaces[7] = DejarikPiece("Houjix", 4, 4, 1, 1)

        # Player 2 pieces (C positions)
        self.spaces[13] = DejarikPiece("Strider", 2, 7, 3, 2)
        self.spaces[15] = DejarikPiece("Ng'ok", 3, 8, 1, 2)
        self.spaces[17] = DejarikPiece("K'lor'slug", 7, 3, 2, 2)
        self.spaces[19] = DejarikPiece("Molator", 8, 2, 2, 2)

    def is_valid_move(self, from_pos, to_pos, current_player):
        if not (0 <= from_pos < 25 and 0 <= to_pos < 25):
            return False
        
        piece = self.spaces[from_pos]
        if piece is None or piece.player != current_player:
            return False

        # Calculate ring distances and valid movements
        from_ring = 'A' if from_pos == 0 else 'B' if from_pos < 13 else 'C'
        to_ring = 'A' if to_pos == 0 else 'B' if to_pos < 13 else 'C'
        
        # Special center position rules
        if from_ring == 'A' or to_ring == 'A':
            return piece.move_range >= 1 and (self.spaces[to_pos] is None or 
                                            self.spaces[to_pos].player != current_player)

        # Calculate circular distance within rings
        from_pos_adj = from_pos if from_pos < 13 else from_pos - 12
        to_pos_adj = to_pos if to_pos < 13 else to_pos - 12
        distance = min(abs(to_pos_adj - from_pos_adj), 12 - abs(to_pos_adj - from_pos_adj))
        
        # Add 1 to distance if changing rings
        if from_ring != to_ring:
            distance += 1

        return distance <= piece.move_range and (self.spaces[to_pos] is None or 
                                               self.spaces[to_pos].player != current_player)

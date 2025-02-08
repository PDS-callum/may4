import tkinter as tk
import math
from game import DejarikBoard

class DejarikGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dejarik")
        
        self.board = DejarikBoard()
        self.current_player = 1
        self.selected_piece = None
        
        self.canvas = tk.Canvas(self.root, width=600, height=600, bg='black')
        self.canvas.pack(pady=20)
        
        self.status_label = tk.Label(self.root, text=f"Player {self.current_player}'s turn")
        self.status_label.pack()
        
        self.canvas.bind('<Button-1>', self.handle_click)
        self.tooltip_window = None
        self.canvas.bind('<Motion>', self.show_piece_info)
        self.canvas.bind('<Leave>', self.hide_piece_info)
        self.draw_board()
        
    def draw_board(self):
        self.canvas.delete('all')
        
        center_x, center_y = 300, 300
        outer_radius = 250
        middle_radius = 175
        inner_radius = 100
        center_radius = 40
        
        # Draw the rings
        self.canvas.create_oval(
            center_x - outer_radius, center_y - outer_radius,
            center_x + outer_radius, center_y + outer_radius,
            fill='#444444', outline='#666666', width=2
        )
        self.canvas.create_oval(
            center_x - middle_radius, center_y - middle_radius,
            center_x + middle_radius, center_y + middle_radius,
            outline='#666666', width=2
        )
        self.canvas.create_oval(
            center_x - inner_radius, center_y - inner_radius,
            center_x + inner_radius, center_y + inner_radius,
            outline='#666666', width=2
        )
        
        # Draw center position (A1)
        self.canvas.create_oval(
            center_x - center_radius, center_y - center_radius,
            center_x + center_radius, center_y + center_radius,
            fill='#555555', outline='#666666'
        )
        
        # Draw segments
        for i in range(12):
            angle = i * (2 * math.pi / 12)
            # Draw lines from inner to outer circle
            x1 = center_x + math.cos(angle) * inner_radius
            y1 = center_y + math.sin(angle) * inner_radius
            x2 = center_x + math.cos(angle) * outer_radius
            y2 = center_y + math.sin(angle) * outer_radius
            self.canvas.create_line(x1, y1, x2, y2, fill='#666666', width=2)
            
            # Draw B ring positions
            b_x = center_x + math.cos(angle) * (inner_radius + middle_radius) / 2
            b_y = center_y + math.sin(angle) * (inner_radius + middle_radius) / 2
            self.draw_position(i + 1, b_x, b_y)  # B positions: 1-12
            
            # Draw C ring positions
            c_x = center_x + math.cos(angle) * (middle_radius + outer_radius) / 2
            c_y = center_y + math.sin(angle) * (middle_radius + outer_radius) / 2
            self.draw_position(i + 13, c_x, c_y)  # C positions: 13-24

        # Draw center piece if present
        self.draw_position(0, center_x, center_y)  # A1 position

    def draw_position(self, pos, x, y):
        is_selected = pos == self.selected_piece
        space_color = '#666666' if is_selected else '#555555'
        self.canvas.create_oval(x-20, y-20, x+20, y+20, fill=space_color)
        
        piece = self.board.spaces[pos]
        if piece:
            color = 'blue' if piece.player == 1 else 'red'
            self.canvas.create_oval(x-15, y-15, x+15, y+15, fill=color)
            self.canvas.create_text(x, y, text=piece.name[:1], fill='white')
            self.canvas.create_text(x, y+25, text=f"HP:{piece.health}", fill='white')

    def handle_click(self, event):
        center_x, center_y = 300, 300
        click_x, click_y = event.x, event.y
        
        # Check center position (A1)
        if (click_x - center_x)**2 + (click_y - center_y)**2 <= 40**2:
            self.handle_position_click(0)
            return
            
        # Check other positions
        for i in range(24):
            angle = (i % 12) * (2 * math.pi / 12)
            radius = 212.5 if i >= 12 else 137.5  # Average of ring radii
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            
            if (click_x - x)**2 + (click_y - y)**2 <= 20**2:
                self.handle_position_click(i + 1)
                break

    def handle_position_click(self, position):
        if self.selected_piece is None:
            # Select piece
            if (self.board.spaces[position] and 
                self.board.spaces[position].player == self.current_player):
                self.selected_piece = position
                self.status_label.config(text=f"Selected piece at position {position}")
        else:
            # Move piece
            if self.board.is_valid_move(self.selected_piece, position, self.current_player):
                # Handle combat
                if self.board.spaces[position]:
                    attacker = self.board.spaces[self.selected_piece]
                    defender = self.board.spaces[position]
                    defender.health -= attacker.attack
                    self.status_label.config(text=f"{attacker.name} attacks {defender.name}")
                    if defender.health <= 0:
                        self.board.spaces[position] = None

                # Move piece if destination is empty
                if self.board.spaces[position] is None:
                    self.board.spaces[position] = self.board.spaces[self.selected_piece]
                    self.board.spaces[self.selected_piece] = None
                    self.current_player = 3 - self.current_player
                    self.status_label.config(text=f"Player {self.current_player}'s turn")

            self.selected_piece = None
        self.draw_board()
        
        # Check win condition
        pieces_remaining = [piece for piece in self.board.spaces 
                          if piece and piece.player != self.current_player]
        if not pieces_remaining:
            self.status_label.config(text=f"Player {3-self.current_player} wins!")
            self.root.after(2000, self.root.quit)

    def show_piece_info(self, event):
        # Hide any existing tooltip
        self.hide_piece_info(None)
        
        # Find piece under cursor
        piece_pos = self.get_position_at_coordinates(event.x, event.y)
        if piece_pos is not None and self.board.spaces[piece_pos]:
            piece = self.board.spaces[piece_pos]
            
            # Create tooltip window
            self.tooltip_window = tk.Toplevel(self.root)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.configure(bg='#2c2c2c')
            
            # Position tooltip near cursor but not under it
            x = self.root.winfo_x() + event.x + 20
            y = self.root.winfo_y() + event.y + 20
            self.tooltip_window.geometry(f"+{x}+{y}")
            
            # Create card-like display
            frame = tk.Frame(self.tooltip_window, bg='#2c2c2c', padx=10, pady=10)
            frame.pack()
            
            # Title
            tk.Label(frame, text=piece.name, font=('Arial', 12, 'bold'), 
                    fg='white', bg='#2c2c2c').pack()
            
            # Stats with custom formatting
            stats_frame = tk.Frame(frame, bg='#2c2c2c', pady=5)
            stats_frame.pack()
            
            # Attack stat
            tk.Label(stats_frame, text="⚔️", fg='red', bg='#2c2c2c').grid(row=0, column=0)
            tk.Label(stats_frame, text=str(piece.attack), fg='white', 
                    bg='#2c2c2c').grid(row=0, column=1)
            
            # Defense stat
            tk.Label(stats_frame, text="🛡️", fg='blue', bg='#2c2c2c').grid(row=0, column=2)
            tk.Label(stats_frame, text=str(piece.health), fg='white', 
                    bg='#2c2c2c').grid(row=0, column=3)
            
            # Movement stat
            tk.Label(stats_frame, text="⚡", fg='yellow', bg='#2c2c2c').grid(row=0, column=4)
            tk.Label(stats_frame, text=str(piece.move_range), fg='white', 
                    bg='#2c2c2c').grid(row=0, column=5)
            
            # Player indicator
            player_color = 'blue' if piece.player == 1 else 'red'
            tk.Label(frame, text=f"Player {piece.player}", fg=player_color,
                    bg='#2c2c2c').pack()

    def hide_piece_info(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def get_position_at_coordinates(self, x, y):
        center_x, center_y = 300, 300
        
        # Check center position (A1)
        if (x - center_x)**2 + (y - center_y)**2 <= 40**2:
            return 0
            
        # Check ring positions
        for i in range(24):
            angle = (i % 12) * (2 * math.pi / 12)
            radius = 212.5 if i >= 12 else 137.5
            pos_x = center_x + math.cos(angle) * radius
            pos_y = center_y + math.sin(angle) * radius
            
            if (x - pos_x)**2 + (y - pos_y)**2 <= 20**2:
                return i + 1
        
        return None

    def run(self):
        self.root.mainloop()

import pygame
import tkinter as tk
import random
import math

class RaceWindow:
    def __init__(self, master):
        # Initialize pygame mixer with higher frequency for faster playback
        pygame.mixer.init(44100, -16, 2, 512, allowedchanges=0)
        pygame.mixer.set_num_channels(8)
        
        # Load and pre-modify sound effects
        self.sounds = {
            'countdown': pygame.mixer.Sound('sounds/countdown.mp3'),
            'start': pygame.mixer.Sound('sounds/start.wav'),
            # 'engine_trouble': pygame.mixer.Sound('sounds/engine_trouble.wav'),
            # 'sand_storm': pygame.mixer.Sound('sounds/sand_storm.wav'),
            # 'debris_hit': pygame.mixer.Sound('sounds/debris_hit.wav'),
            # 'explosion': pygame.mixer.Sound('sounds/explosion.wav'),
            # 'finish': pygame.mixer.Sound('sounds/finish.wav')
        }
        # Speed up countdown sound
        self.sounds['countdown'].set_volume(0.7)  # Adjust volume to compensate for speed
        
        # Load background music
        pygame.mixer.music.load('./sounds/pod_race_intro.mp3')
        pygame.mixer.music.play(-1)  # -1 means loop forever
        
        # Store race theme path for later
        self.race_theme = './sounds/pod_race_race_theme.mp3'
        
        self.master = master
        self.master.title("Pod Race Simulator")
        
        # Set fullscreen
        self.master.attributes('-fullscreen', True)
        self.master.bind('<Escape>', lambda e: self.master.destroy())  # Allow escape to exit
        
        # Get screen dimensions
        self.width = self.master.winfo_screenwidth()
        self.height = self.master.winfo_screenheight()
        
        # Change to Tatooine sand color background
        self.canvas = tk.Canvas(master, width=self.width, height=self.height, bg='#C2B280')  # Desert sand
        self.canvas.pack(fill='both', expand=True)
        
        # Increase sand particles for more desert feel
        self.sand_particles = [(random.randint(0, self.width), 
                              random.randint(0, self.height), 
                              random.uniform(1, 4))  # Larger size variation
                             for _ in range(int((self.width * self.height) / 1000))]  # More particles
        
        # Add dune positions
        self.dunes = [(random.randint(0, self.width), 
                      random.randint(self.height//2, self.height),
                      random.randint(100, 300))  # Dune sizes
                     for _ in range(5)]
        
        # Heat wave effect parameters
        self.heat_wave_offset = 0
        
        # More vibrant pod colors
        self.pod_colors = ['#FF0000', '#00FF00', '#0088FF', '#FF00FF', 
                          '#FFFF00', '#00FFAA']  # 6 colors
        self.pod_shapes = self.create_pod_shapes()
        self.race_started = False
        self.start_button = None
        self.button_frame = None  # Add reference to button frame
        self.event_messages = []  # List to store active event messages
        
    def create_pod_shapes(self):
        # Define complex pod shapes as coordinate lists - flipped horizontally
        # Create 6 unique pod shapes
        shapes = [
            [(30,0), (10,8), (0,0), (10,-8)],     # Arrow shape
            [(30,0), (5,10), (10,0), (5,-10)],    # Diamond shape
            [(30,0), (0,5), (5,0), (0,-5)],       # Dart shape
            [(30,0), (10,5), (0,0), (10,-5)],     # Teardrop shape
            [(30,0), (15,10), (0,0), (15,-10)],   # Wide arrow
            [(25,0), (15,5), (0,0), (15,-5)]      # Stubby arrow
        ]
        return shapes
        
    def draw_race(self, racers, distance, obstacles, speed_gates):
        self.canvas.delete("all")
        
        # Draw desert background
        self.canvas.create_rectangle(0, 0, self.width, self.height, 
                                   fill='#DAA520', outline='')
        
        # Draw scattered rocks and dunes
        for i in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(5, 15)
            color = random.choice(['#8B4513', '#CD853F', '#DEB887'])
            self.canvas.create_oval(x, y, x+size, y+size, 
                                  fill=color, outline='')
        
        # Draw finish line
        finish_x = self.width - 60
        stripe_height = 20
        for j in range(int(self.height // stripe_height)):
            y = j * stripe_height
            color = '#FFFFFF' if j % 2 == 0 else '#000000'
            self.canvas.create_rectangle(finish_x, y,
                                          finish_x + 20, y + stripe_height,
                                          fill=color, outline='')
        
        # Draw obstacles
        for obstacle in obstacles:
            points = obstacle.get_shape_points()
            shadow_points = [(x+2, y+2) for x, y in points]
            self.canvas.create_polygon(shadow_points,
                                    fill='#463E3F',
                                    outline='')
            self.canvas.create_polygon(points,
                                    fill=obstacle.color,
                                    outline='#463E3F',
                                    width=1)
        
        # Draw speed gates
        for gate in speed_gates:
            y = gate.y_pos
            
            for i in range(3):
                size = gate.size - (i * 5)
                opacity = ['#00FFFF', '#00CCCC', '#009999'][i]
                points = []
                for j in range(4):
                    angle = j * math.pi / 2 + math.pi / 4
                    px = gate.x_pos + size * math.cos(angle)
                    py = y + size * math.sin(angle)
                    points.append((px, py))
                self.canvas.create_polygon(points,
                                        fill=opacity if not gate.activated else '#335577',
                                        outline='white',
                                        width=1)
        
        # Draw racers
        num_racers = len(racers)
        for i, racer in enumerate(racers):
            if racer.destroyed or racer.is_exploding:
                frame_progress = racer.explosion_frame / racer.max_explosion_frames
                size = 15 * (1 + frame_progress)
                x = (racer.position / distance) * (self.width - 100)
                y = (i + 1) * (self.height / (num_racers + 1))
                
                self.canvas.create_oval(x-size, y-size, x+size, y+size,
                                     fill='#FF4500',
                                     outline='#FF0000',
                                     width=1)
                
                racer.explosion_frame += 1
                if racer.explosion_frame >= racer.max_explosion_frames:
                    racer.is_exploding = False
                    racer.destroyed = True
                    racer.finished = True
                continue
            
            x = (racer.position / distance) * (self.width - 100)
            y = (i + 1) * (self.height / (num_racers + 1))
            
            shadow_shape = [(x+cx+2, y+cy+2) for cx,cy in self.pod_shapes[i]]
            self.canvas.create_polygon(shadow_shape,
                                    fill='#463E3F',
                                    outline='')
            
            pod_shape = [(x+cx, y+cy) for cx,cy in self.pod_shapes[i]]
            self.canvas.create_polygon(pod_shape,
                                    fill=self.pod_colors[i],
                                    outline='white',
                                    width=2)
            
            if not racer.finished:
                glow_x = x - 5
                self.canvas.create_oval(glow_x-8, y-3, glow_x-2, y+3,
                                     fill='#FF4500',
                                     outline='')
                self.canvas.create_oval(glow_x-12, y-5, glow_x, y+5,
                                     fill='#FF9933',
                                     outline='',
                                     stipple='gray50')
            
            status_color = self.pod_colors[i]
            status_text = racer.name
            if racer.destroyed:
                status_text += " [DESTROYED]"
                status_color = '#FF0000'
            elif racer.active_event:
                status_text += f" [{racer.active_event.name}]"
            
            self.canvas.create_text(20, y + 10,
                                  text=status_text,
                                  fill=status_color,
                                  anchor='w',
                                  font=('Arial', 12, 'bold'))
            
            if racer.destroyed:
                continue
            
            self.canvas.create_text(200, y + 10,
                                  text=f"Speed: {racer.speed:.2f}x",
                                  fill='white',
                                  anchor='w')
            self.canvas.create_text(350, y + 10,
                                  text=f"Distance: {racer.position:.1f}m",
                                  fill='white',
                                  anchor='w')
            
            progress = (racer.position / distance) * 150
            self.canvas.create_rectangle(500, y + 5, 650, y + 15, 
                                      outline='white')
            self.canvas.create_rectangle(500, y + 5, 500 + progress, y + 15,
                                      fill=self.pod_colors[i])
            
            health_width = 100
            health_x = 700
            
            health_fill = (racer.current_health / racer.max_health) * health_width
            health_color = '#00FF00' if racer.current_health > racer.max_health * 0.6 else \
                         '#FFFF00' if racer.current_health > racer.max_health * 0.3 else '#FF0000'
            
            self.canvas.create_rectangle(health_x, y + 5,
                                      health_x + health_width, y + 15,
                                      fill='#400000', outline='white')
            
            self.canvas.create_rectangle(health_x, y + 5,
                                      health_x + health_fill, y + 15,
                                      fill=health_color, outline='')
            
            self.canvas.create_text(health_x + health_width + 10, y + 10,
                                  text=f"HP: {int(racer.current_health)}/{int(racer.max_health)}",
                                  fill='white',
                                  anchor='w',
                                  font=('Arial', 10))
            
            if racer.boost_timer > 0:
                trail_length = 40
                trail_points = []
                for j in range(5):
                    offset = j * (trail_length/4)
                    trail_points.extend([x-offset-10, y-5, x-offset, y+5])
                
                self.canvas.create_polygon(trail_points,
                                        fill='#00FFFF',
                                        stipple='gray50')
            
            if racer.boost_animation_frames > 0:
                progress = racer.boost_animation_frames / racer.max_boost_animation_frames
                
                ring_size = 40 * (1 - progress)
                ring_opacity = ['#00FFFF', '#00CCFF', '#0088FF'][int(progress * 2.99)]
                
                for ring in range(3):
                    ring_radius = ring_size * (1 - ring * 0.2)
                    self.canvas.create_oval(x - ring_radius, y - ring_radius,
                                         x + ring_radius, y + ring_radius,
                                         outline=ring_opacity,
                                         width=2)
                
                line_length = 60 * progress
                for offset in [-10, 0, 10]:
                    self.canvas.create_line(x - line_length, y + offset,
                                          x, y + offset,
                                          fill='#00FFFF',
                                          width=2,
                                          dash=(10, 5))
                
                racer.boost_animation_frames -= 1

            if racer.speed_gate_animation_frames > 0:
                progress = racer.speed_gate_animation_frames / racer.max_speed_gate_animation_frames
                ring_size = 40 * (1 - progress)
                ring_opacity = ['#00FFFF', '#00CCFF', '#0088FF'][int(progress * 2.99)]
                
                for ring in range(3):
                    ring_radius = ring_size * (1 - ring * 0.2)
                    self.canvas.create_oval(x - ring_radius, y - ring_radius,
                                         x + ring_radius, y + ring_radius,
                                         outline=ring_opacity,
                                         width=2)
                
                racer.speed_gate_animation_frames -= 1

        message_height = 30
        for i, (message, color, frames_left) in enumerate(self.event_messages):
            self.canvas.create_text(self.width/2, 50 + i*message_height,
                                  text=message,
                                  fill=color,
                                  font=('Arial', 20, 'bold'))
            
        self.event_messages = [(m, c, f-1) for m, c, f in self.event_messages if f > 0]
        
        self.master.update()
    
    def gradient_color(self, color1, color2, ratio):
        """Helper function to create color gradients"""
        # Convert hex to RGB
        r1 = int(color1[1:3], 16)
        g1 = int(color2[3:5], 16)
        b1 = int(color2[5:7], 16)
        r2 = int(color2[1:3], 16)
        g2 = int(color2[3:5], 16)
        b2 = int(color2[5:7], 16)
        
        # Interpolate
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'

    def draw_countdown(self, count):
        self.canvas.delete("all")
        
        # Draw desert background and scattered rocks
        self.canvas.create_rectangle(0, 0, self.width, self.height, 
                                   fill='#DAA520', outline='')
        
        # Draw scattered rocks and dunes
        for i in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(5, 15)
            color = random.choice(['#8B4513', '#CD853F', '#DEB887'])
            self.canvas.create_oval(x, y, x+size, y+size, 
                                  fill=color, outline='')
        
        # Draw track base
        self.canvas.create_rectangle(0, 0, self.width, self.height,
                                   fill='#B8860B', outline='')
        
        # Play countdown sound
        if count == 3:
            self.play_sound('countdown')
        elif count == 0:
            self.play_sound('start')
        # Draw basic track elements
        for particle in self.sand_particles:
            x, y, size = particle
            self.canvas.create_oval(x, y, x+size, y+size, 
                                  fill='#F4A460', 
                                  outline='#DEB887')
            
        finish_x = self.width - 60
        self.canvas.create_rectangle(finish_x, 0, finish_x + 20, self.height, fill='#A0522D')
        for i in range(self.height // 20):
            y = i * 20
            self.canvas.create_rectangle(finish_x, y, finish_x + 20, y+10, fill='#8B4513')
        
        # Center countdown text on screen
        self.canvas.create_text(self.width/2, self.height/2,
                              text=str(count) if count > 0 else "GO!",
                              fill='#FF4500',
                              font=('Arial', int(self.height/8), 'bold'))
        self.master.update()

    def draw_podium(self, racers):
        self.canvas.delete("all")
        
        # Draw desert background
        self.canvas.create_rectangle(0, 0, self.width, self.height, 
                                   fill='#DAA520', outline='')
        
        # Draw scattered rocks and dunes
        for i in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(5, 15)
            color = random.choice(['#8B4513', '#CD853F', '#DEB887'])
            self.canvas.create_oval(x, y, x+size, y+size, 
                                  fill=color, outline='')
        
        # Draw title with desert theme
        self.canvas.create_text(self.width/2, 50,
                              text="FINAL STANDINGS",
                              fill='#FF4500',
                              font=('Arial', 36, 'bold'))
        
        # Draw leaderboard entries - modified for all racers
        entry_height = 60  # Reduced height to fit all racers
        start_y = 120    # Start higher to fit all entries
        board_width = 600
        
        # Create scrolling region if needed
        total_height = entry_height * len(racers)
        visible_height = self.height - start_y - 50
        
        for i, racer in enumerate(racers):
            y = start_y + (i * entry_height)
            
            # Skip if entry would be off screen
            if y > self.height - 30:
                continue
                
            x = self.width/2
            
            # Find original racer index for correct color and pod shape
            original_index = int(racer.name.split()[-1]) - 1
            
            # Create background rectangle with sand theme
            self.canvas.create_rectangle(x - board_width/2, y,
                                       x + board_width/2, y + entry_height - 5,
                                       fill='#8B4513',  # Desert brown
                                       outline=self.pod_colors[original_index])
            
            # Draw position number
            position_text = f"#{i+1}"
            self.canvas.create_text(x - board_width/2 + 40, y + entry_height/2,
                                  text=position_text,
                                  fill='#F5DEB3',  # Wheat color
                                  font=('Arial', 20, 'bold'))
            
            # Draw pod with correct shape and color - smaller size
            pod_y = y + entry_height/2
            pod_x = x - board_width/2 + 100
            scale = 0.8  # Scale factor for pod size
            pod_shape = [(pod_x+cx*scale, pod_y+cy*scale) for cx,cy in self.pod_shapes[original_index]]
            
            # Add pod shadow
            shadow_shape = [(x+2, y+2) for x, y in pod_shape]
            self.canvas.create_polygon(shadow_shape,
                                    fill='#463E3F',
                                    outline='')
            
            # Draw actual pod
            self.canvas.create_polygon(pod_shape,
                                    fill=self.pod_colors[original_index],
                                    outline='white',
                                    width=2)
            
            # Draw stats with desert theme - adjusted positions
            name_x = x + 30
            self.canvas.create_text(name_x, y + entry_height/2,
                                  text=racer.name,
                                  fill=self.pod_colors[original_index],
                                  anchor='w',
                                  font=('Arial', 16, 'bold'))
            
            # Add stats with shadow effect
            stats_x = x + 200
            odds = round(1.0 / racer.speed * 2, 2)
            stats_text = f"Speed: {racer.speed:.2f}x   Odds: {odds}:1"
            
            # Add shadow
            self.canvas.create_text(stats_x+1, y + entry_height/2 + 1,
                                  text=stats_text,
                                  fill='#463E3F',
                                  anchor='w',
                                  font=('Arial', 14))
            # Main text
            self.canvas.create_text(stats_x, y + entry_height/2,
                                  text=stats_text,
                                  fill='#F5DEB3',
                                  anchor='w',
                                  font=('Arial', 14))
            
            # Add destroyed status if applicable
            if racer.destroyed:
                self.canvas.create_text(x + board_width/2 - 50, y + entry_height/2,
                                      text="DESTROYED",
                                      fill='#FF0000',
                                      font=('Arial', 14, 'bold'))
        
        self.master.update()
    
    def draw_odds_screen(self, racers):
        self.canvas.delete("all")
        
        # Draw desert background
        self.canvas.create_rectangle(0, 0, self.width, self.height, 
                                   fill='#DAA520', outline='')
        
        # Draw scattered rocks and dunes
        for i in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(5, 15)
            color = random.choice(['#8B4513', '#CD853F', '#DEB887'])
            self.canvas.create_oval(x, y, x+size, y+size, 
                                  fill=color, outline='')
        
        # Draw track base
        self.canvas.create_rectangle(0, self.width*0.1, self.width, self.height*0.9,
                                   fill='#B8860B', outline='')
        
        # Draw title
        self.canvas.create_text(self.width/2, 50,
                              text="POD RACING ODDS",
                              fill='#FF4500',
                              font=('Arial', 36, 'bold'))
        
        # Draw racer cards
        card_width = 300
        card_height = 150
        padding = 50
        cards_per_row = 2
        
        for i, racer in enumerate(racers):
            row = i // cards_per_row
            col = i % cards_per_row
            
            x = self.width/2 + (col - 1) * (card_width + padding)
            y = self.height/2 + (row - 1) * (card_height + padding)
            
            # Update card backgrounds for better contrast
            self.canvas.create_rectangle(x, y, x + card_width, y + card_height,
                                      fill='#1a2f2f',  # Darker slate gray
                                      outline=self.pod_colors[i])
            
            # Draw pod
            pod_x = x + 50
            pod_y = y + card_height/2
            pod_shape = [(pod_x+cx, pod_y+cy) for cx,cy in self.pod_shapes[i]]
            self.canvas.create_polygon(pod_shape,
                                    fill=self.pod_colors[i],
                                    outline='white',
                                    width=2)
            
            # Calculate odds based on speed (higher speed = lower odds)
            odds = round(1.0 / racer.speed * 2, 2)
            
            # Draw racer info with agility stat
            self.canvas.create_text(x + card_width - 100, y + 40,
                                  text=racer.name,
                                  fill=self.pod_colors[i],
                                  font=('Arial', 16, 'bold'))
            self.canvas.create_text(x + card_width - 100, y + 70,
                                  text=f"Base Speed: {racer.speed:.2f}x",
                                  fill='white',
                                  font=('Arial', 12))
            self.canvas.create_text(x + card_width - 100, y + 85,  # Add agility stat
                                  text=f"Agility: {racer.agility:.2f}x",
                                  fill='#00FFAA',
                                  font=('Arial', 12))
            self.canvas.create_text(x + card_width - 100, y + 100,
                                  text=f"Odds: {odds}:1",
                                  fill='#FFFF00',
                                  font=('Arial', 14, 'bold'))
        
        # Create start button if it doesn't exist
        if not self.start_button:
            self.button_frame = tk.Frame(self.master)
            self.button_frame.place(relx=0.5, rely=0.85, anchor='center')
            
            # Update button colors
            self.start_button = tk.Button(self.button_frame,
                                        text="START RACE",
                                        font=('Arial', 20, 'bold'),
                                        bg='#32CD32',  # Lime Green
                                        fg='white',
                                        padx=30,
                                        pady=15,
                                        command=self.start_race)
            self.start_button.pack()
        
        self.master.update()
    
    def start_race(self):
        if self.start_button:
            self.start_button.destroy()
            self.start_button = None
        if self.button_frame:
            self.button_frame.destroy()
            self.button_frame = None
            
        # Change music to race theme
        pygame.mixer.music.stop()
        pygame.mixer.music.load(self.race_theme)
        pygame.mixer.music.play(-1)
        
        self.race_started = True

    def add_event_message(self, racer_name, event_name, lethal=False):
        # Find the racer's color by matching the name
        racer_index = int(racer_name.split()[-1]) - 1  # Extract number from "Pod X"
        message_color = '#FF0000' if lethal else self.pod_colors[racer_index]
        message = f"{racer_name}: {event_name}!"
        self.event_messages.append((message, message_color, 60))  # Show for 60 frames

    def play_sound(self, sound_name):
        try:
            self.sounds[sound_name].play()
        except KeyError:
            print(f"Sound {sound_name} not found")
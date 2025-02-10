import random
import time
import tkinter as tk
from tkinter import ttk
import pygame.mixer
import math

class Event:
    def __init__(self, name, probability, duration, speed_modifier, lethal=False):
        self.name = name
        self.probability = probability
        self.duration = duration
        self.speed_modifier = speed_modifier
        self.lethal = lethal  # This will now only affect speed, not destroy directly

class Obstacle:
    def __init__(self, x_pos, size=20):
        self.x_pos = x_pos
        self.size = random.randint(20, 35)
        self.speed = 15
        self.y_offset = random.choice([-0.6, -0.3, 0, 0.3, 0.6])
        # Static shape generation
        self.points = self._generate_shape()
        self.color = random.choice(['#8B4513', '#A0522D', '#6B4423'])  # Earth tones

    def _generate_shape(self):
        # Generate a single random but static shape
        num_points = random.randint(6, 8)  # Random number of points for variety
        points = []
        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            # Add some randomness to the radius while keeping it static
            radius = self.size * (0.8 + random.uniform(0, 0.3))
            points.append((math.cos(angle) * radius, math.sin(angle) * radius))
        return points

    def get_shape_points(self, base_y):
        y = base_y + (self.y_offset * 60)
        # Transform the stored points to screen coordinates
        return [(self.x_pos + dx, y + dy) for dx, dy in self.points]

    def update(self):
        self.x_pos -= self.speed
        return self.x_pos > -self.size  # Return False when off screen

class SpeedGate:
    def __init__(self, x_pos, size=30):
        self.x_pos = x_pos
        self.size = size
        self.speed = 15  # Same speed as obstacles
        self.y_offset = random.choice([-0.3, 0, 0.3])  # Less extreme positions than obstacles
        self.activated = False  # Track if a racer has used this gate
        
    def update(self):
        self.x_pos -= self.speed
        return self.x_pos > -self.size

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
        
    def draw_race(self, racers, distance, obstacles, speed_gates):  # Add speed_gates parameter
        self.canvas.delete("all")
        
        # Draw desert background
        # Sand base
        self.canvas.create_rectangle(0, 0, self.width, self.height, 
                                   fill='#DAA520', outline='')
        
        # Draw scattered rocks and dunes
        for i in range(50):  # Background terrain
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(5, 15)
            color = random.choice(['#8B4513', '#CD853F', '#DEB887'])
            self.canvas.create_oval(x, y, x+size, y+size, 
                                  fill=color, outline='')
        
        # Draw multiple race tracks (one per racer)
        num_lanes = len(racers)
        lane_height = self.height / num_lanes
        
        # Draw lane dividers
        for i in range(num_lanes + 1):
            y = i * lane_height
            self.canvas.create_line(0, y, self.width, y,
                                  fill='#F5DEB3', width=2)
            
        # Draw finish line in each lane
        finish_x = self.width - 60
        for i in range(num_lanes):
            lane_y = i * lane_height
            stripe_height = 20
            for j in range(int(lane_height // stripe_height)):
                y = lane_y + (j * stripe_height)
                color = '#FFFFFF' if j % 2 == 0 else '#000000'
                self.canvas.create_rectangle(finish_x, y,
                                          finish_x + 20, y + stripe_height,
                                          fill=color, outline='')
        
        # Draw obstacles in their respective lanes
        for obstacle in obstacles:
            lane_y = obstacle.lane * lane_height + (lane_height / 2)
            points = obstacle.get_shape_points(lane_y)
            # Add shadow effect
            shadow_points = [(x+2, y+2) for x, y in points]
            self.canvas.create_polygon(shadow_points,
                                    fill='#463E3F',
                                    outline='')
            self.canvas.create_polygon(points,
                                    fill=obstacle.color,
                                    outline='#463E3F',
                                    width=1)
        
        # Draw speed gates as shimmering portals
        for gate in speed_gates:
            lane_y = gate.lane * lane_height + (lane_height / 2)
            y = lane_y + (gate.y_offset * 60)
            
            # Portal effect with multiple layers
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
        
        # Draw racers as sleek pods
        for i, racer in enumerate(racers):
            if racer.destroyed or racer.is_exploding:
                # Smaller explosion effect with reduced size
                frame_progress = racer.explosion_frame / racer.max_explosion_frames
                size = 15 * (1 + frame_progress)  # Reduced from 25 to 15
                x = (racer.position / distance) * (self.width - 100)
                lane_center = (i * lane_height) + (lane_height / 2)
                y = lane_center + racer.y_offset
                
                self.canvas.create_oval(x-size, y-size, x+size, y+size,
                                     fill='#FF4500',
                                     outline='#FF0000',
                                     width=1)  # Reduced outline width
                
                racer.explosion_frame += 1
                if racer.explosion_frame >= racer.max_explosion_frames:
                    racer.is_exploding = False
                    racer.destroyed = True
                    racer.finished = True
                continue
            
            x = (racer.position / distance) * (self.width - 100)
            lane_center = (i * lane_height) + (lane_height / 2)
            y = lane_center + racer.y_offset
            
            # Draw shadow
            shadow_shape = [(x+cx+2, y+cy+2) for cx,cy in self.pod_shapes[i]]
            self.canvas.create_polygon(shadow_shape,
                                    fill='#463E3F',
                                    outline='')
            
            # Draw pod
            pod_shape = [(x+cx, y+cy) for cx,cy in self.pod_shapes[i]]
            self.canvas.create_polygon(pod_shape,
                                    fill=self.pod_colors[i],
                                    outline='white',
                                    width=2)
            
            # Add engine glow
            if not racer.finished:
                glow_x = x - 5
                # Inner glow
                self.canvas.create_oval(glow_x-8, y-3, glow_x-2, y+3,
                                     fill='#FF4500',
                                     outline='')
                # Outer glow
                self.canvas.create_oval(glow_x-12, y-5, glow_x, y+5,
                                     fill='#FF9933',
                                     outline='',
                                     stipple='gray50')
            
            # Draw stats in lane instead of bottom of screen
            lane_y = (i * lane_height) + lane_height - 30  # 30 pixels from bottom of lane
            
            # Remove the background rectangle and just draw the stats directly
            # Pod name and status
            status_color = self.pod_colors[i]
            status_text = racer.name
            if racer.destroyed:
                status_text += " [DESTROYED]"
                status_color = '#FF0000'
            elif racer.active_event:
                status_text += f" [{racer.active_event.name}]"
            
            self.canvas.create_text(20, lane_y + 10,
                                  text=status_text,
                                  fill=status_color,
                                  anchor='w',
                                  font=('Arial', 12, 'bold'))
            
            # Skip rest of stats if destroyed
            if racer.destroyed:
                continue
            
            # Speed and distance info
            self.canvas.create_text(200, lane_y + 10,
                                  text=f"Speed: {racer.speed:.2f}x",
                                  fill='white',
                                  anchor='w')
            self.canvas.create_text(350, lane_y + 10,
                                  text=f"Distance: {racer.position:.1f}m",
                                  fill='white',
                                  anchor='w')
            
            # Progress bar
            progress = (racer.position / distance) * 150
            self.canvas.create_rectangle(500, lane_y + 5, 650, lane_y + 15, 
                                      outline='white')
            self.canvas.create_rectangle(500, lane_y + 5, 500 + progress, lane_y + 15,
                                      fill=self.pod_colors[i])
            
            # Health bar
            health_width = 100
            health_x = 700
            
            # Health fill
            health_fill = (racer.current_health / racer.max_health) * health_width
            health_color = '#00FF00' if racer.current_health > racer.max_health * 0.6 else \
                         '#FFFF00' if racer.current_health > racer.max_health * 0.3 else '#FF0000'
            
            # Background
            self.canvas.create_rectangle(health_x, lane_y + 5,
                                      health_x + health_width, lane_y + 15,
                                      fill='#400000', outline='white')
            
            # Fill
            self.canvas.create_rectangle(health_x, lane_y + 5,
                                      health_x + health_fill, lane_y + 15,
                                      fill=health_color, outline='')
            
            # Health text
            self.canvas.create_text(health_x + health_width + 10, lane_y + 10,
                                  text=f"HP: {int(racer.current_health)}/{int(racer.max_health)}",
                                  fill='white',
                                  anchor='w',
                                  font=('Arial', 10))
            
            # Add boost effect
            if racer.boost_timer > 0:
                # Add blue trailing effect
                trail_length = 40
                trail_points = []
                for j in range(5):
                    offset = j * (trail_length/4)
                    trail_points.extend([x-offset-10, y-5, x-offset, y+5])
                
                self.canvas.create_polygon(trail_points,
                                        fill='#00FFFF',
                                        stipple='gray50')  # Makes it semi-transparent
            
            # Keep the boost animation code
            if racer.boost_animation_frames > 0:
                # Calculate animation progress (1.0 to 0.0)
                progress = racer.boost_animation_frames / racer.max_boost_animation_frames
                
                # Draw expanding ring effect
                ring_size = 40 * (1 - progress)  # Grows as animation progresses
                ring_opacity = ['#00FFFF', '#00CCFF', '#0088FF'][int(progress * 2.99)]  # Color transition
                
                # Draw multiple rings for effect
                for ring in range(3):
                    ring_radius = ring_size * (1 - ring * 0.2)
                    self.canvas.create_oval(x - ring_radius, y - ring_radius,
                                         x + ring_radius, y + ring_radius,
                                         outline=ring_opacity,
                                         width=2)
                
                # Add speed lines
                line_length = 60 * progress
                for offset in [-10, 0, 10]:  # Three lines at different heights
                    self.canvas.create_line(x - line_length, y + offset,
                                          x, y + offset,
                                          fill='#00FFFF',
                                          width=2,
                                          dash=(10, 5))
                
                racer.boost_animation_frames -= 1

        # Draw event notifications
        message_height = 30
        for i, (message, color, frames_left) in enumerate(self.event_messages):
            self.canvas.create_text(self.width/2, 50 + i*message_height,
                                  text=message,
                                  fill=color,
                                  font=('Arial', 20, 'bold'))
            
        # Remove expired messages
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
        
        lane_height = self.height / 4
        for i in range(5):
            y = i * lane_height
            self.canvas.create_line(0, y, self.width, y, fill='#CD853F', dash=(8,4))
            
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

class Racer:
    def __init__(self, name):
        self.name = name
        self.position = 0
        self.finished = False
        self.base_speed = random.uniform(1, 1.4)
        self.speed = self.base_speed
        self.slowdown_timer = 0
        self.active_event = None
        self.event_duration = 0
        self.destroyed = False
        self.y_offset = 0
        self.max_y_offset = 25
        self.current_lane_position = 0
        self.target_lane_position = 0
        self.boost_timer = 0
        self.boost_multiplier = 1.0
        self.explosion_frame = 0
        self.max_explosion_frames = 30
        self.is_exploding = False
        self.agility = random.uniform(0.8, 1.5)
        self.max_health = random.randint(80, 150)
        self.current_health = self.max_health
        self.health_regen_timer = 0
        self.health_regen_delay = 500
        self.health_regen_rate = 0.2
        self.seek_range = 400
        self.avoid_range = 300
        self.momentum_smoothing = 0
        self.vertical_momentum = 0
        self.center_threshold = 0
        self.is_centered = False
        self.move_speed = 2.0  # Speed of vertical movement
        self.base_move_speed = 1.0  # Base speed of vertical movement
        self.max_move_speed = 4.0  # Maximum vertical movement speed 
        self.current_move_speed = 0  # Current vertical movement speed
        self.acceleration = 0.2  # How quickly speed builds up
        self.active_direction = 0  # Current direction of movement (-1, 0, or 1)
        self.speed_boost_amount = 1.5  # 50% speed increase when boosted
        self.speed_penalty_amount = 0.6  # 40% speed decrease when hit
        self.speed_effect_duration = 45  # Duration of speed effects in frames
        self.speed_effect_timer = 0  # Timer for temporary speed effects
        self.normal_speed = 0  # Store normal speed during effects
        self.boost_animation_frames = 0
        self.max_boost_animation_frames = 20  # Duration of boost animation

    def update_movement(self, nearest_gate, nearest_obstacle, lane_height):
        """Smooth movement update with acceleration"""
        target_y = self.current_lane_position
        new_direction = 0

        # Check obstacles first (priority)
        if nearest_obstacle and nearest_obstacle[1] < self.avoid_range:
            target_y = -nearest_obstacle[0].y_offset * 40
        # Then check gates
        elif nearest_gate and nearest_gate[1] < self.seek_range and not nearest_gate[0].activated:
            target_y = nearest_gate[0].y_offset * 40

        # Determine direction of movement
        diff = target_y - self.current_lane_position
        if abs(diff) > 0.1:  # Add small threshold to prevent jitter
            new_direction = 1 if diff > 0 else -1
        
        # Update acceleration based on direction change
        if new_direction != self.active_direction:
            self.current_move_speed = self.base_move_speed
            self.active_direction = new_direction
        else:
            # Accelerate if moving in same direction
            self.current_move_speed = min(
                self.current_move_speed + self.acceleration * self.agility,
                self.max_move_speed * self.agility
            )

        # Apply movement with current speed
        if self.active_direction != 0:
            movement = self.current_move_speed * self.active_direction
            self.current_lane_position += movement

        # Enforce boundaries
        self.current_lane_position = max(min(self.current_lane_position, 
                                           self.max_y_offset), 
                                       -self.max_y_offset)
        self.y_offset = self.current_lane_position

    def update_speed(self):
        """Update speed based on timers and effects"""
        if self.speed_effect_timer > 0:
            self.speed_effect_timer -= 1
            if self.speed_effect_timer == 0:
                self.speed = self.normal_speed  # Restore normal speed

        if self.slowdown_timer > 0:
            self.slowdown_timer -= 1
            if self.slowdown_timer == 0:
                self.speed = self.base_speed  # Restore original speed

        if self.boost_timer > 0:
            self.boost_timer -= 1
            if self.boost_timer == 0:
                self.boost_multiplier = 1.0

    def update_health(self):
        """Handle health regeneration"""
        if self.health_regen_timer < self.health_regen_delay:
            self.health_regen_timer += 1
        elif self.current_health < self.max_health:
            self.current_health = min(self.max_health, 
                                    self.current_health + self.health_regen_rate)

    def apply_event(self, event):
        """Apply an event effect to the racer"""
        self.active_event = event
        self.event_duration = event.duration

    def apply_slowdown(self):
        """Apply a temporary speed reduction"""
        self.speed *= 0.8  # Slow down to 80% speed
        self.slowdown_timer = 60  # Recover after 60 frames

    def apply_boost(self):
        """Apply a temporary speed boost"""
        self.boost_timer = 45  # Boost duration
        self.boost_multiplier = 2.0  # Double speed

    def take_obstacle_damage(self):
        """Handle collision damage from obstacles"""
        base_damage = random.randint(20, 45)
        speed_multiplier = self.speed * self.boost_multiplier
        total_damage = base_damage * speed_multiplier
        
        self.current_health = max(0, self.current_health - total_damage)
        self.health_regen_timer = 0  # Reset regeneration timer
        
        if self.current_health <= 0:
            self.is_exploding = True
            self.explosion_frame = 0

    def apply_speed_boost(self):
        """Apply temporary speed boost from gates"""
        self.normal_speed = self.speed  # Store current speed
        self.speed *= self.speed_boost_amount
        self.speed_effect_timer = self.speed_effect_duration
        self.boost_animation_frames = self.max_boost_animation_frames  # Start animation

    def apply_speed_penalty(self):
        """Apply temporary speed reduction from obstacles"""
        self.normal_speed = self.speed  # Store current speed
        self.speed *= self.speed_penalty_amount
        self.speed_effect_timer = self.speed_effect_duration

class Race:
    def __init__(self, distance, racers, window):
        self.distance = distance
        self.racers = [Racer(name) for name in racers]
        self.window = window
        self.countdown = 3  # Add countdown state
        self.started = False
        self.finished_racers = []  # Add list to track finishing order
        self.preview = True  # Add preview state
        self.events = [
            Event("Engine Trouble", 0.005, 50, 0.5),    # 0.5% chance, reduced from 1%
            Event("Sand Storm", 0.002, 100, 0.7),       # 0.2% chance, reduced from 0.5%
            Event("Debris Hit", 0.003, 30, 0.6),        # 0.3% chance, reduced from 0.8%
            Event("Critical Failure", 0.0005, 1, 0, True), # 0.05% chance, reduced from 0.1%
        ]
        self.obstacles = []  # List to track active obstacles
        self.obstacle_spawn_rate = 0.015  # Slightly reduced
        self.min_obstacle_spacing = 150  # Adjusted for per-lane spacing
        self.speed_gates = []  # List to track active speed gates
        self.gate_spawn_rate = 0.006  # Slightly reduced
        self.min_gate_spacing = 400  # Larger spacing than obstacles
        
    def is_lane_active(self, lane):
        racer = self.racers[lane]
        return not (racer.finished or racer.destroyed)
    
    def update(self):
        if self.preview:
            if self.window.race_started:
                self.preview = False
            else:
                self.window.draw_odds_screen(self.racers)
                return

        if self.countdown >= 0:
            self.window.draw_countdown(self.countdown)
            self.countdown -= 1
            return

        # Spawn and update obstacles/gates
        self._handle_spawns()
        self.obstacles = [obs for obs in self.obstacles if obs.update()]
        self.speed_gates = [gate for gate in self.speed_gates if gate.update()]

        # Update racers
        for i, racer in enumerate(self.racers):
            if not racer.finished and not racer.destroyed:
                self._update_racer(i, racer)

        self.window.draw_race(self.racers, self.distance, self.obstacles, self.speed_gates)

    def _handle_spawns(self):
        """Handle obstacle and gate spawning"""
        active_lanes = [i for i in range(len(self.racers)) 
                       if not self.racers[i].finished and not self.racers[i].destroyed]
        
        if not active_lanes:
            return

        # Spawn obstacles
        if random.random() < self.obstacle_spawn_rate:
            self._try_spawn_obstacle(random.choice(active_lanes))

        # Spawn gates
        if random.random() < self.gate_spawn_rate:
            self._try_spawn_gate(random.choice(active_lanes))

    def _try_spawn_obstacle(self, lane):
        if not any(obs.x_pos > self.window.width - self.min_obstacle_spacing 
                  and obs.lane == lane for obs in self.obstacles):
            new_obstacle = Obstacle(self.window.width)
            new_obstacle.lane = lane
            self.obstacles.append(new_obstacle)

    def _try_spawn_gate(self, lane):
        if not any(gate.x_pos > self.window.width - self.min_gate_spacing 
                  and gate.lane == lane for gate in self.speed_gates):
            new_gate = SpeedGate(self.window.width)
            new_gate.lane = lane
            self.speed_gates.append(new_gate)

    def _update_racer(self, lane, racer):
        """Update single racer's state"""
        racer_x = (racer.position / self.distance) * (self.window.width - 100)

        # Find nearest obstacles and gates
        nearest_gate = self._find_nearest(self.speed_gates, lane, racer_x, 
                                        lambda g: not g.activated)
        nearest_obstacle = self._find_nearest(self.obstacles, lane, racer_x)

        # Update movement and handle collisions
        racer.update_movement(nearest_gate, nearest_obstacle, 
                            self.window.height / len(self.racers))
        
        self._handle_collisions(racer, racer_x, lane)
        self._update_racer_state(racer)

    def _find_nearest(self, objects, lane, racer_x, condition=None):
        nearest = None
        min_dist = float('inf')
        
        for obj in objects:
            if obj.lane == lane and (condition is None or condition(obj)):
                dist = obj.x_pos - racer_x
                if dist > 0 and dist < min_dist:
                    min_dist = dist
                    nearest = (obj, dist)
        
        return nearest

    def _handle_collisions(self, racer, racer_x, lane):
        """Handle collisions with obstacles and speed gates"""
        # Check obstacle collisions
        for obs in self.obstacles:
            if obs.lane == lane:
                if (racer_x >= obs.x_pos - obs.size/2 and 
                    racer_x <= obs.x_pos + obs.size/2):
                    
                    # Check vertical position
                    obstacle_y = obs.y_offset * 60
                    if abs(racer.current_lane_position - obstacle_y) < obs.size:
                        # Direct hit
                        racer.take_obstacle_damage()
                        racer.apply_speed_penalty()  # Apply speed penalty instead of slowdown
                    else:
                        # Near miss - smaller speed penalty
                        racer.apply_speed_penalty()
        
        # Check speed gate collisions - improved precision
        for gate in self.speed_gates:
            if gate.lane == lane and not gate.activated:
                gate_left = gate.x_pos - gate.size/2
                gate_right = gate.x_pos + gate.size/2
                gate_y = gate.y_offset * 60
                
                # Store previous x position
                prev_x = ((racer.position - racer.speed) / self.distance) * (self.window.width - 100)
                
                # Check if racer passed through gate (crossed x boundary and close enough to y)
                if (prev_x <= gate_left and racer_x >= gate_left and  # Crossed left boundary
                    racer_x <= gate_right and  # Still within gate
                    abs(racer.current_lane_position - gate_y) < gate.size/2):  # Vertically aligned
                    gate.activated = True
                    racer.apply_speed_boost()  # Apply speed boost instead of boost_multiplier

    def _update_racer_state(self, racer):
        """Update racer state including events, health, and position"""
        # Update event duration
        if racer.active_event:
            racer.event_duration -= 1
            if racer.event_duration <= 0:
                racer.active_event = None
        
        # Check for new random event
        if not racer.active_event:
            for event in self.events:
                if random.random() < event.probability:
                    if event.lethal:
                        self.window.play_sound('explosion')
                    elif event.name == "Engine Trouble":
                        self.window.play_sound('engine_trouble')
                    elif event.name == "Sand Storm":
                        self.window.play_sound('sand_storm')
                    elif event.name == "Debris Hit":
                        self.window.play_sound('debris_hit')
                    
                    racer.apply_event(event)
                    self.window.add_event_message(racer.name, event.name, event.lethal)
                    break
        
        # Calculate movement
        base_movement = random.uniform(1.0, 2.0) * racer.speed * 20 * racer.boost_multiplier
        if racer.active_event:
            base_movement *= racer.active_event.speed_modifier
        
        # Update position
        racer.position += base_movement
        if racer.position >= self.distance:
            if not racer.finished:
                self.window.play_sound('finish')
                racer.finished = True
                racer.position = self.distance
                if racer not in self.finished_racers:
                    self.finished_racers.append(racer)
        
        # Update speed and health
        racer.update_speed()
        racer.update_health()
    
    # ...rest of the Race class methods...

# ...rest of the file...

def main():
    root = tk.Tk()
    race_window = RaceWindow(root)
    
    racers = [f"Pod {i+1}" for i in range(6)]  # Create 6 racers
    race = Race(25000, racers, race_window)  # Updated to 25,000 meters
    
    def update_race():
        if not race.started or not race.is_race_finished():
            race.update()
            if race.started and not race.preview:  # Only show status after preview and countdown
                race.display_status()
            root.after(1400 if race.countdown >= 0 else 20, update_race)  # Even faster update rate
        else:
            print("\nRace finished!")
            # Show all racers in final standings
            race_window.draw_podium(race.finished_racers)
            # Print full results
            for i, racer in enumerate(race.finished_racers, 1):
                print(f"{i}. {racer.name}")

    try:
        update_race()
        root.mainloop()
    finally:
        pygame.mixer.quit()  # Clean up pygame mixer

if __name__ == "__main__":
    main()

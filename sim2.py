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
        self.lethal = lethal

class Obstacle:
    def __init__(self, lane, x_pos, size=20):
        self.lane = lane
        self.x_pos = x_pos
        self.size = size
        self.speed = 15  # Speed of approach
        # Add vertical offset within lane (-1 for top, 0 for center, 1 for bottom)
        self.y_offset = random.choice([-0.5, 0, 0.5])
        
    def update(self):
        self.x_pos -= self.speed
        return self.x_pos > -self.size  # Return False when off screen

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
        self.pod_colors = ['#FF0000', '#00FF00', '#0088FF', '#FF00FF']  # Red, Green, Blue, Magenta
        self.pod_shapes = self.create_pod_shapes()
        self.race_started = False
        self.start_button = None
        self.button_frame = None  # Add reference to button frame
        self.event_messages = []  # List to store active event messages
        
    def create_pod_shapes(self):
        # Define complex pod shapes as coordinate lists - flipped horizontally
        shapes = [
            [(30,0), (10,8), (0,0), (10,-8)],    # Arrow shape
            [(30,0), (5,10), (10,0), (5,-10)],   # Diamond shape
            [(30,0), (0,5), (5,0), (0,-5)],      # Dart shape
            [(30,0), (10,5), (0,0), (10,-5)]     # Teardrop shape
        ]
        return shapes
        
    def draw_race(self, racers, distance, obstacles):
        self.canvas.delete("all")
        
        # 1. Draw background elements first
        # Draw background dunes at the very back
        for x, y, size in self.dunes:
            points = [
                (x - size, y + size/2),  # Move dunes lower
                (x - size/2, y + size/3),
                (x, y),
                (x + size/2, y + size/3),
                (x + size, y + size/2)
            ]
            self.canvas.create_polygon(points, 
                                    fill='#B8860B',
                                    outline='#DAA520')
        
        # 2. Draw sand particles in background
        for i, particle in enumerate(self.sand_particles):
            x, y, size = particle
            x = (x + random.uniform(1, 3)) % self.width
            y = (y + random.uniform(-0.5, 0.5)) % self.height
            self.sand_particles[i] = (x, y, size)
            
            # Only draw particles if they're in the background area
            if y > self.height/2:  # Only draw particles in lower half of screen
                self.canvas.create_oval(x, y, x+size, y+size, 
                                      fill='#FFE4B5',
                                      outline='#DEB887')
        
        # 3. Draw track elements
        # More visible track lanes with Tatooine style
        lane_height = self.height / len(racers)
        for i in range(len(racers) + 1):
            y = i * lane_height
            self.canvas.create_line(0, y, self.width, y, 
                                  fill='#FFFFFF',  # Make lanes more visible
                                  dash=(8,4),
                                  width=2)  # Make lines thicker
        
        # Update finish line to look like ancient stone markers
        finish_x = self.width - 60
        self.canvas.create_rectangle(finish_x-2, 0, finish_x + 22, self.height, 
                                   fill='#8B4513',
                                   outline='#654321')
        for i in range(self.height // 20):
            y = i * 20
            if i % 2:
                self.canvas.create_rectangle(finish_x, y, finish_x + 20, y+10, 
                                          fill='#DEB887')
        
        # Draw obstacles
        for obstacle in obstacles:
            base_y = obstacle.lane * lane_height + lane_height/2
            y = base_y + (obstacle.y_offset * 60)  # Use same max offset as racers
            # Draw obstacle as red hexagon
            points = []
            for i in range(6):
                angle = i * math.pi / 3
                px = obstacle.x_pos + obstacle.size * math.cos(angle)
                py = y + obstacle.size * math.sin(angle)
                points.append((px, py))
            self.canvas.create_polygon(points, 
                                    fill='#FF0000', 
                                    outline='#FFFFFF',
                                    width=2)
        
        # 4. Draw racers and HUD on top of everything
        # Draw racers with adjusted positions
        for i, racer in enumerate(racers):
            # Calculate positions
            x = (racer.position / distance) * (self.width - 100)  # Adjust for wider screen
            base_y = i * lane_height + lane_height/2
            y = base_y + racer.y_offset  # Apply vertical offset
            
            # Draw pod
            pod_shape = [(x+cx, y+cy) for cx,cy in self.pod_shapes[i]]
            self.canvas.create_polygon(pod_shape, 
                                    fill=self.pod_colors[i],
                                    outline='white',
                                    width=2)
            
            # Add engine glow if not finished
            if not racer.finished:
                glow_x = x - 5
                self.canvas.create_oval(glow_x-10, y-5, glow_x, y+5, 
                                      fill='#FF9933', outline='#FF6600')
            
            # Skip destroyed pods
            if racer.destroyed:
                continue
                
            # Draw pod with event effects
            if racer.active_event:
                # Add visual effect for active event
                effect_color = '#FF0000' if racer.active_event.lethal else '#FFFF00'
                self.canvas.create_oval(x-20, y-20, x+20, y+20,
                                     outline=effect_color,
                                     width=2)
            
            # Draw HUD information at bottom of lane
            lane_bottom = (i + 1) * lane_height - 10  # 10 pixels from bottom of lane
            
            # Status text (name and events)
            status_color = self.pod_colors[i]
            status_text = racer.name
            if racer.destroyed:
                status_text += " [DESTROYED]"
                status_color = '#FF0000'
            elif racer.active_event:
                status_text += f" [{racer.active_event.name}]"
            
            self.canvas.create_text(10, lane_bottom, 
                                  text=status_text, 
                                  fill=status_color, 
                                  anchor='sw',  # Southwest anchor for bottom alignment
                                  font=('Arial', 12, 'bold'))
            
            # Skip destroyed pods
            if racer.destroyed:
                continue
            
            # Speed and distance info
            self.canvas.create_text(200, lane_bottom,
                                  text=f"Speed: {racer.speed:.2f}x",
                                  fill='white',
                                  anchor='sw')
            self.canvas.create_text(350, lane_bottom,
                                  text=f"Distance: {racer.position:.1f}m",
                                  fill='white',
                                  anchor='sw')
            
            # Progress bar above stats
            progress = (racer.position / distance) * 150
            bar_y = lane_bottom - 20  # 20 pixels above stats
            self.canvas.create_rectangle(500, bar_y, 650, bar_y+5, outline='white')
            self.canvas.create_rectangle(500, bar_y, 500+progress, bar_y+5, 
                                      fill=self.pod_colors[i])
        
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

    def draw_countdown(self, count):
        self.canvas.delete("all")
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
        
        # Draw sand particle background
        for particle in self.sand_particles:
            x, y, size = particle
            self.canvas.create_oval(x, y, x+size, y+size, 
                                  fill='#F4A460', 
                                  outline='#DEB887')
        
        # Draw leaderboard title
        self.canvas.create_text(self.width/2, 50,
                              text="FINAL STANDINGS",
                              fill='#FF4500',
                              font=('Arial', 36, 'bold'))
        
        # Draw leaderboard entries
        entry_height = 80  # Height for each leaderboard entry
        start_y = 150     # Starting Y position
        board_width = 600 # Width of leaderboard entries
        
        for i, racer in enumerate(racers):
            y = start_y + (i * entry_height)
            x = self.width/2
            
            # Create background rectangle for entry
            self.canvas.create_rectangle(x - board_width/2, y,
                                       x + board_width/2, y + entry_height - 10,
                                       fill='#1a2f2f',
                                       outline=self.pod_colors[racers.index(racer)])
            
            # Draw position number
            position_text = f"#{i+1}"
            self.canvas.create_text(x - board_width/2 + 50, y + entry_height/2,
                                  text=position_text,
                                  fill='#FFFFFF',
                                  font=('Arial', 24, 'bold'))
            
            # Draw pod
            pod_y = y + entry_height/2
            pod_x = x - board_width/2 + 120
            pod_shape = [(pod_x+cx, pod_y+cy) for cx,cy in self.pod_shapes[racers.index(racer)]]
            self.canvas.create_polygon(pod_shape,
                                    fill=self.pod_colors[racers.index(racer)],
                                    outline='white',
                                    width=2)
            
            # Draw racer name and final stats
            name_x = x + 50
            self.canvas.create_text(name_x, y + entry_height/2 - 15,
                                  text=racer.name,
                                  fill=self.pod_colors[racers.index(racer)],
                                  anchor='w',
                                  font=('Arial', 20, 'bold'))
            
            self.canvas.create_text(name_x, y + entry_height/2 + 15,
                                  text=f"Final Speed: {racer.speed:.2f}x",
                                  fill='white',
                                  anchor='w',
                                  font=('Arial', 16))
            
            # Add destroyed status if applicable
            if racer.destroyed:
                self.canvas.create_text(x + board_width/2 - 50, y + entry_height/2,
                                      text="DESTROYED",
                                      fill='#FF0000',
                                      font=('Arial', 16, 'bold'))
        
        self.master.update()
    
    def draw_odds_screen(self, racers):
        self.canvas.delete("all")
        
        # Draw sand particles
        for particle in self.sand_particles:
            x, y, size = particle
            self.canvas.create_oval(x, y, x+size, y+size, 
                                  fill='#F4A460', 
                                  outline='#DEB887')
        
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
            
            # Draw racer info
            self.canvas.create_text(x + card_width - 100, y + 40,
                                  text=racer.name,
                                  fill=self.pod_colors[i],
                                  font=('Arial', 16, 'bold'))
            self.canvas.create_text(x + card_width - 100, y + 70,
                                  text=f"Base Speed: {racer.speed:.2f}x",
                                  fill='white',
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
        self.speed = random.uniform(0.8, 1.2)
        self.active_event = None
        self.event_duration = 0
        self.destroyed = False
        self.y_offset = 0  # Vertical offset from lane center
        self.target_y_offset = 0  # Target position for smooth movement
        self.max_y_offset = 60  # Increased for more vertical movement
        self.y_speed = 4  # Faster vertical movement
        self.dodge_direction = 0  # -1 for up, 1 for down, 0 for center
        self.target_y = 0  # Target y position within lane
        
    def apply_event(self, event):
        self.active_event = event
        self.event_duration = event.duration
        if event.lethal:
            self.destroyed = True
            self.finished = True

    def update_vertical_position(self):
        # More fluid vertical movement
        if self.dodge_direction != 0:
            target = self.dodge_direction * self.max_y_offset
            if self.y_offset < target:
                self.y_offset = min(self.y_offset + self.y_speed, target)
            elif self.y_offset > target:
                self.y_offset = max(self.y_offset - self.y_speed, target)
        else:
            # Return to center when no obstacles
            if self.y_offset > 0:
                self.y_offset = max(self.y_offset - self.y_speed, 0)
            elif self.y_offset < 0:
                self.y_offset = min(self.y_offset + self.y_speed, 0)

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
        self.obstacle_spawn_rate = 0.015  # Reduced spawn rate
        self.min_obstacle_spacing = 300  # Increased spacing
        
    def update(self):
        if self.preview:
            if self.window.race_started:
                self.preview = False
            else:
                self.window.draw_odds_screen(self.racers)
                return
                
        if self.countdown > 0:
            self.window.draw_countdown(self.countdown)
            self.countdown -= 1
            return
        elif self.countdown == 0:
            self.window.draw_countdown(self.countdown)
            self.countdown -= 1
            self.started = True
            return
            
        # Spawn new obstacles
        if random.random() < self.obstacle_spawn_rate:
            # Check if there's enough space for a new obstacle
            can_spawn = True
            spawn_lane = random.randint(0, len(self.racers)-1)
            for obs in self.obstacles:
                if obs.lane == spawn_lane and obs.x_pos > self.window.width - self.min_obstacle_spacing:
                    can_spawn = False
                    break
            
            if can_spawn:
                self.obstacles.append(Obstacle(spawn_lane, self.window.width))
        
        # Update obstacles
        self.obstacles = [obs for obs in self.obstacles if obs.update()]
        
        # Update racers with obstacle avoidance
        for racer in self.racers:
            if not racer.finished and not racer.destroyed:
                # Check for collisions with obstacles
                racer_x = (racer.position / self.distance) * (self.window.width - 100)
                for obs in self.obstacles:
                    if obs.lane == self.racers.index(racer):
                        if abs(racer_x - obs.x_pos) < obs.size:
                            # Collision! Apply penalty
                            racer.speed *= 0.8  # Slow down
                
                # Update event duration
                if racer.active_event:
                    racer.event_duration -= 1
                    if racer.event_duration <= 0:
                        racer.active_event = None
                
                # Check for new random event
                if not racer.active_event:
                    for event in self.events:
                        if random.random() < event.probability:
                            # Play appropriate sound for event
                            if event.lethal:
                                self.window.play_sound('explosion')
                            elif event.name == "Engine Trouble":
                                self.window.play_sound('engine_trouble')
                            elif event.name == "Sand Storm":
                                self.window.play_sound('sand_storm')
                            elif event.name == "Debris Hit":
                                self.window.play_sound('debris_hit')
                            
                            racer.apply_event(event)
                            # Add event notification
                            self.window.add_event_message(racer.name, event.name, event.lethal)
                            break
                
                # Calculate movement with event modifications and increased base speed
                base_movement = random.uniform(1.0, 2.0) * racer.speed * 20  # Increased speed multiplier
                if racer.active_event:
                    base_movement *= racer.active_event.speed_modifier
                
                racer.position += base_movement
                if racer.position >= self.distance:
                    if not racer.finished:  # Only play finish sound once
                        self.window.play_sound('finish')
                    racer.finished = True
                    racer.position = self.distance
                    if racer not in self.finished_racers:
                        self.finished_racers.append(racer)
                
                # Check for upcoming obstacles
                racer_x = (racer.position / self.distance) * (self.window.width - 100)
                
                # Reset dodge direction if no obstacles nearby
                nearest_obstacle = None
                min_distance = float('inf')
                
                # Find nearest obstacle in racer's lane
                for obs in self.obstacles:
                    if obs.lane == self.racers.index(racer):
                        distance = obs.x_pos - racer_x
                        if 0 < distance < min_distance:
                            min_distance = distance
                            nearest_obstacle = obs
                
                # Update dodge behavior with chance to not dodge
                if nearest_obstacle and min_distance < 300:  # Detection range
                    if racer.dodge_direction == 0:
                        # 80% chance to attempt dodge
                        if random.random() < 0.8:
                            # Choose dodge direction based on position in lane
                            lane_center = (self.racers.index(racer) + 0.5) * (self.window.height / len(self.racers))
                            racer.dodge_direction = -1 if racer.y_offset < lane_center else 1
                        else:
                            # No dodge attempt
                            racer.dodge_direction = 0
                elif min_distance > 100:  # Return to center after passing obstacle
                    racer.dodge_direction = 0
                
                # Hit detection happens regardless of dodge attempt
                if nearest_obstacle and abs(racer_x - nearest_obstacle.x_pos) < nearest_obstacle.size:
                    racer.speed *= 0.8  # Slow down
                
                # Update vertical position
                racer.update_vertical_position()
                
        self.window.draw_race(self.racers, self.distance, self.obstacles)  # Add obstacles parameter
    
    def is_race_finished(self):
        return all(racer.finished for racer in self.racers)
    
    def display_status(self):
        print("\n" + "=" * 50)
        for racer in self.racers:
            progress = int((racer.position / self.distance) * 20)
            print(f"{racer.name}: {'#' * progress}{'-' * (20-progress)} {racer.position:.1f}m")

def main():
    root = tk.Tk()
    race_window = RaceWindow(root)
    
    racers = ["Pod 1", "Pod 2", "Pod 3", "Pod 4"]
    race = Race(25000, racers, race_window)  # Updated to 25,000 meters
    
    def update_race():
        if not race.started or not race.is_race_finished():
            race.update()
            if race.started and not race.preview:  # Only show status after preview and countdown
                race.display_status()
            root.after(1400 if race.countdown >= 0 else 20, update_race)  # Even faster update rate
        else:
            print("\nRace finished!")
            # Show podium with first 3 finishers
            race_window.draw_podium(race.finished_racers[:3])
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

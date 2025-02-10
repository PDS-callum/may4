from utils.racer import Racer
from utils.events import Obstacle, SpeedGate,  Event
import random

class Race:
    def __init__(self, distance, racers, window):
        self.distance = distance
        self.racers = [Racer(name) for name in racers]
        self.window = window  # Set the window attribute before using it
        for i, racer in enumerate(self.racers):
            racer.set_initial_y_position(i, len(self.racers), self.window.height)
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
        self.obstacle_spawn_rate = 0.03  # Increased spawn rate
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
        for racer in self.racers:
            if not racer.finished and not racer.destroyed:
                self._update_racer(racer)

        self.window.draw_race(self.racers, self.distance, self.obstacles, self.speed_gates)

    def _handle_spawns(self):
        active_racers = [racer for racer in self.racers if not racer.finished and not racer.destroyed]
        
        if not active_racers:
            return

        if random.random() < self.obstacle_spawn_rate:
            self._try_spawn_obstacle()

        if random.random() < self.gate_spawn_rate:
            self._try_spawn_gate()

    def _try_spawn_obstacle(self):
        if not any(obs.x_pos > self.window.width - self.min_obstacle_spacing for obs in self.obstacles):
            new_obstacle = Obstacle(self.window.width,self.window.height)
            self.obstacles.append(new_obstacle)

    def _try_spawn_gate(self):
        if not any(gate.x_pos > self.window.width - self.min_gate_spacing for gate in self.speed_gates):
            new_gate = SpeedGate(self.window.width,self.window.height)
            self.speed_gates.append(new_gate)

    def _update_racer(self, racer):
        racer_x = (racer.position / self.distance) * (self.window.width - 100)

        nearest_gate = self._find_nearest(self.speed_gates, racer_x, lambda g: not g.activated)
        nearest_obstacle = self._find_nearest(self.obstacles, racer_x)

        racer.update_movement(nearest_gate, nearest_obstacle, self.window.height)
        racer.update_position(self.distance, self.window.height)  # Update racer's position and y position
        
        self._handle_collisions(racer, racer_x)
        self._update_racer_state(racer)

    def _find_nearest(self, objects, racer_x, condition=None):
        nearest = None
        min_dist = float('inf')
        
        for obj in objects:
            dist = obj.x_pos - racer_x
            if dist > 0 and dist < min_dist and (condition is None or condition(obj)):
                min_dist = dist
                nearest = (obj, dist)
        
        return nearest

    def _handle_collisions(self, racer, racer_x):
        for obs in self.obstacles:
            if (racer_x >= obs.x_pos - obs.size/2 and 
                racer_x <= obs.x_pos + obs.size/2):
                
                obstacle_y = obs.y_pos  # Use y_pos for vertical location
                if abs(racer.y_offset - obstacle_y) < obs.size:
                    racer.take_obstacle_damage()
                    racer.apply_speed_penalty()
                else:
                    racer.apply_speed_penalty()
        
        for gate in self.speed_gates:
            if not gate.activated:
                gate_left = gate.x_pos - gate.size/2
                gate_right = gate.x_pos + gate.size/2
                gate_y = gate.y_offset * self.window.height
                
                prev_x = ((racer.position - racer.speed * racer.boost_multiplier) / self.distance) * (self.window.width - 100)
                
                if (prev_x <= gate_left and racer_x >= gate_left and
                    racer_x <= gate_right and
                    abs(racer.y_offset - gate_y) < gate.size/2):
                    gate.activated = True
                    racer.apply_speed_boost()

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
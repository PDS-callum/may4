import random
import math

class Racer:
    def __init__(self, name):
        # Basic properties
        self.name = name
        self.finished = False
        self.destroyed = False
        
        # Position and movement
        self.x = 0  # X coordinate
        self.y = 0  # Y coordinate
        self.velocity_x = random.uniform(0.3, 0.5)  # Reduced from (1, 1.4)
        self.velocity_y = 0  # Vertical speed
        self.max_velocity_y = 3.0  # Reduced from 6.0
        self.acceleration = 0.15  # Reduced from 0.3
        self.friction = 0.05  # Reduced from 0.1 for smoother movement
        
        # Race stats
        self.base_speed = self.velocity_x
        self.agility = random.uniform(0.8, 1.5)
        self.max_health = random.randint(80, 150)
        self.current_health = self.max_health
        
        # Status effects
        self.active_event = None
        self.event_duration = 0
        self.boost_multiplier = 1.0
        self.boost_timer = 0
        
        # Visual effects
        self.explosion_frame = 0
        self.max_explosion_frames = 30
        self.is_exploding = False
        self.boost_animation_frames = 0
        self.max_boost_animation_frames = 20
        
        # Health regeneration
        self.health_regen_timer = 0
        self.health_regen_delay = 500
        self.health_regen_rate = 0.2

    def set_initial_position(self, total_racers, index, window_height):
        """Set the initial y position based on total racers"""
        lane_height = window_height / (total_racers + 1)
        self.y = lane_height * (index + 1)
        self.target_y = self.y

    def update_position(self, delta_time, window_width, window_height):
        """Update position based on velocities and time"""
        # Update x position
        base_movement = self.velocity_x * self.boost_multiplier * delta_time
        if self.active_event:
            base_movement *= self.active_event.speed_modifier
        
        self.x += base_movement
        
        # Update y position with smooth acceleration and deceleration
        if abs(self.velocity_y) > 0:
            self.y += self.velocity_y * delta_time * self.agility  # Added agility factor
            self.velocity_y *= (1 - self.friction)
            if abs(self.velocity_y) < 0.1:
                self.velocity_y = 0
        
        # Keep racer within screen bounds with bounce effect
        if self.y < 50:
            self.y = 50
            self.velocity_y = abs(self.velocity_y) * 0.5  # Bounce up
        elif self.y > window_height - 50:
            self.y = window_height - 50
            self.velocity_y = -abs(self.velocity_y) * 0.5  # Bounce down
        
        # Check if finished
        if self.x >= window_width - 100:
            self.x = window_width - 100
            self.finished = True

    def move_vertical(self, direction):
        """Apply vertical movement (-1 for up, 1 for down)"""
        target_velocity = direction * self.max_velocity_y * self.agility
        self.velocity_y = target_velocity

    def apply_event(self, event):
        """Apply an event effect to the racer"""
        self.active_event = event
        self.event_duration = event.duration
        if event.lethal:
            self.is_exploding = True
            self.explosion_frame = 0

    def apply_boost(self):
        """Apply a temporary speed boost"""
        self.boost_timer = 45
        self.boost_multiplier = 2.0
        self.boost_animation_frames = self.max_boost_animation_frames

    def update(self, delta_time, window_width, window_height):
        """Main update method to be called each frame"""
        # Update position
        self.update_position(delta_time, window_width, window_height)
        
        # Update boost
        if self.boost_timer > 0:
            self.boost_timer -= 1
            if self.boost_timer == 0:
                self.boost_multiplier = 1.0
        
        # Update event
        if self.active_event:
            self.event_duration -= 1
            if self.event_duration <= 0:
                self.active_event = None
        
        # Update health regeneration
        if self.health_regen_timer < self.health_regen_delay:
            self.health_regen_timer += 1
        elif self.current_health < self.max_health:
            self.current_health = min(self.max_health, 
                                    self.current_health + self.health_regen_rate)
        
        # Update explosion animation
        if self.is_exploding:
            self.explosion_frame += 1
            if self.explosion_frame >= self.max_explosion_frames:
                self.is_exploding = False
                self.destroyed = True
                self.finished = True

    def get_progress(self, race_distance):
        """Get race progress as a percentage"""
        return (self.x / race_distance) * 100

    def get_position(self):
        """Get current coordinates"""
        return (self.x, self.y)
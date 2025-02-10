import random

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
        self.speed_gate_animation_frames = 0
        self.max_speed_gate_animation_frames = 20  # Duration of speed gate animation

    def update_movement(self, nearest_gate, nearest_obstacle, height):
        target_y = self.y_offset
        new_direction = 0

        if nearest_obstacle and nearest_obstacle[1] < self.avoid_range:
            if nearest_obstacle[0].y_pos > self.y_offset:
                target_y = self.y_offset - nearest_obstacle[0].size
            else:
                target_y = self.y_offset + nearest_obstacle[0].size
        elif nearest_gate and nearest_gate[1] < self.seek_range and not nearest_gate[0].activated:
            target_y = nearest_gate[0].y_offset * height

        diff = target_y - self.y_offset
        if abs(diff) > 0.1:
            new_direction = 1 if diff > 0 else -1
        
        if new_direction != self.active_direction:
            self.current_move_speed = self.base_move_speed
            self.active_direction = new_direction
        else:
            self.current_move_speed = min(
                self.current_move_speed + self.acceleration * self.agility,
                self.max_move_speed * self.agility
            )

        if self.active_direction != 0:
            movement = self.current_move_speed * self.active_direction
            self.y_offset += movement

        self.y_offset = max(min(self.y_offset, self.max_y_offset), -self.max_y_offset)

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
        self.speed_gate_animation_frames = self.max_speed_gate_animation_frames  # Start speed gate animation

    def apply_speed_penalty(self):
        """Apply temporary speed reduction from obstacles"""
        self.normal_speed = self.speed  # Store current speed
        self.speed *= self.speed_penalty_amount
        self.speed_effect_timer = self.speed_effect_duration

    def update_position(self, distance, height):
        """Update the racer's position based on speed and events"""
        base_movement = random.uniform(1.0, 2.0) * self.speed * 20 * self.boost_multiplier
        if self.active_event:
            base_movement *= self.active_event.speed_modifier
        
        self.position += base_movement
        if self.position >= distance:
            self.position = distance
            self.finished = True
        
        # Update y position based on y_offset
        self.y_pos = self.y_offset * height

    def set_initial_y_position(self, index, total_racers, height):
        """Set the initial y position of the racer based on its index and total number of racers"""
        self.y_offset = (index + 1) / (total_racers + 1)
        self.y_pos = self.y_offset * height